"""
fingerprintService.py - Motor de fingerprinting (Constellation Map con 3 bandas).

Algoritmo:
1. STFT → espectrograma
2. Por cada frame temporal detecta 3 componentes:
   a) f_peak  — pico dominante en todo el espectro (frecuencia alta)
   b) f_midlow — pico dominante en la mitad inferior (frecuencia media-baja)
   c) distance — distancia entre f_peak y f_midlow (relación espectral)
3. Genera pares constelación: compara el trío (f_peak, f_midlow, dist)
   del frame en segundo t con el del frame en segundo t+0.5 s.
4. Hash = SHA-1(f_peak_t1 | f_midlow_t1 | dist_t1 | f_peak_t2 | f_midlow_t2 | dist_t2)
5. Almacena (hash, anchor_time) en BD.

Búsqueda:
- Genera fingerprints del audio capturado.
- Busca hashes coincidentes en BD y para cada match calcula
  offset_diff = db_anchor_time − query_anchor_time.
- Agrupa matches por (canción, offset_diff).  Si un grupo tiene
  ≥ MIN_MATCHES (25) coincidencias temporalmente coherentes,
  la canción está CONFIRMADA.
"""

import io
import hashlib
import struct
from collections import defaultdict
import numpy as np
from scipy.signal import spectrogram as scipy_spectrogram
from django.db import connection


# ── Configuración ──────────────────────────────────────────────────────
SAMPLE_RATE = 11025            # Remuestreo (suficiente para música)
NPERSEG     = 1024             # Ventana FFT
NOVERLAP    = 512              # Solapamiento
HOP         = NPERSEG - NOVERLAP             # = 512 samples
FPS         = SAMPLE_RATE / HOP              # ≈ 21.5 frames/s
FREQ_QUANT  = 4                # Cuantización de bins (tolerancia ≈43 Hz)

# Deltas temporales para pares constelación (en frames).
# 0.5 s ≈ 11 frames.  Usamos 9, 11, 13 para mayor robustez.
TARGET_DELTAS = [9, 11, 13]

# Mínimo de matches temporalmente coherentes para confirmar
MIN_MATCHES = 25


