// mismatch.js - Mismatch reports functionality

document.addEventListener('DOMContentLoaded', function() {
    loadMismatches();
    setupSearch();
    setupLogout();
});

let searchTimeout;

async function loadMismatches(searchQuery = '') {
    try {
        let url = '/mismatches/list/';

        if (searchQuery) {
            url += `?search=${encodeURIComponent(searchQuery)}`;
        }

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            const mismatchesList = await response.json();

            updateMismatchStats(mismatchesList);

            const tbody = document.getElementById('mismatches-list');
            if (tbody && mismatchesList.length > 0) {
                tbody.innerHTML = mismatchesList.map(mismatch => `
                    <tr>
                        <td>${mismatch.order_number || mismatch.order}</td>
                        <td>${mismatch.expected_product || 'N/A'}</td>
                        <td>${mismatch.scanned_product || 'N/A'}</td>
                        <td><span class="badge badge-${getStatusBadgeColor(mismatch.status)}">${mismatch.status}</span></td>
                        <td>${new Date(mismatch.reported_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-sm" onclick="viewMismatch(${mismatch.id})">View</button>
                            <button class="btn btn-sm btn-success" onclick="resolveMismatch(${mismatch.id})">Resolve</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #6b7280;">No mismatches found</td></tr>';
            }
        }
    } catch (error) {
        console.error('Error loading mismatches:', error);
    }
}

function updateMismatchStats(mismatches) {
    const totalMismatches = document.getElementById('total-mismatches');
    const pendingReview = document.getElementById('pending-review');
    const resolvedCount = document.getElementById('resolved-count');

    if (totalMismatches) totalMismatches.textContent = mismatches.length;

    const pending = mismatches.filter(m => m.status === 'unresolved' || m.status === 'pending').length;
    const resolved = mismatches.filter(m => m.status === 'resolved').length;

    if (pendingReview) pendingReview.textContent = pending;
    if (resolvedCount) resolvedCount.textContent = resolved;
}

function setupSearch() {
    const searchInput = document.querySelector('.search-bar');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                loadMismatches(e.target.value);
            }, 300); // Debounce search
        });
    }
}

async function viewMismatch(mismatchId) {
    try {
        const response = await fetch(`/mismatches/detail/${mismatchId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            const mismatch = await response.json();
            showMismatchDetails(mismatch);
        } else {
            showToast('Error loading mismatch details', 'error');
        }
    } catch (error) {
        console.error('Error loading mismatch details:', error);
        showToast('Error loading mismatch details', 'error');
    }
}

function showMismatchDetails(mismatch) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Mismatch Details</h3>
                <span class="modal-close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="detail-row">
                    <strong>Order:</strong> ${mismatch.order_number || mismatch.order}
                </div>
                <div class="detail-row">
                    <strong>Expected Product:</strong> ${mismatch.expected_product || 'N/A'}
                </div>
                <div class="detail-row">
                    <strong>Scanned Product:</strong> ${mismatch.scanned_product || 'N/A'}
                </div>
                <div class="detail-row">
                    <strong>Status:</strong> <span class="badge badge-${getStatusBadgeColor(mismatch.status)}">${mismatch.status}</span>
                </div>
                <div class="detail-row">
                    <strong>Created:</strong> ${new Date(mismatch.reported_at).toLocaleString()}
                </div>
                <div class="detail-row">
                    <strong>Reported by:</strong> ${mismatch.reported_by_name || 'System'}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal()">Close</button>
                ${mismatch.status !== 'resolved' ? `<button class="btn btn-success" onclick="resolveMismatch(${mismatch.id}); closeModal();">Mark as Resolved</button>` : ''}
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.style.display = 'block';

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

async function resolveMismatch(mismatchId) {
    try {
        const response = await fetch(`/mismatches/resolve/${mismatchId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();
        
        if (response.ok && data.success) {
            // Reload the page to update the table and stats
            location.reload();
        } else {
            showToast('Error resolving mismatch: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error resolving mismatch:', error);
        showToast('Error resolving mismatch', 'error');
    }
}

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

function getStatusBadgeColor(status) {
    switch (status) {
        case 'unresolved': return 'danger';
        case 'pending': return 'warning';
        case 'resolved': return 'success';
        default: return 'primary';
    }
}

function showToast(message, type = 'info') {
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
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add modal and animation styles
const style = document.createElement('style');
style.textContent = `
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

.modal-body {
    padding: 20px;
}

.detail-row {
    margin-bottom: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
    border-bottom: none;
}

.modal-footer {
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
document.head.appendChild(style);