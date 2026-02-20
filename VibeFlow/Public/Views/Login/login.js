/* ── Login JS ── */

const API = '/api/auth/';

const form     = document.getElementById('loginForm');
const msgEl    = document.getElementById('loginMessage');
const btnLogin = document.getElementById('btnLogin');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msgEl.textContent = '';
    msgEl.className   = 'login-message';

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showMessage('Completa todos los campos', 'error');
        return;
    }

    btnLogin.disabled    = true;
    btnLogin.textContent = 'Verificando...';

    try {
        const res  = await fetch(API + 'login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ username, password }),
        });

        const json = await res.json();

        if (json.status) {
            // Guardar token JWT en localStorage
            if (json.token) {
                localStorage.setItem('vf_token', json.token);
            }
            showMessage(json.message, 'success');
            // Redirigir al panel después de 1 s
            setTimeout(() => {
                window.location.href = '/panel/';
            }, 1000);
        } else {
            showMessage(json.message || 'Credenciales incorrectas', 'error');
        }
    } catch (err) {
        showMessage('Error de conexión con el servidor', 'error');
        console.error(err);
    } finally {
        btnLogin.disabled    = false;
        btnLogin.textContent = 'Iniciar sesión';
    }
});

function showMessage(text, type) {
    msgEl.textContent = text;
    msgEl.className   = 'login-message ' + type;
}

function getCSRFToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

function togglePassword() {
    const input = document.getElementById('password');
    const btn = input.nextElementSibling;
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
}

/* ── Google Sign-In (OAuth2 Popup - sin FedCM) ── */
const GOOGLE_CLIENT_ID = '267804810810-2n76u7dmoq9v8kbvgjfn2g23eqsm16ks.apps.googleusercontent.com';

function googleSignIn() {
    console.log('[GoogleSignIn] Iniciando...');

    if (typeof google === 'undefined' || !google.accounts || !google.accounts.oauth2) {
        showMessage('Cargando Google Sign-In, intenta de nuevo en unos segundos...', 'error');
        console.warn('[GoogleSignIn] google.accounts.oauth2 no disponible aún');
        return;
    }

    try {
        const client = google.accounts.oauth2.initTokenClient({
            client_id: GOOGLE_CLIENT_ID,
            scope: 'email profile',
            callback: handleGoogleToken,
            error_callback: (err) => {
                console.error('[GoogleSignIn] error_callback:', err);
                showMessage('No se pudo abrir la ventana de Google. Permite pop-ups e intenta de nuevo.', 'error');
            },
        });

        console.log('[GoogleSignIn] requestAccessToken...');
        client.requestAccessToken();
    } catch (e) {
        console.error('[GoogleSignIn] Excepción:', e);
        showMessage('Error al iniciar Google Sign-In: ' + e.message, 'error');
    }
}

async function handleGoogleToken(tokenResponse) {
    console.log('[GoogleSignIn] Callback recibido', tokenResponse);

    if (tokenResponse.error) {
        console.warn('[GoogleSignIn] Error en tokenResponse:', tokenResponse.error);
        showMessage('Google Sign-In cancelado o fallido', 'error');
        return;
    }

    if (!tokenResponse.access_token) {
        console.warn('[GoogleSignIn] No se recibió access_token');
        showMessage('No se obtuvo token de Google', 'error');
        return;
    }

    msgEl.textContent = '';
    msgEl.className   = 'login-message';
    showMessage('Verificando con Google...', 'success');

    try {
        const res = await fetch(API + 'google/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ access_token: tokenResponse.access_token }),
        });

        console.log('[GoogleSignIn] Respuesta backend status:', res.status);
        const json = await res.json();
        console.log('[GoogleSignIn] Respuesta backend:', json);

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
        console.error('[GoogleSignIn] Error fetch:', err);
        showMessage('Error de conexión con el servidor', 'error');
    }
}
