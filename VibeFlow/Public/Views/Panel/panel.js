const ICONS = {
    'view-users': '👤',
    'view-roles': '🛡️',
    'view-user-roles': '🔗',
    'view-routes': '🗺️',
    'route-permissions': '🔐',
};

function loadView(urlPath, el) {
    document.getElementById('view-frame').src = '/' + urlPath;
    document.querySelectorAll('#nav-menu a').forEach(a => a.classList.remove('active'));
    if (el) el.classList.add('active');
}

async function loadMenu() {
    try {
        const res = await fetch('/api/auth/my-routes/');
        const json = await res.json();
        const routes = json.data || [];
        const nav = document.getElementById('nav-menu');

        if (routes.length === 0) {
            nav.innerHTML = '<p class="nav-empty">No tienes rutas asignadas</p>';
            return;
        }

        nav.innerHTML = routes.map((r, i) => {
            const icon = ICONS[r.route_name] || '📄';
            const active = i === 0 ? ' class="active"' : '';
            return `<a href="#"${active} onclick="loadView('${r.url_path}', this)">
                <span class="icon">${icon}</span> ${r.route_name}
            </a>`;
        }).join('');

        // Cargar la primera vista automáticamente
        document.getElementById('view-frame').src = '/' + routes[0].url_path;
    } catch (e) {
        console.error('Error cargando menú:', e);
        document.getElementById('nav-menu').innerHTML = '<p class="nav-empty">Error cargando menú</p>';
    }
}

loadMenu();
