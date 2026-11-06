"""PathMatch AI - Occupational Knowledge Retrieval Agent.

Coordinates database candidate retrieval, enforces O*NET SOC taxonomy standards,
and guarantees distinction between verified official records and sample records.
"""

from typing import List, Dict, Any
from src.database.models import Occupation
from src.services.occupation_retriever import OccupationalRetriever
from src.utils.logging_config import logger


class OccupationalRetrievalAgent:
    """Agent 3: Retrieves relevant candidate occupations from O*NET database."""

    def __init__(self):
        self.retriever = OccupationalRetriever()
        self.agent_name = "OccupationalRetrievalAgent"

    def retrieve_candidates(
        self,
        skills: List[str],
        interests: List[str],
        career_goals: List[str],
        max_candidates: int = 12
    ) -> List[Occupation]:
        """Query and select candidate occupations from database without traditional ML similarity."""
        candidates = self.retriever.retrieve_candidates_for_profile(
            skills=skills,
            interests=interests,
            career_goals=career_goals,
            limit=max_candidates
        )
        logger.info(f"Retrieved {len(candidates)} candidate occupations from database.")
        return candidates

    def format_candidates_block(self, candidates: List[Occupation]) -> str:
        """Format candidate occupations into prompt text block."""
        return self.retriever.format_candidates_for_prompt(candidates)

