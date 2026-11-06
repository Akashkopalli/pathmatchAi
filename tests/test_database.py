"""PathMatch AI - Database Layer Automated Unit Tests."""

import pytest
import sqlite3
from src.database.db import init_db, get_connection
from src.services.profile_service import ProfileService
from src.services.occupation_retriever import OccupationalRetriever
from src.database.models import Student, Occupation


@pytest.fixture
def db_conn():
    """Initializes in-memory database for testing."""
    init_db(":memory:")
    yield get_connection(":memory:")


def test_db_initialization(db_conn):
    """Test that all required relational tables are created in SQLite."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]

    required_tables = [
        "students", "student_skills", "student_projects",
        "occupations", "recommendation_runs", "recommendations",
        "skill_gaps", "learning_roadmaps", "chat_sessions",
        "chat_messages", "llm_usage_logs"
    ]
    for tbl in required_tables:
        assert tbl in tables, f"Expected table {tbl} was not found in schema"


def test_student_and_skills_persistence(db_conn):
    """Test inserting and retrieving student records and skill relations."""
    profile_data = {
        "name": "Test Student",
        "degree": "Computer Science",
        "specialization": "Software Engineering",
        "education_level": "Undergraduate (3rd Year)",
        "skills": [
            {"name": "Python", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Docker", "evidence": "Explicitly provided", "proficiency": "Beginner"}
        ],
        "projects": [
            {"name": "Web Scraper", "technologies": ["Python", "BeautifulSoup"]}
        ],
        "interests": ["Backend Systems"],
        "career_goals": ["Backend Engineer"]
    }

    student_id = ProfileService.save_or_update_student(profile_data)
    assert student_id is not None

    student = ProfileService.get_student_by_id(student_id)
    assert student is not None
    assert student.name == "Test Student"
    assert len(student.skills) == 2
    assert student.skills[0].skill_name == "Python"
    assert len(student.projects) == 1
    assert student.projects[0].name == "Web Scraper"


def test_occupations_soc_uniqueness(db_conn):
    """Test that SOC codes are enforced unique in occupations table."""
    cursor = db_conn.cursor()
    cursor.execute("""
    INSERT INTO occupations (soc_code, title, description, source, verification_status)
    VALUES ('15-1252.00', 'Software Developer', 'Test description', 'O*NET 29.1', 'verified_sample');
    """)
    db_conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
        INSERT INTO occupations (soc_code, title, description, source, verification_status)
        VALUES ('15-1252.00', 'Software Developer Duplicate', 'Another', 'O*NET 29.1', 'verified_sample');
        """)
        db_conn.commit()


def test_import_official_onet_files_graceful(tmp_path):
    """Test official O*NET file importer handles missing files gracefully and parses when present."""
    from scripts.prepare_dataset import import_official_onet_files

    # Missing directory/files
    assert import_official_onet_files(tmp_path / "nonexistent") is False

    # Create mock O*NET tab-delimited files
    raw_dir = tmp_path / "onet_raw"
    raw_dir.mkdir()
    occ_file = raw_dir / "Occupation Data.txt"
    occ_file.write_text(
        "O*NET-SOC Code\tTitle\tDescription\n"
        "15-9999.00\tCustom Test Engineer\tDevelops cutting edge robotics systems.\n",
        encoding="utf-8"
    )

    skills_file = raw_dir / "Skills.txt"
    skills_file.write_text(
        "O*NET-SOC Code\tElement Name\tScale ID\n"
        "15-9999.00\tRobotics\tIM\n",
        encoding="utf-8"
    )

    imported = import_official_onet_files(raw_dir)
    assert imported is True

    occ = OccupationalRetriever.get_by_soc_code("15-9999.00")
    assert occ is not None
    assert occ.title == "Custom Test Engineer"
    assert occ.verification_status == "official_imported"
    assert "Robotics" in occ.required_skills

