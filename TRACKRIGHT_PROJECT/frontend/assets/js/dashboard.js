// dashboard.js - Dashboard stats and charts

document.addEventListener('DOMContentLoaded', async function() {
    try {
        const orders = await getOrders();
        const products = await getProducts();
        const statsDiv = document.getElementById('stats');
        statsDiv.innerHTML = `
            <div class="card">
                <h3>Total Orders</h3>
                <p class="count-up" data-target="${orders.length}">0</p>
            </div>
            <div class="card">
                <h3>Total Products</h3>
                <p class="count-up" data-target="${products.length}">0</p>
            </div>
        `;

        // Animate count-up
        const counters = document.querySelectorAll('.count-up');
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            let count = 0;
            const increment = target / 100;
            const timer = setInterval(() => {
                count += increment;
                if (count >= target) {
                    counter.innerText = target;
                    clearInterval(timer);
                } else {
                    counter.innerText = Math.floor(count);
                }
            }, 20);
        });

        // Chart
        const ctx = document.getElementById('ordersChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Pending', 'Shipped', 'Delivered'],
                datasets: [{
                    label: 'Orders',
                    data: [
                        orders.filter(o => o.status === 'pending').length,
                        orders.filter(o => o.status === 'shipped').length,
                        orders.filter(o => o.status === 'delivered').length
                    ],
                    backgroundColor: ['#ffc107', '#007bff', '#28a745'],
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuad'
                    }
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                animation: {
                    onComplete: () => {
                        showToast('Dashboard loaded successfully!', 'success');
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error loading dashboard', 'error');
    }
});

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message;
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3000);
}