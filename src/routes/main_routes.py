"""PathMatch AI - Main Web UI Routes.

Serves application pages: Home, Profile, Recommendations, Dashboard, Roadmap, Methodology, Assistant.
"""

from flask import Blueprint, render_template, request, jsonify, redirect
from collections import Counter
import json
from config import get_config
from src.services.recommendation_service import RecommendationService
from src.services.profile_service import ProfileService
from src.services.occupation_retriever import OccupationalRetriever
from src.database.models import safe_json_loads

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home landing page."""
    cfg = get_config()
    return render_template(
        "index.html",
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


@main_bp.route("/profile")
def profile():
    """Student profile input and management page."""
    cfg = get_config()
    return render_template(
        "profile.html",
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


@main_bp.route("/recommendations")
def recommendations():
    """Recommendations result page."""
    cfg = get_config()
    run_id = request.args.get("run_id", type=int)
    run_data = None
    if run_id:
        run_data = RecommendationService.get_run_details(run_id)

    return render_template(
        "recommendations.html",
        run_id=run_id,
        run_data=run_data,
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


@main_bp.route("/dashboard")
def dashboard():
    """System analytics and O*NET occupational dataset explorer."""
    cfg = get_config()
    runs = RecommendationService.get_run_history(limit=50)
    occupations = OccupationalRetriever.get_all_occupations(limit=100)
    students = ProfileService.get_all_students(limit=50)

    # Compute quick totals from occupations
    unique_skills = set()
    unique_tech = set()
    domains = set()
    for occ in occupations:
        unique_skills.update(occ.required_skills)
        unique_tech.update(occ.technology_skills)
        if occ.domain:
            domains.add(occ.domain)

    return render_template(
        "dashboard.html",
        total_runs=len(runs),
        total_occupations=len(occupations),
        total_students=len(students),
        total_skills=len(unique_skills),
        total_technologies=len(unique_tech),
        total_domains=len(domains),
        domains_list=sorted(list(domains)),
        runs=runs,
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


@main_bp.route("/roadmap")
def roadmap():
    """Redirect learning roadmap URL to recommendations or dashboard."""
    run_id = request.args.get("run_id", type=int)
    if run_id:
        return redirect(f"/recommendations?run_id={run_id}")
    return redirect("/dashboard")


@main_bp.route("/methodology")
def methodology():
    """Architecture and methodology explanation page."""
    cfg = get_config()
    return render_template(
        "methodology.html",
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


@main_bp.route("/career-assistant")
def career_assistant():
    """Interactive career assistant conversational page."""
    cfg = get_config()
    students = ProfileService.get_all_students(limit=10)
    return render_template(
        "career_assistant.html",
        students=students,
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


@main_bp.route("/api/dashboard/stats")
def dashboard_stats():
    """Return aggregated live dashboard metrics and occupational dataset catalog."""
    from src.database.db import get_db_cursor
    with get_db_cursor(commit=False) as cursor:
        # Fetch all occupations with full metadata
        cursor.execute("""
        SELECT id, soc_code, title, description, domain, education_level,
               required_skills_json, technology_skills_json, knowledge_areas_json, work_activities_json,
               source, verification_status
        FROM occupations
        ORDER BY domain ASC, title ASC
        """)
        occ_rows = cursor.fetchall()

        skill_counter = Counter()
        tech_counter = Counter()
        domain_counter = Counter()
        edu_counter = Counter()
        occupations_list = []

        for row in occ_rows:
            req_skills = safe_json_loads(row["required_skills_json"], [])
            tech_skills = safe_json_loads(row["technology_skills_json"], [])
            knowledge = safe_json_loads(row["knowledge_areas_json"], [])
            activities = safe_json_loads(row["work_activities_json"], [])

            for s in req_skills:
                skill_counter[s] += 1
            for t in tech_skills:
                tech_counter[t] += 1

            domain_val = row["domain"] or "General Technology"
            domain_counter[domain_val] += 1

            edu_raw = row["education_level"] or "Bachelor's Degree"
            if "Master" in edu_raw:
                edu_group = "Master's Degree"
            elif "Bachelor" in edu_raw:
                edu_group = "Bachelor's Degree"
            elif "Associate" in edu_raw or "Diploma" in edu_raw:
                edu_group = "Associate / Diploma"
            else:
                edu_group = "Professional Certification"
            edu_counter[edu_group] += 1

            occupations_list.append({
                "id": row["id"],
                "soc_code": row["soc_code"],
                "title": row["title"],
                "description": row["description"],
                "domain": domain_val,
                "education_level": row["education_level"],
                "required_skills": req_skills,
                "technology_skills": tech_skills,
                "knowledge_areas": knowledge,
                "work_activities": activities,
                "source": row["source"],
                "verification_status": row["verification_status"]
            })

        # Score brackets from recommendations
        cursor.execute("""
        SELECT 
            CASE 
                WHEN match_score >= 86 THEN '86-100 (Exceptional)'
                WHEN match_score >= 76 THEN '76-85 (Strong)'
                WHEN match_score >= 61 THEN '61-75 (Moderate)'
                ELSE '50-60 (Low)'
            END as bracket,
            COUNT(*) as count
        FROM recommendations
        GROUP BY bracket
        """)
        score_counts = cursor.fetchall()

        # Total counts
        cursor.execute("SELECT COUNT(*) as count FROM recommendation_runs")
        total_runs = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM students")
        total_students = cursor.fetchone()["count"]

    # Format domain distribution
    domain_dist = [{"domain": k, "count": v} for k, v in domain_counter.most_common()]
    
    # Format top required skills (top 12)
    top_skills = [{"skill": k, "count": v} for k, v in skill_counter.most_common(12)]

    # Format top technology tools (top 10)
    top_tech = [{"tech": k, "count": v} for k, v in tech_counter.most_common(10)]

    # Format education distribution
    education_dist = [{"education": k, "count": v} for k, v in edu_counter.most_common()]

    return jsonify({
        "status": "success",
        "total_runs": total_runs,
        "total_occupations": len(occupations_list),
        "total_students": total_students,
        "total_skills": len(skill_counter),
        "total_technologies": len(tech_counter),
        "domain_distribution": domain_dist,
        "score_distribution": score_counts,
        "top_skills": top_skills,
        "top_technologies": top_tech,
        "education_distribution": education_dist,
        "occupations": occupations_list
    })


@main_bp.route("/health")
def health():
    """System health check endpoint."""
    cfg = get_config()
    return jsonify({
        "status": "healthy",
        "service": "PathMatch AI",
        "version": "1.0.0",
        "provider": cfg.LLM_PROVIDER,
        "is_demo_mode": cfg.is_demo_mode
    })

