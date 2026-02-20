const API = '/api/routes/';

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

async function loadRoutes() {
    const res = await fetch(API);
    const json = await res.json();
    const routes = json.data || [];
    const tbody = document.getElementById('routes-table');
    tbody.innerHTML = routes.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${r.url_path}</td>
            <td>${r.template_name}</td>
            <td>${r.name}</td>
            <td><span class="badge ${r.is_active ? 'badge-green' : 'badge-red'}">${r.is_active ? 'Activa' : 'Inactiva'}</span></td>
            <td>${r.created_at ? new Date(r.created_at).toLocaleDateString('es') : '—'}</td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-toggle" onclick="toggleRoute(${r.id})">${r.is_active ? 'Desactivar' : 'Activar'}</button>
                    <button class="btn btn-danger" onclick="deleteRoute(${r.id})">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

document.getElementById('form-route').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        url_path: document.getElementById('url_path').value,
        template_name: document.getElementById('template_name').value,
        name: document.getElementById('route_name').value,
        is_active: document.getElementById('is_active').checked,
    };
    const res = await fetch(API + 'create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) {
        showMsg('msg-route', data.message, true);
        e.target.reset();
        document.getElementById('is_active').checked = true;
        loadRoutes();
    } else {
        showMsg('msg-route', data.message || 'Error al crear ruta', false);
    }
});

async function toggleRoute(id) {
    const res = await fetch(API + id + '/toggle/', { method: 'PATCH' });
    if (res.ok) loadRoutes();
}

async function deleteRoute(id) {
    if (!confirm('¿Eliminar esta ruta?')) return;
    const res = await fetch(API + id + '/delete/', { method: 'DELETE' });
    if (res.ok) loadRoutes();
}

loadRoutes();
