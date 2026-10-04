document.addEventListener('DOMContentLoaded', function () {
    if (typeof analyticsData === 'undefined') return;

    const greenPalette = ['#2d6a4f', '#52b788', '#95d5b2', '#d8f3dc', '#b7e4c7', '#40916c'];
    const redOrange = ['#e76f51', '#f4a261', '#e9c46a', '#264653', '#2a9d8f', '#a8dadc'];

    // 1. Fate Doughnut Chart (Consumed vs Wasted vs Expired)
    const fateCtx = document.getElementById('fateChart');
    if (fateCtx) {
        new Chart(fateCtx, {
            type: 'doughnut',
            data: {
                labels: ['Consumed', 'Wasted', 'Expired'],
                datasets: [{
                    data: [analyticsData.consumed, analyticsData.wasted, analyticsData.expired],
                    backgroundColor: ['#2d6a4f', '#f4a261', '#e76f51'],
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` ${ctx.label}: ${ctx.parsed} items`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Category Bar Chart
    const catCtx = document.getElementById('categoryChart');
    if (catCtx && analyticsData.category) {
        const catLabels = Object.keys(analyticsData.category);
        const catValues = Object.values(analyticsData.category);
        new Chart(catCtx, {
            type: 'bar',
            data: {
                labels: catLabels.length > 0 ? catLabels : ['No data'],
                datasets: [{
                    label: 'Quantity Wasted',
                    data: catValues.length > 0 ? catValues : [0],
                    backgroundColor: greenPalette,
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }

    // 3. Reason Doughnut Chart
    const reasonCtx = document.getElementById('reasonChart');
    if (reasonCtx && analyticsData.reason) {
        const reasonLabels = Object.keys(analyticsData.reason);
        const reasonValues = Object.values(analyticsData.reason);
        new Chart(reasonCtx, {
            type: 'doughnut',
            data: {
                labels: reasonLabels.length > 0 ? reasonLabels : ['No data'],
                datasets: [{
                    data: reasonValues.length > 0 ? reasonValues : [1],
                    backgroundColor: redOrange,
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }

    // 4. Monthly Trend Line Chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx && analyticsData.trend && analyticsData.trend.length > 0) {
        const trendLabels = analyticsData.trend.map(t => t.month);
        const trendWasted = analyticsData.trend.map(t => t.wasted);
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: trendLabels,
                datasets: [{
                    label: 'Items Wasted',
                    data: trendWasted,
                    borderColor: '#e76f51',
                    backgroundColor: 'rgba(231, 111, 81, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#e76f51',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }
});
