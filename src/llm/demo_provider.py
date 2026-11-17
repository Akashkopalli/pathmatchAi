"""PathMatch AI - Demo LLM Provider.

Provides an offline LLM simulation provider for demonstration, local hackathon presentation,
and testing environments where external paid API credentials are not active.

IMPORTANT:
- Explicitly flags all outputs with `is_demo_mode = True` and provider = 'demo'.
- Strictly adheres to the LLM agent structured JSON output schemas without using traditional ML algorithms.
- Simulates realistic agent reasoning across all seven PathMatch agents.
"""

import json
import time
import re
from typing import Dict, Any, List

from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.utils.validators import normalize_skill_name


class DemoProvider(BaseLLMProvider):
    """Demo LLM Provider providing structured, multi-agent simulated LLM reasoning."""

    def __init__(self, model: str = "demo-agent-v1", timeout_seconds: int = 5, max_retries: int = 0):
        super().__init__(model=model, timeout_seconds=timeout_seconds, max_retries=max_retries)
        self.provider_name = "demo"
        self.is_demo_mode = True

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> LLMResponse:
        """Route to appropriate simulated agent output based on prompt context."""
        start_time = time.time()
        sys_lower = system_prompt.lower()
        user_lower = user_prompt.lower()

        # Identify which agent is executing by specific role title
        if "career assistant" in sys_lower or "conversational career" in sys_lower:
            content = self._simulate_assistant_agent(user_prompt)
        elif "role evaluation" in sys_lower or "recommendation agent" in sys_lower:
            content = self._simulate_recommendation_agent(user_prompt)
        elif "skill gap analysis" in sys_lower or "skill gap agent" in sys_lower:
            content = self._simulate_skill_gap_agent(user_prompt)
        elif "learning roadmap" in sys_lower or "roadmap agent" in sys_lower:
            content = self._simulate_roadmap_agent(user_prompt)
        elif "profile understanding" in sys_lower or "profile extraction" in sys_lower:
            content = self._simulate_profile_agent(user_prompt)
        elif "skill intelligence" in sys_lower:
            content = self._simulate_skill_intelligence_agent(user_prompt)
        else:
            content = json.dumps({"status": "ok", "message": "Demo mode simulated response."})

        exec_time = int((time.time() - start_time) * 1000) + 120  # realistic simulated latency
        p_tokens = len(system_prompt.split()) + len(user_prompt.split())
        c_tokens = len(content.split())
        t_tokens = p_tokens + c_tokens

        return LLMResponse(
            content=content,
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            total_tokens=t_tokens,
            model=self.model,
            provider=self.provider_name,
            execution_time_ms=exec_time,
            is_demo_mode=True
        )

    def _simulate_profile_agent(self, user_prompt: str) -> str:
        """Simulate Profile Understanding Agent extracting skills and projects."""
        text = user_prompt.lower()
        detected_skills = []
        # Known skill catalog with word boundary checking
        known_skill_keywords = [
            ("python", "Python"), ("sql", "SQL"), ("excel", "Excel"),
            ("statistics", "Statistics"), ("data visualization", "Data Visualization"),
            ("machine learning", "Machine Learning"), ("pandas", "Pandas"),
            ("numpy", "NumPy"), ("scikit-learn", "Scikit-learn"), ("matplotlib", "Matplotlib"),
            ("html", "HTML"), ("css", "CSS"), ("javascript", "JavaScript"),
            ("react", "React"), ("figma", "Figma"), ("git", "Git"),
            ("java", "Java"), ("oop", "OOP"), ("mysql", "MySQL"),
            ("spring boot", "Spring Boot"), ("rest api", "REST API"),
            ("c\\+\\+", "C++"), ("computer networks", "Computer Networks"),
            ("linux", "Linux"), ("wireshark", "Wireshark"), ("cybersecurity", "Cybersecurity Basics")
        ]

        for kw, canonical in known_skill_keywords:
            pattern = r"\b" + kw + r"\b"
            if re.search(pattern, text):
                detected_skills.append({
                    "name": canonical,
                    "evidence": "Explicitly provided",
                    "proficiency": "Intermediate" if "intermediate" in text else "Unspecified"
                })

        # Infer project mentions
        projects = []
        if "project" in text or "developed" in text or "built" in text:
            # Extract basic project snippet
            projects.append({
                "name": "Student Portfolio Project",
                "technologies": [s["name"] for s in detected_skills[:3]],
                "description": "Practical application implementing demonstrated core technical competencies."
            })

        interests = []
        if "data" in text or "analytics" in text:
            interests.append("Data Analysis")
        if "ai" in text or "machine learning" in text:
            interests.append("Artificial Intelligence")
        if "frontend" in text or "design" in text or "ui" in text:
            interests.append("Frontend Development")
            interests.append("UI Design")
        if "backend" in text:
            interests.append("Backend Development")
        if "security" in text or "network" in text:
            interests.append("Cybersecurity")
            interests.append("Networking")

        goals = []
        if "machine learning" in text:
            goals.append("Machine Learning Engineer")
        elif "frontend" in text:
            goals.append("Frontend Web Developer")
        elif "backend" in text or "java" in text:
            goals.append("Backend Engineer")
        elif "security" in text:
            goals.append("Information Security Analyst")
        else:
            goals.append("Software Developer")

        output = {
            "skills": detected_skills if detected_skills else [{"name": "Problem Solving", "evidence": "Explicitly provided", "proficiency": "Intermediate"}],
            "projects": projects,
            "interests": interests or ["Software Engineering"],
            "career_goals": goals
        }
        return json.dumps(output, indent=2)

    def _simulate_skill_intelligence_agent(self, user_prompt: str) -> str:
        """Simulate Skill Intelligence Agent classifying relationships dynamically from user input."""
        skills_match = re.search(r"Confirmed Student Skills:\s*([^\n\r]+)", user_prompt)
        raw_skills = skills_match.group(1).strip() if skills_match else ""
        skills_list = [s.strip() for s in raw_skills.split(",") if s.strip() and s.strip().lower() != "none explicitly listed"]
        if not skills_list:
            skills_list = ["Foundational Computing"]

        s_lower = {s.lower() for s in skills_list}
        related = []
        transferable = ["Structured Problem Decomposition", "Technical Logic"]
        skills_to_learn = []

        if "html" in s_lower or "css" in s_lower:
            related.extend(["Semantic HTML5", "Responsive Web Design (Flexbox/Grid)", "CSS Box Model", "Web Accessibility (WCAG)"])
            transferable.extend(["Visual Layout Structuring", "Cross-Browser Compatibility"])
            if "javascript" not in s_lower:
                skills_to_learn.append("JavaScript (DOM Manipulation & ES6+)")
            if "git" not in s_lower:
                skills_to_learn.append("Git Version Control & GitHub")
            if "react" not in s_lower and "vue" not in s_lower:
                skills_to_learn.append("Frontend Frameworks (React or Vue)")

        if "python" in s_lower:
            related.extend(["Object-Oriented Python", "Scripting & Automation", "Virtual Environments"])
            transferable.extend(["Data Processing", "Algorithmic Thinking"])
            if "sql" not in s_lower:
                skills_to_learn.append("SQL Database Querying")
            if "docker" not in s_lower:
                skills_to_learn.append("Docker Containerization")

        if "java" in s_lower:
            related.extend(["OOP Design Patterns", "JVM Architecture", "Exception Handling"])
            transferable.extend(["Modular Software Design", "Transactional Architecture"])
            if "spring boot" not in s_lower:
                skills_to_learn.append("Spring Boot Framework")

        if "sql" in s_lower:
            related.extend(["Relational Schema Design", "Index Optimization", "Query Planning"])
            transferable.extend(["Data Integrity Auditing", "Analytical Queries"])

        if not skills_to_learn:
            skills_to_learn = ["Production CI/CD Workflows", "Cloud Deployment (AWS/GCP)", "Automated Unit Testing"]

        output = {
            "confirmed_skills": skills_list,
            "related_skills": related or ["Core Programming Syntax", "Software Architecture"],
            "transferable_skills": transferable,
            "skills_requiring_verification": ["Production Scalability", "System Architecture"],
            "skills_to_learn": skills_to_learn[:4],
            "reasoning": f"Confirmed capabilities evaluated for {', '.join(skills_list)}. Evaluated strictly without artificial exaggeration."
        }
        return json.dumps(output, indent=2)

    def _simulate_recommendation_agent(self, user_prompt: str) -> str:
        """Simulate LLM Evaluation Agent evaluating candidate occupations dynamically against student profile."""
        # 1. Parse student profile from prompt
        confirmed_skills = []
        skills_match = re.search(r"Confirmed Skills:\s*([^\n\r]+)", user_prompt)
        if skills_match:
            raw_s = skills_match.group(1).strip()
            if raw_s.lower() not in ["none explicitly listed", "none listed"]:
                confirmed_skills = [s.strip() for s in raw_s.split(",") if s.strip()]

        s_lower_set = {s.lower() for s in confirmed_skills}

        # Check projects
        project_techs = set()
        if "Portfolio Projects:" in user_prompt and "- Stated Interests:" in user_prompt:
            try:
                proj_part = user_prompt.split("Portfolio Projects:")[1].split("- Stated Interests:")[0].strip()
                projects = json.loads(proj_part)
                if isinstance(projects, list):
                    for p in projects:
                        if isinstance(p, dict):
                            for t in p.get("technologies", []):
                                project_techs.add(t.lower().strip())
            except Exception:
                pass

        # Interests & goals
        int_match = re.search(r"Stated Interests:\s*([^\n\r]+)", user_prompt)
        interests_str = (int_match.group(1).lower() if int_match else "")
        goal_match = re.search(r"Career Goals:\s*([^\n\r]+)", user_prompt)
        goals_str = (goal_match.group(1).lower() if goal_match else "")

        # 2. Parse candidate occupations blocks from RETRIEVED CANDIDATE OCCUPATIONS
        candidates = []
        blocks = re.split(r"Candidate\s+\d+:\s*", user_prompt)[1:]
        for b in blocks:
            soc_m = re.search(r"SOC:\s*([^\s|]+)", b)
            title_m = re.search(r"Title:\s*([^\n\r]+)", b)
            dom_m = re.search(r"Domain:\s*([^\s|]+(?:\s+[^\s|]+)*)", b)
            desc_m = re.search(r"Description:\s*([^\n\r]+)", b)
            req_m = re.search(r"Required Skills:\s*([^\n\r]+)", b)
            tech_m = re.search(r"Technology Skills:\s*([^\n\r]+)", b)

            if soc_m and title_m:
                req_list = [s.strip() for s in req_m.group(1).split(",") if s.strip()] if req_m else []
                tech_list = [s.strip() for s in tech_m.group(1).split(",") if s.strip()] if tech_m else []
                candidates.append({
                    "soc": soc_m.group(1).strip(),
                    "title": title_m.group(1).strip(),
                    "domain": dom_m.group(1).strip() if dom_m else "",
                    "description": desc_m.group(1).strip() if desc_m else "",
                    "required_skills": req_list,
                    "technology_skills": tech_list
                })

        # Helper to check if student actually has a candidate skill
        def normalize_skill(sk):
            return re.sub(r"[^a-z0-9]", "", sk.lower())

        def has_skill(cand_sk):
            c_norm = normalize_skill(cand_sk)
            for s in confirmed_skills:
                s_norm = normalize_skill(s)
                if s_norm == c_norm:
                    return True
                pairs = [
                    ({"html", "html5"}),
                    ({"css", "css3"}),
                    ({"js", "javascript"}),
                    ({"py", "python"}),
                    ({"ts", "typescript"}),
                ]
                for p in pairs:
                    if s_norm in p and c_norm in p:
                        return True
            return False

        recommendations = []
        for c in candidates:
            title = c["title"]
            soc = c["soc"]
            req_skills = c["required_skills"]
            tech_skills = c["technology_skills"]
            domain = c["domain"]

            # Compute ACTUAL matching skills: ONLY skills from the candidate requirement that student actually has!
            matching = []
            for sk in req_skills + tech_skills:
                if has_skill(sk) and sk not in matching:
                    matching.append(sk)

            # Compute ACTUAL missing skills
            missing = []
            for sk in req_skills:
                if not has_skill(sk) and sk not in missing:
                    missing.append(sk)
            for sk in tech_skills:
                if not has_skill(sk) and sk not in missing and len(missing) < 5:
                    missing.append(sk)

            # Realistic 6-Dimension Score Calculation
            # D1: Required Skills Coverage (38 points max)
            req_match_cnt = len([sk for sk in req_skills if has_skill(sk)])
            req_ratio = req_match_cnt / max(len(req_skills), 1)
            score_d1 = req_ratio * 38.0

            # D2: Technology Skills Coverage (12 points max)
            tech_match_cnt = len([t for t in tech_skills if has_skill(t)])
            tech_ratio = tech_match_cnt / max(len(tech_skills), 1)
            score_d2 = tech_ratio * 12.0

            # D3: Project Evidence (15 points max)
            if project_techs:
                proj_overlap = len([t for t in (req_skills + tech_skills) if t.lower() in project_techs])
                score_d3 = min(15.0, 4.0 + (proj_overlap * 3.5))
            else:
                score_d3 = 3.0  # baseline without projects

            # D4: Interest & Career Goal Fit (15 points max)
            t_low = title.lower()
            d_low = domain.lower()
            t_words = set(re.findall(r"\w+", t_low + " " + d_low))
            int_words = set(re.findall(r"\w+", interests_str + " " + goals_str))
            int_words = {w for w in int_words if len(w) > 2 and w not in {"and", "the", "for", "with", "general", "developer", "development", "specialist"}}
            if t_words.intersection(int_words):
                score_d4 = 14.0
            elif any(w in interests_str or w in goals_str for w in [t_low, d_low]) or any(w in t_low for w in interests_str.split(",")):
                score_d4 = 14.0
            elif any(w in interests_str for w in ["web", "software", "tech", "computer", "data"]):
                score_d4 = 9.0
            else:
                score_d4 = 3.0

            # D5: Degree Suitability (12 points max)
            score_d5 = 11.0

            # D6: Foundational & Transferable (8 points max)
            score_d6 = 7.0 if confirmed_skills else 2.0

            total_score = int(round(score_d1 + score_d2 + score_d3 + score_d4 + score_d5 + score_d6))
            total_score = max(18, min(95, total_score))

            if matching:
                reason = (
                    f"You have confirmed competencies in {', '.join(matching)}, providing foundational layout alignment for {title}. "
                    f"To reach full internship readiness, focus on acquiring {', '.join(missing[:2])}."
                )
            else:
                reason = (
                    f"Foundational interest in {title}, but missing direct technical prerequisites in {', '.join(missing[:2])}."
                )

            recommendations.append({
                "occupation_title": title,
                "soc_code": soc,
                "match_score": total_score,
                "matching_skills": matching if matching else ["Foundational Computing"],
                "missing_skills": missing if missing else ["Industry Standards", "System Architecture"],
                "project_relevance": "Demonstrated via portfolio code" if project_techs else "Coursework foundation without verified project implementation",
                "interest_alignment": f"Directly aligns with {domain} interest" if score_d4 >= 10 else "General computing interest",
                "reason": reason,
                "improvement_suggestions": [
                    f"Build a practical hands-on mini-project demonstrating {missing[0]}" if missing else "Deepen project portfolio",
                    f"Gain familiarity with {missing[1]}" if len(missing) > 1 else "Prepare for technical interviews"
                ],
                "confidence": "High" if total_score >= 75 and project_techs else ("Moderate" if total_score >= 50 else "Low")
            })

        # Sort recommendations by match score descending
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return json.dumps(recommendations[:6], indent=2)

    def _simulate_skill_gap_agent(self, user_prompt: str) -> str:
        """Simulate Skill Gap Analysis Agent evaluating real student skills against target role."""
        # Extract student skills
        skills_match = re.search(r"(?:Confirmed Skills|Student Skills):\s*([^\n\r]+)", user_prompt, re.IGNORECASE)
        raw_sk = skills_match.group(1).strip() if skills_match else ""
        student_skills = [
            s.strip() for s in raw_sk.split(",")
            if s.strip() and s.strip().lower() not in ["none listed", "none explicitly listed"]
        ]
        s_lower_set = {s.lower() for s in student_skills}

        # Extract required skills and tech skills of target occupation
        req_match = re.search(r"(?:Core Required Skills|Required Skills):\s*([^\n\r]+)", user_prompt, re.IGNORECASE)
        raw_req = req_match.group(1).strip() if req_match else ""
        req_skills = [s.strip() for s in raw_req.split(",") if s.strip()]

        tech_match = re.search(r"Technology Skills:\s*([^\n\r]+)", user_prompt, re.IGNORECASE)
        raw_tech = tech_match.group(1).strip() if tech_match else ""
        tech_skills = [s.strip() for s in raw_tech.split(",") if s.strip()]

        def normalize_skill(sk):
            return re.sub(r"[^a-z0-9]", "", sk.lower())

        def has_skill(cand_sk):
            c_norm = normalize_skill(cand_sk)
            for s in student_skills:
                s_norm = normalize_skill(s)
                if s_norm == c_norm:
                    return True
                pairs = [
                    ({"html", "html5"}),
                    ({"css", "css3"}),
                    ({"js", "javascript"}),
                    ({"py", "python"}),
                    ({"ts", "typescript"}),
                ]
                for p in pairs:
                    if s_norm in p and c_norm in p:
                        return True
            return False

        matching_unique = []
        for sk in req_skills + tech_skills:
            if has_skill(sk) and sk not in matching_unique:
                matching_unique.append(sk)

        missing_essential = [sk for sk in req_skills if not has_skill(sk)]
        missing_tech = [t for t in tech_skills if not has_skill(t)]

        essential_items = [
            {"name": sk, "priority": "High", "impact": "Core prerequisite requirement for this occupational standard."}
            for sk in missing_essential[:3]
        ]
        if not essential_items:
            essential_items = [{"name": "Advanced Architecture", "priority": "Medium", "impact": "Enterprise scaling."}]

        additional_items = [
            {"name": sk, "priority": "Medium", "impact": "Standard developer toolchain competency."}
            for sk in missing_tech[:3]
        ]
        if not additional_items:
            additional_items = [{"name": "CI/CD & DevOps", "priority": "Medium", "impact": "Automated deployment."}]

        transferable = []
        if "html" in s_lower_set or "css" in s_lower_set:
            transferable.append({"name": "Visual Hierarchy & Layout", "context": "Directly transfers from HTML/CSS markup to component design."})
            transferable.append({"name": "Web Standards Awareness", "context": "Understanding semantic tags aids in accessibility and search optimization."})
        elif "python" in s_lower_set:
            transferable.append({"name": "Algorithmic Scripting", "context": "Python data structure skills transfer across backend and analytics."})
        else:
            transferable.append({"name": "Problem Solving", "context": "Academic computer science foundation transfers to debugging."})

        first_missing = missing_essential[0] if missing_essential else "Git Version Control"
        suggestions = [
            f"Build a focused practical project demonstrating {first_missing}.",
            f"Practice writing clean code and versioning your changes using Git.",
            f"Review standard technical interview concepts for this role."
        ]

        output = {
            "existing_skills": student_skills if student_skills else ["Foundational Computing"],
            "matching_skills": matching_unique if matching_unique else ["Foundational Knowledge"],
            "missing_essential_skills": essential_items,
            "additional_recommended_skills": additional_items,
            "transferable_skills": transferable,
            "skills_requiring_verification": ["Production Scalability", "System Optimization"],
            "practical_improvement_suggestions": suggestions
        }
        return json.dumps(output, indent=2)

    def _simulate_roadmap_agent(self, user_prompt: str) -> str:
        """Simulate Learning Roadmap Agent for 30-, 60-, and 90-day learning plans."""
        output = {
            "target_occupation": "Internship Role Specialist",
            "roadmap_30_days": [
                {
                    "week": "Weeks 1-2",
                    "skill_to_learn": "Core Architectural Foundations & Tools",
                    "learning_objective": "Master foundational prerequisite tools and standardized workflow practices.",
                    "suggested_topics": ["Advanced Git branching", "Modern packaging & virtual environments", "API contract design with OpenAPI"],
                    "practical_exercises": ["Configure multi-branch Git workflow with pre-commit hooks", "Design a CRUD API specification"],
                    "mini_project": "Build an authenticated REST microservice with automated unit tests.",
                    "expected_outcome": "Solidified core engineering hygiene and development velocity.",
                    "estimated_duration": "15-20 hours",
                    "learning_resources": ["Official Documentation (docs.python.org / spring.io)", "MDN Web Docs (developer.mozilla.org)"]
                },
                {
                    "week": "Weeks 3-4",
                    "skill_to_learn": "Containerization & Environment Reproducibility",
                    "learning_objective": "Containerize development services and configure multi-stage Docker builds.",
                    "suggested_topics": ["Dockerfile syntax", "Docker Compose multi-container networks", "Environment variable injection"],
                    "practical_exercises": ["Write optimized Dockerfiles with minimal layers", "Orchestrate app + database via Docker Compose"],
                    "mini_project": "Containerize student portfolio project with database migration scripts.",
                    "expected_outcome": "Ability to package and run services consistently across any environment.",
                    "estimated_duration": "15 hours",
                    "learning_resources": ["Official Docker Documentation (docs.docker.com)"]
                }
            ],
            "roadmap_60_days": [
                {
                    "month": "Month 2 (Days 31-60)",
                    "skill_to_learn": "Continuous Integration & Cloud Services",
                    "learning_objective": "Automate testing pipelines and deploy resilient services to cloud infrastructure.",
                    "suggested_topics": ["GitHub Actions workflows", "Cloud compute and serverless instances", "Cloud database configuration"],
                    "practical_exercises": ["Build a CI workflow testing lint, unit, and integration suites on pull requests", "Provision cloud database with SSL"],
                    "mini_project": "Deploy an end-to-end application with automated CI/CD and monitoring.",
                    "expected_outcome": "Demonstrated full-lifecycle production deployment proficiency.",
                    "estimated_duration": "30-35 hours",
                    "learning_resources": ["GitHub Actions Documentation (docs.github.com/actions)", "AWS Skill Builder Free Fundamentals"]
                }
            ],
            "roadmap_90_days": [
                {
                    "month": "Month 3 (Days 61-90)",
                    "skill_to_learn": "Domain Capstone Project & Internship Readiness",
                    "learning_objective": "Architect a production-grade portfolio capstone showcasing end-to-end domain problem solving.",
                    "suggested_topics": ["Performance profiling and latency reduction", "Security hardening (OWASP Top 10)", "Executive technical presentation & documentation"],
                    "practical_exercises": ["Execute benchmark load tests and optimize query execution plans", "Perform security review and input audit"],
                    "mini_project": "Complete open-source portfolio capstone project with live demo URL, architecture diagrams, and comprehensive README.",
                    "expected_outcome": "Internship-ready portfolio project demonstrably aligned with target O*NET occupational standards.",
                    "estimated_duration": "40 hours",
                    "learning_resources": ["OWASP Foundation Guidelines (owasp.org)", "Google Cloud Architecture Framework"]
                }
            ],
            "resources": [
                {"name": "Official Documentation Hubs", "url": "https://developer.mozilla.org", "category": "Reference"},
                {"name": "O*NET Online Occupational Data", "url": "https://www.onetonline.org", "category": "Career Standards"},
                {"name": "GitHub Skills Interactive Labs", "url": "https://skills.github.com", "category": "Interactive"}
            ]
        }
        return json.dumps(output, indent=2)

    def _simulate_assistant_agent(self, user_prompt: str) -> str:
        """Simulate Conversational Career Assistant Agent with direct, concise, and accurate answers."""
        # 1. Extract user message
        user_msg = ""
        if "STUDENT MESSAGE:" in user_prompt:
            user_msg = user_prompt.split("STUDENT MESSAGE:")[-1].strip()
        else:
            user_msg = user_prompt.strip()

        msg_low = user_msg.lower().strip()

        # 2. Extract student metadata from prompt if available
        student_name = "there"
        match_name = re.search(r"Name:\s*([^\n\r]+)", user_prompt)
        if match_name and match_name.group(1).strip() and match_name.group(1).strip().lower() != "student":
            student_name = match_name.group(1).strip()

        degree = "Computer Science"
        match_deg = re.search(r"Degree:\s*([^\n\r]+)", user_prompt)
        if match_deg and match_deg.group(1).strip():
            degree = match_deg.group(1).strip()

        skills = []
        match_skills = re.search(r"Confirmed Skills:\s*([^\n\r]+)", user_prompt)
        if match_skills and match_skills.group(1).strip():
            raw_s = match_skills.group(1).strip()
            if raw_s.lower() not in ["none listed", "none explicitly listed"]:
                skills = [s.strip() for s in raw_s.split(",") if s.strip()]

        skill_summary = ", ".join(skills) if skills else "your declared skills"

        # Extract top role and match score from prompt
        top_role = "Web Developer (Frontend)"
        top_score = 52
        match_role = re.search(r"#1:\s*([^(\n\r]+)\s*\(Match:\s*(\d+)/100", user_prompt)
        if match_role:
            top_role = match_role.group(1).strip()
            top_score = int(match_role.group(2))
        else:
            match_role_fallback = re.search(r"#1:\s*([^(\n\r]+)", user_prompt)
            if match_role_fallback:
                top_role = match_role_fallback.group(1).strip()

        second_role = ""
        match_role2 = re.search(r"#2:\s*([^(\n\r]+)", user_prompt)
        if match_role2:
            second_role = match_role2.group(1).strip()

        # Extract missing skills from prompt
        missing_skills_str = ""
        match_gaps = re.search(r"Active Skill Gaps:\s*([^\n\r]+)", user_prompt)
        if match_gaps and match_gaps.group(1).strip() and match_gaps.group(1).strip().lower() != "none identified yet.":
            missing_skills_str = match_gaps.group(1).strip()
        else:
            s_lows = [s.lower() for s in skills]
            if "html" in s_lows or "css" in s_lows:
                missing_skills_str = "JavaScript, Git, React"
            elif "python" in s_lows:
                missing_skills_str = "SQL, Docker, Cloud Deployment"
            elif "java" in s_lows:
                missing_skills_str = "Spring Boot, Docker, REST APIs"
            else:
                missing_skills_str = "Core Programming, Version Control"

        raw_missing = [m.strip() for m in missing_skills_str.split(",") if m.strip()]

        def normalize_skill(sk):
            return re.sub(r"[^a-z0-9]", "", sk.lower())

        s_norms = {normalize_skill(s) for s in skills}
        # Filter out any skill the student already has
        missing_list = [m for m in raw_missing if normalize_skill(m) not in s_norms]
        if not missing_list:
            missing_list = ["JavaScript", "Git", "React"] if any(s.lower() in ["html", "css"] for s in skills) else ["System Design", "Cloud Infrastructure"]
        first_missing = missing_list[0]

        # 3. Direct, Focused Answers Based on User's Question
        # Question: What is my role / suitable roles?
        if any(w in msg_low for w in ["what is my role", "what role", "which role", "my role", "what job", "suitable for", "what am i suitable"]):
            ans = f"Based on your profile, your primary recommended role is **{top_role}** (Suitability Match: **{top_score}%**)"
            if second_role:
                ans += f", followed by **{second_role}**"
            ans += f".\n\nWith your skills in **{skill_summary}**, you have foundational alignment for this path. To qualify for competitive internships, learning **{first_missing}** is your most important next step."
            return ans

        # Question: Skills needed / what to learn?
        elif any(w in msg_low for w in ["skills needed", "what skills", "which skills", "what to learn", "missing skills", "skills required", "needed skills"]):
            bullet_items = "\n".join([f"  {idx+1}. **{m}** (Priority)" for idx, m in enumerate(missing_list[:3])])
            return (
                f"For **{top_role}**, here is your exact skill roadmap:\n\n"
                f"• **Skills you have:** {skill_summary}\n"
                f"• **Essential skills to learn next:**\n{bullet_items}\n\n"
                f"Start with **{first_missing}** first, as it is the most critical requirement for entry-level roles."
            )

        # Question: Is HTML/CSS enough?
        elif any(w in msg_low for w in ["enough", "only html", "only css"]):
            return (
                f"Knowing **{skill_summary}** is a great start for web layout and styling, but on its own it is generally **not enough** for professional internships.\n\n"
                f"To be internship-ready, you also need:\n"
                f"1. **JavaScript** (for DOM manipulation, event handling, and interactivity)\n"
                f"2. **Git & GitHub** (for version control and team code collaboration)\n\n"
                f"Adding basic JavaScript will immediately make you eligible for Junior Web Development opportunities!"
            )

        # Question: How to prepare?
        elif any(w in msg_low for w in ["how to prepare", "where to start", "how to start", "what should i do", "how do i prepare"]):
            return (
                f"Here is a simple 3-step action plan to prepare for **{top_role}** internships:\n\n"
                f"1. **Build a project:** Create a small website using your current skills ({skill_summary}).\n"
                f"2. **Add {first_missing}:** Implement basic interactive features using {first_missing}.\n"
                f"3. **Publish to GitHub:** Upload your code with a clear README so recruiters can see it.\n\n"
                f"This hands-on proof is what matters most to hiring managers."
            )

        # Question: Interview questions?
        elif any(w in msg_low for w in ["interview", "questions", "coding test"]):
            return (
                f"Here are 3 standard interview questions for **{top_role}**:\n\n"
                f"1. *'Explain the CSS Box Model and how padding, border, and margin differ.'*\n"
                f"2. *'What is semantic HTML and why does it matter for accessibility and SEO?'*\n"
                f"3. *'How do you make a webpage responsive across mobile and desktop devices?'*\n\n"
                f"Be ready to explain your answers with practical examples from your code."
            )

        # Question: Project ideas?
        elif any(w in msg_low for w in ["project", "build", "portfolio"]):
            return (
                f"Here are 2 high-impact project ideas for **{top_role}** based on your skills ({skill_summary}):\n\n"
                f"1. **Responsive Portfolio Website:** Build a clean personal portfolio showcasing your background and skills with custom CSS Flexbox/Grid.\n"
                f"2. **Interactive Landing Page:** Create a responsive product showcase with a navigation bar, pricing cards, and a contact form.\n\n"
                f"Host them live for free on GitHub Pages so recruiters can view them with one click."
            )

        # Question: Salary / Vacancy / Hiring?
        elif any(w in msg_low for w in ["salary", "stipend", "vacancy", "openings", "hiring"]):
            return (
                f"PathMatch AI evaluates occupational skill suitability based on O*NET standards; it does not list live job vacancies or commercial salaries.\n\n"
                f"However, entry-level internships for **{top_role}** typically offer competitive stipends once you master {skill_summary} and basic {first_missing}."
            )

        # Fallback: Simple, direct 2-3 sentence answer targeting the query
        else:
            clean_q = user_msg.replace("?", "").strip()
            return (
                f"Regarding **'{clean_q}'**:\n\n"
                f"For your target path in **{top_role}**, the most important next step is applying your current knowledge in {skill_summary} while learning {first_missing}. "
                f"Feel free to ask about specific skills, interview questions, or project ideas!"
            )
