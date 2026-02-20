function getToken() { return localStorage.getItem('vf_token') || ''; }
function authH(extra = {}) { return { 'Authorization': 'Bearer ' + getToken(), ...extra }; }

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

async function loadSelects() {
    const [usersRes, rolesRes] = await Promise.all([fetch('/api/users/', { headers: authH() }), fetch('/api/roles/', { headers: authH() })]);
    const usersJson = await usersRes.json();
    const rolesJson = await rolesRes.json();
    const users = usersJson.data || [];
    const roles = rolesJson.data || [];

    const userSel = document.getElementById('user_id');
    userSel.innerHTML = '<option value="">-- Seleccionar usuario --</option>' +
        users.map(u => `<option value="${u.id}">${u.username} (${u.email})</option>`).join('');

    const roleSel = document.getElementById('role_id');
    roleSel.innerHTML = '<option value="">-- Seleccionar rol --</option>' +
        roles.map(r => `<option value="${r.id}">${r.name}</option>`).join('');
}

async function loadUserRoles() {
    const res = await fetch('/api/user-roles/', { headers: authH() });
    const json = await res.json();
    const data = json.data || [];
    const tbody = document.getElementById('ur-table');
    tbody.innerHTML = data.map(ur => `
        <tr>
            <td>${ur.username}</td>
            <td>${ur.role_name}</td>
            <td><button class="btn btn-danger" onclick="deleteUR('${ur.user_id}', ${ur.role_id})">Eliminar</button></td>
        </tr>
    `).join('');
}

document.getElementById('form-ur').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        user_id: document.getElementById('user_id').value,
        role_id: parseInt(document.getElementById('role_id').value),
    };
    const res = await fetch('/api/user-roles/assign/', { method: 'POST', headers: authH({'Content-Type': 'application/json'}), body: JSON.stringify(body) });
    const data = await res.json();
    if (res.ok) { showMsg('msg-ur', data.message, true); e.target.reset(); loadUserRoles(); }
    else { showMsg('msg-ur', data.message || data.error, false); }
});

async function deleteUR(userId, roleId) {
    if (!confirm('¿Eliminar esta asignación?')) return;
    const res = await fetch(`/api/user-roles/${userId}/${roleId}/delete/`, { method: 'DELETE', headers: authH() });
    if (res.ok) loadUserRoles();
}

loadSelects();
loadUserRoles();
