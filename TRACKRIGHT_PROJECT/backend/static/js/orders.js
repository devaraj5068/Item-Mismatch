// orders.js - Orders page functionality

document.addEventListener('DOMContentLoaded', function() {
    loadOrders();
    setupSearch();
    setupNewOrderModal();
    setupLogout();
});

let currentPage = 1;
let searchTimeout;

async function loadOrders(searchQuery = '') {
    console.log('Loading orders...');
    try {
        const token = localStorage.getItem('auth_token');
        console.log('Auth token for orders:', token ? 'present' : 'missing');
        let url = '/api/orders/';

        if (searchQuery) {
            url += `?search=${encodeURIComponent(searchQuery)}`;
        }

        console.log('Fetching orders from:', url);
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        console.log('Orders response status:', response.status);
        if (response.ok) {
            const orders = await response.json();
            console.log('Orders data:', orders);
            const ordersList = Array.isArray(orders) ? orders : orders.results || [];

            const tbody = document.getElementById('orders-list');
            if (tbody && ordersList.length > 0) {
                tbody.innerHTML = ordersList.map(order => {
                    // Get barcodes from order items
                        return `
                    <tr>
                        <td>${order.order_number}</td>
                        <td>${order.customer_name}</td>
                        <td>${order.items ? order.items.length : 0} items</td>
                        <td style="font-family: monospace; font-size: 12px;">${order.barcode || 'Generating...'}</td>
                        <td><span class="badge badge-${getStatusBadgeColor(order.status)}">${order.status}</span></td>
                        <td>${new Date(order.created_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-sm" onclick="viewOrder(${order.id})">View</button>
                            <button class="btn btn-sm btn-warning" onclick="editOrder(${order.id})">Edit</button>
                            <button class="btn btn-sm btn-info" onclick="printBarcode('${order.barcode}', '${order.order_number}', '${order.customer_name}')">🖨️ Print</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteOrder(${order.id})">Delete</button>
                        </td>
                    </tr>
                `}).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #6b7280;">No orders found</td></tr>';
            }
        }
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

function setupSearch() {
    const searchInput = document.querySelector('.search-bar');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                loadOrders(e.target.value);
            }, 300); // Debounce search
        });
    }
}

function setupNewOrderModal() {
    const newOrderBtn = document.querySelector('.btn-primary');
    if (newOrderBtn && newOrderBtn.textContent.includes('New Order')) {
        newOrderBtn.addEventListener('click', showNewOrderModal);
    }
}

function showNewOrderModal() {
    // Create modal HTML
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Create New Order</h3>
                <span class="modal-close">&times;</span>
            </div>
            <form id="new-order-form">
                <div class="form-group">
                    <label for="order_number">Order Number</label>
                    <input type="text" id="order_number" name="order_number" required>
                </div>
                <div class="form-group">
                    <label for="customer_name">Customer Name</label>
                    <input type="text" id="customer_name" name="customer_name" required>
                </div>
                <div class="form-group">
                    <label for="status">Status</label>
                    <select id="status" name="status" required>
                        <option value="pending">Pending</option>
                        <option value="processing">Processing</option>
                        <option value="shipped">Shipped</option>
                        <option value="delivered">Delivered</option>
                    </select>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Order</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);
    modal.style.display = 'block';

    // Setup form submission
    const form = modal.querySelector('#new-order-form');
    form.addEventListener('submit', handleNewOrderSubmit);

    // Setup close button
    const closeBtn = modal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => closeModal());

    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
}

async function handleNewOrderSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const orderData = {
        order_number: formData.get('order_number'),
        customer_name: formData.get('customer_name'),
        status: formData.get('status')
    };

    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('http://localhost:8000/api/orders/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            closeModal();
            loadOrders();
            showToast('Order created successfully!', 'success');
        } else {
            const error = await response.json();
            showToast('Error creating order: ' + JSON.stringify(error), 'error');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        showToast('Error creating order', 'error');
    }
}

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

async function viewOrder(orderId) {
    // Navigate to order detail page
    window.location.href = `/orders/view/${orderId}/`;
}

