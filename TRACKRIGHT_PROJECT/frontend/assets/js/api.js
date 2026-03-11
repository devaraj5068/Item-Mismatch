// api.js - Backend API calls

const API_BASE = '/api/';

function getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Token ${token}` : ''
    };
}

async function apiCall(endpoint, options = {}) {
    const url = API_BASE + endpoint;
    const config = {
        headers: getAuthHeaders(),
        ...options
    };
    const response = await fetch(url, config);
    if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
    }
    return response.json();
}

async function login(username, password) {
    const response = await fetch(API_BASE + 'login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    if (!response.ok) {
        throw new Error('Login failed');
    }
    return response.json();
}

async function getOrders() {
    return apiCall('orders/');
}

async function getProducts() {
    return apiCall('products/');
}

async function getMismatchReports() {
    return apiCall('mismatchreports/');
}