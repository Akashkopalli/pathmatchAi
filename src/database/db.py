"""PathMatch AI - Database Connection and Schema Management.

Provides thread-safe SQLite connection handling, schema migration, and transaction utilities.
"""

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
import os

from config import get_config

_local = threading.local()


def get_db_path() -> str:
    """Return database path from configuration."""
    cfg = get_config()
    db_path = cfg.DATABASE_PATH
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return db_path


def dict_factory(cursor, row):
    """Row factory that converts SQLite rows to dictionaries."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Get or create a thread-local SQLite connection."""
    target_path = db_path or get_db_path()

    # For in-memory testing databases, store on thread
    if target_path == ":memory:":
        if not hasattr(_local, "memory_conn") or _local.memory_conn is None:
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            conn.row_factory = dict_factory
            conn.execute("PRAGMA foreign_keys = ON;")
            _local.memory_conn = conn
        return _local.memory_conn

    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db_cursor(commit: bool = True) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for obtaining a database cursor with automatic commit/rollback."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        # For non-memory connections, close connection if not pooled
        if get_db_path() != ":memory:":
            conn.close()


def init_db(db_path: str = None):
    """Initialise SQLite database schema."""
    target_path = db_path or get_db_path()
    if target_path != ":memory:":
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection(target_path)
    cursor = conn.cursor()

    # Execute schema creation in order with foreign keys
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        degree TEXT,
        specialization TEXT,
        education_level TEXT,
        natural_input TEXT,
        interests_json TEXT DEFAULT '[]',
        career_goals_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS student_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        evidence_type TEXT DEFAULT 'explicit',
        proficiency TEXT DEFAULT 'Unspecified',
        classification TEXT DEFAULT 'confirmed',
        source TEXT DEFAULT 'profile',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS student_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        technologies_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS occupations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        soc_code TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills_json TEXT DEFAULT '[]',
        knowledge_areas_json TEXT DEFAULT '[]',
        work_activities_json TEXT DEFAULT '[]',
        technology_skills_json TEXT DEFAULT '[]',
        education_level TEXT,
        domain TEXT DEFAULT 'Technology',
        source TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS recommendation_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        model_provider TEXT NOT NULL,
        model_name TEXT NOT NULL,
        is_demo_mode INTEGER DEFAULT 0,
        status TEXT DEFAULT 'completed',
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        occupation_id INTEGER NOT NULL,
        occupation_title TEXT NOT NULL,
        soc_code TEXT NOT NULL,
        match_score INTEGER NOT NULL,
        matching_skills_json TEXT DEFAULT '[]',
        missing_skills_json TEXT DEFAULT '[]',
        project_relevance TEXT,
        interest_alignment TEXT,
        reason TEXT,
        improvement_suggestions_json TEXT DEFAULT '[]',
        confidence TEXT DEFAULT 'Moderate',
        rank_order INTEGER NOT NULL,
        FOREIGN KEY (run_id) REFERENCES recommendation_runs(id) ON DELETE CASCADE,
        FOREIGN KEY (occupation_id) REFERENCES occupations(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS skill_gaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        occupation_id INTEGER NOT NULL,
        missing_essential_skills_json TEXT DEFAULT '[]',
        recommended_skills_json TEXT DEFAULT '[]',
        transferable_skills_json TEXT DEFAULT '[]',
        verification_required_skills_json TEXT DEFAULT '[]',
        priority_levels_json TEXT DEFAULT '{}',
        improvement_actions_json TEXT DEFAULT '[]',
        FOREIGN KEY (run_id) REFERENCES recommendation_runs(id) ON DELETE CASCADE,
        FOREIGN KEY (occupation_id) REFERENCES occupations(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS learning_roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        target_occupation TEXT NOT NULL,
        roadmap_30_days_json TEXT DEFAULT '[]',
        roadmap_60_days_json TEXT DEFAULT '[]',
        roadmap_90_days_json TEXT DEFAULT '[]',
        resources_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES recommendation_runs(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        session_title TEXT DEFAULT 'Career Advisory Session',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        context_used_json TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS llm_usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT NOT NULL,
        provider TEXT NOT NULL,
        model TEXT NOT NULL,
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        execution_time_ms INTEGER DEFAULT 0,
        status TEXT DEFAULT 'success',
        error_message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_occupations_soc ON occupations(soc_code);
    CREATE INDEX IF NOT EXISTS idx_recommendations_run ON recommendations(run_id);
    CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
    """)

    conn.commit()
    if target_path != ":memory:":
        conn.close()

