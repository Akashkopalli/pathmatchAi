/**
 * PathMatch AI - Main Client-Side Logic
 */

let studentSkills = [];

// Initialize
document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const sampleParam = urlParams.get("sample");
    if (sampleParam) {
        loadSampleProfile(sampleParam);
    }
});

function renderSkills() {
    const container = document.getElementById("skillsContainer");
    if (!container) return;

    container.innerHTML = "";
    if (studentSkills.length === 0) {
        container.innerHTML = '<span class="text-muted small fst-italic">No skills added yet. Type a skill above or extract from narrative.</span>';
        return;
    }

    studentSkills.forEach((skill, index) => {
        const badge = document.createElement("span");
        badge.className = "skill-tag skill-neutral";
        badge.innerHTML = `
            ${skill.name}
            <i class="fa-solid fa-xmark ms-2 text-danger" style="cursor: pointer;" onclick="removeSkill(${index})"></i>
        `;
        container.appendChild(badge);
    });
}

function addSkillTag() {
    const input = document.getElementById("newSkillInput");
    const val = input.value.trim();
    if (!val) return;

    // Check comma separated
    const parts = val.split(",").map(s => s.trim()).filter(s => s);
    parts.forEach(p => {
        if (!studentSkills.some(s => s.name.toLowerCase() === p.toLowerCase())) {
            studentSkills.push({ name: p, evidence: "Explicitly provided", proficiency: "Unspecified" });
        }
    });

    input.value = "";
    renderSkills();
}

function removeSkill(index) {
    studentSkills.splice(index, 1);
    renderSkills();
}

async function loadSampleProfile(sampleName) {
    try {
        const resp = await fetch("/api/sample-profiles");
        const data = await resp.json();
        if (resp.ok && data.sample_profiles) {
            const profile = data.sample_profiles.find(p => p.name.toLowerCase() === sampleName.toLowerCase());
            if (profile) {
                populateProfileForm(profile);
            }
        }
    } catch (e) {
        console.error("Failed to load sample profile:", e);
    }
}

function populateProfileForm(profile) {
    const nameEl = document.getElementById("studentName");
    const degreeEl = document.getElementById("degree");
    const specEl = document.getElementById("specialization");
    const eduEl = document.getElementById("educationLevel");
    const natEl = document.getElementById("naturalInput");
    const projEl = document.getElementById("projectsInput");
    const intEl = document.getElementById("interestsInput");
    const goalsEl = document.getElementById("goalsInput");

    if (nameEl) nameEl.value = profile.name || "";
    if (degreeEl) degreeEl.value = profile.degree || "Computer Science";
    if (specEl) specEl.value = profile.specialization || "";
    if (eduEl) eduEl.value = profile.education_level || "Undergraduate (3rd Year)";
    if (natEl) natEl.value = profile.natural_input || "";
    if (projEl) projEl.value = JSON.stringify(profile.projects || [], null, 2);
    if (intEl) intEl.value = (profile.interests || []).join(", ");
    if (goalsEl) goalsEl.value = (profile.career_goals || []).join(", ");

    studentSkills = [];
    if (profile.skills && Array.isArray(profile.skills)) {
        profile.skills.forEach(s => {
            studentSkills.push({
                name: s.name || s,
                evidence: s.evidence || "Explicitly provided",
                proficiency: s.proficiency || "Unspecified"
            });
        });
    }
    renderSkills();
}

function showLoading(title, subtext) {
    const modalEl = document.getElementById("loadingModal");
    if (!modalEl) return;
    if (title) document.getElementById("loadingTitle").textContent = title;
    if (subtext) document.getElementById("loadingSubtext").textContent = subtext;
    
    const instance = bootstrap.Modal.getOrCreateInstance(modalEl, {
        backdrop: 'static',
        keyboard: true
    });
    instance.show();
}

