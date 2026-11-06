"""PathMatch AI - Occupational Knowledge Retrieval Service.

Retrieves relevant candidate occupational records from SQLite database for LLM evaluation.
Adheres strictly to the architectural rule: database queries and relational filters only.
"""

from typing import List, Dict, Any, Optional
from src.database.db import get_db_cursor
from src.database.models import Occupation, safe_json_loads


class OccupationalRetriever:
    """Retrieves candidate occupations from database for prompt injection into LLM agents."""

    @staticmethod
    def get_all_occupations(limit: int = 100) -> List[Occupation]:
        """Fetch all occupations from database up to limit."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
            SELECT id, soc_code, title, description, required_skills_json,
                   knowledge_areas_json, work_activities_json, technology_skills_json,
                   education_level, domain, source, verification_status, created_at
            FROM occupations
            ORDER BY id ASC
            LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [Occupation.from_row(r) for r in rows]

    @staticmethod
    def get_by_soc_code(soc_code: str) -> Optional[Occupation]:
        """Fetch single occupation by exact SOC code."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
            SELECT id, soc_code, title, description, required_skills_json,
                   knowledge_areas_json, work_activities_json, technology_skills_json,
                   education_level, domain, source, verification_status, created_at
            FROM occupations
            WHERE soc_code = ?
            """, (soc_code.strip(),))
            row = cursor.fetchone()
            return Occupation.from_row(row) if row else None

    @staticmethod
    def retrieve_candidates_for_profile(
        skills: List[str],
        interests: List[str],
        career_goals: List[str],
        limit: int = 12
    ) -> List[Occupation]:
        """Retrieve candidate occupations using database queries.

        Selects relevant candidate occupations based on matching skill tags, interests,
        and domain relevance, while maintaining broad diversity for the LLM to rank.
        """
        all_occupations = OccupationalRetriever.get_all_occupations(limit=100)
        if not all_occupations:
            return []

        # Identify target domains from interests and career goals
        interest_text = " ".join(interests + career_goals).lower()
        skills_set = {s.lower().strip() for s in skills}

        scored_candidates = []
        for occ in all_occupations:
            relevance_score = 0
            occ_skills = [s.lower().strip() for s in occ.required_skills + occ.technology_skills]
            occ_domain = occ.domain.lower()

            # Check domain interest alignment
            for interest in interests:
                if interest.lower() in occ_domain or interest.lower() in occ.title.lower():
                    relevance_score += 3

            # Check overlap count with required or tech skills
            skill_overlap = len(skills_set.intersection(occ_skills))
            relevance_score += skill_overlap * 2

            scored_candidates.append((relevance_score, occ))

        # Sort candidates by preliminary database relevance
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Select top candidates, ensuring a healthy selection pool for LLM comparative reasoning
        selected = [item[1] for item in scored_candidates[:limit]]

        # If candidates are too few, pad with general diverse roles
        if len(selected) < limit:
            existing_socs = {o.soc_code for o in selected}
            for occ in all_occupations:
                if occ.soc_code not in existing_socs:
                    selected.append(occ)
                    if len(selected) >= limit:
                        break

        return selected

    @staticmethod
    def format_candidates_for_prompt(candidates: List[Occupation]) -> str:
        """Format candidate occupations into clean text block for LLM prompt context."""
        blocks = []
        for idx, occ in enumerate(candidates, 1):
            block = (
                f"Candidate {idx}:\n"
                f"  SOC: {occ.soc_code} | Title: {occ.title}\n"
                f"  Domain: {occ.domain} | Education: {occ.education_level}\n"
                f"  Description: {occ.description}\n"
                f"  Required Skills: {', '.join(occ.required_skills[:6])}\n"
                f"  Technology Skills: {', '.join(occ.technology_skills[:6])}\n"
                f"  Knowledge Areas: {', '.join(occ.knowledge_areas[:4])}\n"
                f"  Source: {occ.source} ({occ.verification_status})"
            )
            blocks.append(block)
        return "\n\n".join(blocks)

