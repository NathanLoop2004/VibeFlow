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

/* ── Google Sign-In (OAuth2 Redirect — sin librería GSI) ── */
const GOOGLE_CLIENT_ID = '267804810810-ft6b1qb4bp9arnffa0101t07hf15rutg.apps.googleusercontent.com';
const REDIRECT_URI     = window.location.origin + '/api/auth/google/callback/';

function googleSignIn() {
    const params = new URLSearchParams({
        client_id:     GOOGLE_CLIENT_ID,
        redirect_uri:  REDIRECT_URI,
        response_type: 'code',
        scope:         'openid email profile',
        access_type:   'online',
        prompt:        'select_account',
    });
    window.location.href = 'https://accounts.google.com/o/oauth2/v2/auth?' + params.toString();
}

/* Si volvemos del callback con token en query, guardarlo y redirigir */
(function checkGoogleCallback() {
    const params = new URLSearchParams(window.location.search);
    const token  = params.get('token');
    const error  = params.get('error');
    if (token) {
        localStorage.setItem('vf_token', token);
        showMessage('Login con Google exitoso', 'success');
        setTimeout(() => { window.location.href = '/panel/'; }, 800);
    } else if (error) {
        showMessage(decodeURIComponent(error), 'error');
    }
})();
