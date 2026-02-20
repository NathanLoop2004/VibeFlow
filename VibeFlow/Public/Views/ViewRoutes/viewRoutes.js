const API = '/api/routes/';

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

/* ── Carga de selects en cascada ── */
async function loadModuleSelect() {
    const res = await fetch('/api/modules/');
    const json = await res.json();
    const modules = json.data || [];
    const sel = document.getElementById('module_id');
    sel.innerHTML = '<option value="">-- Sin módulo --</option>' +
        modules.map(m => `<option value="${m.id}">${m.icon} ${m.name}</option>`).join('');
}

document.getElementById('module_id').addEventListener('change', async function () {
    const famSel = document.getElementById('family_id');
    const sfSel = document.getElementById('subfamily_id');
    sfSel.innerHTML = '<option value="">-- Sin subfamilia --</option>';
    sfSel.disabled = true;

    if (!this.value) {
        famSel.innerHTML = '<option value="">-- Sin familia --</option>';
        famSel.disabled = true;
        return;
    }
    const res = await fetch('/api/families/module/' + this.value + '/');
    const json = await res.json();
    const families = json.data || [];
    famSel.innerHTML = '<option value="">-- Sin familia --</option>' +
        families.map(f => `<option value="${f.id}">${f.icon} ${f.name}</option>`).join('');
    famSel.disabled = false;
});

document.getElementById('family_id').addEventListener('change', async function () {
    const sfSel = document.getElementById('subfamily_id');
    if (!this.value) {
        sfSel.innerHTML = '<option value="">-- Sin subfamilia --</option>';
        sfSel.disabled = true;
        return;
    }
    const res = await fetch('/api/subfamilies/family/' + this.value + '/');
    const json = await res.json();
    const sfs = json.data || [];
    sfSel.innerHTML = '<option value="">-- Sin subfamilia --</option>' +
        sfs.map(s => `<option value="${s.id}">${s.icon} ${s.name}</option>`).join('');
    sfSel.disabled = false;
});

/* ── Tabla de rutas ── */
let routesCache = [];

