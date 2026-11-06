/**
 * PathMatch AI - Enhanced O*NET Dataset Dashboard & Analytics
 * Dynamically queries /api/dashboard/stats for real-time SQLite metrics,
 * powers Chart.js visualizations, and provides interactive search/filter
 * across all 72 O*NET occupations.
 */

let allOccupations = [];
let activeDomain = "ALL";
let occModalInstance = null;

document.addEventListener("DOMContentLoaded", async function () {
    // Initialize Modal instance
    const modalEl = document.getElementById("occupationModal");
    if (modalEl && typeof bootstrap !== "undefined") {
        occModalInstance = new bootstrap.Modal(modalEl);
    }

    // Set up search and filter events
    setupFilterControls();

    // Fetch live dashboard statistics from database
    try {
        const resp = await fetch("/api/dashboard/stats");
        if (resp.ok) {
            const data = await resp.json();
            if (data.status === "success") {
                // Update KPI text counts if available
                if (data.total_occupations) {
                    const el = document.getElementById("statTotalOccupations");
                    if (el) el.textContent = data.total_occupations;
                    const elTotal = document.getElementById("totalOccCount");
                    if (elTotal) elTotal.textContent = data.total_occupations;
                }
                if (data.total_skills) {
                    const el = document.getElementById("statTotalSkills");
                    if (el) el.textContent = data.total_skills;
                }
                if (data.total_technologies) {
                    const el = document.getElementById("statTotalTech");
                    if (el) el.textContent = data.total_technologies;
                }
                if (data.total_runs !== undefined) {
                    const el = document.getElementById("statTotalRuns");
                    if (el) el.textContent = data.total_runs;
                }

                // Render Chart.js visual analytics
                initSkillsChart(data.top_skills);
                initDomainChart(data.domain_distribution);
                initTechChart(data.top_technologies);
                initScoreDistChart(data.score_distribution);

                // Populate Occupational Table
                if (data.occupations && data.occupations.length > 0) {
                    allOccupations = data.occupations;
                    renderOccupationsTable(allOccupations);

                    // Check for URL query parameter filter (e.g. ?search=... or ?soc=...)
                    checkUrlParams();
                }
            }
        }
    } catch (e) {
        console.warn("Could not load dynamic dashboard stats:", e);
    }
});

/**
 * Initialize Top Skills Horizontal Bar Chart
 */
