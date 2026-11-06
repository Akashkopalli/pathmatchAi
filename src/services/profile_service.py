"""PathMatch AI - Profile Persistence and Retrieval Service."""

from typing import Dict, Any, List, Optional
from src.database.db import get_db_cursor
from src.database.models import Student, safe_json_dumps, safe_json_loads
from src.utils.validators import validate_profile_payload
from src.utils.logging_config import logger


class ProfileService:
    """Handles CRUD persistence for students, skills, and projects."""

    @staticmethod
    def save_or_update_student(profile_data: Dict[str, Any]) -> int:
        """Save or update student entity along with skills and projects."""
        is_valid, err_msg, clean_data = validate_profile_payload(profile_data)
        if not is_valid:
            clean_data = profile_data

        student_id = profile_data.get("id")

        with get_db_cursor() as cursor:
            if student_id:
                cursor.execute("""
                UPDATE students SET
                    name = ?, degree = ?, specialization = ?, education_level = ?,
                    natural_input = ?, interests_json = ?, career_goals_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """, (
                    clean_data.get("name", "Student"),
                    clean_data.get("degree", "Computer Science"),
                    clean_data.get("specialization", ""),
                    clean_data.get("education_level", "Undergraduate"),
                    clean_data.get("natural_input", ""),
                    safe_json_dumps(clean_data.get("interests", [])),
                    safe_json_dumps(clean_data.get("career_goals", [])),
                    student_id
                ))
            else:
                cursor.execute("""
                INSERT INTO students (
                    name, degree, specialization, education_level, natural_input,
                    interests_json, career_goals_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    clean_data.get("name", "Student"),
                    clean_data.get("degree", "Computer Science"),
                    clean_data.get("specialization", ""),
                    clean_data.get("education_level", "Undergraduate"),
                    clean_data.get("natural_input", ""),
                    safe_json_dumps(clean_data.get("interests", [])),
                    safe_json_dumps(clean_data.get("career_goals", []))
                ))
                student_id = cursor.lastrowid

            # Update skills
            cursor.execute("DELETE FROM student_skills WHERE student_id = ?", (student_id,))
            for sk in clean_data.get("skills", []):
                name = sk.get("name") if isinstance(sk, dict) else str(sk)
                ev = sk.get("evidence", "explicit") if isinstance(sk, dict) else "explicit"
                prof = sk.get("proficiency", "Unspecified") if isinstance(sk, dict) else "Unspecified"
                cursor.execute("""
                INSERT INTO student_skills (
                    student_id, skill_name, evidence_type, proficiency, classification, source
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id, name, ev, prof, "confirmed", "profile"))

            # Update projects
            cursor.execute("DELETE FROM student_projects WHERE student_id = ?", (student_id,))
            for prj in clean_data.get("projects", []):
                pname = prj.get("name", "Project")
                pdesc = prj.get("description", "")
                ptechs = prj.get("technologies", [])
                cursor.execute("""
                INSERT INTO student_projects (
                    student_id, name, description, technologies_json
                ) VALUES (?, ?, ?, ?)
                """, (student_id, pname, pdesc, safe_json_dumps(ptechs)))

        return student_id

    @staticmethod
    def get_student_by_id(student_id: int) -> Optional[Student]:
        """Fetch complete student entity by ID."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            s_row = cursor.fetchone()
            if not s_row:
                return None

            cursor.execute("SELECT * FROM student_skills WHERE student_id = ?", (student_id,))
            skills = cursor.fetchall()

            cursor.execute("SELECT * FROM student_projects WHERE student_id = ?", (student_id,))
            projects = cursor.fetchall()

            return Student.from_row(s_row, skills=skills, projects=projects)

    @staticmethod
    def get_all_students(limit: int = 50) -> List[Student]:
        """Fetch list of all registered students."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT id FROM students ORDER BY id DESC LIMIT ?", (limit,))
            ids = [r["id"] for r in cursor.fetchall()]

        students = []
        for sid in ids:
            st = ProfileService.get_student_by_id(sid)
            if st:
                students.append(st)
        return students

