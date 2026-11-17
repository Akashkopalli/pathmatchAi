import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = BASE_DIR / "Technical_Diagrams"
DIAGRAMS_DIR.mkdir(exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

# -------------------------------------------------------------
# FIG 5: SYSTEM ARCHITECTURE
# -------------------------------------------------------------
def create_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Background canvas
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Title
    ax.text(50, 96, "FIG. 5: PATHMATCH AI SYSTEM ARCHITECTURE", ha="center", va="center", fontsize=14, fontweight="bold", color="#111827")
    ax.text(50, 92.5, "Orchestrated Multi-Agent Cognitive Architecture with Standardized Occupational Knowledge Base", ha="center", va="center", fontsize=10, color="#4b5563")

    # Layer 1: Client & Ingestion Layer
    rect1 = patches.FancyBboxPatch((4, 73), 92, 16, boxstyle="round,pad=1", ec="#2563eb", fc="#eff6ff", lw=1.5)
    ax.add_patch(rect1)
    ax.text(7, 85, "LAYER 1: CLIENT PRESENTATION & DATA INGESTION", fontsize=10, fontweight="bold", color="#1e40af")
    
    components_l1 = [
        ("Web Browser UI\n(Responsive Flask/Jinja)", 18),
        ("Student Profile Form\n(Courses, Skills, Projects)", 42),
        ("Unstructured Text Parser\n(Natural Language Inputs)", 66),
        ("Defense / Sanitization Gate\n(Prompt Injection Defense)", 87)
    ]
    for title, x_pos in components_l1:
        box = patches.FancyBboxPatch((x_pos-9, 74.5), 18, 8.5, boxstyle="round,pad=0.5", ec="#93c5fd", fc="#ffffff", lw=1)
        ax.add_patch(box)
        ax.text(x_pos, 78.75, title, ha="center", va="center", fontsize=7.5, color="#1e3a8a", fontweight="semibold")

    # Downward arrow 1
    ax.annotate("", xy=(50, 68), xytext=(50, 72.5), arrowprops=dict(arrowstyle="->", lw=2, color="#2563eb"))

    # Layer 2: Multi-Agent LLM Orchestration Engine
    rect2 = patches.FancyBboxPatch((4, 31), 92, 36, boxstyle="round,pad=1", ec="#7c3aed", fc="#f5f3ff", lw=1.5)
    ax.add_patch(rect2)
    ax.text(7, 63.5, "LAYER 2: MULTI-AGENT PURE LLM REASONING PIPELINE (ZERO TRADITIONAL ML)", fontsize=10, fontweight="bold", color="#5b21b6")

    agents = [
        ("Agent 1: Profile Understanding", "Normalizes academic coursework,\nprojects & verified competencies", 20, 53),
        ("Agent 2: Skill Intelligence", "Maps technical relationships,\ntransferable skills & hierarchies", 50, 53),
        ("Agent 3: Occupational Matching", "Evaluates 72 O*NET SOC profiles\nacross 6-dimension rubric", 80, 53),
        ("Agent 4: Skill-Gap Diagnostic", "Identifies exact prerequisite & tool\ndeficits without hallucination", 20, 37),
        ("Agent 5: Strategic Learning Path", "Synthesizes structured 30-60-90 day\nprogressive milestone roadmaps", 50, 37),
        ("Agent 6: Career Guidance Assistant", "Interactive conversational mentor\nwith concise, actionable guidance", 80, 37)
    ]
    for name, desc, x, y in agents:
        abox = patches.FancyBboxPatch((x-13.5, y-5), 27, 9.5, boxstyle="round,pad=0.5", ec="#c4b5fd", fc="#ffffff", lw=1.2)
        ax.add_patch(abox)
        ax.text(x, y+1.8, name, ha="center", va="center", fontsize=7.8, fontweight="bold", color="#4c1d95")
        ax.text(x, y-2, desc, ha="center", va="center", fontsize=6.5, color="#374151")

    # Downward arrow 2
    ax.annotate("", xy=(50, 26), xytext=(50, 30.5), arrowprops=dict(arrowstyle="->", lw=2, color="#7c3aed"))

    # Layer 3: Authoritative Knowledge Base & Storage Layer
    rect3 = patches.FancyBboxPatch((4, 4), 92, 21, boxstyle="round,pad=1", ec="#059669", fc="#ecfdf5", lw=1.5)
    ax.add_patch(rect3)
    ax.text(7, 21.5, "LAYER 3: AUTHORITATIVE OCCUPATIONAL KNOWLEDGE BASE & AUDIT DATA STORE", fontsize=10, fontweight="bold", color="#065f46")

    dbs = [
        ("U.S. Dept of Labor O*NET 2018 SOC Database\n72 Official Occupations | 10 Technical Domains\nValidated Competencies, Tech Stacks & Tasks", 28, 12, 42, 11),
        ("Relational SQLite Application Store\nStudent Profiles, Structured Recommendations,\nAudit Trail & Evaluation Logs", 72, 12, 38, 11)
    ]
    for dtitle, x, y, w, h in dbs:
        dbox = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.5", ec="#6ee7b7", fc="#ffffff", lw=1)
        ax.add_patch(dbox)
        ax.text(x, y, dtitle, ha="center", va="center", fontsize=7.5, color="#064e3b", fontweight="semibold")

    plt.tight_layout()
    out_path = DIAGRAMS_DIR / "FIG_5_System_Architecture.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path.name}")

