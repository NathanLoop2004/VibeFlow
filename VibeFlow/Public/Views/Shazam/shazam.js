/* ====================================================================
   Shazam MVP — VibeFlow
   Upload songs → generate fingerprints → record 30s → search matches
   ==================================================================== */

const API = '/api/shazam/';

/* ── Auth helpers ── */
function getToken() { return localStorage.getItem('vf_token') || ''; }
function authH(extra = {}) { return { 'Authorization': 'Bearer ' + getToken(), ...extra }; }

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 5000);
}

/* ====================================================================
   WAV Encoder — convierte AudioBuffer → ArrayBuffer (PCM 16-bit WAV)
   Esto permite enviar cualquier formato de audio al server como WAV puro
   ya que el navegador decodifica MP3/OGG/etc. con decodeAudioData().
   ==================================================================== */
function audioBufferToWav(audioBuffer) {
    const numChannels = 1; // mono
    const sampleRate = audioBuffer.sampleRate;
    const format = 1; // PCM
    const bitsPerSample = 16;

    // Downmix a mono
    let samples;
    if (audioBuffer.numberOfChannels === 1) {
        samples = audioBuffer.getChannelData(0);
    } else {
        const left = audioBuffer.getChannelData(0);
        const right = audioBuffer.getChannelData(1);
        samples = new Float32Array(left.length);
        for (let i = 0; i < left.length; i++) {
            samples[i] = (left[i] + right[i]) / 2;
        }
    }

    const byteRate = sampleRate * numChannels * bitsPerSample / 8;
    const blockAlign = numChannels * bitsPerSample / 8;
    const dataSize = samples.length * numChannels * bitsPerSample / 8;
    const bufferSize = 44 + dataSize;
    const buffer = new ArrayBuffer(bufferSize);
    const view = new DataView(buffer);

    // RIFF header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, bufferSize - 8, true);
    writeString(view, 8, 'WAVE');

    // fmt chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);           // chunk size
    view.setUint16(20, format, true);       // PCM
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);

    // data chunk
    writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    // PCM samples
    let offset = 44;
    for (let i = 0; i < samples.length; i++) {
        const s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        offset += 2;
    }

    return buffer;
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    const chunkSize = 8192;
    for (let i = 0; i < bytes.length; i += chunkSize) {
        binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
    }
    return btoa(binary);
}

/* ====================================================================
   Drop Zone — soporte drag & drop + click
   ==================================================================== */
const dropZone = document.getElementById('drop-zone');
const upFile   = document.getElementById('up-file');
const dropText = document.getElementById('drop-text');

dropZone.addEventListener('click', () => upFile.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        upFile.files = e.dataTransfer.files;
        dropText.textContent = e.dataTransfer.files[0].name;
    }
});
upFile.addEventListener('change', () => {
    if (upFile.files.length) dropText.textContent = upFile.files[0].name;
});

/* ====================================================================
   Upload Song — lee archivo, convierte a WAV vía Web Audio, sube
   ==================================================================== */
