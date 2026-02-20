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

/* ── Google Sign-Up (OAuth2 Redirect — sin librería GSI) ── */
const GOOGLE_CLIENT_ID = '267804810810-ft6b1qb4bp9arnffa0101t07hf15rutg.apps.googleusercontent.com';
const REDIRECT_URI     = window.location.origin + '/api/auth/google/callback/';

function googleSignUp() {
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
        showMessage('Registro con Google exitoso', 'success');
        setTimeout(() => { window.location.href = '/panel/'; }, 800);
    } else if (error) {
        showMessage(decodeURIComponent(error), 'error');
    }
})();
