"""PathMatch AI - Conversational Career Assistant API Routes."""

from flask import Blueprint, request, jsonify
from src.agents.career_assistant_agent import CareerAssistantAgent
from src.llm.llm_factory import get_llm_provider
from src.services.profile_service import ProfileService
from src.services.recommendation_service import RecommendationService
from src.database.db import get_db_cursor
from src.database.models import safe_json_dumps, safe_json_loads
from src.utils.security import is_rate_limited
from src.utils.logging_config import logger

assistant_bp = Blueprint("assistant_api", __name__, url_prefix="/api")


@assistant_bp.route("/career-chat", methods=["POST"])
def career_chat():
    """Engage in interactive conversation with Career Guidance Assistant."""
    ip = request.remote_addr or "127.0.0.1"
    if is_rate_limited(ip, limit=40, window_seconds=60):
        return jsonify({"error": "Rate limit exceeded. Please wait a moment."}), 429

    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    session_id = data.get("session_id")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # Retrieve student profile if available, or default to the most recent student
    student_profile = {}
    if student_id:
        student = ProfileService.get_student_by_id(student_id)
        if student:
            student_profile = student.to_dict()
    else:
        all_students = ProfileService.get_all_students(limit=1)
        if all_students:
            student = all_students[0]
            student_profile = student.to_dict()
            student_id = student.id

    # Retrieve latest recommendation run for student if exists
    latest_recs = []
    latest_gaps = {}
    if student_id:
        runs = RecommendationService.get_run_history(limit=5)
        for r in runs:
            if r.get("student_id") == student_id:
                details = RecommendationService.get_run_details(r["id"])
                if details:
                    latest_recs = details.get("recommendations", [])
                    latest_gaps = details.get("skill_gap", {})
                break

    # Manage chat session in DB
    with get_db_cursor() as cursor:
        if not session_id:
            cursor.execute("""
            INSERT INTO chat_sessions (student_id, session_title)
            VALUES (?, ?)
            """, (student_id, f"Advisory: {user_message[:30]}..."))
            session_id = cursor.lastrowid
        else:
            cursor.execute("SELECT id FROM chat_sessions WHERE id = ?", (session_id,))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO chat_sessions (student_id, session_title)
                VALUES (?, ?)
                """, (student_id, f"Advisory: {user_message[:30]}..."))
                session_id = cursor.lastrowid

        # Fetch chat history
        cursor.execute("""
        SELECT role, content FROM chat_messages
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT 10
        """, (session_id,))
        history = cursor.fetchall()

        # Save user message
        cursor.execute("""
        INSERT INTO chat_messages (session_id, role, content)
        VALUES (?, 'user', ?)
        """, (session_id, user_message))

    provider = get_llm_provider()
    agent = CareerAssistantAgent(provider)

    try:
        reply_content, response = agent.respond(
            student_profile=student_profile,
            latest_recommendations=latest_recs,
            chat_history=history,
            user_message=user_message,
            skill_gaps=latest_gaps
        )

        # Save assistant message
        with get_db_cursor() as cursor:
            cursor.execute("""
            INSERT INTO chat_messages (session_id, role, content, context_used_json)
            VALUES (?, 'assistant', ?, ?)
            """, (session_id, reply_content, safe_json_dumps({
                "student_id": student_id,
                "recs_count": len(latest_recs)
            })))

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "reply": reply_content,
            "metadata": {
                "provider": provider.provider_name,
                "model": provider.model,
                "is_demo_mode": provider.is_demo_mode,
                "tokens": response.total_tokens
            }
        }), 200

    except Exception as e:
        logger.error(f"Career chat error: {e}")
        return jsonify({"error": f"Career Assistant error: {str(e)}"}), 500


@assistant_bp.route("/career-chat/history/<int:session_id>", methods=["GET"])
def get_chat_history(session_id: int):
    """Retrieve message history for a specific chat session."""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
        SELECT id, role, content, created_at
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id ASC
        """, (session_id,))
        messages = cursor.fetchall()

    return jsonify({"status": "success", "session_id": session_id, "messages": messages}), 200

