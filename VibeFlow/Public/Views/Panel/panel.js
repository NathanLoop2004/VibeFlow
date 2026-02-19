function loadView(view) {
    const routes = {
        users: '/views/users/',
        roles: '/views/roles/',
        userRoles: '/views/user-roles/',
    };
    document.getElementById('view-frame').src = routes[view];

    // Update active link
    document.querySelectorAll('.sidebar nav a').forEach(a => a.classList.remove('active'));
    event.currentTarget.classList.add('active');
}