document.getElementById('form-upload').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title  = document.getElementById('up-title').value.trim();
    const artist = document.getElementById('up-artist').value.trim() || 'Desconocido';
    const file   = upFile.files[0];

    if (!file) { showMsg('msg-upload', 'Selecciona un archivo de audio.', false); return; }

    const btnUpload = document.getElementById('btn-upload');
    btnUpload.disabled = true;
    btnUpload.textContent = '⏳ Procesando...';

    const progressBar  = document.getElementById('upload-progress');
    const progressFill = document.getElementById('upload-fill');
    const progressText = document.getElementById('upload-text');
    progressBar.classList.remove('hidden');
    progressFill.style.width = '10%';
    progressText.textContent = 'Leyendo archivo...';

    try {
        // 1. Leer archivo como ArrayBuffer
        const fileBuffer = await file.arrayBuffer();
        progressFill.style.width = '25%';
        progressText.textContent = 'Decodificando audio...';

        // 2. Decodificar a AudioBuffer (el navegador soporta MP3, OGG, WAV, etc.)
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const audioBuffer = await audioCtx.decodeAudioData(fileBuffer);
        audioCtx.close();

        progressFill.style.width = '50%';
        progressText.textContent = 'Convirtiendo a WAV...';

        // 3. Convertir a WAV PCM 16-bit
        const wavBuffer = audioBufferToWav(audioBuffer);
        const wavBase64 = arrayBufferToBase64(wavBuffer);

        progressFill.style.width = '70%';
        progressText.textContent = 'Subiendo y generando fingerprints...';

        // 4. Enviar al server
        const resp = await fetch(API + 'upload/', {
            method: 'POST',
            headers: authH({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({
                title,
                artist,
                audio_base64: wavBase64,
                file_type: 'audio/wav',
                file_size: wavBuffer.byteLength,
                duration_seconds: Math.round(audioBuffer.duration)
            })
        });

        const data = await resp.json();
        progressFill.style.width = '100%';

        if (data.status) {
            progressText.textContent = `✅ ${data.message}`;
            showMsg('msg-upload', data.message, true);
            document.getElementById('form-upload').reset();
            dropText.textContent = 'Arrastra un archivo o haz clic para seleccionar';
            loadSongs();
        } else {
            progressText.textContent = '❌ Error';
            showMsg('msg-upload', data.message, false);
        }

        setTimeout(() => progressBar.classList.add('hidden'), 3000);

    } catch (err) {
        console.error('Upload error:', err);
        progressText.textContent = '❌ Error';
        showMsg('msg-upload', 'Error procesando audio: ' + err.message, false);
        setTimeout(() => progressBar.classList.add('hidden'), 3000);
    } finally {
        btnUpload.disabled = false;
        btnUpload.textContent = '📤 Subir y Generar Fingerprints';
    }
});

/* ====================================================================
   Search Tabs
   ==================================================================== */
function switchSearchTab(tab) {
    document.querySelectorAll('.stab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.stab-content').forEach(c => c.classList.remove('active'));
    document.querySelector(`.stab[data-stab="${tab}"]`).classList.add('active');
    document.getElementById('stab-' + tab).classList.add('active');
}

/* ====================================================================
   WebSocket URL
   ==================================================================== */
function getWsUrl() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    return `${proto}://${location.host}/ws/shazam/`;
}

/* ====================================================================
   Mic Recording — streaming en tiempo real vía WebSocket
   Graba audio del micrófono → convierte a WAV PCM 16-bit en tiempo real
   → envía chunks binarios por WebSocket → recibe resultados parciales.
   ==================================================================== */
let isListening = false;
let activeWs = null;

