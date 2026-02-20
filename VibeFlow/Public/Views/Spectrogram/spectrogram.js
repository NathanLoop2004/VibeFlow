/* ====================================================================
   Espectrograma Waterfall + Grabación de Audio — VibeFlow
   Soporta micrófono en tiempo real y carga de archivos de audio.
   ==================================================================== */

const API = '/api/recordings/';

/* ── Helpers ── */
function getToken() { return localStorage.getItem('vf_token') || ''; }
function authH(extra = {}) { return { 'Authorization': 'Bearer ' + getToken(), ...extra }; }

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 4000);
}

/* ====================================================================
   Color Maps — mapea 0-255 → [r, g, b]
   ==================================================================== */
const COLORMAPS = {
    inferno: v => {
        const t = v / 255;
        const r = Math.floor(Math.min(255, t < 0.5 ? t * 510 : 255));
        const g = Math.floor(Math.min(255, t < 0.33 ? 0 : t < 0.66 ? (t - 0.33) * 765 : 255));
        const b = Math.floor(t < 0.25 ? t * 400 : t < 0.5 ? (1 - (t - 0.25) * 4) * 100 : 0);
        return [r, g, b];
    },
    viridis: v => {
        const t = v / 255;
        const r = Math.floor(68 + t * 120);
        const g = Math.floor(t < 0.5 ? 1 + t * 380 : 190 + (t - 0.5) * 130);
        const b = Math.floor(t < 0.5 ? 84 + t * 260 : 214 - (t - 0.5) * 360);
        return [Math.min(255, r), Math.min(255, g), Math.max(0, b)];
    },
    plasma: v => {
        const t = v / 255;
        const r = Math.floor(13 + t * 242);
        const g = Math.floor(t < 0.5 ? 8 + t * 200 : 108 + (t - 0.5) * 294);
        const b = Math.floor(t < 0.4 ? 135 + t * 300 : 255 - (t - 0.4) * 425);
        return [Math.min(255, r), Math.min(255, g), Math.max(0, Math.min(255, b))];
    },
    cool: v => {
        const t = v / 255;
        return [Math.floor(t * 255), Math.floor(255 - t * 150), 255];
    },
};

function getColormap() {
    return COLORMAPS[document.getElementById('colormap-select').value] || COLORMAPS.inferno;
}

/* ====================================================================
   Audio Context & State
   ==================================================================== */
let audioCtx = null;
let analyser = null;
let source = null;
let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let animFrameId = null;
let isRunning = false;
let recStartTime = 0;
let recTimerInterval = null;

// Para archivo
let fileAudioBuffer = null;
let fileSource = null;

/* Canvas refs */
const barsCanvas = document.getElementById('bars-canvas');
const barsCtx = barsCanvas.getContext('2d');
const wfCanvas = document.getElementById('waterfall-canvas');
const wfCtx = wfCanvas.getContext('2d');

function resizeCanvases() {
    const dpr = window.devicePixelRatio || 1;
    barsCanvas.width = barsCanvas.clientWidth * dpr;
    barsCanvas.height = barsCanvas.clientHeight * dpr;
    barsCtx.scale(dpr, dpr);

    wfCanvas.width = wfCanvas.clientWidth * dpr;
    wfCanvas.height = wfCanvas.clientHeight * dpr;
    wfCtx.scale(dpr, dpr);
}
resizeCanvases();
window.addEventListener('resize', resizeCanvases);

/* Freq axis labels */
function buildFreqAxis() {
    const el = document.getElementById('freq-axis');
    const labels = ['0', '500', '1k', '2k', '4k', '8k', '16k', '20k'];
    el.innerHTML = labels.map(l => `<span>${l} Hz</span>`).join('');
}
buildFreqAxis();

/* ====================================================================
   Tab switching
   ==================================================================== */
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === 'tab-' + tab));
    // Stop any running source when switching
    stopMic();
    stopFile();
}

/* ====================================================================
   Microphone
   ==================================================================== */
async function startMic() {
    try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') await audioCtx.resume();

        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.8;

        source = audioCtx.createMediaStreamSource(mediaStream);
        source.connect(analyser);

        // MediaRecorder para guardar
        recordedChunks = [];
        mediaRecorder = new MediaRecorder(mediaStream, { mimeType: getSupportedMime() });
        mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordedChunks.push(e.data); };
        mediaRecorder.start(100); // chunk cada 100ms

        recStartTime = Date.now();
        recTimerInterval = setInterval(updateRecTimer, 500);

        isRunning = true;
        updateButtons('mic-running');
        draw();
    } catch (err) {
        showMsg('msg-main', 'Error al acceder al micrófono: ' + err.message, false);
    }
}

function stopMic() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
    if (mediaStream) { mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null; }
    if (source) { source.disconnect(); source = null; }
    isRunning = false;
    clearInterval(recTimerInterval);
    cancelAnimationFrame(animFrameId);
    updateButtons('idle');
}