async function editOrder(orderId) {
    // Navigate to order edit page
    window.location.href = `/orders/edit/${orderId}/`;
}

async function deleteOrder(orderId) {
    if (confirm('Are you sure you want to delete this order?')) {
        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(`http://localhost:8000/api/orders/${orderId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                loadOrders();
                showToast('Order deleted successfully!', 'success');
            } else {
                showToast('Error deleting order', 'error');
            }
        } catch (error) {
            console.error('Error deleting order:', error);
            showToast('Error deleting order', 'error');
        }
    }
}

function getStatusBadgeColor(status) {
    switch (status) {
        case 'pending': return 'primary';
        case 'processing': return 'warning';
        case 'shipped': return 'info';
        case 'delivered': return 'success';
        default: return 'primary';
    }
}

function printBarcode(barcode, orderNumber, customerName) {
    const printWindow = window.open('', '_blank');
    const barcodeDisplay = generateBarcodeDisplay(barcode);
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Print Barcode - ${orderNumber}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background: white;
                }
                .barcode-container {
                    border: 2px solid #333;
                    padding: 20px;
                    text-align: center;
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                }
                .order-header {
                    margin-bottom: 20px;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 15px;
                }
                .order-number {
                    font-size: 18px;
                    font-weight: bold;
                    color: #1f2937;
                }
                .customer-name {
                    font-size: 14px;
                    color: #6b7280;
                    margin-top: 5px;
                }
                .barcode-display {
                    font-family: 'Courier New', monospace;
                    font-size: 48px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    margin: 30px 0;
                    padding: 20px;
                    border: 1px solid #ddd;
                    background: #f9fafb;
                }
                .barcode-label {
                    font-size: 12px;
                    color: #6b7280;
                    margin-top: 10px;
                }
                @media print {
                    body { margin: 0; padding: 0; }
                    .barcode-container { border: 1px solid #000; }
                }
            </style>
        </head>
        <body>
            <div class="barcode-container">
                <div class="order-header">
                    <div class="order-number">Order: ${orderNumber}</div>
                    <div class="customer-name">Customer: ${customerName}</div>
                </div>
                <div class="barcode-display">${barcodeDisplay}</div>
                <div class="barcode-label">Scan barcode for order verification</div>
            </div>
            <script>
                window.print();
                setTimeout(() => window.close(), 500);
            </script>
        </body>
        </html>
    `);
    printWindow.document.close();
}

function generateBarcodeDisplay(barcode) {
    // Return the barcode as-is for display
    // In a real system, this could generate an actual barcode image
    // For now, just format it nicely
    if (barcode && barcode.length >= 12) {
        // Display in chunks: XXX-XXX-XXX-XXX
        return barcode.substring(0, 3) + '-' + 
               barcode.substring(3, 6) + '-' + 
               barcode.substring(6, 9) + '-' + 
               (barcode.length > 9 ? barcode.substring(9) : '');
    }
    return barcode || 'NO-BARCODE';
}

function showToast(message, type = 'info') {
    // Simple toast implementation
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function setupLogout() {
    const logoutBtn = document.getElementById('logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('auth_token');
            window.location.href = '/accounts/login/';
        });
    }
}

// Add modal styles
const modalStyles = `
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

.modal-content {
    background-color: white;
    margin: 10% auto;
    padding: 0;
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    animation: modalFadeIn 0.3s ease;
}

.modal-header {
    padding: 20px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    color: #1f2937;
}

.modal-close {
    font-size: 28px;
    font-weight: bold;
    color: #6b7280;
    cursor: pointer;
}

.modal-close:hover {
    color: #374151;
}

.form-actions {
    padding: 20px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.btn-sm {
    padding: 6px 12px;
    font-size: 12px;
}

.btn-secondary {
    background: #6b7280;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
}

.btn-secondary:hover {
    background: #4b5563;
}

@keyframes modalFadeIn {
    from { opacity: 0; transform: translateY(-50px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}

@keyframes slideOut {
    from { transform: translateX(0); }
    to { transform: translateX(100%); }
}
`;

// Add styles to head
const style = document.createElement('style');
style.textContent = modalStyles;
document.head.appendChild(style);