async function startListening() {
    if (isListening) return;
    isListening = true;

    const btnListen = document.getElementById('btn-listen');
    const status    = document.getElementById('listen-status');
    const countdown = document.getElementById('listen-countdown');
    const canvas    = document.getElementById('mini-viz');
    const ctx       = canvas.getContext('2d');

    btnListen.disabled = true;
    status.classList.remove('hidden');

    let vizRunning = true;
    let stream = null;
    let audioCtx = null;
    let songFound = false;

    function cleanup() {
        vizRunning = false;
        if (stream) stream.getTracks().forEach(t => t.stop());
        if (audioCtx && audioCtx.state !== 'closed') audioCtx.close();
        if (activeWs && activeWs.readyState === WebSocket.OPEN) activeWs.close();
        activeWs = null;
        ctx.fillStyle = '#0a0a1a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        isListening = false;
        btnListen.disabled = false;
        status.classList.add('hidden');
    }

    try {
        // 1. Abrir WebSocket
        const ws = new WebSocket(getWsUrl());
        activeWs = ws;

        await new Promise((resolve, reject) => {
            ws.onopen = resolve;
            ws.onerror = () => reject(new Error('No se pudo conectar al WebSocket'));
            setTimeout(() => reject(new Error('Timeout conectando WebSocket')), 5000);
        });

        // Manejar mensajes del servidor
        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                console.log('[WS]', msg.type, msg.message || '');

                if (msg.type === 'confirmed') {
                    songFound = true;
                    countdown.textContent = '✅ ¡Canción encontrada!';
                    displayResult({ status: true, data: msg.data, message: msg.message });
                    cleanup();
                } else if (msg.type === 'partial') {
                    countdown.textContent = `⏳ ${msg.message}`;
                    displayResult({ status: true, data: msg.data, message: msg.message });
                } else if (msg.type === 'no_match') {
                    countdown.textContent = '🎤 Sin coincidencias aún...';
                } else if (msg.type === 'error') {
                    showMsg('msg-search', msg.message, false);
                } else if (msg.type === 'status') {
                    console.log('[WS status]', msg.message);
                }
            } catch (e) {
                console.error('Error parseando mensaje WS:', e);
            }
        };

        ws.onclose = () => {
            if (!songFound && isListening) {
                countdown.textContent = 'Conexión cerrada';
                cleanup();
            }
        };

        // 2. Obtener micrófono
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // 3. Visualizador
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioCtx.createMediaStreamSource(stream);
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function drawViz() {
            if (!vizRunning) return;
            requestAnimationFrame(drawViz);
            analyser.getByteFrequencyData(dataArray);
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            const barW = canvas.width / bufferLength * 2;
            let x = 0;
            for (let i = 0; i < bufferLength; i++) {
                const h = (dataArray[i] / 255) * canvas.height;
                const hue = 270 + (dataArray[i] / 255) * 30;
                ctx.fillStyle = `hsl(${hue}, 80%, ${40 + (dataArray[i] / 255) * 30}%)`;
                ctx.fillRect(x, canvas.height - h, barW - 1, h);
                x += barW;
            }
        }
        drawViz();

        // 4. Capturar audio con ScriptProcessorNode y enviar WAV PCM por WebSocket
        //    Usamos un buffer size de 4096 samples → ~93 ms por chunk a 44100 Hz
        const processor = audioCtx.createScriptProcessor(4096, 1, 1);
        source.connect(processor);
        processor.connect(audioCtx.destination);

        processor.onaudioprocess = (e) => {
            if (songFound || ws.readyState !== WebSocket.OPEN) return;

            // Obtener muestras mono float32
            const inputData = e.inputBuffer.getChannelData(0);

            // Convertir a PCM 16-bit WAV (con header) para que el server pueda parsear
            const wavBuffer = float32ToWav(inputData, e.inputBuffer.sampleRate);
            ws.send(wavBuffer);
        };

        // 5. Countdown 30 → 0
        let remaining = 30;
        countdown.textContent = `🎤 Escuchando en vivo... ${remaining}s`;

        const timer = setInterval(() => {
            if (songFound) { clearInterval(timer); return; }
            remaining--;
            if (remaining > 0) {
                countdown.textContent = `🎤 Escuchando en vivo... ${remaining}s`;
            } else {
                countdown.textContent = '🔍 Búsqueda final...';
                clearInterval(timer);
            }
        }, 1000);

        // 6. Esperar hasta 30 s o hasta encontrar canción
        await new Promise(resolve => {
            const timeout = setTimeout(resolve, 30000);
            const checkInterval = setInterval(() => {
                if (songFound) {
                    clearTimeout(timeout);
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 200);

            // Limpiar interval al terminar timeout
            const origResolve = resolve;
            setTimeout(() => clearInterval(checkInterval), 30500);
        });

        // Si no se encontró, forzar búsqueda final
        if (!songFound && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: 'search' }));
            // Esperar respuesta
            await new Promise(resolve => setTimeout(resolve, 3000));
        }

        if (!songFound) {
            displayResult({
                status: true,
                data: null,
                message: 'No se encontró ninguna coincidencia tras 30 segundos de escucha.'
            });
        }

    } catch (err) {
        console.error('Mic/WS error:', err);
        if (err.name === 'NotAllowedError') {
            showMsg('msg-search', 'Permiso de micrófono denegado. Habilítalo en la configuración del navegador.', false);
        } else {
            showMsg('msg-search', 'Error: ' + err.message, false);
        }
    } finally {
        cleanup();
    }
}

/**
 * Convierte un array Float32 (muestras mono) a un ArrayBuffer WAV PCM 16-bit.
 * Incluye header WAV completo para que el server pueda parsearlo.
 */
function float32ToWav(samples, sampleRate) {
    const numSamples = samples.length;
    const bitsPerSample = 16;
    const numChannels = 1;
    const byteRate = sampleRate * numChannels * bitsPerSample / 8;
    const blockAlign = numChannels * bitsPerSample / 8;
    const dataSize = numSamples * blockAlign;
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);

    // RIFF header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataSize, true);
    writeString(view, 8, 'WAVE');

    // fmt chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);             // PCM
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);

    // data chunk
    writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    // PCM samples
    let offset = 44;
    for (let i = 0; i < numSamples; i++) {
        const s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        offset += 2;
    }

    return buffer;
}

