// auth.js - JWT authentication

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('auth_token');
    if (!token && window.location.pathname !== '/index.html') {
        window.location.href = 'index.html';
    }
});

document.getElementById('login-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
        const data = await login(username, password);
        localStorage.setItem('auth_token', data.token);
        window.location.href = 'dashboard.html';
    } catch (error) {
        document.getElementById('error-message').textContent = 'Invalid credentials';
    }
});

document.getElementById('logout')?.addEventListener('click', function() {
    localStorage.removeItem('auth_token');
    window.location.href = 'index.html';
});