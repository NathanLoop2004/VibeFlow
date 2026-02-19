const API = '/api/users/';

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

async function loadUsers() {
    const res = await fetch(API);
    const json = await res.json();
    const users = json.data || [];
    const tbody = document.getElementById('users-table');
    tbody.innerHTML = users.map(u => `
        <tr>
            <td>${u.username}</td>
            <td>${u.email}</td>
            <td><span class="badge ${u.is_active ? 'badge-green' : 'badge-red'}">${u.is_active ? 'Sí' : 'No'}</span></td>
            <td><span class="badge ${u.is_verified ? 'badge-green' : 'badge-red'}">${u.is_verified ? 'Sí' : 'No'}</span></td>
            <td><span class="badge ${u.is_superuser ? 'badge-green' : 'badge-red'}">${u.is_superuser ? 'Sí' : 'No'}</span></td>
            <td>${new Date(u.created_at).toLocaleDateString('es')}</td>
            <td><button class="btn btn-danger" onclick="deleteUser('${u.id}')">Eliminar</button></td>
        </tr>
    `).join('');
}

document.getElementById('form-user').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        is_active: document.getElementById('is_active').checked,
        is_verified: document.getElementById('is_verified').checked,
        is_superuser: document.getElementById('is_superuser').checked,
    };
    const res = await fetch(API + 'create/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
    const data = await res.json();
    if (res.ok) { showMsg('msg-user', data.message, true); e.target.reset(); loadUsers(); }
    else { showMsg('msg-user', data.message || data.error, false); }
});

async function deleteUser(id) {
    if (!confirm('¿Eliminar este usuario?')) return;
    const res = await fetch(API + id + '/delete/', { method: 'DELETE' });
    if (res.ok) loadUsers();
}

loadUsers();
