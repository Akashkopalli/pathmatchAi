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
        known_skill_keywords = [
            ("python", "Python"), ("sql", "SQL"), ("excel", "Excel"),
            ("statistics", "Statistics"), ("data visualization", "Data Visualization"),
            ("machine learning", "Machine Learning"), ("pandas", "Pandas"),
            ("numpy", "NumPy"), ("scikit-learn", "Scikit-learn"), ("matplotlib", "Matplotlib"),
            ("html", "HTML"), ("css", "CSS"), ("javascript", "JavaScript"),
            ("react", "React"), ("figma", "Figma"), ("git", "Git"),
            ("java", "Java"), ("oop", "OOP"), ("mysql", "MySQL"),
            ("spring boot", "Spring Boot"), ("rest api", "REST API"),
            ("c++", "C++"), ("c ", "C"), ("computer networks", "Computer Networks"),
            ("linux", "Linux"), ("wireshark", "Wireshark"), ("cybersecurity", "Cybersecurity Basics")
        ]

        for kw, canonical in known_skill_keywords:
            if kw in text:
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
        """Simulate Skill Intelligence Agent classifying relationships."""
        output = {
            "confirmed_skills": ["Python", "SQL", "Git"],
            "related_skills": ["Database Design", "Version Control", "Scripting"],
            "transferable_skills": ["Algorithmic Thinking", "Problem Decomposition", "Technical Documentation"],
            "skills_requiring_verification": ["Production Scalability", "System Architecture"],
            "skills_to_learn": ["Cloud Deployment (Docker/AWS)", "CI/CD Workflows"],
            "reasoning": "Explicit student skills validated against occupational standards without artificial capability exaggeration."
        }
        return json.dumps(output, indent=2)

    def _simulate_recommendation_agent(self, user_prompt: str) -> str:
        """Simulate LLM Evaluation Agent evaluating candidate occupations based on prompt context."""
        # Check prompt for candidate occupations passed by retriever
        recommendations = []

        # Find candidate occupations listed in user_prompt
        # Match pattern: SOC: (15-\d{4}\.\d{2}) | Title: ([^\n]+)
        candidates = re.findall(r"SOC:\s*(\d{2}-\d{4}\.\d{2})\s*\|\s*Title:\s*([^\n\r]+)", user_prompt)

        # Isolate student profile part to avoid false matches against candidate descriptions
        if "RETRIEVED CANDIDATE OCCUPATIONS:" in user_prompt:
            p_lower = user_prompt.split("RETRIEVED CANDIDATE OCCUPATIONS:")[0].lower()
        else:
            p_lower = user_prompt.lower()

        if candidates:
            # Score each candidate thoughtfully based on student profile in prompt
            for soc, title in candidates[:12]:
                title_clean = title.strip()
                t_low = title_clean.lower()

                score = 55
                matching = []
                missing = ["Cloud Infrastructure", "System Architecture"]
                proj_rel = "Relevant academic and hands-on portfolio implementation demonstrates foundational readiness."
                interest_al = "Alignment with general technology principles."

                # Java / Backend Developer (e.g. Mohit)
                if ("java" in p_lower or "spring" in p_lower or "backend" in p_lower) and ("backend" in t_low or "java" in t_low or "software developer" in t_low or "api" in t_low or "spring" in t_low):
                    score = 91 if ("java" in t_low or "backend" in t_low or "spring" in t_low) else 82
                    matching = ["Java", "OOP", "MySQL", "REST API", "Spring Boot"]
                    missing = ["Docker / Containerization", "Kafka / Message Queues", "Microservice Security"]
                    interest_al = "Matches interest in robust server-side architecture and transactional reliability."
                # Frontend / Web Developer (e.g. Ananya)
                elif ("react" in p_lower or "html" in p_lower or "frontend" in p_lower or "figma" in p_lower) and ("web" in t_low or "designer" in t_low or "frontend" in t_low or "mobile" in t_low or "vue" in t_low or "interface" in t_low):
                    score = 92 if ("frontend" in t_low or "web" in t_low) else 83
                    matching = ["HTML", "CSS", "JavaScript", "React", "Figma"]
                    missing = ["TypeScript", "Next.js / SSR", "Web Accessibility (WCAG)"]
                    interest_al = "Aligns seamlessly with student's passion for interactive user interfaces and visual aesthetics."
                # Cybersecurity / Networking (e.g. Arjun)
                elif ("cybersecurity" in p_lower or "wireshark" in p_lower or "network" in p_lower or "linux" in p_lower and "c++" in p_lower) and ("security" in t_low or "network" in t_low or "forensics" in t_low or "administrator" in t_low):
                    score = 90 if ("security" in t_low or "network" in t_low) else 80
                    matching = ["C", "C++", "Computer Networks", "Linux", "Cybersecurity Basics", "Wireshark"]
                    missing = ["SIEM Tools (Splunk)", "Firewall Architecture", "Incident Triage Frameworks"]
                    interest_al = "Directly mirrors the candidate's dedication to network defense and vulnerability analysis."
                # Machine Learning / AI (e.g. Sneha)
                elif ("machine learning" in p_lower or "scikit" in p_lower or "artificial intelligence" in p_lower) and ("machine learning" in t_low or "data scientist" in t_low or "ai" in t_low or "deep learning" in t_low or "vision" in t_low):
                    score = 93 if ("machine learning" in t_low or "data scientist" in t_low) else 82
                    matching = ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn"]
                    missing = ["Deep Learning (PyTorch)", "MLOps & Model Monitoring", "Docker"]
                    interest_al = "High synergy with student's aspiration to build predictive AI pipelines."
                # Data Analytics / BI (e.g. Rahul)
                elif ("data" in p_lower or "analytics" in p_lower or "excel" in p_lower or "visualization" in p_lower) and ("data" in t_low or "analyst" in t_low or "intelligence" in t_low or "statistician" in t_low or "database" in t_low):
                    score = 89 if ("analyst" in t_low or "intelligence" in t_low or "scientist" in t_low) else 81
                    matching = ["Python", "SQL", "Statistics", "Data Visualization"]
                    missing = ["Tableau / Power BI Advanced Modeling", "Cloud Data Warehouses"]
                    interest_al = "Directly matches analytical curiosity and data-driven problem solving interest."

                recommendations.append({
                    "occupation_title": title_clean,
                    "soc_code": soc,
                    "match_score": score,
                    "matching_skills": matching or ["Programming Basics", "Problem Solving"],
                    "missing_skills": missing,
                    "project_relevance": proj_rel,
                    "interest_alignment": interest_al,
                    "reason": f"Demonstrates strong foundational alignment for {title_clean}. Core prerequisite competencies match student profile; recommended upskilling in missing domain tools.",
                    "improvement_suggestions": [f"Undertake practical project covering {missing[0]}", f"Deepen knowledge in {missing[-1]}"],
                    "confidence": "High" if score >= 85 else "Moderate"
                })

        # Sort recommendations by match score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return json.dumps(recommendations[:6], indent=2)

    def _simulate_skill_gap_agent(self, user_prompt: str) -> str:
        """Simulate Skill Gap Analysis Agent."""
        output = {
            "existing_skills": ["Python", "SQL", "Git"],
            "matching_skills": ["Python", "SQL"],
            "missing_essential_skills": [
                {"name": "Production Docker & Containerization", "priority": "High", "impact": "Prerequisite for deploying scalable services in modern team workflows."},
                {"name": "Automated Unit Testing & CI/CD", "priority": "High", "impact": "Ensures reliability and test coverage for collaborative codebases."}
            ],
            "additional_recommended_skills": [
                {"name": "Cloud Deployment (AWS / GCP Basics)", "priority": "Medium", "impact": "Expands practical systems architecture versatility."},
                {"name": "Microservices Communication (REST / gRPC)", "priority": "Medium", "impact": "Enhances distributed software modularity."}
            ],
            "transferable_skills": [
                {"name": "Analytical Problem Solving", "context": "Directly transfers from academic computer science algorithms to real-world edge-case debugging."},
                {"name": "Modular Software Design", "context": "Applies across all object-oriented and functional software domains."}
            ],
            "skills_requiring_verification": ["System Scalability", "Production Database Indexing"],
            "practical_improvement_suggestions": [
                "Build and containerize an end-to-end project using Docker and publish images to Docker Hub.",
                "Integrate automated test runs into GitHub Actions for all pull requests.",
                "Deploy the service to a free-tier cloud host (e.g. AWS or Render) with environment isolation."
            ]
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
        """Simulate Conversational Career Assistant Agent with highly responsive, context-aware answers."""
        # 1. Extract user message
        user_msg = ""
        if "STUDENT MESSAGE:" in user_prompt:
            user_msg = user_prompt.split("STUDENT MESSAGE:")[-1].strip()
        else:
            user_msg = user_prompt.strip()

        msg_low = user_msg.lower()

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
            skills = [s.strip() for s in match_skills.group(1).split(",") if s.strip()]

        top_role = "Software Development Role"
        match_roles = re.search(r"#1:\s*([^(\n\r]+)", user_prompt)
        if match_roles and match_roles.group(1).strip():
            top_role = match_roles.group(1).strip()

        skill_summary = ", ".join(skills[:4]) if skills else "core programming"

        # 3. Dynamic Topic Matchers based on User's EXACT Question
        # Interview & Coding Prep
        if any(w in msg_low for w in ["interview", "coding round", "technical round", "online assessment", "oa"]):
            return (
                f"Great question regarding technical interviews, {student_name}!\n\n"
                f"For internship roles in {top_role}, technical evaluations typically follow three distinct stages:\n\n"
                f"1. **Online Coding Assessment (OA):** Focus heavily on Data Structures & Algorithms. Practice medium-difficulty LeetCode problems on Arrays, Strings, Hash Maps, and Two Pointers. For your background in {skill_summary}, ensure you can write clean, bug-free solutions with proper time & space complexity analysis.\n\n"
                f"2. **Core CS Fundamentals:** Expect questions on Object-Oriented Programming (OOPS), Database normalization/indexing, and basic Operating Systems concepts (processes, threads, deadlocks).\n\n"
                f"3. **Project Deep-Dive:** Be prepared to walk through your projects line by line. Interviewers will ask: *'Why did you choose this technology?', 'How did you handle edge cases?',* and *'How would you scale this to 10,000 users?'*\n\n"
                f"**Pro Tip:** Always articulate your thought process out loud before typing any code!"
            )

        # DSA & LeetCode
        elif any(w in msg_low for w in ["dsa", "leetcode", "algorithm", "data structure"]):
            return (
                f"Here is a structured approach to mastering DSA for your internship search, {student_name}:\n\n"
                f"1. **Foundational Topics (Weeks 1-3):** Master Arrays, Strings, Hash Tables, and Two-Pointer patterns. Solve 20-25 problems until pattern recognition becomes second nature.\n"
                f"2. **Intermediate Topics (Weeks 4-6):** Recursion, Linked Lists, Stacks, Queues, and Binary Search. Focus on boundary conditions.\n"
                f"3. **Advanced Topics (Weeks 7-8):** Trees, Depth-First Search (DFS), Breadth-First Search (BFS), and basic Dynamic Programming.\n\n"
                f"Quality beats quantity: thoroughly solving 75 curated problems (like Blind 75) is far more effective than skimming 300 solutions without retention."
            )

        # Resume & CV
        elif any(w in msg_low for w in ["resume", "cv", "portfolio", "github"]):
            return (
                f"Here are key recommendations to make your resume stand out for {top_role} internships, {student_name}:\n\n"
                f"1. **Single-Page Limit:** Keep your resume strictly to 1 page using a clean, ATS-compliant single-column template.\n"
                f"2. **Impact-Driven Project Bullets:** Use the XYZ formula (*'Accomplished [X] as measured by [Y] by doing [Z]'*). Instead of *'Built a web app with React'*, write: *'Architected a responsive single-page store in React, implementing cart state persistence and reducing client-side load time by 35% via code-splitting.'*\n"
                f"3. **Clean GitHub Presence:** Pin your top 2-3 repositories. Every pinned repo must feature a comprehensive README, an architectural diagram, installation commands, and ideally a live deployed URL (e.g. on Vercel, Netlify, or Render).\n"
                f"4. **Skills Section:** Group skills into Languages, Frameworks, Developer Tools, and Databases."
            )

        # How to find / apply for internships (Off-Campus / Cold Outreach)
        elif any(w in msg_low for w in ["how to apply", "find internship", "get internship", "off campus", "cold email", "hiring"]):
            return (
                f"Finding quality tech internships requires a multi-channel strategy, {student_name}:\n\n"
                f"1. **LinkedIn Alumni Outreach:** Reach out to college alumni currently working in {top_role} positions. Send a brief, polite note: *'Hi [Name], I'm a student at [College] passionate about [Domain]. I loved your recent post on [Topic] and would value 10 minutes of advice on preparing for internships at [Company].'*\n"
                f"2. **Early-Stage Startups (Wellfound / AngelList):** Startups provide incredible hands-on mentorship and faster interview turnaround compared to corporate queues.\n"
                f"3. **Open Source Contributions:** Find active open-source repositories on GitHub tagged with `good-first-issue`. Contributing bug fixes or documentation proves real-world teamwork skills before you even interview.\n"
                f"4. **Targeted Job Portals:** Check official career portals in August–October for summer roles, and January–March for off-cycle roles."
            )

        # Specific Technology Questions
        elif "docker" in msg_low or "container" in msg_low:
            return (
                f"Docker is one of the highest-return skills you can learn right now, {student_name}!\n\n"
                f"**Why it matters:** In team environments, 'it works on my machine' is unacceptable. Docker packages your application code, runtime, system tools, and libraries into a lightweight, reproducible container.\n\n"
                f"**How to master it in 3 steps:**\n"
                f"1. Write a `Dockerfile` for your existing project (use multi-stage builds to keep image sizes small).\n"
                f"2. Write a `docker-compose.yml` file to orchestrate both your application and a database (e.g. PostgreSQL or MySQL) on a shared network.\n"
                f"3. Push your image to Docker Hub and test pulling it on a fresh machine or free cloud VM."
            )

        elif "react" in msg_low or "frontend" in msg_low:
            return (
                f"For modern Frontend / React internships, focus on these core competencies, {student_name}:\n\n"
                f"1. **React Fundamentals:** Functional components, Hooks (`useState`, `useEffect`, `useCallback`, `useMemo`), and custom hooks.\n"
                f"2. **State Management:** Master local vs. global state (Context API, Zustand, or Redux Toolkit).\n"
                f"3. **Web Standards & Performance:** Semantic HTML5, accessible ARIA attributes, responsive CSS layouts (Flexbox/Grid), and Core Web Vitals (LCP, FID, CLS).\n"
                f"4. **Build a Capstone:** Build a rich, interactive web application consuming third-party REST APIs with client-side routing, loading skeletons, and error boundaries."
            )

        elif "python" in msg_low or "machine learning" in msg_low or "data science" in msg_low or "ai" in msg_low:
            return (
                f"For AI and Data Science internships, hiring managers look for practical end-to-end execution, {student_name}:\n\n"
                f"1. **Data Wrangling:** Solid mastery of Pandas and NumPy for cleaning messy tabular data, handling missing values, and reshaping dataframes.\n"
                f"2. **Scikit-learn Pipelines:** Don't just call `.fit()` and `.predict()`. Build clean `Pipeline` and `ColumnTransformer` workflows that prevent data leakage and implement k-fold cross-validation.\n"
                f"3. **Model Interpretability:** Understand precision, recall, F1-score, ROC-AUC, and feature importances rather than relying solely on raw accuracy.\n"
                f"4. **Interactive Deployment:** Wrap your trained model in a Streamlit dashboard or FastAPI endpoint and deploy it online so recruiters can test it live."
            )

        elif "java" in msg_low or "spring" in msg_low or "backend" in msg_low:
            return (
                f"For Backend Java and Enterprise Software internships, here is what sets top candidates apart, {student_name}:\n\n"
                f"1. **Spring Boot Architecture:** Understand `@RestController`, `@Service`, and `@Repository` layers and Dependency Injection (Inversion of Control).\n"
                f"2. **Data Persistence:** Spring Data JPA, Hibernate entity lifecycles, and writing optimized JPQL queries.\n"
                f"3. **RESTful API Standards:** Proper HTTP status codes (201 Created, 204 No Content, 400 Bad Request, 404 Not Found), request validation with `@Valid`, and custom global exception handlers (`@ControllerAdvice`).\n"
                f"4. **Database Transactions:** Understand `@Transactional` boundaries, ACID guarantees, and connection pooling."
            )

        elif "cybersecurity" in msg_low or "network" in msg_low or "security" in msg_low or "linux" in msg_low:
            return (
                f"For Cybersecurity and Network Engineering internships, practical hands-on lab experience is key, {student_name}:\n\n"
                f"1. **Networking Protocols:** Master the OSI 7-layer model and TCP/IP stack. Understand how TCP handshakes, DNS resolution, DHCP, and ARP operate under the hood.\n"
                f"2. **Packet Analysis:** Use Wireshark to capture and inspect live network traffic, identifying anomalous packet sequences or plaintext credentials.\n"
                f"3. **Linux Command Line:** Comfort with Linux permissions (`chmod`, `chown`), process management (`ps`, `top`), network utilities (`netstat`, `ss`, `iptables`), and Bash scripting.\n"
                f"4. **Security Concepts:** Familiarize yourself with the OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, IDOR) and write remediation guides."
            )

        elif "sql" in msg_low or "database" in msg_low:
            return (
                f"For Database and Data Engineering roles, focus on these critical areas, {student_name}:\n\n"
                f"1. **Complex Queries:** Master multi-table `INNER`, `LEFT`, and `FULL OUTER` JOINs, subqueries, and Window Functions (`ROW_NUMBER()`, `RANK()`, `LEAD()`, `LAG()`).\n"
                f"2. **Database Design:** Normalization (1NF through 3NF), primary keys, foreign key constraints, and indexing strategies (B-Trees vs. Hash indexes).\n"
                f"3. **Transactions:** Understand ACID properties and how isolation levels prevent dirty reads and phantom reads."
            )

        elif "project" in msg_low or "build" in msg_low:
            return (
                f"Based on your profile with skills in {skill_summary}, here is an impactful project concept you can build, {student_name}:\n\n"
                f"**Project Concept:** *Full-Stack Analytical Dashboard with Role-Based Access*\n"
                f"- **Core Tech:** Connect your preferred language ({skill_summary}) with an API backend and an interactive client interface.\n"
                f"- **Key Features:** User authentication (JWT), database persistence, automated test suite, and containerized deployment with Docker.\n"
                f"- **Why Recruiters Love It:** It proves you understand full-lifecycle development: architecture, validation, security, testing, and deployment."
            )

        elif "gap" in msg_low or "missing" in msg_low or "what to learn" in msg_low:
            return (
                f"Looking at your profile against industry standards for {top_role}, here are your two highest-priority areas to address, {student_name}:\n\n"
                f"1. **Production Deployment & CI/CD:** Learning Docker containerization and automated GitHub Actions test runs will immediately put you in the top tier of applicants.\n"
                f"2. **Cloud Fundamentals:** Getting familiar with basic cloud hosting (AWS or Render/Railway) demonstrates that you understand how code runs outside of localhost."
            )

        elif "why am i suitable" in msg_low or "suitability" in msg_low:
            return (
                f"You have strong alignment for {top_role}, {student_name}!\n\n"
                f"Specifically, your verified competencies in {skill_summary} match the core prerequisite requirements cataloged in the O*NET database. "
                f"Your academic foundation in {degree} provides the theoretical grounding, and adding one production-grade portfolio project will cement your internship readiness."
            )

        # Dynamic Synthesizer for ANY OTHER general question
        else:
            clean_q = user_msg.replace("?", "").strip()
            return (
                f"Regarding your inquiry about **'{clean_q}'**, {student_name}:\n\n"
                f"As a {degree} student targeting roles in **{top_role}**, here is how you should think about this:\n\n"
                f"1. **Core Relevance:** In modern software engineering, mastering fundamentals and understanding *how systems fit together* matters far more than memorizing syntax. With your current background in {skill_summary}, exploring this will broaden your practical versatility.\n\n"
                f"2. **Actionable Implementation:** The best way to approach this is through hands-on experimentation. Try building a small proof-of-concept script or module that directly tests this concept.\n\n"
                f"3. **Connecting to Your Career Goals:** Document your learnings in a technical blog post or add it as an enhancement to your GitHub portfolio. Demonstrating curiosity and continuous learning is one of the top traits internship interviewers evaluate.\n\n"
                f"Feel free to ask for specific code examples, project architectures, or study resources on this topic!"
            )
