"""PathMatch AI - Recommendation Service and End-to-End Pipeline Tests."""

import pytest
from src.database.db import init_db
from src.services.recommendation_service import RecommendationService
from scripts.prepare_dataset import SAMPLE_PROFILES


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Ensure database has schema and data loaded."""
    init_db()


def test_recommendation_pipeline_rahul():
    """Test full pipeline for Profile 1: Rahul (Data Analytics)."""
    service = RecommendationService("demo")
    rahul_profile = SAMPLE_PROFILES[0]
    result = service.execute_recommendation_pipeline(rahul_profile, top_k=4)

    assert result["run_id"] is not None
    assert len(result["recommendations"]) > 0
    top_rec = result["recommendations"][0]
    assert top_rec["match_score"] >= 70
    assert len(top_rec["matching_skills"]) > 0
    assert "roadmap" in result


def test_recommendation_pipeline_ananya():
    """Test full pipeline for Profile 2: Ananya (Frontend & UI Design)."""
    service = RecommendationService("demo")
    ananya_profile = SAMPLE_PROFILES[1]
    result = service.execute_recommendation_pipeline(ananya_profile, top_k=4)

    recs = result["recommendations"]
    assert len(recs) > 0
    # Top rec should align with web/frontend
    top_title = recs[0]["occupation_title"].lower()
    assert any(term in top_title for term in ["web", "frontend", "interface", "developer"])


def test_recommendation_pipeline_mohit():
    """Test full pipeline for Profile 3: Mohit (Backend Development)."""
    service = RecommendationService("demo")
    mohit_profile = SAMPLE_PROFILES[2]
    result = service.execute_recommendation_pipeline(mohit_profile, top_k=4)

    recs = result["recommendations"]
    assert len(recs) > 0
    top_title = recs[0]["occupation_title"].lower()
    assert any(term in top_title for term in ["backend", "java", "software", "developer", "api"])


def test_recommendation_pipeline_sneha():
    """Test full pipeline for Profile 4: Sneha (AI & Data Science)."""
    service = RecommendationService("demo")
    sneha_profile = SAMPLE_PROFILES[3]
    result = service.execute_recommendation_pipeline(sneha_profile, top_k=4)

    recs = result["recommendations"]
    assert len(recs) > 0
    top_title = recs[0]["occupation_title"].lower()
    assert any(term in top_title for term in ["machine learning", "data scientist", "ai", "analyst"])


def test_recommendation_pipeline_arjun():
    """Test full pipeline for Profile 5: Arjun (Cybersecurity & Networking)."""
    service = RecommendationService("demo")
    arjun_profile = SAMPLE_PROFILES[4]
    result = service.execute_recommendation_pipeline(arjun_profile, top_k=4)

    recs = result["recommendations"]
    assert len(recs) > 0
    top_title = recs[0]["occupation_title"].lower()
    assert any(term in top_title for term in ["security", "network", "administrator", "analyst"])


def test_no_soc_hallucinations():
    """Verify that only candidate occupations provided by the retriever are in the output."""
    from src.agents.recommendation_agent import RoleRecommendationAgent
    from src.llm.demo_provider import DemoProvider
    from src.services.occupation_retriever import OccupationalRetriever

    candidates = OccupationalRetriever.get_all_occupations(limit=5)
    allowed_socs = {o.soc_code for o in candidates}

    agent = RoleRecommendationAgent(DemoProvider())
    recs, _ = agent.evaluate_and_rank(SAMPLE_PROFILES[0], candidates)

    for r in recs:
        assert r["soc_code"] in allowed_socs, f"Hallucinated SOC code {r['soc_code']} found in recommendations!"

