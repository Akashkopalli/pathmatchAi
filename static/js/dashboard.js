/**
 * PathMatch AI - Dashboard Charts Initialization
 * Dynamically queries /api/dashboard/stats for real-time SQLite metrics.
 */

document.addEventListener("DOMContentLoaded", async function () {
    let stats = null;
    try {
        const resp = await fetch("/api/dashboard/stats");
        if (resp.ok) {
            const data = await resp.json();
            if (data.status === "success") {
                stats = data;
            }
        }
    } catch (e) {
        console.warn("Could not load dynamic dashboard stats, using defaults:", e);
    }

    initDomainChart(stats ? stats.domain_distribution : null);
    initScoreDistChart(stats ? stats.score_distribution : null);
});

function initDomainChart(domainData) {
    const ctx = document.getElementById("domainChart");
    if (!ctx) return;

    let labels = [
        "Software Engineering",
        "Data Science & AI",
        "Cybersecurity & Net",
        "Web & Mobile Dev",
        "Cloud & DevOps",
        "QA & Systems"
    ];
    let dataCounts = [26, 24, 18, 16, 10, 6];

    if (domainData && domainData.length > 0) {
        labels = domainData.map(d => d.domain);
        dataCounts = domainData.map(d => d.count);
    }

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: dataCounts,
                backgroundColor: [
                    "#3b82f6",
                    "#10b981",
                    "#f59e0b",
                    "#8b5cf6",
                    "#06b6d4",
                    "#ec4899",
                    "#6366f1",
                    "#14b8a6"
                ],
                borderWidth: 2,
                borderColor: "#ffffff"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 12,
                        padding: 10,
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

function initScoreDistChart(scoreData) {
    const ctx = document.getElementById("scoreDistChart");
    if (!ctx) return;

    let labels = ["50-60 (Low)", "61-75 (Moderate)", "76-85 (Strong)", "86-100 (Exceptional)"];
    let dataCounts = [4, 12, 28, 16];

    if (scoreData && scoreData.length > 0) {
        const countsMap = {};
        scoreData.forEach(item => {
            countsMap[item.bracket] = item.count;
        });
        labels = ["50-60 (Low)", "61-75 (Moderate)", "76-85 (Strong)", "86-100 (Exceptional)"];
        dataCounts = labels.map(l => countsMap[l] || 0);
    }

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Evaluated Roles",
                data: dataCounts,
                backgroundColor: "#3b82f6",
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