async function loadRoutes() {
    const res = await fetch(API);
    const json = await res.json();
    routesCache = json.data || [];
    const tbody = document.getElementById('routes-table');
    tbody.innerHTML = routesCache.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${r.url_path}</td>
            <td>${r.template_name}</td>
            <td>${r.name}</td>
            <td>${r.module_name || '<span class="text-muted">—</span>'}</td>
            <td>${r.family_name || '<span class="text-muted">—</span>'}</td>
            <td>${r.subfamily_name || '<span class="text-muted">—</span>'}</td>
            <td><span class="badge ${r.is_active ? 'badge-active' : 'badge-inactive'}">${r.is_active ? 'Activa' : 'Inactiva'}</span></td>
            <td>
                <div class="actions">
                    <button class="btn btn-edit" onclick="openEditModal(${r.id})">Editar</button>
                    <button class="btn btn-warning" onclick="toggleRoute(${r.id})">${r.is_active ? 'Desactivar' : 'Activar'}</button>
                    <button class="btn btn-danger" onclick="deleteRoute(${r.id})">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

/* ── Crear ruta ── */
document.getElementById('form-route').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        url_path: document.getElementById('url_path').value,
        template_name: document.getElementById('template_name').value,
        name: document.getElementById('route_name').value,
        is_active: document.getElementById('is_active').checked,
        module_id: parseInt(document.getElementById('module_id').value) || null,
        family_id: parseInt(document.getElementById('family_id').value) || null,
        subfamily_id: parseInt(document.getElementById('subfamily_id').value) || null,
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
        document.getElementById('family_id').disabled = true;
        document.getElementById('subfamily_id').disabled = true;
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

/* ── Modal Editar ── */
async function loadEditModuleSelect() {
    const res = await fetch('/api/modules/');
    const json = await res.json();
    const modules = json.data || [];
    const sel = document.getElementById('edit_module_id');
    sel.innerHTML = '<option value="">-- Sin módulo --</option>' +
        modules.map(m => `<option value="${m.id}">${m.icon} ${m.name}</option>`).join('');
}

document.getElementById('edit_module_id').addEventListener('change', async function () {
    const famSel = document.getElementById('edit_family_id');
    const sfSel = document.getElementById('edit_subfamily_id');
    sfSel.innerHTML = '<option value="">-- Sin subfamilia --</option>';
    sfSel.disabled = true;
    if (!this.value) {
        famSel.innerHTML = '<option value="">-- Sin familia --</option>';
        famSel.disabled = true;
        return;
    }
    const res = await fetch('/api/families/module/' + this.value + '/');
    const json = await res.json();
    const families = json.data || [];
    famSel.innerHTML = '<option value="">-- Sin familia --</option>' +
        families.map(f => `<option value="${f.id}">${f.icon} ${f.name}</option>`).join('');
    famSel.disabled = false;
});

document.getElementById('edit_family_id').addEventListener('change', async function () {
    const sfSel = document.getElementById('edit_subfamily_id');
    if (!this.value) {
        sfSel.innerHTML = '<option value="">-- Sin subfamilia --</option>';
        sfSel.disabled = true;
        return;
    }
    const res = await fetch('/api/subfamilies/family/' + this.value + '/');
    const json = await res.json();
    const sfs = json.data || [];
    sfSel.innerHTML = '<option value="">-- Sin subfamilia --</option>' +
        sfs.map(s => `<option value="${s.id}">${s.icon} ${s.name}</option>`).join('');
    sfSel.disabled = false;
});

async function openEditModal(id) {
    const route = routesCache.find(r => r.id === id);
    if (!route) return;

    document.getElementById('edit_id').value = route.id;
    document.getElementById('edit_url_path').value = route.url_path;
    document.getElementById('edit_template_name').value = route.template_name;
    document.getElementById('edit_route_name').value = route.name;
    document.getElementById('edit_is_active').checked = route.is_active;

    await loadEditModuleSelect();

    const modSel = document.getElementById('edit_module_id');
    const famSel = document.getElementById('edit_family_id');
    const sfSel = document.getElementById('edit_subfamily_id');

    if (route.module_id) {
        modSel.value = route.module_id;
        // Load families for this module
        const famRes = await fetch('/api/families/module/' + route.module_id + '/');
        const famJson = await famRes.json();
        const families = famJson.data || [];
        famSel.innerHTML = '<option value="">-- Sin familia --</option>' +
            families.map(f => `<option value="${f.id}">${f.icon} ${f.name}</option>`).join('');
        famSel.disabled = false;

        if (route.family_id) {
            famSel.value = route.family_id;
            // Load subfamilies for this family
            const sfRes = await fetch('/api/subfamilies/family/' + route.family_id + '/');
            const sfJson = await sfRes.json();
            const sfs = sfJson.data || [];
            sfSel.innerHTML = '<option value="">-- Sin subfamilia --</option>' +
                sfs.map(s => `<option value="${s.id}">${s.icon} ${s.name}</option>`).join('');
            sfSel.disabled = false;

            if (route.subfamily_id) {
                sfSel.value = route.subfamily_id;
            }
        }
    }

    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

// Cerrar modal al hacer click fuera
document.getElementById('modal-overlay').addEventListener('click', function (e) {
    if (e.target === this) closeEditModal();
});

document.getElementById('form-edit').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit_id').value;
    const body = {
        url_path: document.getElementById('edit_url_path').value,
        template_name: document.getElementById('edit_template_name').value,
        name: document.getElementById('edit_route_name').value,
        is_active: document.getElementById('edit_is_active').checked,
        module_id: parseInt(document.getElementById('edit_module_id').value) || null,
        family_id: parseInt(document.getElementById('edit_family_id').value) || null,
        subfamily_id: parseInt(document.getElementById('edit_subfamily_id').value) || null,
    };
    const res = await fetch(API + id + '/update/', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) {
        showMsg('msg-edit', data.message, true);
        setTimeout(() => {
            closeEditModal();
            loadRoutes();
        }, 1000);
    } else {
        showMsg('msg-edit', data.message || 'Error al actualizar', false);
    }
});

loadModuleSelect().then(() => loadRoutes());
