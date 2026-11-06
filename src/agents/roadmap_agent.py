"""PathMatch AI - Learning Roadmap Agent.

Generates actionable 30-, 60-, and 90-day personalized learning roadmaps
aligned with O*NET occupational standards and identified student skill gaps.
"""

from typing import Dict, Any, List, Tuple
from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.database.models import Occupation
from src.prompts.roadmap_prompts import (
    ROADMAP_SYSTEM_PROMPT,
    ROADMAP_USER_PROMPT_TEMPLATE
)
from src.utils.logging_config import logger


class RoadmapAgent:
    """Agent 6: Generates personalized 30-60-90 day milestone learning roadmaps."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.agent_name = "RoadmapAgent"

    def generate_roadmap(
        self,
        student_profile: Dict[str, Any],
        target_occupation: Occupation,
        missing_skills: List[str]
    ) -> Tuple[Dict[str, Any], LLMResponse]:
        """Generate milestone-based learning roadmap for the student."""
        confirmed_skills = [
            (s.get("name") or s.get("skill_name") or str(s)) if isinstance(s, dict) else str(s)
            for s in student_profile.get("skills", [])
        ]
        confirmed_skills = [str(s) for s in confirmed_skills if s]

        user_prompt = ROADMAP_USER_PROMPT_TEMPLATE.format(
            target_occupation_title=target_occupation.title,
            soc_code=target_occupation.soc_code,
            missing_skills=", ".join(missing_skills) or "Advanced domain tooling",
            student_skills=", ".join(confirmed_skills) or "Foundational computer science",
            student_interests=", ".join(student_profile.get("interests", [])) or "Technology"
        )

        parsed_json, response = self.provider.generate_json(
            system_prompt=ROADMAP_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2
        )

        if not isinstance(parsed_json, dict):
            parsed_json = {
                "target_occupation": target_occupation.title,
                "roadmap_30_days": [],
                "roadmap_60_days": [],
                "roadmap_90_days": [],
                "resources": []
            }

        return parsed_json, response
