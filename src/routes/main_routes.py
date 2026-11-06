"""PathMatch AI - Main Web UI Routes.

Serves application pages: Home, Profile, Recommendations, Dashboard, Roadmap, Methodology, Assistant.
"""

from flask import Blueprint, render_template, request, jsonify
from config import get_config
from src.services.recommendation_service import RecommendationService
from src.services.profile_service import ProfileService
from src.services.occupation_retriever import OccupationalRetriever

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
    """System analytics dashboard."""
    cfg = get_config()
    runs = RecommendationService.get_run_history(limit=50)
    occupations = OccupationalRetriever.get_all_occupations(limit=100)
    students = ProfileService.get_all_students(limit=50)

    return render_template(
        "dashboard.html",
        total_runs=len(runs),
        total_occupations=len(occupations),
        total_students=len(students),
        runs=runs,
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


@main_bp.route("/roadmap")
def roadmap():
    """Personalized learning roadmap page."""
    cfg = get_config()
    run_id = request.args.get("run_id", type=int)
    run_data = None
    if run_id:
        run_data = RecommendationService.get_run_details(run_id)

    return render_template(
        "roadmap.html",
        run_data=run_data,
        is_demo_mode=cfg.is_demo_mode,
        provider=cfg.LLM_PROVIDER
    )


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
    """Return aggregated live dashboard metrics from database."""
    from src.database.db import get_db_cursor
    with get_db_cursor(commit=False) as cursor:
        # Domain distribution
        cursor.execute("""
        SELECT domain, COUNT(*) as count
        FROM occupations
        GROUP BY domain
        ORDER BY count DESC
        """)
        domain_counts = cursor.fetchall()

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

        cursor.execute("SELECT COUNT(*) as count FROM occupations")
        total_occupations = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM students")
        total_students = cursor.fetchone()["count"]

    return jsonify({
        "status": "success",
        "total_runs": total_runs,
        "total_occupations": total_occupations,
        "total_students": total_students,
        "domain_distribution": domain_counts,
        "score_distribution": score_counts
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

