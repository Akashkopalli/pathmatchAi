"""PathMatch AI - Database Models and Domain Entities.

Provides dataclass representations and serialization methods for PathMatch database entities.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json


def safe_json_loads(data: Any, default: Any = None):
    """Safely decode JSON string with fallback default."""
    if default is None:
        default = []
    if isinstance(data, (list, dict)):
        return data
    if not data or not isinstance(data, str):
        return default
    try:
        return json.loads(data)
    except Exception:
        return default


def safe_json_dumps(data: Any) -> str:
    """Safely dump data to JSON string."""
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return "[]"


@dataclass
class StudentSkill:
    """Skill entry associated with a student."""
    skill_name: str
    evidence_type: str = "explicit"  # 'explicit', 'inferred_from_project', 'certification'
    proficiency: str = "Unspecified"  # 'Beginner', 'Intermediate', 'Advanced', 'Unspecified'
    classification: str = "confirmed"  # 'confirmed', 'related', 'transferable', 'requires_verification'
    source: str = "profile"
    id: Optional[int] = None
    student_id: Optional[int] = None

    @property
    def name(self) -> str:
        return self.skill_name

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["name"] = self.skill_name
        return d


@dataclass
class StudentProject:
    """Project entry associated with a student."""
    name: str
    technologies: List[str] = field(default_factory=list)
    description: Optional[str] = None
    id: Optional[int] = None
    student_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Student:
    """Student profile domain entity."""
    name: str
    degree: str = "Computer Science"
    specialization: Optional[str] = None
    education_level: str = "Undergraduate"
    natural_input: Optional[str] = None
    interests: List[str] = field(default_factory=list)
    career_goals: List[str] = field(default_factory=list)
    skills: List[StudentSkill] = field(default_factory=list)
    projects: List[StudentProject] = field(default_factory=list)
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["skills"] = [s.to_dict() for s in self.skills]
        res["projects"] = [p.to_dict() for p in self.projects]
        return res

    @classmethod
    def from_row(cls, row: Dict[str, Any], skills: List[Dict[str, Any]] = None, projects: List[Dict[str, Any]] = None):
        skills_objs = [
            StudentSkill(
                id=s.get("id"),
                student_id=s.get("student_id"),
                skill_name=s.get("skill_name"),
                evidence_type=s.get("evidence_type", "explicit"),
                proficiency=s.get("proficiency", "Unspecified"),
                classification=s.get("classification", "confirmed"),
                source=s.get("source", "profile")
            ) for s in (skills or [])
        ]
        proj_objs = [
            StudentProject(
                id=p.get("id"),
                student_id=p.get("student_id"),
                name=p.get("name"),
                description=p.get("description"),
                technologies=safe_json_loads(p.get("technologies_json", "[]"))
            ) for p in (projects or [])
        ]
        return cls(
            id=row.get("id"),
            name=row.get("name", "Anonymous"),
            degree=row.get("degree", ""),
            specialization=row.get("specialization", ""),
            education_level=row.get("education_level", ""),
            natural_input=row.get("natural_input", ""),
            interests=safe_json_loads(row.get("interests_json", "[]")),
            career_goals=safe_json_loads(row.get("career_goals_json", "[]")),
            skills=skills_objs,
            projects=proj_objs,
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        )


@dataclass
class Occupation:
    """Occupational record sourced from O*NET database."""
    soc_code: str
    title: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    knowledge_areas: List[str] = field(default_factory=list)
    work_activities: List[str] = field(default_factory=list)
    technology_skills: List[str] = field(default_factory=list)
    education_level: str = "Bachelor's Degree"
    domain: str = "Technology"
    source: str = "O*NET 29.1 Standard Sample"
    verification_status: str = "verified_sample"  # 'official_imported', 'verified_sample', 'unverified_imported'
    id: Optional[int] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Dict[str, Any]):
        return cls(
            id=row.get("id"),
            soc_code=row.get("soc_code", ""),
            title=row.get("title", ""),
            description=row.get("description", ""),
            required_skills=safe_json_loads(row.get("required_skills_json", "[]")),
            knowledge_areas=safe_json_loads(row.get("knowledge_areas_json", "[]")),
            work_activities=safe_json_loads(row.get("work_activities_json", "[]")),
            technology_skills=safe_json_loads(row.get("technology_skills_json", "[]")),
            education_level=row.get("education_level", "Bachelor's Degree"),
            domain=row.get("domain", "Technology"),
            source=row.get("source", "O*NET Standard Sample"),
            verification_status=row.get("verification_status", "verified_sample"),
            created_at=row.get("created_at")
        )


@dataclass
class RoleRecommendation:
    """Individual role recommendation produced by LLM."""
    occupation_id: int
    occupation_title: str
    soc_code: str
    match_score: int
    matching_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    project_relevance: str = ""
    interest_alignment: str = ""
    reason: str = ""
    improvement_suggestions: List[str] = field(default_factory=list)
    confidence: str = "Moderate"
    rank_order: int = 1
    id: Optional[int] = None
    run_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationRun:
    """A single evaluation and recommendation execution run."""
    student_id: int
    model_provider: str
    model_name: str
    is_demo_mode: bool = False
    status: str = "completed"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    id: Optional[int] = None
    run_timestamp: Optional[str] = None
    recommendations: List[RoleRecommendation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["recommendations"] = [r.to_dict() for r in self.recommendations]
        return res