function initSkillsChart(skillsData) {
    const ctx = document.getElementById("skillsChart");
    if (!ctx) return;

    let labels = ["Python", "Linux", "Git", "SQL", "REST API", "JavaScript", "Docker", "Cybersecurity Basics", "HTML", "OOP"];
    let dataCounts = [26, 21, 19, 17, 16, 10, 9, 9, 7, 7];

    if (skillsData && skillsData.length > 0) {
        labels = skillsData.map(item => item.skill);
        dataCounts = skillsData.map(item => item.count);
    }

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Demanded in Occupations",
                data: dataCounts,
                backgroundColor: "rgba(37, 99, 235, 0.85)",
                borderColor: "#1d4ed8",
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { precision: 0 },
                    title: { display: true, text: "Number of Roles Requiring Skill", font: { size: 11 } }
                },
                y: {
                    ticks: { font: { size: 11, weight: "bold" } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return ` Required by ${context.parsed.x} occupations`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Domain Distribution Doughnut Chart
 */
function initDomainChart(domainData) {
    const ctx = document.getElementById("domainChart");
    if (!ctx) return;

    let labels = [
        "Data Science & AI",
        "Software Engineering",
        "Web & Mobile Development",
        "Cybersecurity & Networking",
        "Cloud & DevOps",
        "Quality Assurance",
        "Database & Storage",
        "Systems & Embedded"
    ];
    let dataCounts = [17, 13, 11, 11, 6, 4, 4, 3];

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
                    "#14b8a6",
                    "#64748b",
                    "#a855f7"
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
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const val = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = Math.round((val / total) * 100);
                            return ` ${context.label}: ${val} roles (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Top Tech Tools Vertical Bar Chart
 */
function initTechChart(techData) {
    const ctx = document.getElementById("techChart");
    if (!ctx) return;

    let labels = ["Linux", "Python", "Git", "Docker", "SQL", "PostgreSQL", "Excel", "Kubernetes", "Java", "Postman"];
    let dataCounts = [22, 22, 22, 13, 10, 9, 7, 6, 6, 6];

    if (techData && techData.length > 0) {
        labels = techData.map(item => item.tech);
        dataCounts = techData.map(item => item.count);
    }

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Associated Roles",
                data: dataCounts,
                backgroundColor: "rgba(16, 185, 129, 0.8)",
                borderColor: "#059669",
                borderWidth: 1,
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
                },
                x: {
                    ticks: { font: { size: 11 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

/**
 * Initialize Suitability Score Distribution Chart
 */
function initScoreDistChart(scoreData) {
    const ctx = document.getElementById("scoreDistChart");
    if (!ctx) return;

    let labels = ["50-60 (Low)", "61-75 (Moderate)", "76-85 (Strong)", "86-100 (Exceptional)"];
    let dataCounts = [2, 6, 18, 12];

    if (scoreData && scoreData.length > 0) {
        const countsMap = {};
        scoreData.forEach(item => {
            countsMap[item.bracket] = item.count;
        });
        dataCounts = labels.map(l => countsMap[l] || 0);
    }

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Evaluated Roles",
                data: dataCounts,
                backgroundColor: [
                    "rgba(239, 68, 68, 0.75)",
                    "rgba(245, 158, 11, 0.75)",
                    "rgba(59, 130, 246, 0.75)",
                    "rgba(16, 185, 129, 0.75)"
                ],
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

/**
 * Set up search input and domain pill filter handlers
 */
function setupFilterControls() {
    const searchInput = document.getElementById("occSearchInput");
    const clearBtn = document.getElementById("clearSearchBtn");
    const domainPills = document.querySelectorAll(".domain-pill");

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            filterOccupations();
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            if (searchInput) {
                searchInput.value = "";
                filterOccupations();
                searchInput.focus();
            }
        });
    }

    domainPills.forEach(pill => {
        pill.addEventListener("click", function () {
            domainPills.forEach(p => {
                p.classList.remove("btn-primary", "active");
                p.classList.add("btn-outline-secondary");
            });
            this.classList.remove("btn-outline-secondary");
            this.classList.add("btn-primary", "active");
            activeDomain = this.getAttribute("data-domain") || "ALL";
            filterOccupations();
        });
    });
}

/**
 * Filter occupations list based on search term and active domain
 */
function filterOccupations() {
    const searchInput = document.getElementById("occSearchInput");
    const query = (searchInput ? searchInput.value : "").trim().toLowerCase();

    const filtered = allOccupations.filter(occ => {
        // Domain match
        let domainMatch = true;
        if (activeDomain !== "ALL") {
            domainMatch = occ.domain && occ.domain.toLowerCase().includes(activeDomain.toLowerCase());
        }

        if (!domainMatch) return false;

        // Search match (title, soc_code, skills, tech, description)
        if (!query) return true;

        const titleMatch = (occ.title || "").toLowerCase().includes(query);
        const socMatch = (occ.soc_code || "").toLowerCase().includes(query);
        const domainTextMatch = (occ.domain || "").toLowerCase().includes(query);
        const skillsMatch = (occ.required_skills || []).some(s => s.toLowerCase().includes(query));
        const techMatch = (occ.technology_skills || []).some(t => t.toLowerCase().includes(query));
        const descMatch = (occ.description || "").toLowerCase().includes(query);

        return titleMatch || socMatch || domainTextMatch || skillsMatch || techMatch || descMatch;
    });

    renderOccupationsTable(filtered);
}

/**
 * Render occupations into the table
 */
function renderOccupationsTable(occupations) {
    const tbody = document.getElementById("occupationsTableBody");
    const countEl = document.getElementById("visibleOccCount");

    if (!tbody) return;

    if (countEl) {
        countEl.textContent = occupations.length;
    }

    if (!occupations || occupations.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-5 text-muted">
                    <i class="fa-solid fa-folder-open fa-2xl text-secondary mb-3 d-block"></i>
                    <strong>No matching occupations found.</strong><br>
                    <span class="small">Try clearing your search term or selecting "All" domains.</span>
                </td>
            </tr>
        `;
        return;
    }

    let rowsHtml = "";
    occupations.forEach(occ => {
        // Domain badge color helper
        const domainBadge = getDomainBadge(occ.domain);

        // Required skills pills (first 4)
        const skillsBadges = (occ.required_skills || []).slice(0, 4).map(s => `
            <span class="badge bg-light text-dark border me-1 mb-1 font-monospace" style="font-size: 0.72rem;">${escapeHtml(s)}</span>
        `).join("");

        // Tech pills (first 3)
        const techBadges = (occ.technology_skills || []).slice(0, 3).map(t => `
            <span class="badge bg-info-subtle text-info-emphasis border border-info-subtle me-1 mb-1 font-monospace" style="font-size: 0.72rem;">${escapeHtml(t)}</span>
        `).join("");

        rowsHtml += `
            <tr id="occ-row-${escapeHtml(occ.soc_code)}">
                <td>
                    <span class="badge bg-dark font-monospace" style="font-size: 0.75rem;">${escapeHtml(occ.soc_code)}</span>
                </td>
                <td>
                    <div class="fw-bold text-dark">${escapeHtml(occ.title)}</div>
                    <small class="text-muted text-truncate d-inline-block" style="max-width: 280px;" title="${escapeHtml(occ.description || '')}">
                        ${escapeHtml((occ.description || '').substring(0, 75))}...
                    </small>
                </td>
                <td>
                    ${domainBadge}
                </td>
                <td>
                    <div class="d-flex flex-wrap">${skillsBadges || '<span class="text-muted small">—</span>'}</div>
                </td>
                <td>
                    <div class="d-flex flex-wrap">${techBadges || '<span class="text-muted small">—</span>'}</div>
                </td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary py-0 px-2" style="font-size: 0.8rem;" onclick="inspectOccupation('${escapeHtml(occ.soc_code)}')">
                        <i class="fa-solid fa-eye me-1"></i> Specs
                    </button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = rowsHtml;
}

/**
 * Open Occupation Details Modal with full O*NET specifications
 */
function inspectOccupation(socCode) {
    const occ = allOccupations.find(o => o.soc_code === socCode);
    if (!occ) return;

    document.getElementById("modalSocCode").textContent = occ.soc_code;
    document.getElementById("occModalTitle").textContent = occ.title;
    document.getElementById("modalDomain").textContent = occ.domain;
    document.getElementById("modalDescription").textContent = occ.description;
    document.getElementById("modalEducation").textContent = occ.education_level || "Bachelor's Degree in Computer Science or related field";

    // Required Skills
    const skillsContainer = document.getElementById("modalSkills");
    skillsContainer.innerHTML = (occ.required_skills || []).map(s => `
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle p-2">
            <i class="fa-solid fa-check me-1 text-primary"></i> ${escapeHtml(s)}
        </span>
    `).join("") || '<span class="text-muted small">None listed</span>';

    // Tech Tools
    const techContainer = document.getElementById("modalTech");
    techContainer.innerHTML = (occ.technology_skills || []).map(t => `
        <span class="badge bg-dark text-light p-2 font-monospace">
            <i class="fa-solid fa-terminal me-1 text-info"></i> ${escapeHtml(t)}
        </span>
    `).join("") || '<span class="text-muted small">None listed</span>';

    // Knowledge Areas
    const knowledgeList = document.getElementById("modalKnowledge");
    knowledgeList.innerHTML = (occ.knowledge_areas || []).map(k => `
        <li class="mb-1">${escapeHtml(k)}</li>
    `).join("") || '<li class="text-muted">General Computer Science & Technical Knowledge</li>';

    // Work Activities
    const activitiesList = document.getElementById("modalActivities");
    activitiesList.innerHTML = (occ.work_activities || []).map(a => `
        <li class="mb-1">${escapeHtml(a)}</li>
    `).join("") || '<li class="text-muted">Standard technical engineering and systems activities</li>';

    // Update Profile Link
    const profileLink = document.getElementById("modalProfileLink");
    if (profileLink) {
        profileLink.href = `/profile?goal=${encodeURIComponent(occ.title)}`;
    }

    if (occModalInstance) {
        occModalInstance.show();
    } else {
        const modalEl = document.getElementById("occupationModal");
        if (modalEl && typeof bootstrap !== "undefined") {
            const m = new bootstrap.Modal(modalEl);
            m.show();
        }
    }
}

/**
 * Return styled domain badge
 */
function getDomainBadge(domain) {
    const d = (domain || "").toLowerCase();
    if (d.includes("data") || d.includes("ai")) {
        return `<span class="badge bg-primary-subtle text-primary border border-primary-subtle">${escapeHtml(domain)}</span>`;
    } else if (d.includes("software")) {
        return `<span class="badge bg-success-subtle text-success border border-success-subtle">${escapeHtml(domain)}</span>`;
    } else if (d.includes("web") || d.includes("mobile")) {
        return `<span class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle">${escapeHtml(domain)}</span>`;
    } else if (d.includes("cyber") || d.includes("network")) {
        return `<span class="badge bg-danger-subtle text-danger border border-danger-subtle">${escapeHtml(domain)}</span>`;
    } else if (d.includes("cloud") || d.includes("devops")) {
        return `<span class="badge bg-info-subtle text-info border border-info-subtle">${escapeHtml(domain)}</span>`;
    } else {
        return `<span class="badge bg-secondary-subtle text-secondary border border-secondary-subtle">${escapeHtml(domain || "General")}</span>`;
    }
}

/**
 * Check URL query parameters for auto-filter (e.g. ?search=... or ?soc=...)
 */
function checkUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const searchParam = params.get("search") || params.get("soc");
    if (searchParam) {
        const searchInput = document.getElementById("occSearchInput");
        if (searchInput) {
            searchInput.value = searchParam;
            filterOccupations();
            // Scroll to explorer
            const explorer = document.getElementById("datasetExplorer");
            if (explorer) {
                explorer.scrollIntoView({ behavior: "smooth" });
            }
        }
    }
}

/**
 * Helper to escape HTML characters
 */
function escapeHtml(text) {
    if (!text) return "";
    const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#039;"
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}
