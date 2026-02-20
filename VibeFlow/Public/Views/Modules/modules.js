const API = '/api/modules/';

function getToken() { return localStorage.getItem('vf_token') || ''; }
function authH(extra = {}) { return { 'Authorization': 'Bearer ' + getToken(), ...extra }; }

function showMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + (ok ? 'msg-ok' : 'msg-err');
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

let modulesCache = [];

async function loadModules() {
    const res = await fetch(API, { headers: authH() });
    const json = await res.json();
    modulesCache = json.data || [];
    const tbody = document.getElementById('modules-table');
    tbody.innerHTML = modulesCache.map(m => `
        <tr>
            <td>${m.id}</td>
            <td class="icon-cell">${m.icon}</td>
            <td>${m.name}</td>
            <td>${m.display_order}</td>
            <td><span class="badge ${m.is_active ? 'badge-active' : 'badge-inactive'}">${m.is_active ? 'Activo' : 'Inactivo'}</span></td>
            <td>
                <div class="actions">
                    <button class="btn btn-edit" onclick="openModal(${m.id})">Editar</button>
                    <button class="btn btn-danger" onclick="deleteModule(${m.id})">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

/* Crear */
document.getElementById('form-module').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        name: document.getElementById('name').value.trim(),
        icon: document.getElementById('icon').value.trim() || '📁',
        display_order: parseInt(document.getElementById('display_order').value) || 0,
        is_active: document.getElementById('is_active').checked,
    };
    const res = await fetch(API + 'create/', {
        method: 'POST',
        headers: authH({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
    });
    const data = await res.json();
    if (res.ok) {
        showMsg('msg-create', data.message, true);
        e.target.reset();
        document.getElementById('icon').value = '📁';
        document.getElementById('is_active').checked = true;
        loadModules();
    } else {
        showMsg('msg-create', data.message || 'Error al crear', false);
    }
});

/* Eliminar */
async function deleteModule(id) {
    if (!confirm('¿Eliminar este módulo? Se desvinculará de las rutas asociadas.')) return;
    const res = await fetch(API + id + '/delete/', { method: 'DELETE', headers: authH() });
    if (res.ok) loadModules();
}

/* Modal Editar */
function openModal(id) {
    const m = modulesCache.find(x => x.id === id);
    if (!m) return;
    document.getElementById('edit_id').value = m.id;
    document.getElementById('edit_name').value = m.name;
    document.getElementById('edit_icon').value = m.icon;
    document.getElementById('edit_display_order').value = m.display_order;
    document.getElementById('edit_is_active').checked = m.is_active;
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
        setTimeout(() => { closeModal(); loadModules(); }, 800);
    } else {
        showMsg('msg-edit', data.message || 'Error al actualizar', false);
    }
});

loadModules();