# ── WAV Parser ─────────────────────────────────────────────────────────
def _parse_wav_bytes(wav_bytes):
    """
    Parsea WAV bytes manualmente (PCM 8/16/32-bit, IEEE float 32/64).
    Retorna (sample_rate, samples_mono_float32).
    """
    data = io.BytesIO(wav_bytes)

    riff = data.read(4)
    if riff != b'RIFF':
        raise ValueError("No es un archivo WAV válido (falta RIFF)")
    data.read(4)  # file size
    wave = data.read(4)
    if wave != b'WAVE':
        raise ValueError("No es un archivo WAV válido (falta WAVE)")

    fmt_found = False
    sample_rate = 44100
    num_channels = 1
    bits_per_sample = 16
    audio_format = 1
    audio_data = None

    while True:
        chunk_id = data.read(4)
        if len(chunk_id) < 4:
            break
        chunk_size = struct.unpack('<I', data.read(4))[0]

        if chunk_id == b'fmt ':
            fmt_data = data.read(chunk_size)
            audio_format   = struct.unpack('<H', fmt_data[0:2])[0]
            num_channels   = struct.unpack('<H', fmt_data[2:4])[0]
            sample_rate    = struct.unpack('<I', fmt_data[4:8])[0]
            bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
            fmt_found = True
        elif chunk_id == b'data':
            audio_data = data.read(chunk_size)
            break
        else:
            data.read(chunk_size)

    if not fmt_found or audio_data is None:
        raise ValueError("WAV incompleto: falta chunk fmt o data")

    if audio_format == 3:  # IEEE float
        dtype = np.float32 if bits_per_sample == 32 else np.float64
        samples = np.frombuffer(audio_data, dtype=dtype).astype(np.float32)
    elif audio_format == 1:  # PCM
        if bits_per_sample == 16:
            samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        elif bits_per_sample == 8:
            samples = np.frombuffer(audio_data, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
        elif bits_per_sample == 32:
            samples = np.frombuffer(audio_data, dtype=np.int32).astype(np.float32) / 2147483648.0
        else:
            raise ValueError(f"Bits por sample no soportados: {bits_per_sample}")
    else:
        raise ValueError(f"Formato de audio no soportado: {audio_format}")

    if num_channels > 1:
        samples = samples.reshape(-1, num_channels).mean(axis=1)

    return sample_rate, samples


def _resample(samples, orig_sr, target_sr):
    """Resamplea audio a la frecuencia objetivo (interpolación lineal)."""
    if orig_sr == target_sr:
        return samples
    target_len = int(len(samples) * target_sr / orig_sr)
    indices = np.linspace(0, len(samples) - 1, target_len)
    return np.interp(indices, np.arange(len(samples)), samples).astype(np.float32)


# ── Extracción de picos por banda ──────────────────────────────────────
def _extract_band_peaks(Sxx_db):
    """
    Para cada frame temporal extrae:
      f_peak   — bin cuantizado del pico dominante (espectro completo)
      f_midlow — bin cuantizado del pico en la mitad inferior
      distance — f_peak - f_midlow  (relación espectral)

    Retorna lista de tuplas (f_peak_q, f_midlow_q, distance) por frame.
    """
    n_bins   = Sxx_db.shape[0]          # 513 para NPERSEG=1024
    n_frames = Sxx_db.shape[1]
    mid_bin  = n_bins // 2              # ≈ 256 (frontera mitad inferior)

    frame_peaks = []
    for t in range(n_frames):
        col = Sxx_db[:, t]

        # Pico dominante en todo el espectro (primera frecuencia)
        f_peak = int(np.argmax(col[1:])) + 1        # saltar DC (bin 0)

        # Pico dominante en la mitad inferior (frecuencia media-baja)
        f_midlow = int(np.argmax(col[1:mid_bin])) + 1

        # Cuantizar para tolerancia al ruido/micrófono
        fp_q = f_peak   // FREQ_QUANT
        fm_q = f_midlow // FREQ_QUANT

        # Distancia espectral (tercera componente)
        dist = fp_q - fm_q

        frame_peaks.append((fp_q, fm_q, dist))

    return frame_peaks


# ── Generación de fingerprints ─────────────────────────────────────────
def generate_fingerprints(wav_bytes):
    """
    Genera fingerprints del audio WAV.

    Algoritmo:
    1. Parsea WAV → mono → resample a 11025 Hz.
    2. STFT → espectrograma en dB.
    3. Extrae (f_peak, f_midlow, distance) por frame.
    4. Para cada frame t1 y cada delta en TARGET_DELTAS,
       toma t2 = t1 + delta y genera:
       hash = SHA-1(fp1|fm1|d1|fp2|fm2|d2)
       Se almacena (hash, t1).

    Retorna list[ (hash_hex, anchor_frame_int) ].
    """
    orig_sr, samples = _parse_wav_bytes(wav_bytes)
    samples = _resample(samples, orig_sr, SAMPLE_RATE)

    if len(samples) < NPERSEG:
        return []

    # Espectrograma (STFT)
    _freqs, _times, Sxx = scipy_spectrogram(
        samples,
        fs=SAMPLE_RATE,
        nperseg=NPERSEG,
        noverlap=NOVERLAP,
        scaling='spectrum',
    )
    Sxx_db = 10 * np.log10(Sxx + 1e-10)

    # Extraer tríos (f_peak, f_midlow, distance) por frame
    frame_peaks = _extract_band_peaks(Sxx_db)
    n_frames = len(frame_peaks)

    # Generar pares constelación con cada delta
    max_delta = max(TARGET_DELTAS)
    fingerprints = []

    for t1 in range(n_frames - max_delta):
        fp1, fm1, d1 = frame_peaks[t1]
        for delta in TARGET_DELTAS:
            t2 = t1 + delta
            fp2, fm2, d2 = frame_peaks[t2]

            # Hash = SHA-1 del par de tríos espectrales
            raw = f"{fp1}|{fm1}|{d1}|{fp2}|{fm2}|{d2}"
            h = hashlib.sha1(raw.encode()).hexdigest()
            fingerprints.append((h, int(t1)))

    return fingerprints


# ── Almacenamiento ─────────────────────────────────────────────────────
def store_fingerprints(song_id, fingerprints):
    """Guarda fingerprints en BD (batch de 500)."""
    if not fingerprints:
        return 0

    with connection.cursor() as cursor:
        batch_size = 500
        total = 0

        for i in range(0, len(fingerprints), batch_size):
            batch = fingerprints[i:i + batch_size]
            values = []
            params = []
            for h, t in batch:
                values.append("(%s, %s, %s)")
                params.extend([song_id, h, t])

            sql = f"INSERT INTO app.fingerprints (song_id, hash, time_offset) VALUES {','.join(values)}"
            cursor.execute(sql, params)
            total += len(batch)

        cursor.execute(
            "UPDATE app.songs SET fingerprint_count = %s, updated_at = NOW() WHERE id = %s",
            [total, song_id],
        )

    return total


# ── Búsqueda con coherencia temporal ──────────────────────────────────
def search_by_fingerprints(fingerprints):
    """
    Busca coincidencias en BD usando coherencia temporal.

    1. Para cada hash del query, busca registros en BD.
    2. Por cada match calcula offset_diff = db_time − query_time.
    3. Agrupa por (song_id, offset_diff).
    4. El grupo más grande indica la mejor coincidencia.
    5. Si el grupo ≥ MIN_MATCHES (25) → confirmado.

    Retorna dict con resultado o None.
    """
    if not fingerprints:
        return None

    # Mapear hash → lista de query_times (un hash puede repetirse)
    hash_to_qtimes = defaultdict(list)
    for h, t in fingerprints:
        hash_to_qtimes[h].append(t)

    unique_hashes = list(hash_to_qtimes.keys())

    # Buscar en BD (lotes de 500)
    db_rows = []
    batch_size = 500
    for i in range(0, len(unique_hashes), batch_size):
        batch = unique_hashes[i:i + batch_size]
        ph = ','.join(['%s'] * len(batch))
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT f.song_id, f.hash, f.time_offset,
                       s.title, s.artist
                FROM app.fingerprints f
                JOIN app.songs s ON s.id = f.song_id
                WHERE f.hash IN ({ph})
            """, batch)
            cols = [c[0] for c in cursor.description]
            db_rows.extend(dict(zip(cols, row)) for row in cursor.fetchall())

    if not db_rows:
        return None

    # Coherencia temporal: agrupar por (song_id, offset_diff)
    coherent = defaultdict(int)   # (song_id, offset_diff) → count
    song_info = {}                # song_id → {title, artist}

    for m in db_rows:
        sid      = m['song_id']
        db_time  = m['time_offset']
        db_hash  = m['hash']
        song_info[sid] = {'title': m['title'], 'artist': m['artist']}

        for qt in hash_to_qtimes.get(db_hash, []):
            offset_diff = db_time - qt
            coherent[(sid, offset_diff)] += 1

    if not coherent:
        return None

    # Mejor grupo coherente por canción
    song_best = {}   # song_id → max coherent count
    for (sid, _od), cnt in coherent.items():
        if sid not in song_best or cnt > song_best[sid]:
            song_best[sid] = cnt

    # Mejor global
    best_sid = max(song_best, key=song_best.get)
    best_count = song_best[best_sid]

    is_confirmed = best_count >= MIN_MATCHES
    confidence = round((best_count / len(fingerprints)) * 100, 1)

    # Candidatos (top 5)
    candidates = []
    for sid, cnt in sorted(song_best.items(), key=lambda x: x[1], reverse=True)[:5]:
        c_conf = round((cnt / len(fingerprints)) * 100, 1)
        candidates.append({
            'song_id': sid,
            'title':   song_info[sid]['title'],
            'artist':  song_info[sid]['artist'],
            'matched_hashes': cnt,
            'confidence': c_conf,
        })

    return {
        'song_id':        best_sid,
        'title':          song_info[best_sid]['title'],
        'artist':         song_info[best_sid]['artist'],
        'matched_hashes': best_count,
        'query_hashes':   len(fingerprints),
        'confidence':     confidence,
        'is_confirmed':   is_confirmed,
        'min_required':   MIN_MATCHES,
        'candidates':     candidates,
    }


# ── Regeneración de fingerprints ──────────────────────────────────────
def regenerate_song(song_id):
    """
    Regenera los fingerprints de UNA canción usando el audio_data
    ya almacenado en BD.  No necesita re-subir el archivo.

    1. Lee audio_data binario de la canción.
    2. Borra fingerprints viejos.
    3. Genera y guarda fingerprints con el algoritmo actual.

    Retorna cantidad de fingerprints generados.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, title, audio_data FROM app.songs WHERE id = %s",
            [song_id],
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Canción {song_id} no encontrada")

        sid, title, audio_data = row
        if not audio_data:
            raise ValueError(f"Canción {song_id} ('{title}') no tiene audio almacenado")

        wav_bytes = bytes(audio_data)

    # Borrar fingerprints anteriores
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM app.fingerprints WHERE song_id = %s", [song_id])

    # Generar nuevos fingerprints
    fps = generate_fingerprints(wav_bytes)
    count = store_fingerprints(song_id, fps)
    return count


def regenerate_all():
    """
    Regenera fingerprints de TODAS las canciones.
    Útil al cambiar parámetros del algoritmo.

    Retorna dict con resumen: {total_songs, processed, results: [{id, title, fp_count}]}
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, title FROM app.songs ORDER BY id")
        songs = cursor.fetchall()

    results = []
    for sid, title in songs:
        try:
            count = regenerate_song(sid)
            results.append({'id': sid, 'title': title, 'fingerprints': count, 'status': 'ok'})
        except Exception as e:
            results.append({'id': sid, 'title': title, 'fingerprints': 0, 'status': f'error: {e}'})

    return {
        'total_songs': len(songs),
        'processed': len(results),
        'results': results,
    }
