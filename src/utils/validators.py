"""PathMatch AI - Data and Output Validation Utilities.

Validates student profile inputs, LLM JSON structures, SOC codes, and match scores.
"""

import re
import json
from typing import Dict, Any, List, Tuple

SOC_CODE_REGEX = re.compile(r"^\d{2}-\d{4}\.\d{2}$")

SKILL_CANONICAL_MAP = {
    "py": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "db": "Database Management",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "git": "Git",
    "github": "Git",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "golang": "Go",
    "go": "Go",
    "linux": "Linux",
    "wireshark": "Wireshark",
    "cybersecurity": "Cybersecurity Basics",
    "cyber security": "Cybersecurity Basics",
}


def normalize_skill_name(raw_name: str) -> str:
    """Normalize a raw skill string to canonical form."""
    if not raw_name:
        return ""
    clean = raw_name.strip()
    lowered = clean.lower()
    return SKILL_CANONICAL_MAP.get(lowered, clean)


def is_valid_soc_code(soc_code: str) -> bool:
    """Check if code matches standard SOC format XX-XXXX.XX."""
    if not soc_code or not isinstance(soc_code, str):
        return False
    return bool(SOC_CODE_REGEX.match(soc_code.strip()))


def validate_match_score(score: Any) -> int:
    """Validate and clamp match score between 0 and 100."""
    try:
        val = int(score)
        return max(0, min(100, val))
    except (ValueError, TypeError):
        return 50


def validate_profile_payload(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate student profile creation / analysis payload.

    Returns (is_valid, error_msg, sanitized_data)
    """
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object", {}

    name = str(data.get("name", "")).strip() or "Student"
    degree = str(data.get("degree", "Computer Science")).strip()
    specialization = str(data.get("specialization", "")).strip()
    education_level = str(data.get("education_level", "Undergraduate")).strip()
    natural_input = str(data.get("natural_input", "")).strip()

    raw_skills = data.get("skills", [])
    raw_projects = data.get("projects", [])
    raw_interests = data.get("interests", [])
    raw_goals = data.get("career_goals", [])

    # Process skills
    cleaned_skills = []
    if isinstance(raw_skills, list):
        for sk in raw_skills:
            if isinstance(sk, dict) and "name" in sk:
                norm = normalize_skill_name(str(sk["name"]))
                if norm:
                    cleaned_skills.append({
                        "name": norm,
                        "evidence": sk.get("evidence", "Explicitly provided"),
                        "proficiency": sk.get("proficiency", "Unspecified")
                    })
            elif isinstance(sk, str) and sk.strip():
                norm = normalize_skill_name(sk)
                if norm:
                    cleaned_skills.append({
                        "name": norm,
                        "evidence": "Explicitly provided",
                        "proficiency": "Unspecified"
                    })

    # Process projects
    cleaned_projects = []
    if isinstance(raw_projects, list):
        for prj in raw_projects:
            if isinstance(prj, dict) and "name" in prj:
                techs = [normalize_skill_name(t) for t in prj.get("technologies", []) if t]
                cleaned_projects.append({
                    "name": str(prj["name"]).strip(),
                    "description": str(prj.get("description", "")).strip(),
                    "technologies": techs
                })

    # Process interests & goals
    cleaned_interests = [str(i).strip() for i in raw_interests if str(i).strip()] if isinstance(raw_interests, list) else []
    cleaned_goals = [str(g).strip() for g in raw_goals if str(g).strip()] if isinstance(raw_goals, list) else []

    if not natural_input and not cleaned_skills and not cleaned_projects:
        return False, "Please provide at least a natural language description, skills, or projects.", {}

    return True, "", {
        "name": name,
        "degree": degree,
        "specialization": specialization,
        "education_level": education_level,
        "natural_input": natural_input,
        "skills": cleaned_skills,
        "projects": cleaned_projects,
        "interests": cleaned_interests,
        "career_goals": cleaned_goals
    }


def validate_recommendation_output(data: Any, allowed_soc_codes: List[str] = None) -> List[Dict[str, Any]]:
    """Validate and filter LLM recommendation output list against candidate occupations."""
    if not isinstance(data, list):
        if isinstance(data, dict) and "recommendations" in data:
            data = data["recommendations"]
        else:
            return []

    validated_results = []
    seen_socs = set()

    for item in data:
        if not isinstance(item, dict):
            continue

        title = str(item.get("occupation_title", "")).strip()
        soc = str(item.get("soc_code", "")).strip()

        # If allowed_soc_codes provided, ensure LLM strictly hallucination-free
        if allowed_soc_codes and soc not in allowed_soc_codes:
            continue

        if soc in seen_socs:
            continue

        seen_socs.add(soc)

        score = validate_match_score(item.get("match_score", 50))
        matching = [str(s).strip() for s in item.get("matching_skills", []) if str(s).strip()]
        missing = [str(s).strip() for s in item.get("missing_skills", []) if str(s).strip()]
        reason = str(item.get("reason", "")).strip()
        proj_rel = str(item.get("project_relevance", "")).strip()
        interest_al = str(item.get("interest_alignment", "")).strip()
        conf = str(item.get("confidence", "Moderate")).strip()
        suggestions = [str(s).strip() for s in item.get("improvement_suggestions", []) if str(s).strip()]

        validated_results.append({
            "occupation_title": title,
            "soc_code": soc,
            "match_score": score,
            "matching_skills": matching,
            "missing_skills": missing,
            "project_relevance": proj_rel,
            "interest_alignment": interest_al,
            "reason": reason,
            "improvement_suggestions": suggestions,
            "confidence": conf,
            "rank_order": len(validated_results) + 1
        })

    # Sort by match score descending
    validated_results.sort(key=lambda x: x["match_score"], reverse=True)
    for idx, r in enumerate(validated_results):
        r["rank_order"] = idx + 1

    return validated_results

