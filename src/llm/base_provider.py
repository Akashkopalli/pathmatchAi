"""PathMatch AI - Base LLM Provider.

Defines the abstract base class and standardized response models for LLM integrations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
import json
import re
import time

from src.utils.logging_config import logger


@dataclass
class LLMResponse:
    """Standardized metadata and payload container for LLM generation responses."""
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = "unknown"
    provider: str = "unknown"
    execution_time_ms: int = 0
    is_demo_mode: bool = False
    error: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers (OpenAI, Groq, Ollama, Demo)."""

    def __init__(self, model: str, timeout_seconds: int = 30, max_retries: int = 2):
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.provider_name = "base"
        self.is_demo_mode = False

    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> LLMResponse:
        """Generate a raw text completion given system and user instructions."""
        pass

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> Tuple[Any, LLMResponse]:
        """Generate and parse structured JSON output.

        Appends explicit JSON-only constraints and extracts valid JSON payload.
        """
        json_instruction = "\nIMPORTANT: You must reply ONLY with a valid JSON object or array. Do not include markdown preamble or commentary outside the JSON."
        full_system = system_prompt + json_instruction

        response = self.generate_text(full_system, user_prompt, temperature=temperature)
        if response.error:
            raise RuntimeError(f"LLM Provider Error ({self.provider_name}): {response.error}")

        parsed_data = self.extract_json_from_text(response.content)
        return parsed_data, response

    @staticmethod
    def extract_json_from_text(text: str) -> Any:
        """Extract JSON payload from raw model output, handling markdown blocks or formatting."""
        if not text:
            raise ValueError("LLM returned an empty response.")

        clean_text = text.strip()

        # Handle ```json ... ``` markdown fence
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
        if fence_match:
            clean_text = fence_match.group(1).strip()

        # Try direct parse
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass

        # Try locating outer braces { ... } or brackets [ ... ]
        first_bracket = clean_text.find("[")
        last_bracket = clean_text.rfind("]")
        first_brace = clean_text.find("{")
        last_brace = clean_text.rfind("}")

        # If array seems outer
        if first_bracket != -1 and last_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
            substring = clean_text[first_bracket:last_bracket + 1]
            try:
                return json.loads(substring)
            except json.JSONDecodeError:
                pass

        # If object seems outer
        if first_brace != -1 and last_brace != -1:
            substring = clean_text[first_brace:last_brace + 1]
            try:
                return json.loads(substring)
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Failed to parse valid JSON from LLM response content:\n{text[:300]}...")

