"""PathMatch AI - Flask Web and REST API Automated Integration Tests."""

import pytest
import json
from app import create_app
from src.database.db import init_db


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    init_db()
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check route."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "PathMatch AI"


def test_web_routes(client):
    """Test that all primary HTML templates render without error."""
    routes = [
        "/",
        "/profile",
        "/recommendations",
        "/dashboard",
        "/roadmap",
        "/methodology",
        "/career-assistant"
    ]
    for r in routes:
        resp = client.get(r)
        assert resp.status_code == 200, f"Route {r} returned status {resp.status_code}"
        assert b"PathMatch" in resp.data


def test_api_sample_profiles(client):
    """Test fetching sample student profiles."""
    resp = client.get("/api/sample-profiles")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["sample_profiles"]) == 5
    names = [p["name"] for p in data["sample_profiles"]]
    assert "Rahul" in names
    assert "Ananya" in names
    assert "Mohit" in names
    assert "Sneha" in names
    assert "Arjun" in names


def test_api_profile_analyze(client):
    """Test natural language profile analysis endpoint."""
    payload = {
        "natural_input": "I am a computer science student with Python, SQL, and Git skills. I built a sales dashboard."
    }
    resp = client.post("/api/profile/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "student_id" in data
    assert len(data["profile"]["skills"]) > 0


def test_api_recommend(client):
    """Test full recommendation pipeline API endpoint."""
    payload = {
        "name": "Test Candidate",
        "degree": "Computer Science",
        "skills": [{"name": "Java"}, {"name": "Spring Boot"}, {"name": "MySQL"}],
        "interests": ["Backend Development"],
        "top_k": 4
    }
    resp = client.post("/api/recommend", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "data" in data
    assert "recommendations" in data["data"]
    assert len(data["data"]["recommendations"]) > 0


def test_api_skill_gap(client):
    """Test skill gap API endpoint."""
    # First create student
    prof_resp = client.post("/api/profile/analyze", json={
        "name": "Gap Candidate",
        "skills": [{"name": "Python"}]
    })
    sid = prof_resp.get_json()["student_id"]

    gap_payload = {
        "student_id": sid,
        "soc_code": "15-2051.00"
    }
    resp = client.post("/api/skill-gap", json=gap_payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "missing_essential_skills" in data["data"]


def test_api_learning_roadmap(client):
    """Test learning roadmap API endpoint."""
    prof_resp = client.post("/api/profile/analyze", json={
        "name": "Roadmap Candidate",
        "skills": [{"name": "JavaScript"}, {"name": "React"}]
    })
    sid = prof_resp.get_json()["student_id"]

    road_payload = {
        "student_id": sid,
        "soc_code": "15-1254.00",
        "missing_skills": ["TypeScript", "Next.js"]
    }
    resp = client.post("/api/learning-roadmap", json=road_payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "roadmap_30_days" in data["data"]


def test_api_career_chat(client):
    """Test conversational career assistant endpoint."""
    chat_payload = {
        "message": "What projects should I work on to improve my software engineering profile?"
    }
    resp = client.post("/api/career-chat", json=chat_payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "reply" in data
    assert len(data["reply"]) > 10


def test_api_occupations_catalog(client):
    """Test fetching occupational catalog."""
    resp = client.get("/api/occupations")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["count"] > 50


def test_api_recommendations_history(client):
    """Test fetching recommendations history."""
    resp = client.get("/api/recommendations/history")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert isinstance(data["history"], list)

