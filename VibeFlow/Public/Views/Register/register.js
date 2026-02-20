/* ── Register JS ── */

const API = '/api/auth/';

const form   = document.getElementById('registerForm');
const msgEl  = document.getElementById('registerMessage');
const btnReg = document.getElementById('btnRegister');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msgEl.textContent = '';
    msgEl.className   = 'register-message';

    const username        = document.getElementById('username').value.trim();
    const email           = document.getElementById('email').value.trim();
    const password        = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!username || !email || !password || !confirmPassword) {
        showMessage('Completa todos los campos', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showMessage('Las contraseñas no coinciden', 'error');
        return;
    }

    if (password.length < 6) {
        showMessage('La contraseña debe tener al menos 6 caracteres', 'error');
        return;
    }

    btnReg.disabled    = true;
    btnReg.textContent = 'Registrando...';

    try {
        const res = await fetch(API + 'register/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password }),
        });

        const json = await res.json();

        if (json.status) {
            showMessage(json.message + ' Redirigiendo al login...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showMessage(json.message || 'Error al registrar', 'error');
        }
    } catch (err) {
        showMessage('Error de conexión con el servidor', 'error');
        console.error(err);
    } finally {
        btnReg.disabled    = false;
        btnReg.textContent = 'Crear cuenta';
    }
});

function showMessage(text, type) {
    msgEl.textContent = text;
    msgEl.className   = 'register-message ' + type;
}

function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
}

/* ── Google Sign-Up (OAuth2 Popup - sin FedCM) ── */
const GOOGLE_CLIENT_ID = '267804810810-2n76u7dmoq9v8kbvgjfn2g23eqsm16ks.apps.googleusercontent.com';

function getCSRFToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

function googleSignUp() {
    console.log('[GoogleSignUp] Iniciando...');

    if (typeof google === 'undefined' || !google.accounts || !google.accounts.oauth2) {
        showMessage('Cargando Google Sign-In, intenta de nuevo en unos segundos...', 'error');
        console.warn('[GoogleSignUp] google.accounts.oauth2 no disponible aún');
        return;
    }

    try {
        const client = google.accounts.oauth2.initTokenClient({
            client_id: GOOGLE_CLIENT_ID,
            scope: 'email profile',
            callback: handleGoogleToken,
            error_callback: (err) => {
                console.error('[GoogleSignUp] error_callback:', err);
                showMessage('No se pudo abrir la ventana de Google. Permite pop-ups e intenta de nuevo.', 'error');
            },
        });

        console.log('[GoogleSignUp] requestAccessToken...');
        client.requestAccessToken();
    } catch (e) {
        console.error('[GoogleSignUp] Excepción:', e);
        showMessage('Error al iniciar Google Sign-In: ' + e.message, 'error');
    }
}

async function handleGoogleToken(tokenResponse) {
    console.log('[GoogleSignUp] Callback recibido', tokenResponse);

    if (tokenResponse.error) {
        console.warn('[GoogleSignUp] Error en tokenResponse:', tokenResponse.error);
        showMessage('Google Sign-In cancelado o fallido', 'error');
        return;
    }

    if (!tokenResponse.access_token) {
        console.warn('[GoogleSignUp] No se recibió access_token');
        showMessage('No se obtuvo token de Google', 'error');
        return;
    }

    msgEl.textContent = '';
    msgEl.className   = 'register-message';
    showMessage('Verificando con Google...', 'success');

    try {
        const res = await fetch('/api/auth/google/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ access_token: tokenResponse.access_token }),
        });

        console.log('[GoogleSignUp] Respuesta backend status:', res.status);
        const json = await res.json();
        console.log('[GoogleSignUp] Respuesta backend:', json);

        if (json.status) {
            if (json.token) {
                localStorage.setItem('vf_token', json.token);
            }
            showMessage(json.message, 'success');
            setTimeout(() => {
                window.location.href = '/panel/';
            }, 1000);
        } else {
            showMessage(json.message || 'Error con Google', 'error');
        }
    } catch (err) {
        console.error('[GoogleSignUp] Error fetch:', err);
        showMessage('Error de conexión con el servidor', 'error');
    }
}