function hideLoading(callback) {
    const modalEl = document.getElementById("loadingModal");
    if (!modalEl) {
        if (callback) callback();
        return;
    }

    const instance = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
    
    // Allow any in-progress fade transition to settle, then hide
    setTimeout(() => {
        try {
            instance.hide();
        } catch (e) {
            console.warn("Modal hide error:", e);
        }

        // Complete cleanup fallback to guarantee backdrop and scroll are never stuck
        setTimeout(() => {
            modalEl.classList.remove("show");
            modalEl.style.display = "none";
            modalEl.setAttribute("aria-hidden", "true");
            modalEl.removeAttribute("aria-modal");
            document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
            document.body.classList.remove("modal-open");
            document.body.style.removeProperty("overflow");
            document.body.style.removeProperty("padding-right");
            if (callback) callback();
        }, 300);
    }, 200);
}

function showSuccessToast(message) {
    // Show temporary floating feedback banner
    const existing = document.getElementById("pmSuccessToast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "pmSuccessToast";
    toast.className = "alert alert-success position-fixed top-0 start-50 translate-middle-x mt-4 shadow-lg border-success d-flex align-items-center gap-2";
    toast.style.zIndex = "9999";
    toast.innerHTML = `
        <i class="fa-solid fa-circle-check fs-5"></i>
        <div><strong>Success:</strong> ${message}</div>
        <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => { if (toast.parentElement) toast.remove(); }, 4000);
}

async function analyzeNaturalProfile() {
    const naturalInput = document.getElementById("naturalInput").value.trim();
    if (!naturalInput) {
        alert("Please enter a natural language summary or resume text to analyze.");
        return;
    }

    showLoading(
        "Profile Understanding Agent Active...",
        "Extracting verified skills, projects, and career intentions using pure LLM reasoning..."
    );

    try {
        const resp = await fetch("/api/profile/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ natural_input: naturalInput })
        });

        const res = await resp.json();

        hideLoading(() => {
            if (resp.ok && res.status === "success") {
                populateProfileForm(res.profile);
                const studentIdEl = document.getElementById("studentId");
                if (studentIdEl) studentIdEl.value = res.student_id;
                showSuccessToast("Profile successfully extracted by LLM! Check verified skills and click 'Run LLM Recommendation Pipeline'.");
            } else {
                alert(res.error || "Failed to analyze profile.");
            }
        });

    } catch (e) {
        hideLoading();
        console.error("Error analyzing profile:", e);
        alert("An error occurred during profile analysis. Please check your connection.");
    }
}

async function submitRecommendationPipeline() {
    const name = document.getElementById("studentName").value.trim();
    if (!name) {
        alert("Please enter student name.");
        return;
    }

    if (studentSkills.length === 0 && !document.getElementById("naturalInput").value.trim()) {
        alert("Please provide skills or a profile description.");
        return;
    }

    let projects = [];
    try {
        const projText = document.getElementById("projectsInput").value.trim();
        if (projText) {
            projects = JSON.parse(projText);
        }
    } catch (e) {
        projects = [{ name: "Project", description: document.getElementById("projectsInput").value.trim() }];
    }

    const interests = document.getElementById("interestsInput").value.split(",").map(s => s.trim()).filter(s => s);
    const goals = document.getElementById("goalsInput").value.split(",").map(s => s.trim()).filter(s => s);

    const payload = {
        name: name,
        degree: document.getElementById("degree").value.trim(),
        specialization: document.getElementById("specialization").value.trim(),
        education_level: document.getElementById("educationLevel").value,
        natural_input: document.getElementById("naturalInput").value.trim(),
        skills: studentSkills,
        projects: projects,
        interests: interests,
        career_goals: goals,
        student_id: document.getElementById("studentId").value ? parseInt(document.getElementById("studentId").value) : null
    };

    showLoading(
        "Multi-Agent System Orchestrating...",
        "LLM Evaluation Agent ranking best matching O*NET occupational roles, synthesizing skill gaps & milestone roadmap..."
    );

    try {
        const resp = await fetch("/api/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const res = await resp.json();

        if (resp.ok && res.status === "success") {
            const runId = res.data.run_id;
            hideLoading(() => {
                window.location.href = `/recommendations?run_id=${runId}`;
            });
        } else {
            hideLoading(() => {
                alert(res.error || "Failed to generate recommendations.");
            });
        }
    } catch (e) {
        hideLoading();
        console.error("Recommendation submission error:", e);
        alert("An error occurred during recommendation execution. Please check server logs.");
    }
}