function getSupportedMimeType() {
    const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
    for (const type of types) {
        if (MediaRecorder.isTypeSupported(type)) return type;
    }
    return '';
}

/* ====================================================================
   Search from File
   ==================================================================== */
function onSearchFileSelected(event) {
    const file = event.target.files[0];
    const nameEl = document.getElementById('search-file-name');
    const btn = document.getElementById('btn-search-file');
    if (file) {
        nameEl.textContent = file.name;
        btn.disabled = false;
    } else {
        nameEl.textContent = 'Ningún archivo';
        btn.disabled = true;
    }
}

async function searchFromFile() {
    const fileInput = document.getElementById('search-file');
    const file = fileInput.files[0];
    if (!file) { showMsg('msg-search', 'Selecciona un archivo primero.', false); return; }

    const btn = document.getElementById('btn-search-file');
    btn.disabled = true;
    btn.textContent = '⏳ Procesando...';

    try {
        const fileBuffer = await file.arrayBuffer();

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const audioBuffer = await audioCtx.decodeAudioData(fileBuffer);
        audioCtx.close();

        const wavBuffer = audioBufferToWav(audioBuffer);
        const wavBase64 = arrayBufferToBase64(wavBuffer);

        showMsg('msg-search', '🔍 Buscando coincidencias...', true);

        const resp = await fetch(API + 'search/', {
            method: 'POST',
            headers: authH({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ audio_base64: wavBase64 })
        });

        const result = await resp.json();
        displayResult(result);

    } catch (err) {
        console.error('Search file error:', err);
        showMsg('msg-search', 'Error procesando audio: ' + err.message, false);
    } finally {
        btn.disabled = false;
        btn.textContent = '🔍 Buscar';
    }
}

/* ====================================================================
   Display Result
   ==================================================================== */
function displayResult(result) {
    const panel = document.getElementById('result-panel');
    panel.classList.remove('hidden', 'found', 'notfound');

    if (!result.status || !result.data) {
        // No match
        panel.classList.add('notfound');
        document.getElementById('result-icon').textContent = '❌';
        document.getElementById('result-title').textContent = 'No se encontró coincidencia';
        document.getElementById('result-artist').textContent = '—';
        document.getElementById('result-confidence').textContent = '—';
        document.getElementById('result-matches').textContent = '—';
        document.getElementById('result-candidates').innerHTML = '';
        showMsg('msg-search', result.message || 'No se encontró ninguna coincidencia.', false);
        return;
    }

    const d = result.data;
    const confirmed = d.is_confirmed;

    panel.classList.add(confirmed ? 'found' : 'notfound');
    document.getElementById('result-icon').textContent = confirmed ? '✅' : '⚠️';
    document.getElementById('result-title').textContent =
        (confirmed ? '🎵 ' : '❓ ') + (d.title || '—');
    document.getElementById('result-artist').textContent = d.artist || '—';
    document.getElementById('result-confidence').textContent = d.confidence
        ? d.confidence + '% ' + (confirmed ? '(CONFIRMADO)' : '(no confirmado)')
        : '—';
    document.getElementById('result-matches').textContent = d.matched_hashes != null
        ? `${d.matched_hashes} / ${d.min_required} coherentes necesarios (de ${d.query_hashes} hashes)`
        : '—';

    // Candidatos
    const candContainer = document.getElementById('result-candidates');
    candContainer.innerHTML = '';
    if (d.candidates && d.candidates.length > 1) {
        candContainer.innerHTML = '<h4>Otros candidatos</h4>';
        d.candidates.slice(1).forEach(c => {
            candContainer.innerHTML += `
                <div class="candidate">
                    <span>${c.title} — ${c.artist}</span>
                    <span>${c.matched_hashes} matches (${c.confidence}%)</span>
                </div>`;
        });
    }

    showMsg('msg-search', result.message, confirmed);
}

/* ====================================================================
   Library Table — Load all songs
   ==================================================================== */