function updateRecTimer() {
    const secs = Math.floor((Date.now() - recStartTime) / 1000);
    const m = String(Math.floor(secs / 60)).padStart(2, '0');
    const s = String(secs % 60).padStart(2, '0');
    document.getElementById('rec-time').textContent = m + ':' + s;
}

function getSupportedMime() {
    const mimes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
    for (const m of mimes) { if (MediaRecorder.isTypeSupported(m)) return m; }
    return '';
}

/* ====================================================================
   File Upload
   ==================================================================== */
async function loadFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    document.getElementById('file-name').textContent = file.name;

    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    const arrayBuf = await file.arrayBuffer();
    fileAudioBuffer = await audioCtx.decodeAudioData(arrayBuf);

    // Guardar el archivo original como blob para poder guardarlo en BD
    recordedChunks = [file];

    document.getElementById('btn-play-file').disabled = false;
    showMsg('msg-main', `Archivo cargado: ${file.name} (${fileAudioBuffer.duration.toFixed(1)}s)`, true);
}

async function playFile() {
    if (!fileAudioBuffer) return;
    stopFile(); // Detener si ya estaba reproduciendo

    if (audioCtx.state === 'suspended') await audioCtx.resume();

    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.8;

    fileSource = audioCtx.createBufferSource();
    fileSource.buffer = fileAudioBuffer;
    fileSource.connect(analyser);
    analyser.connect(audioCtx.destination); // Para escuchar el audio
    fileSource.start();

    recStartTime = Date.now();
    recTimerInterval = setInterval(updateRecTimer, 500);

    fileSource.onended = () => {
        isRunning = false;
        clearInterval(recTimerInterval);
        updateButtons('file-ready');
    };

    isRunning = true;
    updateButtons('file-playing');
    draw();
}

function stopFile() {
    if (fileSource) { try { fileSource.stop(); } catch(_){} fileSource = null; }
    isRunning = false;
    clearInterval(recTimerInterval);
    cancelAnimationFrame(animFrameId);
    updateButtons(fileAudioBuffer ? 'file-ready' : 'idle');
}

/* ====================================================================
   Button states
   ==================================================================== */
function updateButtons(state) {
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');
    const recInd = document.getElementById('rec-indicator');
    const btnPlayFile = document.getElementById('btn-play-file');
    const btnStopFile = document.getElementById('btn-stop-file');
    const btnSave = document.getElementById('btn-save');

    btnStart.disabled = state === 'mic-running';
    btnStop.disabled = state !== 'mic-running';
    recInd.classList.toggle('hidden', state !== 'mic-running');

    btnPlayFile.disabled = state === 'file-playing' || !fileAudioBuffer;
    btnStopFile.disabled = state !== 'file-playing';

    btnSave.disabled = recordedChunks.length === 0;
}

/* ====================================================================
   Drawing Loop
   ==================================================================== */
function draw() {
    if (!isRunning || !analyser) return;

    const bufLen = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufLen);
    analyser.getByteFrequencyData(dataArray);

    const gain = parseFloat(document.getElementById('gain-slider').value);
    const speed = parseInt(document.getElementById('speed-slider').value);

    drawBars(dataArray, bufLen, gain);
    drawWaterfall(dataArray, bufLen, gain, speed);

    animFrameId = requestAnimationFrame(draw);
}

function drawBars(data, len, gain) {
    const w = barsCanvas.clientWidth;
    const h = barsCanvas.clientHeight;
    const cmap = getColormap();

    barsCtx.clearRect(0, 0, w, h);

    const barCount = Math.min(len, 256);
    const barW = w / barCount;

    for (let i = 0; i < barCount; i++) {
        let val = Math.min(255, data[i] * gain);
        const barH = (val / 255) * h;
        const [r, g, b] = cmap(val);
        barsCtx.fillStyle = `rgb(${r},${g},${b})`;
        barsCtx.fillRect(i * barW, h - barH, barW - 1, barH);
    }
}

function drawWaterfall(data, len, gain, speed) {
    const w = wfCanvas.clientWidth;
    const h = wfCanvas.clientHeight;
    const cmap = getColormap();

    // Desplazar imagen hacia abajo
    const imgData = wfCtx.getImageData(0, 0, wfCanvas.width, wfCanvas.height);
    wfCtx.putImageData(imgData, 0, speed);

    // Dibujar nueva fila arriba
    const barCount = Math.min(len, w);
    const scale = barCount / w;

    for (let x = 0; x < w; x++) {
        const idx = Math.floor(x * scale);
        let val = Math.min(255, (data[idx] || 0) * gain);
        const [r, g, b] = cmap(val);
        wfCtx.fillStyle = `rgb(${r},${g},${b})`;
        wfCtx.fillRect(x, 0, 1, speed);
    }
}

/* ====================================================================
   Save Recording
   ==================================================================== */
