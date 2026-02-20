const API = '/api/roles/';

function getToken() { return localStorage.getItem('vf_token') || ''; }
function authH(extra = {}) { return { 'Authorization': 'Bearer ' + getToken(), ...extra }; }

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

async function loadRoles() {
    const res = await fetch(API, { headers: authH() });
    const json = await res.json();
    const roles = json.data || [];
    const tbody = document.getElementById('roles-table');
    tbody.innerHTML = roles.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${r.name}</td>
            <td>${r.description || '—'}</td>
            <td><button class="btn btn-danger" onclick="deleteRole(${r.id})">Eliminar</button></td>
        </tr>
    `).join('');
}

document.getElementById('form-role').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
    };
    const res = await fetch(API + 'create/', { method: 'POST', headers: authH({'Content-Type': 'application/json'}), body: JSON.stringify(body) });
    const data = await res.json();
    if (res.ok) { showMsg('msg-role', data.message, true); e.target.reset(); loadRoles(); }
    else { showMsg('msg-role', data.message || data.error, false); }
});

async function deleteRole(id) {
    if (!confirm('¿Eliminar este rol?')) return;
    const res = await fetch(API + id + '/delete/', { method: 'DELETE', headers: authH() });
    if (res.ok) loadRoles();
}

loadRoles();
