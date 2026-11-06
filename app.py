"""PathMatch AI - Flask Web Application Entry Point.

SIH25034 — LLM-Powered Internship Role Recommendation and Career Guidance System.
"""

import os
from flask import Flask, render_template, jsonify
from config import get_config
from src.database.db import init_db
from src.routes.main_routes import main_bp
from src.routes.profile_routes import profile_bp
from src.routes.recommendation_routes import rec_bp
from src.routes.assistant_routes import assistant_bp
from src.utils.logging_config import logger


def create_app(config_name: str = None) -> Flask:
    """Create and configure the PathMatch Flask application."""
    app = Flask(__name__)
    cfg = get_config(config_name)
    app.config.from_object(cfg)

    # Initialize SQLite database
    init_db(cfg.DATABASE_PATH)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(rec_bp)
    app.register_blueprint(assistant_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_context():
        return {
            "app_name": "PathMatch AI",
            "app_subtitle": "Intelligent LLM-Powered Internship Role Recommendation & Career Guidance System",
            "is_demo_mode": cfg.is_demo_mode,
            "llm_provider": cfg.LLM_PROVIDER,
            "llm_model": (
                cfg.OPENAI_MODEL if cfg.LLM_PROVIDER == "openai"
                else cfg.GROQ_MODEL if cfg.LLM_PROVIDER == "groq"
                else cfg.OLLAMA_MODEL if cfg.LLM_PROVIDER == "ollama"
                else "demo-agent-v1"
            )
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("base.html", error_title="404 - Page Not Found", error_message="The requested resource does not exist."), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error. Please check server logs."}), 500

    @app.errorhandler(429)
    def rate_limit_error(e):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    logger.info(f"PathMatch AI initialized successfully. Provider: {cfg.LLM_PROVIDER} (Demo Mode: {cfg.is_demo_mode})")
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