# -------------------------------------------------------------
# FIG 6: MULTI-AGENT WORKFLOW PIPELINE
# -------------------------------------------------------------
def create_workflow_pipeline():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    ax.text(50, 96, "FIG. 6: PURE LLM MULTI-AGENT REASONING & EXECUTION WORKFLOW", ha="center", va="center", fontsize=14, fontweight="bold", color="#111827")
    ax.text(50, 92.5, "Sequential Execution Flow from Student Ingestion to Milestone Guidance", ha="center", va="center", fontsize=10, color="#4b5563")

    steps = [
        ("Step 1: Ingestion & Sanitization", "Raw natural-language student input is parsed.\nInjection defense guards prompt boundaries.", 14, 76, "#0284c7"),
        ("Step 2: Profile Extraction", "Agent 1 extracts verified technical competencies,\nacademic coursework & substantiated projects.", 38, 76, "#0284c7"),
        ("Step 3: Skill Intelligence", "Agent 2 infers technical relationships, determines\ntransferable competencies & categorizes skills.", 62, 76, "#0284c7"),
        ("Step 4: O*NET Candidate Retrieval", "System queries 72 official O*NET SOC profiles\nto generate high-potential candidate subset.", 86, 76, "#0284c7"),
        
        ("Step 5: 6-Dimension LLM Evaluation", "Agent 3 reasons over student evidence vs O*NET\nstandards. Assigns weighted qualitative scores.", 86, 38, "#7c3aed"),
        ("Step 6: Gap & Deficit Diagnostic", "Agent 4 pinpoints exact prerequisite deficits,\nmissing frameworks & critical toolchain needs.", 62, 38, "#7c3aed"),
        ("Step 7: Milestone Roadmap Generation", "Agent 5 creates structured 30-60-90 day progressive\naction plan with tangible portfolio outcomes.", 38, 38, "#7c3aed"),
        ("Step 8: Interactive Career Mentorship", "Agent 6 provides conversational guidance,\nclarifying occupational fit and technical paths.", 14, 38, "#7c3aed")
    ]

    for title, desc, x, y, color in steps:
        box = patches.FancyBboxPatch((x-10.5, y-10), 21, 16, boxstyle="round,pad=0.6", ec=color, fc="#f8fafc", lw=1.5)
        ax.add_patch(box)
        ax.text(x, y+4.2, title, ha="center", va="center", fontsize=7.8, fontweight="bold", color=color)
        ax.text(x, y-2.5, desc, ha="center", va="center", fontsize=6.8, color="#334155")

    # Connect forward arrows Step 1 -> 2 -> 3 -> 4
    for x1, x2 in [(24.5, 27.5), (48.5, 51.5), (72.5, 75.5)]:
        ax.annotate("", xy=(x2, 76), xytext=(x1, 76), arrowprops=dict(arrowstyle="->", lw=1.8, color="#0284c7"))

    # Down arrow Step 4 -> Step 5
    ax.annotate("", xy=(86, 46.5), xytext=(86, 65.5), arrowprops=dict(arrowstyle="->", lw=1.8, color="#64748b"))

    # Connect backward arrows Step 5 -> 6 -> 7 -> 8
    for x1, x2 in [(75.5, 72.5), (51.5, 48.5), (27.5, 24.5)]:
        ax.annotate("", xy=(x2, 38), xytext=(x1, 38), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7c3aed"))

    # Bottom summary bar
    summary_box = patches.FancyBboxPatch((4, 6), 92, 12, boxstyle="round,pad=0.8", ec="#10b981", fc="#ecfdf5", lw=1.5)
    ax.add_patch(summary_box)
    ax.text(50, 14, "STRICT NON-HALLUCINATION & ANTI-STATISTICAL GUARANTEE", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#065f46")
    ax.text(50, 9, "Pure LLM cognitive reasoning operates without cosine similarity or keyword frequency metrics.\nEvery recommended role is directly linked to official U.S. DOL O*NET database records.", ha="center", va="center", fontsize=7.8, color="#047857")

    plt.tight_layout()
    out_path = DIAGRAMS_DIR / "FIG_6_Multi_Agent_Workflow.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path.name}")

# -------------------------------------------------------------
# FIG 7: 6-DIMENSION EVALUATION RUBRIC
# -------------------------------------------------------------
def create_evaluation_rubric():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    ax.text(50, 96, "FIG. 7: STANDARDIZED SIX-DIMENSION OCCUPATIONAL SUITABILITY RUBRIC", ha="center", va="center", fontsize=13, fontweight="bold", color="#111827")
    ax.text(50, 92, "Qualitative Dimension Weighting Enforced by LLM Reasoning Engine", ha="center", va="center", fontsize=9.5, color="#4b5563")

    dimensions = [
        ("Direct Skill Overlap", "35%", "Verified technical languages, libraries, and frameworks\nmatching mandatory core requirements of O*NET occupation.", "#1d4ed8", 22, 70),
        ("Foundational Knowledge", "20%", "Academic coursework, theoretical computer science concepts,\nand conceptual curriculum grounding.", "#0369a1", 72, 70),
        ("Project Evidence", "20%", "Substantiated application, architecture complexity,\nand tangible deliverables in code repositories.", "#6d28d9", 22, 46),
        ("Transferable Skills", "10%", "Algorithmic reasoning, problem decomposition,\ndatabase structuring, and technical documentation.", "#b45309", 72, 46),
        ("Skill Gap Feasibility", "10%", "Degree of difficulty and estimated effort required to acquire\nmissing prerequisite competencies within 30–90 days.", "#047857", 22, 22),
        ("Career Trajectory", "5%", "Student stated preferences, long-term technical aspirations,\nand alignment with target technological domain.", "#be185d", 72, 22)
    ]

    for title, weight, desc, color, x, y in dimensions:
        box = patches.FancyBboxPatch((x-20, y-9), 40, 17, boxstyle="round,pad=0.8", ec=color, fc="#f8fafc", lw=1.5)
        ax.add_patch(box)
        # Weight badge
        badge = patches.FancyBboxPatch((x+11, y+3.5), 7.5, 4.5, boxstyle="round,pad=0.3", ec="none", fc=color)
        ax.add_patch(badge)
        ax.text(x+14.75, y+5.75, weight, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#ffffff")
        
        ax.text(x-18, y+5.5, title, ha="left", va="center", fontsize=9, fontweight="bold", color=color)
        ax.text(x-18, y-1.5, desc, ha="left", va="center", fontsize=7, color="#374151")

    # Bottom note
    ax.text(50, 5, "Total Weighted Score: 100% | Evaluated qualitatively via LLM prompt constraints without hardcoded numeric heuristics.", ha="center", va="center", fontsize=8, color="#6b7280", style="italic")

    plt.tight_layout()
    out_path = DIAGRAMS_DIR / "FIG_7_Six_Dimension_Evaluation_Rubric.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path.name}")

# -------------------------------------------------------------
# FIG 8: O*NET TAXONOMY INTEGRATION
# -------------------------------------------------------------
def create_onet_taxonomy():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    ax.text(50, 96, "FIG. 8: O*NET 2018 SOC TAXONOMY HIERARCHICAL KNOWLEDGE STRUCTURE", ha="center", va="center", fontsize=13, fontweight="bold", color="#111827")
    ax.text(50, 92, "Ontological Mapping of 72 Technical Occupations Across 10 Standardized Domains", ha="center", va="center", fontsize=9.5, color="#4b5563")

    # Root node
    rbox = patches.FancyBboxPatch((32, 78), 36, 9.5, boxstyle="round,pad=0.6", ec="#1e3a8a", fc="#dbeafe", lw=2)
    ax.add_patch(rbox)
    ax.text(50, 83.5, "U.S. Dept. of Labor O*NET 2018 SOC Taxonomy", ha="center", va="center", fontsize=9, fontweight="bold", color="#1e3a8a")
    ax.text(50, 80, "72 Standardized Computing & Technical Occupations", ha="center", va="center", fontsize=7.5, color="#1e40af")

    # 4 Branch Clusters
    clusters = [
        ("Software Engineering & Architecture", ["15-1252.00 Software Developers", "15-1254.00 Web Developers", "15-1253.00 Software Quality Assurance"], 15, 52, "#1d4ed8"),
        ("Data Science & Machine Learning", ["15-2051.00 Data Scientists", "15-2051.01 Business Intelligence Analysts", "15-1221.00 Computer Research Scientists"], 38, 52, "#7c3aed"),
        ("Cloud, DevOps & Systems", ["15-1244.00 Network & Systems Admins", "15-1241.00 Computer Network Architects", "15-1299.08 Computer Systems Engineers"], 62, 52, "#059669"),
        ("Cybersecurity & Infrastructure", ["15-1212.00 Info Security Analysts", "15-1243.00 Database Architects", "15-1231.00 Computer Network Support"], 85, 52, "#dc2626")
    ]

    for title, roles, x, y, col in clusters:
        # Branch box
        cbox = patches.FancyBboxPatch((x-10.5, y-5), 21, 19, boxstyle="round,pad=0.6", ec=col, fc="#f8fafc", lw=1.3)
        ax.add_patch(cbox)
        ax.text(x, y+11.5, title, ha="center", va="center", fontsize=7.5, fontweight="bold", color=col)
        
        # Line from root
        ax.annotate("", xy=(x, y+14.5), xytext=(50, 78), arrowprops=dict(arrowstyle="->", lw=1.2, color="#94a3b8"))

        # Role list
        role_text = "\n\n".join(roles)
        ax.text(x, y+2, role_text, ha="center", va="center", fontsize=6.3, color="#334155")

    # Knowledge Elements Box
    kbox = patches.FancyBboxPatch((6, 7), 88, 17, boxstyle="round,pad=0.8", ec="#475569", fc="#f1f5f9", lw=1.2)
    ax.add_patch(kbox)
    ax.text(50, 20.5, "MANDATORY ONET ATTRIBUTES EXTRACTED FOR EVERY OCCUPATIONAL NODE", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1e293b")
    
    attrs = [
        ("[1] Core Technical Skills", "Programming, querying,\narchitectural patterns"),
        ("[2] Tools & Technologies", "Frameworks, databases,\ncloud & IDE tooling"),
        ("[3] Knowledge Domains", "CS theory, algorithms,\nnetworks, engineering"),
        ("[4] Work Activities", "Code development, test\nautomation, deployments")
    ]
    for i, (atit, adesc) in enumerate(attrs):
        ax_pos = 16 + i * 22
        ax.text(ax_pos, 15, atit, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0f172a")
        ax.text(ax_pos, 11, adesc, ha="center", va="center", fontsize=6.5, color="#475569")

    plt.tight_layout()
    out_path = DIAGRAMS_DIR / "FIG_8_ONET_Taxonomy_Integration.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path.name}")

if __name__ == "__main__":
    create_system_architecture()
    create_workflow_pipeline()
    create_evaluation_rubric()
    create_onet_taxonomy()
    print("All technical diagrams generated successfully!")
