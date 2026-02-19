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
