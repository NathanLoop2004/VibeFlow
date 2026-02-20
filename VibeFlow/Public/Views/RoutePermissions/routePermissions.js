const API_PERMS = '/api/permissions/';
let allRoles = [];

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
    const [rolesRes, routesRes] = await Promise.all([
        fetch('/api/roles/', { headers: authH() }),
        fetch('/api/routes/', { headers: authH() })
    ]);
    const rolesJson = await rolesRes.json();
    const routesJson = await routesRes.json();
    allRoles = rolesJson.data || [];
    const routes = routesJson.data || [];

    const roleSel = document.getElementById('role_id');
    roleSel.innerHTML = '<option value="">-- Seleccionar rol --</option>' +
        allRoles.map(r => `<option value="${r.id}">${r.name}</option>`).join('');

    const filterSel = document.getElementById('filter-role');
    filterSel.innerHTML = '<option value="">-- Todos los roles --</option>' +
        allRoles.map(r => `<option value="${r.id}">${r.name}</option>`).join('');

    const routeSel = document.getElementById('route_id');
    routeSel.innerHTML = '<option value="">-- Seleccionar ruta --</option>' +
        routes.map(r => `<option value="${r.id}">${r.url_path} (${r.name})</option>`).join('');
}

async function loadPermissions() {
    const filterRole = document.getElementById('filter-role').value;
    let url = API_PERMS;
    if (filterRole) {
        url = API_PERMS + 'role/' + filterRole + '/';
    }
    const res = await fetch(url, { headers: authH() });
    const json = await res.json();
    const perms = json.data || [];
    const tbody = document.getElementById('perms-table');

    // Build a role_id -> name map for display
    const roleMap = {};
    allRoles.forEach(r => roleMap[r.id] = r.name);

    tbody.innerHTML = perms.map(p => {
        const roleName = p.role_name || roleMap[p.role_id] || p.role_id;
        return `
        <tr>
            <td>${p.id}</td>
            <td>${roleName}</td>
            <td>${p.url_path || p.route_name || p.route_id}</td>
            <td><span class="badge ${p.can_get ? 'badge-yes' : 'badge-no'}">${p.can_get ? 'Sí' : 'No'}</span></td>
            <td><span class="badge ${p.can_post ? 'badge-yes' : 'badge-no'}">${p.can_post ? 'Sí' : 'No'}</span></td>
            <td><span class="badge ${p.can_put ? 'badge-yes' : 'badge-no'}">${p.can_put ? 'Sí' : 'No'}</span></td>
            <td><span class="badge ${p.can_delete ? 'badge-yes' : 'badge-no'}">${p.can_delete ? 'Sí' : 'No'}</span></td>
            <td><button class="btn btn-danger" onclick="deletePerm(${p.id})">Eliminar</button></td>
        </tr>`;
    }).join('');
}

document.getElementById('filter-role').addEventListener('change', loadPermissions);

document.getElementById('form-perm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        role_id: parseInt(document.getElementById('role_id').value),
        route_id: parseInt(document.getElementById('route_id').value),
        can_get: document.getElementById('can_get').checked,
        can_post: document.getElementById('can_post').checked,
        can_put: document.getElementById('can_put').checked,
        can_delete: document.getElementById('can_delete').checked,
    };
    const res = await fetch(API_PERMS + 'create/', {
        method: 'POST',
        headers: authH({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) { showMsg('msg-perm', data.message, true); e.target.reset(); loadPermissions(); }
    else { showMsg('msg-perm', data.message || data.error, false); }
});

async function deletePerm(id) {
    if (!confirm('¿Eliminar este permiso?')) return;
    const res = await fetch(API_PERMS + id + '/delete/', { method: 'DELETE', headers: authH() });
    if (res.ok) loadPermissions();
}

loadSelects().then(() => loadPermissions());
