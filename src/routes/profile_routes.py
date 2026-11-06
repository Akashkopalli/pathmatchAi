"""PathMatch AI - Profile API Routes.

Handles student profile parsing, validation, sample profile retrieval, and database persistence.
"""

import json
from pathlib import Path
from flask import Blueprint, request, jsonify
from src.agents.profile_agent import StudentProfileAgent
from src.llm.llm_factory import get_llm_provider
from src.services.profile_service import ProfileService
from src.utils.validators import validate_profile_payload
from src.utils.security import sanitize_text, is_rate_limited
from src.utils.logging_config import logger

profile_bp = Blueprint("profile_api", __name__, url_prefix="/api")


@profile_bp.route("/profile/analyze", methods=["POST"])
def analyze_profile():
    """Extract structured profile from natural language description using Profile Agent."""
    ip = request.remote_addr or "127.0.0.1"
    if is_rate_limited(ip, limit=30, window_seconds=60):
        return jsonify({"error": "Rate limit exceeded. Please wait a moment."}), 429

    data = request.get_json(silent=True) or {}
    natural_input = sanitize_text(data.get("natural_input", ""))

    if not natural_input and not data.get("skills"):
        return jsonify({"error": "Please provide either natural language profile text or explicit skills."}), 400

    provider = get_llm_provider()
    agent = StudentProfileAgent(provider)

    try:
        structured_data, response = agent.analyze_profile_text(natural_input, data)
        # Persist student
        student_id = ProfileService.save_or_update_student(structured_data)
        structured_data["id"] = student_id

        return jsonify({
            "status": "success",
            "student_id": student_id,
            "profile": structured_data,
            "metadata": {
                "provider": provider.provider_name,
                "model": provider.model,
                "is_demo_mode": provider.is_demo_mode,
                "tokens": response.total_tokens
            }
        }), 200

    except Exception as e:
        logger.error(f"Profile analysis failed: {e}")
        return jsonify({"error": f"Failed to analyze profile: {str(e)}"}), 500


@profile_bp.route("/profile/<int:student_id>", methods=["GET"])
def get_profile(student_id: int):
    """Fetch stored student profile by ID."""
    student = ProfileService.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": "Student profile not found."}), 404
    return jsonify({"status": "success", "profile": student.to_dict()}), 200


@profile_bp.route("/sample-profiles", methods=["GET"])
def get_sample_profiles():
    """Return the 5 predefined SIH sample student profiles."""
    profiles_path = Path(__file__).resolve().parent.parent.parent / "data" / "sample_profiles.json"
    if profiles_path.exists():
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
        return jsonify({"status": "success", "sample_profiles": profiles}), 200
    return jsonify({"error": "Sample profiles file not found."}), 404