async function loadSongs() {
    try {
        const resp = await fetch(API, {
            headers: authH()
        });
        const data = await resp.json();
        const tbody = document.getElementById('songs-table');

        if (!data.status || !data.data || data.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#666;">No hay canciones en la biblioteca</td></tr>';
            return;
        }

        tbody.innerHTML = data.data.map(s => {
            const durMin = s.duration_seconds
                ? `${Math.floor(s.duration_seconds / 60)}:${String(s.duration_seconds % 60).padStart(2, '0')}`
                : '—';
            const dateStr = s.created_at
                ? new Date(s.created_at).toLocaleDateString('es-ES')
                : '—';
            const audioIcon = s.has_audio ? '☁️' : '⚠️';
            const playBtn = s.has_audio
                ? `<button class="btn btn-edit" onclick="playSong(${s.id})">▶</button>`
                : `<button class="btn btn-edit" disabled title="Sin audio en TeraBox">▶</button>`;
            return `
                <tr>
                    <td>${s.id}</td>
                    <td>${escapeHtml(s.title)}</td>
                    <td>${escapeHtml(s.artist)}</td>
                    <td>${durMin}</td>
                    <td><span class="badge-fp">${s.fingerprint_count || 0}</span></td>
                    <td>${audioIcon}</td>
                    <td>${dateStr}</td>
                    <td class="actions">
                        ${playBtn}
                        <button class="btn btn-edit" onclick="openModal(${s.id}, '${escapeAttr(s.title)}', '${escapeAttr(s.artist)}')">✏️</button>
                        <button class="btn btn-danger" style="font-size:12px;padding:6px 12px" onclick="deleteSong(${s.id})">🗑️</button>
                    </td>
                </tr>`;
        }).join('');

    } catch (err) {
        console.error('Load songs error:', err);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeAttr(str) {
    if (!str) return '';
    return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

/* ====================================================================
   Play Song
   ==================================================================== */
function playSong(id) {
    const audio = new Audio(API + id + '/audio/');
    audio.play().catch(err => console.error('Play error:', err));
}

/* ====================================================================
   Edit Modal
   ==================================================================== */
function openModal(id, title, artist) {
    document.getElementById('edit_id').value = id;
    document.getElementById('edit_title').value = title;
    document.getElementById('edit_artist').value = artist;
    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

document.getElementById('form-edit').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id    = document.getElementById('edit_id').value;
    const title = document.getElementById('edit_title').value.trim();
    const artist = document.getElementById('edit_artist').value.trim();

    if (!title) { showMsg('msg-edit', 'El título es requerido.', false); return; }

    try {
        const resp = await fetch(API + id + '/update/', {
            method: 'PUT',
            headers: authH({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ title, artist })
        });
        const data = await resp.json();
        if (data.status) {
            showMsg('msg-edit', data.message, true);
            closeModal();
            loadSongs();
        } else {
            showMsg('msg-edit', data.message, false);
        }
    } catch (err) {
        showMsg('msg-edit', 'Error: ' + err.message, false);
    }
});

/* ====================================================================
   Delete Song
   ==================================================================== */
async function deleteSong(id) {
    if (!confirm('¿Eliminar esta canción y todos sus fingerprints?')) return;
    try {
        const resp = await fetch(API + id + '/delete/', {
            method: 'DELETE',
            headers: authH()
        });
        const data = await resp.json();
        if (data.status) {
            showMsg('msg-upload', data.message, true);
            loadSongs();
        } else {
            showMsg('msg-upload', data.message, false);
        }
    } catch (err) {
        showMsg('msg-upload', 'Error: ' + err.message, false);
    }
}

/* ====================================================================
   Regenerar Fingerprints (desde audio ya almacenado)
   ==================================================================== */
async function regenerarTodas() {
    if (!confirm('¿Regenerar fingerprints de TODAS las canciones? Esto puede tardar unos segundos.')) return;
    const btn = document.getElementById('btn-regen');
    const status = document.getElementById('regen-status');
    btn.disabled = true;
    status.textContent = '⏳ Regenerando...';
    try {
        const resp = await fetch(API + 'regenerate-all/', {
            method: 'POST',
            headers: authH()
        });
        const data = await resp.json();
        if (data.status) {
            const r = data.data;
            status.textContent = `✅ ${r.processed} canciones procesadas`;
            showMsg('msg-upload', data.message, true);
            loadSongs();
        } else {
            status.textContent = '❌ Error';
            showMsg('msg-upload', data.message, false);
        }
    } catch (err) {
        status.textContent = '❌ Error';
        showMsg('msg-upload', 'Error: ' + err.message, false);
    } finally {
        btn.disabled = false;
        setTimeout(() => { status.textContent = ''; }, 5000);
    }
}

/* ── Init ── */
document.addEventListener('DOMContentLoaded', () => {
    loadSongs();
});
