"""PathMatch AI - Recommendation API Routes.

Handles role recommendations, skill-gap calculations, roadmap generation, and history.
"""

from flask import Blueprint, request, jsonify
from src.services.recommendation_service import RecommendationService
from src.services.profile_service import ProfileService
from src.services.occupation_retriever import OccupationalRetriever
from src.agents.skill_gap_agent import SkillGapAgent
from src.agents.roadmap_agent import RoadmapAgent
from src.llm.llm_factory import get_llm_provider
from src.utils.security import is_rate_limited
from src.utils.logging_config import logger

rec_bp = Blueprint("recommendation_api", __name__, url_prefix="/api")


@rec_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    """Execute LLM role recommendation pipeline for student profile."""
    ip = request.remote_addr or "127.0.0.1"
    if is_rate_limited(ip, limit=20, window_seconds=60):
        return jsonify({"error": "Rate limit exceeded. Please wait a moment."}), 429

    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")

    # If fresh skills or natural input were submitted in payload, update or save as source of truth
    if data.get("skills") is not None or data.get("natural_input"):
        if student_id:
            data["id"] = student_id
        student_id = ProfileService.save_or_update_student(data)
        student = ProfileService.get_student_by_id(student_id)
        profile_data = student.to_dict() if student else data
    elif student_id:
        student = ProfileService.get_student_by_id(student_id)
        profile_data = student.to_dict() if student else data
    else:
        profile_data = data

    top_k = int(data.get("top_k", 6))

    try:
        service = RecommendationService()
        result = service.execute_recommendation_pipeline(
            profile_data=profile_data,
            student_id=student_id,
            top_k=top_k
        )
        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        logger.error(f"Recommendation execution failed: {e}")
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500


@rec_bp.route("/skill-gap", methods=["POST"])
def get_skill_gap():
    """Generate on-demand skill gap analysis for a specific student and target occupation."""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    soc_code = data.get("soc_code")

    if not student_id or not soc_code:
        return jsonify({"error": "student_id and soc_code are required."}), 400

    student = ProfileService.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": "Student not found."}), 404

    occupation = OccupationalRetriever.get_by_soc_code(soc_code)
    if not occupation:
        return jsonify({"error": "Occupation not found."}), 404

    try:
        provider = get_llm_provider()
        gap_agent = SkillGapAgent(provider)
        gap_data, response = gap_agent.analyze_gap(student.to_dict(), occupation)

        return jsonify({
            "status": "success",
            "data": gap_data,
            "metadata": {
                "provider": provider.provider_name,
                "model": provider.model,
                "is_demo_mode": provider.is_demo_mode,
                "tokens": response.total_tokens
            }
        }), 200

    except Exception as e:
        logger.error(f"Skill gap analysis failed: {e}")
        return jsonify({"error": f"Failed to analyze skill gap: {str(e)}"}), 500


@rec_bp.route("/learning-roadmap", methods=["POST"])
def get_learning_roadmap():
    """Generate personalized 30-60-90 day learning roadmap for student and role."""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    soc_code = data.get("soc_code")
    missing_skills = data.get("missing_skills", [])

    if not student_id or not soc_code:
        return jsonify({"error": "student_id and soc_code are required."}), 400

    student = ProfileService.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": "Student not found."}), 404

    occupation = OccupationalRetriever.get_by_soc_code(soc_code)
    if not occupation:
        return jsonify({"error": "Occupation not found."}), 404

    try:
        provider = get_llm_provider()
        roadmap_agent = RoadmapAgent(provider)
        road_data, response = roadmap_agent.generate_roadmap(student.to_dict(), occupation, missing_skills)

        return jsonify({
            "status": "success",
            "data": road_data,
            "metadata": {
                "provider": provider.provider_name,
                "model": provider.model,
                "is_demo_mode": provider.is_demo_mode,
                "tokens": response.total_tokens
            }
        }), 200

    except Exception as e:
        logger.error(f"Roadmap generation failed: {e}")
        return jsonify({"error": f"Failed to generate roadmap: {str(e)}"}), 500


@rec_bp.route("/recommendations/history", methods=["GET"])
def get_history():
    """Fetch past recommendation runs."""
    limit = int(request.args.get("limit", 20))
    history = RecommendationService.get_run_history(limit=limit)
    return jsonify({"status": "success", "history": history}), 200


@rec_bp.route("/recommendations/<int:run_id>", methods=["GET"])
def get_run_details(run_id: int):
    """Fetch full details of a specific recommendation run."""
    details = RecommendationService.get_run_details(run_id)
    if not details:
        return jsonify({"error": "Run not found."}), 404
    return jsonify({"status": "success", "run": details}), 200


@rec_bp.route("/occupations", methods=["GET"])
def list_occupations():
    """Fetch occupational catalog from O*NET database."""
    limit = int(request.args.get("limit", 80))
    occupations = OccupationalRetriever.get_all_occupations(limit=limit)
    return jsonify({
        "status": "success",
        "count": len(occupations),
        "occupations": [o.to_dict() for o in occupations]
    }), 200

