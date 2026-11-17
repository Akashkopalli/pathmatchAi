"""PathMatch AI - Multi-Agent Recommendation Orchestration Service.

Orchestrates the complete end-to-end pipeline:
1. Profile Understanding Agent
2. Skill Intelligence Agent
3. Occupational Knowledge Retrieval Agent
4. LLM Role Evaluation & Recommendation Agent
5. Skill Gap Analysis Agent
6. Learning Roadmap Agent
7. Relational SQLite persistence and LLM token usage logging.
"""

from typing import Dict, Any, List, Optional
from src.database.db import get_db_cursor
from src.database.models import (
    Student, Occupation, safe_json_dumps, safe_json_loads
)
from src.llm.llm_factory import get_llm_provider
from src.agents.profile_agent import StudentProfileAgent
from src.agents.skill_intelligence_agent import SkillIntelligenceAgent
from src.agents.occupation_agent import OccupationalRetrievalAgent
from src.agents.recommendation_agent import RoleRecommendationAgent
from src.agents.skill_gap_agent import SkillGapAgent
from src.agents.roadmap_agent import RoadmapAgent
from src.services.profile_service import ProfileService
from src.services.occupation_retriever import OccupationalRetriever
from src.utils.logging_config import logger


class RecommendationService:
    """Coordinates multi-agent recommendation execution, database persistence, and token tracking."""

    def __init__(self, provider_name: Optional[str] = None):
        self.provider = get_llm_provider(provider_name)
        self.profile_agent = StudentProfileAgent(self.provider)
        self.skill_agent = SkillIntelligenceAgent(self.provider)
        self.retrieval_agent = OccupationalRetrievalAgent()
        self.recommendation_agent = RoleRecommendationAgent(self.provider)
        self.gap_agent = SkillGapAgent(self.provider)
        self.roadmap_agent = RoadmapAgent(self.provider)

    def log_llm_usage(self, agent_name: str, response, error: str = None):
        """Record token usage and execution metadata into llm_usage_logs table."""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                INSERT INTO llm_usage_logs (
                    agent_name, provider, model, prompt_tokens, completion_tokens,
                    total_tokens, execution_time_ms, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent_name,
                    getattr(response, "provider", self.provider.provider_name),
                    getattr(response, "model", self.provider.model),
                    getattr(response, "prompt_tokens", 0),
                    getattr(response, "completion_tokens", 0),
                    getattr(response, "total_tokens", 0),
                    getattr(response, "execution_time_ms", 0),
                    "error" if error else "success",
                    error
                ))
        except Exception as e:
            logger.warning(f"Failed to log LLM token usage: {e}")

    def execute_recommendation_pipeline(
        self,
        profile_data: Dict[str, Any],
        student_id: Optional[int] = None,
        top_k: int = 6
    ) -> Dict[str, Any]:
        """Execute full multi-agent recommendation pipeline."""
        total_prompt_tokens = 0
        total_completion_tokens = 0

        # Step 1: Profile Understanding (if natural language text provided)
        natural_input = profile_data.get("natural_input", "")
        if natural_input and len(natural_input.strip()) > 15 and not profile_data.get("skills"):
            structured_profile, prof_resp = self.profile_agent.analyze_profile_text(natural_input, profile_data)
            self.log_llm_usage(self.profile_agent.agent_name, prof_resp)
            total_prompt_tokens += prof_resp.prompt_tokens
            total_completion_tokens += prof_resp.completion_tokens
            profile_data = structured_profile

        # Ensure student is persisted with up-to-date profile data
        student_id = ProfileService.save_or_update_student(profile_data)
        profile_data["id"] = student_id

        # Step 2: Skill Intelligence
        confirmed_skills = [
            s.get("name") if isinstance(s, dict) else str(s)
            for s in profile_data.get("skills", [])
        ]
        skill_intel, skill_resp = self.skill_agent.analyze_skills(
            confirmed_skills=confirmed_skills,
            projects=profile_data.get("projects", []),
            interests=profile_data.get("interests", [])
        )
        self.log_llm_usage(self.skill_agent.agent_name, skill_resp)
        total_prompt_tokens += skill_resp.prompt_tokens
        total_completion_tokens += skill_resp.completion_tokens

        # Step 3: Candidate Occupational Retrieval (Database only, no traditional ML)
        candidates = self.retrieval_agent.retrieve_candidates(
            skills=confirmed_skills,
            interests=profile_data.get("interests", []),
            career_goals=profile_data.get("career_goals", []),
            max_candidates=12
        )

        if not candidates:
            # Fallback to general database fetch
            candidates = OccupationalRetriever.get_all_occupations(limit=10)

        # Step 4: Pure LLM Role Evaluation & Ranking
        ranked_recs, rec_resp = self.recommendation_agent.evaluate_and_rank(
            student_profile=profile_data,
            candidate_occupations=candidates,
            limit=top_k
        )
        self.log_llm_usage(self.recommendation_agent.agent_name, rec_resp)
        total_prompt_tokens += rec_resp.prompt_tokens
        total_completion_tokens += rec_resp.completion_tokens

        # Step 5 & 6: Skill Gap & Roadmap for Top Ranked Role
        skill_gap_result = {}
        roadmap_result = {}
        top_occ = None

        if ranked_recs:
            top_soc = ranked_recs[0]["soc_code"]
            top_occ = OccupationalRetriever.get_by_soc_code(top_soc)

            if top_occ:
                # Skill Gap
                gap_data, gap_resp = self.gap_agent.analyze_gap(profile_data, top_occ)
                self.log_llm_usage(self.gap_agent.agent_name, gap_resp)
                total_prompt_tokens += gap_resp.prompt_tokens
                total_completion_tokens += gap_resp.completion_tokens
                skill_gap_result = gap_data

                # Roadmap
                missing = ranked_recs[0].get("missing_skills", [])
                road_data, road_resp = self.roadmap_agent.generate_roadmap(profile_data, top_occ, missing)
                self.log_llm_usage(self.roadmap_agent.agent_name, road_resp)
                total_prompt_tokens += road_resp.prompt_tokens
                total_completion_tokens += road_resp.completion_tokens
                roadmap_result = road_data

        # Step 7: Persist Run into Database
        run_id = self._persist_recommendation_run(
            student_id=student_id,
            recommendations=ranked_recs,
            skill_gap=skill_gap_result,
            roadmap=roadmap_result,
            top_occ_id=top_occ.id if top_occ else None,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens
        )

        return {
            "run_id": run_id,
            "student_id": student_id,
            "student_profile": profile_data,
            "skill_intelligence": skill_intel,
            "recommendations": ranked_recs,
            "skill_gap": skill_gap_result,
            "roadmap": roadmap_result,
            "metadata": {
                "provider": self.provider.provider_name,
                "model": self.provider.model,
                "is_demo_mode": self.provider.is_demo_mode,
                "total_prompt_tokens": total_prompt_tokens,
                "total_completion_tokens": total_completion_tokens,
                "total_tokens": total_prompt_tokens + total_completion_tokens
            }
        }

    def _persist_recommendation_run(
        self,
        student_id: int,
        recommendations: List[Dict[str, Any]],
        skill_gap: Dict[str, Any],
        roadmap: Dict[str, Any],
        top_occ_id: Optional[int],
        prompt_tokens: int,
        completion_tokens: int
    ) -> int:
        """Persist recommendation execution run, recommendations, gap, and roadmap to SQLite."""
        with get_db_cursor() as cursor:
            # 1. Create Run
            cursor.execute("""
            INSERT INTO recommendation_runs (
                student_id, model_provider, model_name, is_demo_mode, status,
                prompt_tokens, completion_tokens, total_tokens
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                self.provider.provider_name,
                self.provider.model,
                1 if self.provider.is_demo_mode else 0,
                "completed",
                prompt_tokens,
                completion_tokens,
                prompt_tokens + completion_tokens
            ))
            run_id = cursor.lastrowid

            # 2. Insert Recommendations
            for r in recommendations:
                soc = r.get("soc_code")
                # Look up occupation id
                cursor.execute("SELECT id FROM occupations WHERE soc_code = ?", (soc,))
                occ_row = cursor.fetchone()
                occ_id = occ_row["id"] if occ_row else 1

                cursor.execute("""
                INSERT INTO recommendations (
                    run_id, occupation_id, occupation_title, soc_code, match_score,
                    matching_skills_json, missing_skills_json, project_relevance,
                    interest_alignment, reason, improvement_suggestions_json,
                    confidence, rank_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id,
                    occ_id,
                    r.get("occupation_title", "Unknown"),
                    soc,
                    r.get("match_score", 50),
                    safe_json_dumps(r.get("matching_skills", [])),
                    safe_json_dumps(r.get("missing_skills", [])),
                    r.get("project_relevance", ""),
                    r.get("interest_alignment", ""),
                    r.get("reason", ""),
                    safe_json_dumps(r.get("improvement_suggestions", [])),
                    r.get("confidence", "Moderate"),
                    r.get("rank_order", 1)
                ))

            # 3. Insert Skill Gap
            if skill_gap and top_occ_id:
                cursor.execute("""
                INSERT INTO skill_gaps (
                    run_id, occupation_id, missing_essential_skills_json,
                    recommended_skills_json, transferable_skills_json,
                    verification_required_skills_json, priority_levels_json,
                    improvement_actions_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id,
                    top_occ_id,
                    safe_json_dumps(skill_gap.get("missing_essential_skills", [])),
                    safe_json_dumps(skill_gap.get("additional_recommended_skills", [])),
                    safe_json_dumps(skill_gap.get("transferable_skills", [])),
                    safe_json_dumps(skill_gap.get("skills_requiring_verification", [])),
                    safe_json_dumps({}),
                    safe_json_dumps(skill_gap.get("practical_improvement_suggestions", []))
                ))

            # 4. Insert Roadmap
            if roadmap:
                cursor.execute("""
                INSERT INTO learning_roadmaps (
                    run_id, target_occupation, roadmap_30_days_json,
                    roadmap_60_days_json, roadmap_90_days_json, resources_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    run_id,
                    roadmap.get("target_occupation", "Recommended Occupation"),
                    safe_json_dumps(roadmap.get("roadmap_30_days", [])),
                    safe_json_dumps(roadmap.get("roadmap_60_days", [])),
                    safe_json_dumps(roadmap.get("roadmap_90_days", [])),
                    safe_json_dumps(roadmap.get("resources", []))
                ))

        return run_id

    @staticmethod
    def get_run_history(limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch past recommendation runs with student names and top matches."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
            SELECT r.id, r.student_id, s.name as student_name, r.run_timestamp,
                   r.model_provider, r.model_name, r.is_demo_mode, r.total_tokens
            FROM recommendation_runs r
            JOIN students s ON r.student_id = s.id
            ORDER BY r.id DESC
            LIMIT ?
            """, (limit,))
            runs = cursor.fetchall()

            results = []
            for run in runs:
                cursor.execute("""
                SELECT occupation_title, soc_code, match_score, rank_order
                FROM recommendations
                WHERE run_id = ?
                ORDER BY rank_order ASC
                LIMIT 3
                """, (run["id"],))
                top_recs = cursor.fetchall()

                run_item = dict(run)
                run_item["top_recommendations"] = top_recs
                results.append(run_item)

            return results

    @staticmethod
    def get_run_details(run_id: int) -> Optional[Dict[str, Any]]:
        """Fetch full details of a specific recommendation run."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
            SELECT r.*, s.name as student_name, s.degree, s.specialization
            FROM recommendation_runs r
            JOIN students s ON r.student_id = s.id
            WHERE r.id = ?
            """, (run_id,))
            run = cursor.fetchone()
            if not run:
                return None

            cursor.execute("""
            SELECT * FROM recommendations WHERE run_id = ? ORDER BY rank_order ASC
            """, (run_id,))
            recs = cursor.fetchall()
            for r in recs:
                r["matching_skills"] = safe_json_loads(r.get("matching_skills_json", "[]"))
                r["missing_skills"] = safe_json_loads(r.get("missing_skills_json", "[]"))
                r["improvement_suggestions"] = safe_json_loads(r.get("improvement_suggestions_json", "[]"))

            cursor.execute("SELECT * FROM skill_gaps WHERE run_id = ?", (run_id,))
            gap = cursor.fetchone()
            if gap:
                gap["missing_essential_skills"] = safe_json_loads(gap.get("missing_essential_skills_json", "[]"))
                gap["additional_recommended_skills"] = safe_json_loads(gap.get("recommended_skills_json", "[]"))
                gap["transferable_skills"] = safe_json_loads(gap.get("transferable_skills_json", "[]"))
                gap["practical_improvement_suggestions"] = safe_json_loads(gap.get("improvement_actions_json", "[]"))

            cursor.execute("SELECT * FROM learning_roadmaps WHERE run_id = ?", (run_id,))
            roadmap = cursor.fetchone()
            if roadmap:
                roadmap["roadmap_30_days"] = safe_json_loads(roadmap.get("roadmap_30_days_json", "[]"))
                roadmap["roadmap_60_days"] = safe_json_loads(roadmap.get("roadmap_60_days_json", "[]"))
                roadmap["roadmap_90_days"] = safe_json_loads(roadmap.get("roadmap_90_days_json", "[]"))
                roadmap["resources"] = safe_json_loads(roadmap.get("resources_json", "[]"))

            return {
                "run": dict(run),
                "recommendations": recs,
                "skill_gap": gap,
                "roadmap": roadmap
            }

