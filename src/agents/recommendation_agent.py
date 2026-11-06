"""PathMatch AI - LLM Role Evaluation and Recommendation Agent.

The core intelligence of PathMatch AI: evaluates candidate occupations using
pure LLM reasoning against the 6-dimension evaluation rubric.
"""

import json
from typing import Dict, Any, List, Tuple
from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.database.models import Occupation
from src.prompts.recommendation_prompts import (
    RECOMMENDATION_SYSTEM_PROMPT,
    RECOMMENDATION_USER_PROMPT_TEMPLATE
)
from src.utils.validators import validate_recommendation_output
from src.utils.logging_config import logger


class RoleRecommendationAgent:
    """Agent 4: Evaluates role suitability and ranks occupations using LLM reasoning."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.agent_name = "RoleRecommendationAgent"

    def evaluate_and_rank(
        self,
        student_profile: Dict[str, Any],
        candidate_occupations: List[Occupation],
        limit: int = 6
    ) -> Tuple[List[Dict[str, Any]], LLMResponse]:
        """Perform LLM role evaluation across candidate occupations."""
        if not candidate_occupations:
            raise ValueError("No candidate occupations provided for evaluation.")

        # Prepare prompt variables
        confirmed_skills = [
            s.get("name") if isinstance(s, dict) else str(s)
            for s in student_profile.get("skills", [])
        ]

        projects = student_profile.get("projects", [])
        projects_summary = [
            {"name": p.get("name"), "technologies": p.get("technologies", []), "description": p.get("description", "")}
            for p in projects
        ]

        from src.services.occupation_retriever import OccupationalRetriever
        candidates_block = OccupationalRetriever.format_candidates_for_prompt(candidate_occupations)
        allowed_socs = [o.soc_code for o in candidate_occupations]

        user_prompt = RECOMMENDATION_USER_PROMPT_TEMPLATE.format(
            student_name=student_profile.get("name", "Student"),
            degree=student_profile.get("degree", "Computer Science"),
            specialization=student_profile.get("specialization", "General"),
            education_level=student_profile.get("education_level", "Undergraduate"),
            confirmed_skills=", ".join(confirmed_skills) or "None explicitly listed",
            projects_json=json.dumps(projects_summary),
            interests=", ".join(student_profile.get("interests", [])) or "Technology",
            career_goals=", ".join(student_profile.get("career_goals", [])) or "Software Professional",
            candidate_occupations_block=candidates_block
        )

        raw_json, response = self.provider.generate_json(
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2
        )

        # Validate and sanitize LLM output strictly against candidate SOC codes
        validated_recs = validate_recommendation_output(raw_json, allowed_soc_codes=allowed_socs)

        # Truncate to desired limit
        final_recs = validated_recs[:limit]

        logger.info(f"LLM successfully evaluated and ranked {len(final_recs)} roles.")
        return final_recs, response