document.getElementById('form-save').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (recordedChunks.length === 0) {
        showMsg('msg-save', 'No hay audio para guardar. Graba o sube un archivo primero.', false);
        return;
    }

    const name = document.getElementById('save-name').value.trim();
    if (!name) return;

    // Detener si está grabando
    if (isRunning) stopMic();

    // Esperar un poco para que el mediaRecorder finalice
    await new Promise(r => setTimeout(r, 300));

    const blob = new Blob(recordedChunks, { type: recordedChunks[0].type || 'audio/webm' });
    const duration = (Date.now() - recStartTime) / 1000;

    // Leer como base64
    const reader = new FileReader();
    reader.onloadend = async () => {
        const base64 = reader.result.split(',')[1]; // quitar data:...;base64,

        const body = {
            name: name,
            audio_base64: base64,
            duration_seconds: parseFloat(duration.toFixed(2)),
            sample_rate: audioCtx ? audioCtx.sampleRate : 44100,
            file_type: blob.type || 'audio/webm',
            file_size: blob.size,
        };

        try {
            const res = await fetch(API + 'create/', {
                method: 'POST',
                headers: authH({ 'Content-Type': 'application/json' }),
                body: JSON.stringify(body),
            });
            const data = await res.json();
            if (res.ok) {
                showMsg('msg-save', data.message, true);
                document.getElementById('save-name').value = '';
                recordedChunks = [];
                updateButtons('idle');
                loadRecordings();
            } else {
                showMsg('msg-save', data.message || 'Error al guardar', false);
            }
        } catch (err) {
            showMsg('msg-save', 'Error de conexión: ' + err.message, false);
        }
    };
    reader.readAsDataURL(blob);
});

/* ====================================================================
   Recordings CRUD
   ==================================================================== */
let recordingsCache = [];

async function loadRecordings() {
    try {
        const res = await fetch(API + 'mine/', { headers: authH() });
        const json = await res.json();
        recordingsCache = json.data || [];

        const tbody = document.getElementById('recordings-table');
        if (recordingsCache.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#666">No hay grabaciones guardadas</td></tr>';
            return;
        }

        tbody.innerHTML = recordingsCache.map(r => {
            const dur = r.duration_seconds ? r.duration_seconds.toFixed(1) + 's' : '—';
            const size = r.file_size ? formatBytes(r.file_size) : '—';
            const date = r.created_at ? new Date(r.created_at).toLocaleString('es') : '—';
            return `<tr>
                <td>${r.id}</td>
                <td>${r.name}</td>
                <td>${dur}</td>
                <td>${r.file_type || '—'}</td>
                <td>${size}</td>
                <td>${date}</td>
                <td>
                    <div class="actions">
                        <button class="btn btn-primary" style="font-size:12px;padding:6px 12px" onclick="playRecording(${r.id})">▶</button>
                        <button class="btn btn-edit" onclick="openModal(${r.id})">✏️</button>
                        <button class="btn btn-danger" style="font-size:12px;padding:6px 12px" onclick="deleteRecording(${r.id})">🗑️</button>
                    </div>
                </td>
            </tr>`;
        }).join('');
    } catch (err) {
        console.error('Error cargando grabaciones:', err);
    }
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

async function playRecording(id) {
    try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') await audioCtx.resume();

        const res = await fetch(API + id + '/audio/', { headers: authH() });
        if (!res.ok) { showMsg('msg-main', 'Audio no disponible', false); return; }

        const arrayBuf = await res.arrayBuffer();
        const audioBuf = await audioCtx.decodeAudioData(arrayBuf);

        // Configurar analyser para visualizar
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.8;

        if (fileSource) try { fileSource.stop(); } catch(_){}
        fileSource = audioCtx.createBufferSource();
        fileSource.buffer = audioBuf;
        fileSource.connect(analyser);
        analyser.connect(audioCtx.destination);
        fileSource.start();

        isRunning = true;
        fileSource.onended = () => { isRunning = false; };
        draw();
    } catch (err) {
        showMsg('msg-main', 'Error al reproducir: ' + err.message, false);
    }
}

async function deleteRecording(id) {
    if (!confirm('¿Eliminar esta grabación?')) return;
    try {
        const res = await fetch(API + id + '/delete/', { method: 'DELETE', headers: authH() });
        if (res.ok) loadRecordings();
    } catch (err) {
        console.error('Error eliminando:', err);
    }
}

/* ── Modal editar ── */
function openModal(id) {
    const r = recordingsCache.find(x => x.id === id);
    if (!r) return;
    document.getElementById('edit_id').value = r.id;
    document.getElementById('edit_name').value = r.name;
    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

document.getElementById('modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

document.getElementById('form-edit').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit_id').value;
    const body = { name: document.getElementById('edit_name').value.trim() };

    const res = await fetch(API + id + '/update/', {
        method: 'PUT',
        headers: authH({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) {
        showMsg('msg-edit', data.message, true);
        setTimeout(() => { closeModal(); loadRecordings(); }, 800);
    } else {
        showMsg('msg-edit', data.message || 'Error al actualizar', false);
    }
});

/* ── Init ── */
loadRecordings();
