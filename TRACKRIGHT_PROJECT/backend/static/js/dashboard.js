// dashboard.js - Dashboard functionality and charts

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Dashboard DOM loaded');
    try {
        const token = localStorage.getItem('auth_token');
        console.log('Auth token:', token ? 'present' : 'missing');
        
        // Load user profile
        loadUserProfile();
        
        // Load dashboard stats
        console.log('Loading dashboard stats...');
        const statsResponse = await fetch('/api/dashboard/stats/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Stats response status:', statsResponse.status);
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            console.log('Stats data:', stats);
            updateDashboardStats(stats);
        } else {
            console.error('Failed to load stats:', statsResponse.status);
        }
        
        // Load recent orders
        loadRecentOrders();
        
        // Load pending tasks
        loadPendingTasks();
        
        // Initialize charts
        initializeCharts();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
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
            if (userNameElement) {
                userNameElement.textContent = user.username;
            }
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

function updateDashboardStats(stats) {
    const scansToday = document.getElementById('scans-today');
    const verifiedOrders = document.getElementById('verified-orders');
    const mismatchRate = document.getElementById('mismatch-rate');
    const totalOrders = document.getElementById('total-orders');

    if (scansToday) scansToday.textContent = stats.todays_scans || 0;
    if (verifiedOrders) verifiedOrders.textContent = stats.verified_orders || 0;
    if (mismatchRate) mismatchRate.textContent = `${stats.mismatch_rate || 0}%`;
    if (totalOrders) totalOrders.textContent = stats.total_orders || 0;

    // Initialize charts with real data
    initializeCharts(stats);
}

async function loadRecentOrders() {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('/api/orders/?limit=5', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const orders = await response.json();
            const ordersList = Array.isArray(orders) ? orders : orders.results || [];
            
            const tbody = document.getElementById('recent-orders');
            if (tbody && ordersList.length > 0) {
                tbody.innerHTML = ordersList.map(order => `
                    <tr>
                        <td>#${order.id}</td>
                        <td>${order.customer_name}</td>
                        <td>N/A</td>
                        <td><span class="badge badge-${getStatusBadgeColor(order.status)}">${order.status}</span></td>
                        <td>${new Date(order.created_at).toLocaleDateString()}</td>
                        <td><button class="btn" style="padding: 5px 10px; font-size: 12px;">View</button></td>
                    </tr>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

async function loadPendingTasks() {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('http://localhost:8000/api/tasks/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const tasks = await response.json();
            const tasksList = Array.isArray(tasks) ? tasks : tasks.results || [];
            const pendingTasks = tasksList.filter(t => t.status !== 'completed');
            
            const tbody = document.getElementById('pending-tasks');
            if (tbody && pendingTasks.length > 0) {
                tbody.innerHTML = pendingTasks.slice(0, 5).map(task => `
                    <tr>
                        <td>${task.title}</td>
                        <td><span class="badge badge-${getPriorityBadgeColor(task.priority)}">${task.priority}</span></td>
                        <td>${task.due_date || '-'}</td>
                    </tr>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function initializeCharts(stats) {
    const ordersChartCanvas = document.getElementById('ordersChart');
    const mismatchChartCanvas = document.getElementById('mismatchChart');

    if (ordersChartCanvas && stats.weekly_scans) {
        const weeklyData = stats.weekly_scans;
        new Chart(ordersChartCanvas, {
            type: 'line',
            data: {
                labels: weeklyData.map(item => new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' })),
                datasets: [{
                    label: 'Daily Scans',
                    data: weeklyData.map(item => item.scans),
                    backgroundColor: 'rgba(30, 64, 175, 0.1)',
                    borderColor: '#1e40af',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // use department data if available, otherwise fallback to status
    if (mismatchChartCanvas) {
        let labels, data, chartLabel, colors;
        if (stats.mismatches_by_department && Object.keys(stats.mismatches_by_department).length) {
            const deptData = stats.mismatches_by_department;
            labels = Object.keys(deptData);
            data = Object.values(deptData);
            chartLabel = 'Mismatches by Department';
            colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#a855f7', '#6366f1'];
        } else if (stats.mismatches_by_status) {
            const mismatchData = stats.mismatches_by_status;
            labels = Object.keys(mismatchData);
            data = Object.values(mismatchData);
            chartLabel = 'Mismatches by Status';
            colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6'];
        }
        if (labels && data) {
            new Chart(mismatchChartCanvas, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        label: chartLabel,
                        data: data,
                        backgroundColor: colors
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'right'
                        }
                    }
                }
            });
        }
    }
}

function getStatusBadgeColor(status) {
    switch (status) {
        case 'pending': return 'primary';
        case 'shipped': return 'warning';
        case 'delivered': return 'success';
        default: return 'primary';
    }
}

function getPriorityBadgeColor(priority) {
    switch (priority) {
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'primary';
        default: return 'primary';
    }
}