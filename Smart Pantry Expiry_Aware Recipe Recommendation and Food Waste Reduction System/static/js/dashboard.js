document.addEventListener('DOMContentLoaded', function() {
    const dataElement = document.getElementById('waste-data');
    if (dataElement) {
        const consumed = parseInt(dataElement.dataset.consumed) || 0;
        const wasted = parseInt(dataElement.dataset.wasted) || 0;
        const expired = parseInt(dataElement.dataset.expired) || 0;

        const ctx = document.getElementById('wasteChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Consumed', 'Wasted', 'Expired'],
                datasets: [{
                    data: [consumed, wasted, expired],
                    backgroundColor: [
                        '#52b788', // Consumed: Medium green
                        '#e76f51', // Wasted: Orange-red
                        '#d62828'  // Expired: Red
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }
});
