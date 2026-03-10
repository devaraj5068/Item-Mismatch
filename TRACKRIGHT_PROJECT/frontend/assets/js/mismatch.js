// mismatch.js - Mismatch reports logic with animations

document.addEventListener('DOMContentLoaded', async function() {
    try {
        const reports = await getMismatchReports();
        const tbody = document.querySelector('#mismatch-table tbody');
        reports.forEach((report, index) => {
            const row = document.createElement('tr');
            row.setAttribute('data-aos', 'fade-up');
            row.setAttribute('data-aos-delay', (index * 100).toString());
            const isCritical = report.expected_quantity !== report.actual_quantity;
            if (isCritical) {
                row.classList.add('error');
                row.style.animation = 'shake 0.5s';
            }
            row.innerHTML = `
                <td>${report.order}</td>
                <td>${report.product}</td>
                <td>${report.expected_quantity}</td>
                <td>${report.actual_quantity}</td>
                <td>${report.reported_at}</td>
            `;
            tbody.appendChild(row);
        });

        // Filter toggle
        document.getElementById('filter-btn').addEventListener('click', function() {
            const filters = document.getElementById('filters');
            if (filters.style.display === 'none') {
                filters.style.display = 'block';
                AOS.refresh();
            } else {
                filters.style.display = 'none';
            }
        });
    } catch (error) {
        console.error('Error loading mismatch reports:', error);
    }
});