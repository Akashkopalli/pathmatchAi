"""PathMatch AI - Configuration Module.

Handles application configuration, environment variable loading, and LLM provider settings.
"""

import os
from pathlib import Path


def load_dotenv_custom(dotenv_path=None):
    """Load environment variables from a .env file without external dependencies."""
    if dotenv_path is None:
        dotenv_path = Path(__file__).resolve().parent / ".env"
    else:
        dotenv_path = Path(dotenv_path)

    if not dotenv_path.exists():
        return

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            # Do not overwrite existing environment variables
            if key not in os.environ:
                os.environ[key] = val


# Load .env file automatically
load_dotenv_custom()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "pathmatch-ai-sih25034-dev-secret-key-2025")
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "pathmatch.db"))

    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "demo").lower()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    MAX_REQUEST_RETRIES = int(os.getenv("MAX_REQUEST_RETRIES", "2"))

    # Recommendation Constraints
    MAX_CANDIDATE_OCCUPATIONS = int(os.getenv("MAX_CANDIDATE_OCCUPATIONS", "12"))
    DEFAULT_RECOMMENDATION_LIMIT = int(os.getenv("DEFAULT_RECOMMENDATION_LIMIT", "6"))

    # Verification flag
    @property
    def is_demo_mode(self) -> bool:
        """Determines if demo mode should be active based on credentials."""
        provider = self.LLM_PROVIDER
        if provider == "demo":
            return True
        if provider == "openai" and not self.OPENAI_API_KEY:
            return True
        if provider == "groq" and not self.GROQ_API_KEY:
            return True
        return False


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = False
    DATABASE_PATH = ":memory:"
    LLM_PROVIDER = "demo"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name=None):
    """Get active configuration class."""
    if env_name is None:
        env_name = os.getenv("FLASK_ENV", "development").lower()
    return CONFIG_MAP.get(env_name, DevelopmentConfig)()

