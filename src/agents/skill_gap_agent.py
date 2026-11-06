"""PathMatch AI - Skill Gap Analysis Agent.

Performs comparative skill gap audits between student abilities and target role requirements.
"""

from typing import Dict, Any, List, Tuple
from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.database.models import Occupation
from src.prompts.skill_gap_prompts import (
    SKILL_GAP_SYSTEM_PROMPT,
    SKILL_GAP_USER_PROMPT_TEMPLATE
)
from src.utils.logging_config import logger


class SkillGapAgent:
    """Agent 5: Analyzes missing essential skills, transferable abilities, and improvement actions."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.agent_name = "SkillGapAgent"

    def analyze_gap(
        self,
        student_profile: Dict[str, Any],
        target_occupation: Occupation
    ) -> Tuple[Dict[str, Any], LLMResponse]:
        """Perform LLM skill gap audit against target occupation."""
        confirmed_skills = [
            (s.get("name") or s.get("skill_name") or str(s)) if isinstance(s, dict) else str(s)
            for s in student_profile.get("skills", [])
        ]
        confirmed_skills = [str(s) for s in confirmed_skills if s]

        projects = student_profile.get("projects", [])
        project_names = [f"{p.get('name', 'Project')} ({', '.join(p.get('technologies', []))})" for p in projects]

        user_prompt = SKILL_GAP_USER_PROMPT_TEMPLATE.format(
            target_occupation_title=target_occupation.title,
            soc_code=target_occupation.soc_code,
            required_skills=", ".join(target_occupation.required_skills),
            technology_skills=", ".join(target_occupation.technology_skills),
            knowledge_areas=", ".join(target_occupation.knowledge_areas),
            student_skills=", ".join(confirmed_skills) or "None listed",
            student_projects="; ".join(project_names) or "No projects submitted",
            degree=student_profile.get("degree", "Computer Science")
        )

        parsed_json, response = self.provider.generate_json(
            system_prompt=SKILL_GAP_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1
        )

        if not isinstance(parsed_json, dict):
            parsed_json = {
                "existing_skills": confirmed_skills,
                "matching_skills": [s for s in confirmed_skills if s in target_occupation.required_skills],
                "missing_essential_skills": [{"name": s, "priority": "High", "impact": "Core requirement"} for s in target_occupation.required_skills[:3]],
                "additional_recommended_skills": [{"name": s, "priority": "Medium", "impact": "Tech skill"} for s in target_occupation.technology_skills[:3]],
                "transferable_skills": [{"name": "Problem Solving", "context": "Universal application"}],
                "skills_requiring_verification": [],
                "practical_improvement_suggestions": ["Complete a project implementing missing core skills."]
            }

        return parsed_json, response
