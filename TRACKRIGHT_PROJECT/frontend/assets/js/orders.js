// orders.js - Orders table rendering with action buttons

document.addEventListener('DOMContentLoaded', async function() {
    try {
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.href = '/login/';
            return;
        }
        
        const response = await fetch('/api/orders/', {
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch orders');
        }
        
        const orders = await response.json();
        const ordersDiv = document.getElementById('orders-list');
        
        if (!orders || orders.length === 0) {
            ordersDiv.innerHTML = '<p style="text-align: center; color: #888; padding: 40px;">No orders found</p>';
            return;
        }
        
        // Create table
        const table = document.createElement('table');
        table.className = 'orders-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Order ID</th>
                    <th>Order Number</th>
                    <th>Customer</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${orders.map(order => `
                    <tr>
                        <td>#${order.id}</td>
                        <td>${order.order_number}</td>
                        <td>${order.customer_name}</td>
                        <td>
                            <span class="status-badge status-${order.status}">
                                ${order.get_status_display || capitalizeStatus(order.status)}
                            </span>
                        </td>
                        <td>${new Date(order.created_at).toLocaleDateString()}</td>
                        <td>
                            <div class="action-buttons">
                                <a href="/orders/view/${order.id}/" class="btn btn-sm btn-view" title="View Details">View</a>
                                <a href="/orders/edit/${order.id}/" class="btn btn-sm btn-edit" title="Edit Order">Edit</a>
                                <a href="/orders/delete/${order.id}/" class="btn btn-sm btn-delete" title="Delete Order" onclick="return confirm('Are you sure you want to delete this order?');">Delete</a>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        
        ordersDiv.appendChild(table);
        
    } catch (error) {
        console.error('Error loading orders:', error);
        const ordersDiv = document.getElementById('orders-list');
        ordersDiv.innerHTML = `<p style="text-align: center; color: #c82333; padding: 40px;">Error loading orders. Please refresh the page.</p>`;
    }
});

function capitalizeStatus(status) {
    return status.charAt(0).toUpperCase() + status.slice(1);
}