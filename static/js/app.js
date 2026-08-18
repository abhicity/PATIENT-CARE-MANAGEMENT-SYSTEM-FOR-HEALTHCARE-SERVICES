document.addEventListener('DOMContentLoaded', () => {
    const dashboardData = window.dashboardData;
    if (!dashboardData) {
        return;
    }

    const monthCanvas = document.getElementById('appointmentsChart');
    if (monthCanvas && dashboardData.monthlyLabels) {
        new Chart(monthCanvas, {
            type: 'line',
            data: {
                labels: dashboardData.monthlyLabels,
                datasets: [{
                    label: 'Appointments',
                    data: dashboardData.monthlyValues,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.15)',
                    tension: 0.35,
                    fill: true,
                }],
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    }

    const genderCanvas = document.getElementById('genderChart');
    if (genderCanvas && dashboardData.genderLabels) {
        new Chart(genderCanvas, {
            type: 'doughnut',
            data: {
                labels: dashboardData.genderLabels,
                datasets: [{
                    data: dashboardData.genderValues,
                    backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545'],
                }],
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
        });
    }

    const doctorCanvas = document.getElementById('doctorChart');
    if (doctorCanvas && dashboardData.doctorLabels) {
        new Chart(doctorCanvas, {
            type: 'bar',
            data: {
                labels: dashboardData.doctorLabels,
                datasets: [{
                    label: 'Consultations',
                    data: dashboardData.doctorValues,
                    backgroundColor: 'rgba(25, 135, 84, 0.7)',
                    borderColor: '#198754',
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    }

});
