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

/* ── Google Sign-Up ── */
const GOOGLE_CLIENT_ID = '267804810810-2n76u7dmoq9v8kbvgjfn2g23eqsm16ks.apps.googleusercontent.com';

function googleSignUp() {
    if (typeof google === 'undefined' || !google.accounts) {
        showMessage('Cargando Google Sign-In, intenta de nuevo...', 'error');
        return;
    }

    google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
    });

    google.accounts.id.prompt();
}

async function handleGoogleResponse(response) {
    msgEl.textContent = '';
    msgEl.className   = 'register-message';

    try {
        const res = await fetch('/api/auth/google/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential: response.credential }),
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
