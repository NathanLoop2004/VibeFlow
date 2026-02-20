function loadView(urlPath, el) {
    document.getElementById('view-frame').src = '/' + urlPath;
    document.querySelectorAll('#nav-menu a.nav-link').forEach(a => a.classList.remove('active'));
    if (el) el.classList.add('active');
}

function toggleSection(header) {
    const content = header.nextElementSibling;
    const arrow = header.querySelector('.arrow');
    const isOpen = content.style.display !== 'none';
    content.style.display = isOpen ? 'none' : 'block';
    arrow.textContent = isOpen ? '▸' : '▾';
}

function buildTree(routes) {
    /*
     * Construye un árbol: módulo → familia → subfamilia → rutas
     * Las rutas sin módulo se agrupan al final como "Sin clasificar"
     */
    const tree = {};
    const loose = [];

    routes.forEach(r => {
        if (!r.module_id) {
            loose.push(r);
            return;
        }
        const mKey = r.module_id;
        if (!tree[mKey]) {
            tree[mKey] = {
                name: r.module_name,
                icon: r.module_icon || '📁',
                order: r.module_order || 0,
                families: {},
                routes: [],
            };
        }
        const mod = tree[mKey];

        if (!r.family_id) {
            mod.routes.push(r);
            return;
        }

        const fKey = r.family_id;
        if (!mod.families[fKey]) {
            mod.families[fKey] = {
                name: r.family_name,
                icon: r.family_icon || '📂',
                order: r.family_order || 0,
                subfamilies: {},
                routes: [],
            };
        }
        const fam = mod.families[fKey];

        if (!r.subfamily_id) {
            fam.routes.push(r);
            return;
        }

        const sfKey = r.subfamily_id;
        if (!fam.subfamilies[sfKey]) {
            fam.subfamilies[sfKey] = {
                name: r.subfamily_name,
                icon: r.subfamily_icon || '📄',
                order: r.subfamily_order || 0,
                routes: [],
            };
        }
        fam.subfamilies[sfKey].routes.push(r);
    });

    return { tree, loose };
}

function renderRouteLink(r, isFirst) {
    const active = isFirst ? ' active' : '';
    return `<a href="#" class="nav-link${active}" onclick="loadView('${r.url_path}', this)">
        <span class="icon">📄</span> ${r.route_name}
    </a>`;
}

function renderNav(routes) {
    if (routes.length === 0) return '<p class="nav-empty">No tienes rutas asignadas</p>';

    const { tree, loose } = buildTree(routes);
    let html = '';
    let first = true;

    // Módulos ordenados
    const modules = Object.values(tree).sort((a, b) => a.order - b.order);

    modules.forEach(mod => {
        html += `<div class="nav-module">
            <div class="nav-header" onclick="toggleSection(this)">
                <span>${mod.icon} ${mod.name}</span><span class="arrow">▸</span>
            </div>
            <div class="nav-content" style="display:none">`;

        // Rutas directas del módulo
        mod.routes.forEach(r => { html += renderRouteLink(r, first); first = false; });

        // Familias ordenadas
        const families = Object.values(mod.families).sort((a, b) => a.order - b.order);
        families.forEach(fam => {
            html += `<div class="nav-family">
                <div class="nav-subheader" onclick="toggleSection(this)">
                    <span>${fam.icon} ${fam.name}</span><span class="arrow">▸</span>
                </div>
                <div class="nav-content" style="display:none">`;

            fam.routes.forEach(r => { html += renderRouteLink(r, first); first = false; });

            // Subfamilias
            const subfams = Object.values(fam.subfamilies).sort((a, b) => a.order - b.order);
            subfams.forEach(sf => {
                html += `<div class="nav-subfamily">
                    <div class="nav-subheader sf" onclick="toggleSection(this)">
                        <span>${sf.icon} ${sf.name}</span><span class="arrow">▸</span>
                    </div>
                    <div class="nav-content" style="display:none">`;
                sf.routes.forEach(r => { html += renderRouteLink(r, first); first = false; });
                html += '</div></div>';
            });

            html += '</div></div>';
        });

        html += '</div></div>';
    });

    // Rutas sin módulo
    loose.forEach(r => { html += renderRouteLink(r, first); first = false; });

    return html;
}

async function loadMenu() {
    try {
        const res = await fetch('/api/auth/my-routes/');
        const json = await res.json();
        const routes = json.data || [];
        const nav = document.getElementById('nav-menu');

        nav.innerHTML = renderNav(routes);

        // Cargar la primera vista
        if (routes.length > 0) {
            const firstRoute = routes.find(r => r.module_id) || routes[0];
            document.getElementById('view-frame').src = '/' + firstRoute.url_path;
        }
    } catch (e) {
        console.error('Error cargando menú:', e);
        document.getElementById('nav-menu').innerHTML = '<p class="nav-empty">Error cargando menú</p>';
    }
}

loadMenu();
