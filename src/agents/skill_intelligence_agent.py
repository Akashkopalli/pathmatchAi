"""PathMatch AI - Skill Intelligence Agent.

Understands skill ontologies, transferable competencies, and prerequisite relationships.
Enforces the strict rule: related skills must NOT automatically become confirmed student skills.
"""

from typing import Dict, Any, List, Tuple
from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.prompts.skill_prompts import (
    SKILL_INTELLIGENCE_SYSTEM_PROMPT,
    SKILL_INTELLIGENCE_USER_PROMPT_TEMPLATE
)
from src.utils.logging_config import logger


class SkillIntelligenceAgent:
    """Agent 2: Evaluates skill relationships, transferable capabilities, and verifications."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.agent_name = "SkillIntelligenceAgent"

    def analyze_skills(
        self,
        confirmed_skills: List[str],
        projects: List[Dict[str, Any]],
        interests: List[str]
    ) -> Tuple[Dict[str, Any], LLMResponse]:
        """Analyze student skill inventory and classify relationships."""
        projects_summary = [
            f"{p.get('name', 'Project')}: using {', '.join(p.get('technologies', []))}"
            for p in projects
        ]

        user_prompt = SKILL_INTELLIGENCE_USER_PROMPT_TEMPLATE.format(
            student_skills=", ".join(confirmed_skills) or "None explicitly provided",
            student_projects="; ".join(projects_summary) or "No project portfolio submitted",
            student_interests=", ".join(interests) or "General Technology"
        )

        parsed_json, response = self.provider.generate_json(
            system_prompt=SKILL_INTELLIGENCE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1
        )

        if not isinstance(parsed_json, dict):
            parsed_json = {
                "confirmed_skills": confirmed_skills,
                "related_skills": [],
                "transferable_skills": ["Problem Solving", "Analytical Thinking"],
                "skills_requiring_verification": [],
                "skills_to_learn": ["Cloud Computing", "CI/CD"],
                "reasoning": "Fallback structured skill evaluation."
            }

        return parsed_json, response

