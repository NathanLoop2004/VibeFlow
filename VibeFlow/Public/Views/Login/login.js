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
    if (typeof google === 'undefined' || !google.accounts) {
        showMessage('Cargando Google Sign-In, intenta de nuevo...', 'error');
        return;
    }

    const client = google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: 'email profile',
        callback: handleGoogleToken,
    });

    client.requestAccessToken();
}

async function handleGoogleToken(tokenResponse) {
    if (tokenResponse.error) {
        showMessage('Google Sign-In cancelado o fallido', 'error');
        return;
    }

    msgEl.textContent = '';
    msgEl.className   = 'login-message';

    try {
        const res = await fetch(API + 'google/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: tokenResponse.access_token }),
        });

        const json = await res.json();

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
        showMessage('Error de conexión con el servidor', 'error');
        console.error(err);
    }
}
