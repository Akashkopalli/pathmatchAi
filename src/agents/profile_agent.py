"""PathMatch AI - Student Profile Understanding Agent.

Parses unstructured student input, natural language descriptions, and resumes
into structured JSON containing validated skills, projects, interests, and career goals.
"""

from typing import Dict, Any, Tuple
from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.prompts.profile_prompts import (
    PROFILE_EXTRACTION_SYSTEM_PROMPT,
    PROFILE_EXTRACTION_USER_PROMPT_TEMPLATE
)
from src.utils.security import wrap_user_prompt, sanitize_text
from src.utils.validators import validate_profile_payload
from src.utils.logging_config import logger


class StudentProfileAgent:
    """Agent 1: Extracts and structures student profile data using LLM reasoning."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.agent_name = "StudentProfileAgent"

    def analyze_profile_text(self, natural_input: str, base_profile: Dict[str, Any] = None) -> Tuple[Dict[str, Any], LLMResponse]:
        """Process natural language student profile text into structured JSON."""
        sanitized = sanitize_text(natural_input)
        delimited_input = wrap_user_prompt(sanitized)

        user_prompt = PROFILE_EXTRACTION_USER_PROMPT_TEMPLATE.format(
            student_input_block=delimited_input
        )

        parsed_json, response = self.provider.generate_json(
            system_prompt=PROFILE_EXTRACTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1
        )

        merged = base_profile.copy() if base_profile else {}
        merged["natural_input"] = sanitized

        if isinstance(parsed_json, dict):
            # Merge extracted skills with existing
            existing_skills = merged.get("skills", [])
            extracted_skills = parsed_json.get("skills", [])
            merged["skills"] = existing_skills + extracted_skills

            # Merge projects
            existing_projects = merged.get("projects", [])
            extracted_projects = parsed_json.get("projects", [])
            merged["projects"] = existing_projects + extracted_projects

            # Merge interests
            existing_interests = merged.get("interests", [])
            extracted_interests = parsed_json.get("interests", [])
            merged["interests"] = list(set(existing_interests + extracted_interests))

            # Merge career goals
            existing_goals = merged.get("career_goals", [])
            extracted_goals = parsed_json.get("career_goals", [])
            merged["career_goals"] = list(set(existing_goals + extracted_goals))

        is_valid, err_msg, validated_data = validate_profile_payload(merged)
        if not is_valid:
            logger.warning(f"Profile validation warning: {err_msg}")

        return validated_data or merged, response

