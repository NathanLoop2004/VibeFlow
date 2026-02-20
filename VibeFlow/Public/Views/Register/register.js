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

/* ── Google Sign-Up (Botón nativo renderizado por Google) ── */
const GOOGLE_CLIENT_ID = '267804810810-2n76u7dmoq9v8kbvgjfn2g23eqsm16ks.apps.googleusercontent.com';

function getCSRFToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

function initGoogleButton() {
    if (typeof google === 'undefined' || !google.accounts) {
        setTimeout(initGoogleButton, 500);
        return;
    }

    console.log('[GoogleSignUp] Inicializando botón nativo...');

    google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleCredential,
        ux_mode: 'popup',
    });

    google.accounts.id.renderButton(
        document.getElementById('g_signup_btn'),
        {
            theme: 'filled_black',
            size: 'large',
            width: 356,
            text: 'signup_with',
            shape: 'rectangular',
            logo_alignment: 'left',
        }
    );

    console.log('[GoogleSignUp] Botón renderizado OK');
}

window.addEventListener('load', initGoogleButton);

async function handleGoogleCredential(response) {
    console.log('[GoogleSignUp] Credential recibido');

    if (!response.credential) {
        showMessage('No se recibió credencial de Google', 'error');
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
            body: JSON.stringify({ credential: response.credential }),
        });

        console.log('[GoogleSignUp] Backend status:', res.status);
        const json = await res.json();
        console.log('[GoogleSignUp] Backend response:', json);

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
