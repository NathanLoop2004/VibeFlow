const API = '/api/subfamilies/';

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

/* Cascada módulo -> familia (crear) */
document.getElementById('module_id').addEventListener('change', async function () {
    const famSel = document.getElementById('family_id');
    if (!this.value) {
        famSel.innerHTML = '<option value="">-- Seleccionar familia --</option>';
        famSel.disabled = true;
        return;
    }
    const res = await fetch('/api/families/module/' + this.value + '/', { headers: authH() });
    const json = await res.json();
    const families = json.data || [];
    famSel.innerHTML = '<option value="">-- Seleccionar familia --</option>' +
        families.map(f => `<option value="${f.id}">${f.icon} ${f.name}</option>`).join('');
    famSel.disabled = false;
});

/* Cascada módulo -> familia (editar) */
document.getElementById('edit_module_id').addEventListener('change', async function () {
    const famSel = document.getElementById('edit_family_id');
    if (!this.value) {
        famSel.innerHTML = '<option value="">-- Seleccionar familia --</option>';
        famSel.disabled = true;
        return;
    }
    const res = await fetch('/api/families/module/' + this.value + '/', { headers: authH() });
    const json = await res.json();
    const families = json.data || [];
    famSel.innerHTML = '<option value="">-- Seleccionar familia --</option>' +
        families.map(f => `<option value="${f.id}">${f.icon} ${f.name}</option>`).join('');
    famSel.disabled = false;
});

let subfamiliesCache = [];

async function loadSubfamilies() {
    const res = await fetch(API, { headers: authH() });
    const json = await res.json();
    subfamiliesCache = json.data || [];
    const tbody = document.getElementById('subfamilies-table');
    tbody.innerHTML = subfamiliesCache.map(sf => `
        <tr>
            <td>${sf.id}</td>
            <td class="icon-cell">${sf.icon}</td>
            <td>${sf.name}</td>
            <td>${sf.family_name || '—'}</td>
            <td>${sf.module_name || '—'}</td>
            <td>${sf.display_order}</td>
            <td><span class="badge ${sf.is_active ? 'badge-active' : 'badge-inactive'}">${sf.is_active ? 'Activa' : 'Inactiva'}</span></td>
            <td>
                <div class="actions">
                    <button class="btn btn-edit" onclick="openModal(${sf.id})">Editar</button>
                    <button class="btn btn-danger" onclick="deleteSubfamily(${sf.id})">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

/* Crear */
document.getElementById('form-subfamily').addEventListener('submit', async (e) => {
    e.preventDefault();
    const family_id = parseInt(document.getElementById('family_id').value);
    if (!family_id) { showMsg('msg-create', 'Selecciona una familia', false); return; }
    const body = {
        family_id,
        name: document.getElementById('name').value.trim(),
        icon: document.getElementById('icon').value.trim() || '📄',
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
        document.getElementById('icon').value = '📄';
        document.getElementById('is_active').checked = true;
        document.getElementById('family_id').disabled = true;
        loadSubfamilies();
    } else {
        showMsg('msg-create', data.message || 'Error al crear', false);
    }
});

/* Eliminar */
async function deleteSubfamily(id) {
    if (!confirm('¿Eliminar esta subfamilia?')) return;
    const res = await fetch(API + id + '/delete/', { method: 'DELETE', headers: authH() });
    if (res.ok) loadSubfamilies();
}

/* Modal Editar */
async function openModal(id) {
    const sf = subfamiliesCache.find(x => x.id === id);
    if (!sf) return;

    document.getElementById('edit_id').value = sf.id;
    document.getElementById('edit_name').value = sf.name;
    document.getElementById('edit_icon').value = sf.icon;
    document.getElementById('edit_display_order').value = sf.display_order;
    document.getElementById('edit_is_active').checked = sf.is_active;

    // Cargar módulo y familia
    if (sf.module_id) {
        document.getElementById('edit_module_id').value = sf.module_id;
        const res = await fetch('/api/families/module/' + sf.module_id + '/', { headers: authH() });
        const json = await res.json();
        const families = json.data || [];
        const famSel = document.getElementById('edit_family_id');
        famSel.innerHTML = '<option value="">-- Seleccionar familia --</option>' +
            families.map(f => `<option value="${f.id}">${f.icon} ${f.name}</option>`).join('');
        famSel.disabled = false;
        famSel.value = sf.family_id;
    }

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
    const family_id = parseInt(document.getElementById('edit_family_id').value);
    if (!family_id) { showMsg('msg-edit', 'Selecciona una familia', false); return; }
    const body = {
        family_id,
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
        setTimeout(() => { closeModal(); loadSubfamilies(); }, 800);
    } else {
        showMsg('msg-edit', data.message || 'Error al actualizar', false);
    }
});

loadModuleSelects().then(() => loadSubfamilies());
