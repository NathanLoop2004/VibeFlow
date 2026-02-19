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
