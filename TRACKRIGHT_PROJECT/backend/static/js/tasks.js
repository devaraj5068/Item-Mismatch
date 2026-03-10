// tasks.js - Tasks management functionality

document.addEventListener('DOMContentLoaded', function() {
    loadTasks();
    setupSearch();
    setupNewTaskModal();
    setupLogout();
});

let searchTimeout;

async function loadTasks(searchQuery = '') {
    console.log('Loading tasks...');
    try {
        const token = localStorage.getItem('auth_token');
        console.log('Auth token for tasks:', token ? 'present' : 'missing');
        let url = '/api/tasks/';

        if (searchQuery) {
            url += `?search=${encodeURIComponent(searchQuery)}`;
        }

        console.log('Fetching tasks from:', url);
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        console.log('Tasks response status:', response.status);
        if (response.ok) {
            const tasks = await response.json();
            console.log('Tasks data:', tasks);
            const tasksList = Array.isArray(tasks) ? tasks : tasks.results || [];

            updateTaskStats(tasksList);

            const tbody = document.getElementById('tasks-list');
            if (tbody && tasksList.length > 0) {
                tbody.innerHTML = tasksList.map(task => `
                    <tr>
                        <td><strong>${task.title}</strong></td>
                        <td><span class="badge badge-${getPriorityBadgeColor(task.priority)}">${task.priority}</span></td>
                        <td><span class="badge badge-${getStatusBadgeColor(task.status)}">${task.status}</span></td>
                        <td>${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</td>
                        <td>
                            <button class="btn btn-sm" onclick="viewTask(${task.id})">View</button>
                            <button class="btn btn-sm btn-warning" onclick="editTask(${task.id})">Edit</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">Delete</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #6b7280;">No tasks found</td></tr>';
            }
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function updateTaskStats(tasks) {
    const pendingCount = document.getElementById('pending-count');
    const inprogressCount = document.getElementById('inprogress-count');
    const completedCount = document.getElementById('completed-count');

    const pending = tasks.filter(t => t.status === 'pending').length;
    const inprogress = tasks.filter(t => t.status === 'in_progress').length;
    const completed = tasks.filter(t => t.status === 'completed').length;

    if (pendingCount) pendingCount.textContent = pending;
    if (inprogressCount) inprogressCount.textContent = inprogress;
    if (completedCount) completedCount.textContent = completed;
}

function setupSearch() {
    const searchInput = document.querySelector('.search-bar');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                loadTasks(e.target.value);
            }, 300); // Debounce search
        });
    }
}

function setupNewTaskModal() {
    const newTaskBtn = document.querySelector('.btn-primary');
    if (newTaskBtn && newTaskBtn.textContent.includes('New Task')) {
        newTaskBtn.addEventListener('click', showNewTaskModal);
    }
}

function showNewTaskModal(taskData = null) {
    const isEdit = !!taskData;
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${isEdit ? 'Edit Task' : 'Create New Task'}</h3>
                <span class="modal-close">&times;</span>
            </div>
            <form id="task-form">
                <div class="form-group">
                    <label for="title">Task Title</label>
                    <input type="text" id="title" name="title" required value="${taskData?.title || ''}">
                </div>
                <div class="form-group">
                    <label for="priority">Priority</label>
                    <select id="priority" name="priority" required>
                        <option value="low" ${taskData?.priority === 'low' ? 'selected' : ''}>Low</option>
                        <option value="medium" ${taskData?.priority === 'medium' ? 'selected' : ''}>Medium</option>
                        <option value="high" ${taskData?.priority === 'high' ? 'selected' : ''}>High</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="status">Status</label>
                    <select id="status" name="status" required>
                        <option value="pending" ${taskData?.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="in_progress" ${taskData?.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${taskData?.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="due_date">Due Date</label>
                    <input type="date" id="due_date" name="due_date" value="${taskData?.due_date ? taskData.due_date.split('T')[0] : ''}">
                </div>
                <div class="form-group">

                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">${isEdit ? 'Update Task' : 'Create Task'}</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);
    modal.style.display = 'block';

    // Setup form submission
    const form = modal.querySelector('#task-form');
    form.addEventListener('submit', (e) => handleTaskSubmit(e, isEdit, taskData?.id));

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

async function handleTaskSubmit(e, isEdit, taskId) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const taskData = {
        title: formData.get('title'),
        priority: formData.get('priority'),
        status: formData.get('status'),
        due_date: formData.get('due_date') || null,

    };

    try {
        const token = localStorage.getItem('auth_token');
        const url = isEdit ? `http://localhost:8000/api/tasks/${taskId}/` : 'http://localhost:8000/api/tasks/';
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            closeModal();
            loadTasks();
            showToast(`Task ${isEdit ? 'updated' : 'created'} successfully!`, 'success');
        } else {
            const error = await response.json();
            showToast(`Error ${isEdit ? 'updating' : 'creating'} task: ${JSON.stringify(error)}`, 'error');
        }
    } catch (error) {
        console.error(`Error ${isEdit ? 'updating' : 'creating'} task:`, error);
        showToast(`Error ${isEdit ? 'updating' : 'creating'} task`, 'error');
    }
}

async function viewTask(taskId) {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/`, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const task = await response.json();
            showTaskDetails(task);
        }
    } catch (error) {
        console.error('Error loading task details:', error);
    }
}

function showTaskDetails(task) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Task Details</h3>
                <span class="modal-close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="detail-row">
                    <strong>Title:</strong> ${task.title}
                </div>
                <div class="detail-row">
                    <strong>Priority:</strong> <span class="badge badge-${getPriorityBadgeColor(task.priority)}">${task.priority}</span>
                </div>
                <div class="detail-row">
                    <strong>Status:</strong> <span class="badge badge-${getStatusBadgeColor(task.status)}">${task.status}</span>
                </div>
                <div class="detail-row">
                    <strong>Due Date:</strong> ${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}
                </div>
                <div class="detail-row">
                    <strong>Created:</strong> ${new Date(task.created_at).toLocaleString()}
                </div>
                <div class="detail-row">
                    <strong>Created by:</strong> ${task.created_by_username || 'System'}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal()">Close</button>
                <button class="btn btn-warning" onclick="editTask(${task.id}); closeModal();">Edit Task</button>
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

async function editTask(taskId) {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/`, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const task = await response.json();
            showNewTaskModal(task);
        }
    } catch (error) {
        console.error('Error loading task for editing:', error);
    }
}

async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                loadTasks();
                showToast('Task deleted successfully!', 'success');
            } else {
                showToast('Error deleting task', 'error');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            showToast('Error deleting task', 'error');
        }
    }
}

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
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

function getStatusBadgeColor(status) {
    switch (status) {
        case 'completed': return 'success';
        case 'in_progress': return 'warning';
        case 'pending': return 'primary';
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
document.head.appendChild(style);