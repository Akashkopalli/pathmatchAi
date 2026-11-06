"""PathMatch AI - Conversational Career Assistant Agent.

Provides context-aware career guidance, internship role explanations, and conversational mentorship.
"""

from typing import Dict, Any, List, Tuple
from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.prompts.assistant_prompts import (
    ASSISTANT_SYSTEM_PROMPT,
    ASSISTANT_USER_PROMPT_TEMPLATE
)
from src.utils.security import sanitize_text, check_prompt_injection
from src.utils.logging_config import logger


class CareerAssistantAgent:
    """Agent 7: Conversational Career Guidance Assistant."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.agent_name = "CareerAssistantAgent"

    def respond(
        self,
        student_profile: Dict[str, Any],
        latest_recommendations: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]],
        user_message: str,
        skill_gaps: Dict[str, Any] = None
    ) -> Tuple[str, LLMResponse]:
        """Generate contextual career advice response for student inquiry."""
        # Check prompt injection
        is_suspicious, sanitized_msg = check_prompt_injection(user_message)
        if is_suspicious:
            logger.warning("Prompt injection attempt intercepted in career chat.")
            return (
                "I am PathMatch AI Career Guidance Assistant. I focus strictly on academic and career guidance "
                "based on verified O*NET occupational standards. How can I assist with your internship planning?",
                LLMResponse(content="", model=self.provider.model, provider=self.provider.provider_name)
            )

        sanitized_msg = sanitize_text(user_message)

        # Summarize recommendations for context
        recs_summary = [
            f"#{r.get('rank_order', idx+1)}: {r.get('occupation_title')} (Match: {r.get('match_score')}/100, SOC: {r.get('soc_code')})"
            for idx, r in enumerate(latest_recommendations[:4])
        ]

        # Summarize chat history
        history_lines = []
        for msg in chat_history[-6:]:
            role = "Student" if msg.get("role") == "user" else "Assistant"
            history_lines.append(f"{role}: {msg.get('content')}")

        gaps_summary = ""
        if skill_gaps and isinstance(skill_gaps, dict):
            missing_items = skill_gaps.get("missing_essential_skills", [])
            gaps_summary = ", ".join([
                item.get("name", "") if isinstance(item, dict) else str(item)
                for item in missing_items[:4]
            ])

        user_prompt = ASSISTANT_USER_PROMPT_TEMPLATE.format(
            student_name=student_profile.get("name", "Student"),
            degree=student_profile.get("degree", "Computer Science"),
            specialization=student_profile.get("specialization", "General"),
            skills=", ".join([
                s.get("name") if isinstance(s, dict) else str(s)
                for s in student_profile.get("skills", [])
            ]) or "None listed",
            projects="; ".join([p.get("name", "") for p in student_profile.get("projects", [])]) or "None",
            career_goals=", ".join(student_profile.get("career_goals", [])) or "Software Development",
            recommendations_summary="; ".join(recs_summary) or "No recommendation run executed yet.",
            skill_gaps_summary=gaps_summary or "None identified yet.",
            chat_history="\n".join(history_lines) or "No previous messages.",
            user_message=sanitized_msg
        )

        response = self.provider.generate_text(
            system_prompt=ASSISTANT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3
        )

        return response.content, response

