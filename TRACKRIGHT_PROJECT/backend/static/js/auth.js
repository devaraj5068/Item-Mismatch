// auth.js - Authentication handling

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('auth_token');
    const currentPath = window.location.pathname;
    
    // Redirect unauthenticated users to login page (except login itself)
    if (!token && !currentPath.includes('login') && !currentPath.includes('landing')) {
        window.location.href = '/accounts/login/';
    }
    
    if (token && currentPath.includes('dashboard')) {
        loadUserProfile();
    }
});

async function loadUserProfile() {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('/api/user/profile/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        if (response.ok) {
            const user = await response.json();
            const userNameElement = document.getElementById('user-name');
            if (userNameElement) userNameElement.textContent = user.username;
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

// Login form handler
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        try {
            const resp = await fetch('/accounts/api/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await resp.json();
            if (resp.ok) {
                localStorage.setItem('auth_token', data.token || 'fake-token');
                window.location.href = data.redirect || '/dashboard/';
            } else {
                document.querySelector('.text-danger')?.remove();
                const err = document.createElement('p');
                err.className = 'text-danger text-center';
                err.textContent = data.error || 'Invalid credentials';
                loginForm.prepend(err);
            }
        } catch (error) {
            console.error('Login request failed', error);
        }
    });
}

// Logout handler
const logoutLink = document.querySelector('a[href="/accounts/logout/"]');
if (logoutLink) {
    logoutLink.addEventListener('click', function() {
        localStorage.removeItem('auth_token');
    });
}
