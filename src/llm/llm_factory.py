"""PathMatch AI - LLM Provider Factory.

Instantiates configured LLM providers with environment-driven switching.
"""

from typing import Optional
from config import get_config
from src.llm.base_provider import BaseLLMProvider
from src.llm.openai_provider import OpenAIProvider
from src.llm.groq_provider import GroqProvider
from src.llm.ollama_provider import OllamaProvider
from src.llm.demo_provider import DemoProvider
from src.utils.logging_config import logger


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """Return an initialized LLM provider instance based on name or environment config."""
    cfg = get_config()
    target_provider = (provider_name or cfg.LLM_PROVIDER or "demo").lower()

    if target_provider == "openai":
        if not cfg.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is not configured. Falling back to DEMO MODE with clear labeling.")
            return DemoProvider(model="demo-agent-v1")
        return OpenAIProvider(
            api_key=cfg.OPENAI_API_KEY,
            model=cfg.OPENAI_MODEL,
            timeout_seconds=cfg.REQUEST_TIMEOUT_SECONDS,
            max_retries=cfg.MAX_REQUEST_RETRIES
        )

    elif target_provider == "groq":
        if not cfg.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not configured. Falling back to DEMO MODE with clear labeling.")
            return DemoProvider(model="demo-agent-v1")
        return GroqProvider(
            api_key=cfg.GROQ_API_KEY,
            model=cfg.GROQ_MODEL,
            timeout_seconds=cfg.REQUEST_TIMEOUT_SECONDS,
            max_retries=cfg.MAX_REQUEST_RETRIES
        )

    elif target_provider == "ollama":
        return OllamaProvider(
            base_url=cfg.OLLAMA_BASE_URL,
            model=cfg.OLLAMA_MODEL,
            timeout_seconds=cfg.REQUEST_TIMEOUT_SECONDS,
            max_retries=cfg.MAX_REQUEST_RETRIES
        )

    elif target_provider == "demo":
        return DemoProvider(model="demo-agent-v1")

    else:
        logger.warning(f"Unrecognized provider '{target_provider}'. Defaulting to DEMO MODE.")
        return DemoProvider(model="demo-agent-v1")

