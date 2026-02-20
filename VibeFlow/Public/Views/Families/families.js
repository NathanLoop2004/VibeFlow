const API = '/api/families/';

function getToken() { return localStorage.getItem('vf_token') || ''; }
function authH(extra = {}) { return { 'Authorization': 'Bearer ' + getToken(), ...extra }; }

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

/* Cargar módulos en selects */
async function loadModuleSelects() {
    const res = await fetch('/api/modules/', { headers: authH() });
    const json = await res.json();
    const modules = json.data || [];
    const opts = '<option value="">-- Seleccionar módulo --</option>' +
        modules.map(m => `<option value="${m.id}">${m.icon} ${m.name}</option>`).join('');
    document.getElementById('module_id').innerHTML = opts;
    document.getElementById('edit_module_id').innerHTML = opts;
}

let familiesCache = [];

async function loadFamilies() {
    const res = await fetch(API, { headers: authH() });
    const json = await res.json();
    familiesCache = json.data || [];
    const tbody = document.getElementById('families-table');
    tbody.innerHTML = familiesCache.map(f => `
        <tr>
            <td>${f.id}</td>
            <td class="icon-cell">${f.icon}</td>
            <td>${f.name}</td>
            <td>${f.module_name || '—'}</td>
            <td>${f.display_order}</td>
            <td><span class="badge ${f.is_active ? 'badge-active' : 'badge-inactive'}">${f.is_active ? 'Activa' : 'Inactiva'}</span></td>
            <td>
                <div class="actions">
                    <button class="btn btn-edit" onclick="openModal(${f.id})">Editar</button>
                    <button class="btn btn-danger" onclick="deleteFamily(${f.id})">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

/* Crear */
document.getElementById('form-family').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        module_id: parseInt(document.getElementById('module_id').value),
        name: document.getElementById('name').value.trim(),
        icon: document.getElementById('icon').value.trim() || '📂',
        display_order: parseInt(document.getElementById('display_order').value) || 0,
        is_active: document.getElementById('is_active').checked,
    };
    if (!body.module_id) { showMsg('msg-create', 'Selecciona un módulo', false); return; }
    const res = await fetch(API + 'create/', {
        method: 'POST',
        headers: authH({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) {
        showMsg('msg-create', data.message, true);
        e.target.reset();
        document.getElementById('icon').value = '📂';
        document.getElementById('is_active').checked = true;
        loadFamilies();
    } else {
        showMsg('msg-create', data.message || 'Error al crear', false);
    }
});

/* Eliminar */
async function deleteFamily(id) {
    if (!confirm('¿Eliminar esta familia?')) return;
    const res = await fetch(API + id + '/delete/', { method: 'DELETE', headers: authH() });
    if (res.ok) loadFamilies();
}

/* Modal Editar */
function openModal(id) {
    const f = familiesCache.find(x => x.id === id);
    if (!f) return;
    document.getElementById('edit_id').value = f.id;
    document.getElementById('edit_name').value = f.name;
    document.getElementById('edit_icon').value = f.icon;
    document.getElementById('edit_display_order').value = f.display_order;
    document.getElementById('edit_is_active').checked = f.is_active;
    document.getElementById('edit_module_id').value = f.module_id;
    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

document.getElementById('modal-overlay').addEventListener('click', function (e) {
    if (e.target === this) closeModal();
});

document.getElementById('form-edit').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit_id').value;
    const body = {
        module_id: parseInt(document.getElementById('edit_module_id').value),
        name: document.getElementById('edit_name').value.trim(),
        icon: document.getElementById('edit_icon').value.trim(),
        display_order: parseInt(document.getElementById('edit_display_order').value) || 0,
        is_active: document.getElementById('edit_is_active').checked,
    };
    const res = await fetch(API + id + '/update/', {
        method: 'PUT',
        headers: authH({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) {
        showMsg('msg-edit', data.message, true);
        setTimeout(() => { closeModal(); loadFamilies(); }, 800);
    } else {
        showMsg('msg-edit', data.message || 'Error al actualizar', false);
    }
});

loadModuleSelects().then(() => loadFamilies());
