# PathMatch AI — Comprehensive Project Study Guide & Technical Report

**Creator / Author:** Akash Kopalli  
**Project:** PathMatch AI (SIH25034 — Smart India Hackathon Innovation)  
**System Type:** Pure LLM Multi-Agent Internship Role Recommendation & Career Guidance System  
**Dataset Grounding:** Official U.S. Department of Labor (DOL) O*NET 2018 SOC Taxonomy  

---

## Executive Summary: How to Describe This Project in 60 Seconds

> *"PathMatch AI is an intelligent multi-agent career guidance system that bridges the gap between student academic projects and standardized industry roles. Instead of using traditional keyword-matching or vector similarity algorithms (TF-IDF, cosine similarity), PathMatch AI relies strictly on **Pure LLM Multi-Agent Reasoning** across 7 specialized AI agents. It evaluates student profiles against 72 verified occupations from the official U.S. Department of Labor O*NET database across a 6-dimension evaluation rubric, conducts precision skill-gap audits, builds personalized 30-60-90 day milestone roadmaps, and provides responsive career guidance. The system supports Groq, OpenAI, Ollama, and an offline zero-cost Demo mode."*

---

## 1. Everything About the LLMs Used

### A. The 4 Supported LLM Providers

| Provider | Model Used | Inference Type | Speed / Throughput | Cost | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Groq Cloud API** | `llama-3.3-70b-versatile` | Cloud (LPU hardware) | ~250–350 tokens/sec (ultra-fast) | Free tier available | Recommended cloud provider for production & hackathon presentations |
| **OpenAI API** | `gpt-4o-mini` / `gpt-4o` | Cloud API | ~60–80 tokens/sec | Paid API credits | High-precision structured JSON reasoning & complex edge cases |
| **Ollama Local** | `llama3:8b` / `mistral` | Local host (GPU/CPU) | Depends on machine hardware | 100% Free & Offline | Air-gapped, privacy-sensitive environments |
| **Intelligent Demo Provider** | `demo-agent-v1` | Built-in Python simulation | Instant (~120ms simulated latency) | Zero cost, no API keys | Guaranteed 100% reliable offline testing & demonstration |

---

### B. How LLMs are Used: The 7-Agent Architecture

PathMatch AI does not use a single monolithic prompt. Instead, it divides responsibilities into **7 specialized agents** to prevent context window saturation, enforce output formatting, and eliminate hallucinations:

```
[Student Profile / Text] 
         │
         ▼
 ┌───────────────┐
 │    AGENT 1    │  Student Profile Understanding Agent
 │               │  • Extracts skills, proficiency, and project evidence into JSON
 └───────┬───────┘
         │
         ▼
 ┌───────────────┐
 │    AGENT 2    │  Skill Intelligence Agent
 │               │  • Identifies confirmed vs. related vs. transferable skills
 └───────┬───────┘
         │
         ▼
 ┌───────────────┐
 │    AGENT 3    │  Occupational Knowledge Retrieval Agent
 │               │  • Queries SQLite to retrieve candidate O*NET records
 └───────┬───────┘
         │
         ▼
 ┌───────────────┐
 │    AGENT 4    │  LLM Role Evaluation & Ranking Agent (Core Engine)
 │               │  • Evaluates candidates against 6-dimension rubric (0–100 score)
 └───────┬───────┘
         │
         ├───────────────────────────────┐
         ▼                               ▼
 ┌───────────────┐               ┌───────────────┐
 │    AGENT 5    │ Skill Gap     │    AGENT 6    │ Learning Roadmap
 │               │ Audit Agent   │               │ Agent (30-60-90 days)
 └───────┬───────┘               └───────┬───────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │    AGENT 7    │ Conversational Career Assistant
                 │               │ • Interactive mentoring chat
                 └───────────────┘
```

#### Detailed Breakdown of Each Agent:

1. **Agent 1: Student Profile Understanding Agent (`src/agents/profile_agent.py`)**
   * **Task:** Takes raw natural language (e.g. *"I am a 3rd year CS student skilled in HTML and CSS"*) and converts it into validated structured JSON.
   * **Key Rule:** Never invents or assumes undeclared skills. If a student only specifies HTML and CSS, only HTML and CSS are extracted.

2. **Agent 2: Skill Intelligence Agent (`src/agents/skill_intelligence_agent.py`)**
   * **Task:** Categorizes skills into:
     * *Confirmed Skills:* Explicitly claimed and verified.
     * *Related Skills:* Natural ecosystem peers (e.g., HTML/CSS relates to semantic tags and responsive design).
     * *Transferable Skills:* Strengths that bridge across domains (e.g., OOP logic or problem decomposition).
     * *Skills Requiring Verification:* Incomplete claims requiring project proof.
   * **Key Rule:** Related skills are **never** promoted to confirmed skills.

3. **Agent 3: Occupational Knowledge Retrieval Agent (`src/agents/occupation_agent.py`)**
   * **Task:** Performs a pre-filtering query against the SQLite database (`data/pathmatch.db`) to select 10–12 candidate O*NET occupations based on domain congruence.
   * **Purpose:** Prevents prompt context overflow by sending only relevant candidate roles to the LLM evaluator.

4. **Agent 4: LLM Role Evaluation & Ranking Agent (`src/agents/recommendation_agent.py`)**
   * **Task:** The core brain of the platform. Evaluates candidate occupations against the student profile using a strict 6-dimension evaluation rubric:
     1. *Required Skill Alignment (~30%):* Direct coverage of O*NET core skills.
     2. *Transferable Skill Alignment (~20%):* Foundational abilities bridging the learning curve.
     3. *Project Evidence (~20%):* Tangible code proof from portfolio projects.
     4. *Interest Alignment (~15%):* Match with student's career aspirations.
     5. *Educational Suitability (~10%):* Degree program compatibility.
     6. *Experience Scope (~5%):* Realistic suitability for an internship / entry-level role.
   * **Output:** Ranked list of top roles with comparative match scores (0–100%), verified matching skills, missing skills, and detailed comparative reasoning.

5. **Agent 5: Skill Gap Analysis Agent (`src/agents/skill_gap_agent.py`)**
   * **Task:** Compares confirmed student skills with the target occupation's requirements to produce a prioritized gap audit:
     * *Missing Essential Skills (High Priority):* Prerequisite tools without which internship performance is blocked.
     * *Additional Recommended Skills (Medium Priority):* Competitive advantage toolchains.
     * *Practical Improvement Actions:* Clear recommendations on what to build.

6. **Agent 6: Learning Roadmap Agent (`src/agents/roadmap_agent.py`)**
   * **Task:** Synthesizes a structured 30-, 60-, and 90-day learning curriculum tailored to the top recommended role:
     * *30-Day Milestone:* Foundation & core prerequisites.
     * *60-Day Milestone:* Frameworks, intermediate tooling & containerization.
     * *90-Day Milestone:* Capstone portfolio project with live deployment.

7. **Agent 7: Conversational Career Assistant (`src/agents/career_assistant_agent.py`)**
   * **Task:** Context-aware interactive mentor. Retains conversation history, active student skills, latest recommendations, and skill gaps in SQLite to answer career questions with direct, concise advice.

---

## 2. API Keys: What They Are, Where They Live, and How They Are Configured

### A. The Environment Configuration File (`.env`)
API credentials are stored in `.env` located at the **root directory** (`c:\Users\kopal\Downloads\pathmatchAi\.env`).

```env
# Active provider: 'demo', 'groq', 'openai', or 'ollama'
LLM_PROVIDER=demo

# Groq Cloud API (Recommended for live LLM: ultra-fast & free at https://console.groq.com/keys)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# OpenAI API (Optional: https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Ollama Local (Optional: http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### B. Zero-Dependency Custom `.env` Loader (`config.py`)
Rather than relying on third-party libraries (like `python-dotenv`), PathMatch AI implements its own `.env` parser inside `config.py`:

```python
def load_dotenv_custom(dotenv_path=None):
    if dotenv_path is None:
        dotenv_path = Path(__file__).resolve().parent / ".env"
    if not dotenv_path.exists():
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = val
```

### C. Automatic Demo Mode Fallback (Graceful Degradation)
If no API keys are provided or if `LLM_PROVIDER=demo`, the application does **not** crash. Instead, `config.py` evaluates:

```python
@property
def is_demo_mode(self) -> bool:
    provider = self.LLM_PROVIDER
    if provider == "demo":
        return True
    if provider == "openai" and not self.OPENAI_API_KEY:
        return True
    if provider == "groq" and not self.GROQ_API_KEY:
        return True
    return False
```
When active:
* The web UI displays a top yellow banner: `DEMO MODE ACTIVE: Pure LLM agent reasoning simulated offline`.
* Requests are handled by `DemoProvider` (`src/llm/demo_provider.py`), executing dynamic set intersection, 6-dimension scoring, and accurate gap analysis with zero external cost.

---

## 3. Dataset: File Location, Origin & Database Structure

### A. Dataset File Locations

| File Path | Description |
| :--- | :--- |
| `data/pathmatch.db` | **Primary SQLite database** storing occupations, student profiles, recommendations, skill gaps, roadmaps, and chat sessions. |
| `data/onet_occupations.json` | Standalone JSON backup of the 72 cataloged O*NET occupations. |
| `scripts/prepare_dataset.py` | Automated dataset ingestion, validation, and database seeding script. |

---

### B. Where Was the Dataset Downloaded From?

* **Official Source:** U.S. Department of Labor (DOL) Employment and Training Administration — **O\*NET Online** (`https://www.onetonline.org`).
* **Taxonomy Standard:** **O\*NET 2018 SOC Taxonomy** (Standard Occupational Classification).
* **Scope:** 72 specialized technical computing occupations across 10 distinct domains:
  1. *Data Science & Artificial Intelligence*
  2. *Software Engineering & Systems*
  3. *Web & Mobile Development*
  4. *Cybersecurity & Information Assurance*
  5. *Cloud Computing & DevOps*
  6. *Database Administration & Data Engineering*
  7. *Quality Assurance & Software Testing*
  8. *Computer Systems & Networking*
  9. *Product Management & Technical Analysis*
  10. *Human-Computer Interaction & UI/UX Design*

---

### C. SQLite Schema Architecture (`src/database/models.py`)

The SQLite database utilizes 8 relational tables:

```
┌──────────────────┐       ┌──────────────────────┐
│     students     │◄──────┤    student_skills    │
└────────┬─────────┘       └──────────────────────┘
         │                 ┌──────────────────────┐
         ├─────────────────┤   student_projects   │
         │                 └──────────────────────┘
         ▼
┌──────────────────────┐   ┌──────────────────────┐
│ recommendation_runs  │◄──┤   recommendations    │
└────────┬─────────────┘   └──────────┬───────────┘
         │                            │
         ├────────────────┐           │
         ▼                ▼           ▼
┌────────────────┐ ┌──────────────┐ ┌─────────────┐
│   skill_gaps   │ │learning_road-│ │ occupations │
└────────────────┘ │    maps      │ └─────────────┘
                   └──────────────┘
```

1. **`occupations`**: Stores the 72 O*NET standards with `soc_code`, `title`, `description`, `domain`, `education_level`, `required_skills_json`, `technology_skills_json`, `knowledge_areas_json`, `work_activities_json`.
2. **`students`**: Stores student profile, degree, specialization, and career intentions.
3. **`student_skills`**: Stores individual skills with verification status (`confirmed`, `source`).
4. **`student_projects`**: Stores portfolio projects with technologies used and descriptions.
5. **`recommendation_runs`**: Records run metadata, model used, prompt/completion tokens, and timestamp.
6. **`recommendations`**: Stores evaluated roles with `match_score`, `matching_skills_json`, `missing_skills_json`, and `reason`.
7. **`skill_gaps`**: Stores prioritized missing essential and recommended tools.
8. **`learning_roadmaps`**: Stores structured 30-, 60-, and 90-day milestone curriculums.

---

## 4. End-to-End Implementation Walkthrough

Here is the exact lifecycle of a recommendation request:

```
[1. User Input]  ──>  [2. Validation]  ──>  [3. Agent 1 & 2]  ──>  [4. DB Retrieval]
                                                                         │
                                                                         ▼
[8. Web UI/Chat] ◄──  [7. DB Commit]   ◄──  [6. Agent 5 & 6]  ◄──  [5. Agent 4 Evaluates]
```

1. **Step 1: Input Acquisition:**
   * Student enters details on `/profile` via natural language narrative or form fields.
2. **Step 2: Profile Understanding (Agent 1 & 2):**
   * Prompt sent to LLM to extract verified technical skills.
   * Student record and confirmed skills saved to SQLite.
3. **Step 3: Candidate Retrieval (Agent 3):**
   * Python queries SQLite (`SELECT * FROM occupations WHERE domain ...`) to retrieve top 10–12 candidates.
4. **Step 4: LLM Evaluation & Ranking (Agent 4):**
   * Candidate profiles and student profile injected into `RECOMMENDATION_USER_PROMPT_TEMPLATE`.
   * LLM evaluates each candidate against the 6-dimension rubric and returns a ranked JSON list.
5. **Step 5: Skill Gap & Roadmap Generation (Agents 5 & 6):**
   * For the top-ranked role (#1), LLM conducts gap audit and generates 30-60-90 day curriculum.
6. **Step 6: Database Persistence:**
   * Run and recommendations saved to SQLite within an ACID transaction.
7. **Step 7: User Presentation:**
   * User redirected to `/recommendations?run_id=<id>` displaying suitability scores, matching/missing skills, O*NET cross-links, and career mentor prompts.

---

## 5. Main Code Files You Must Learn & Understand

### 1. `app.py` — The Application Factory
```python
def create_app(config_name: str = None) -> Flask:
    app = Flask(__name__)
    cfg = get_config(config_name)
    app.config.from_object(cfg)
    init_db(cfg.DATABASE_PATH)          # Initialize SQLite database
    app.register_blueprint(main_bp)      # UI routes (/, /dashboard, etc.)
    app.register_blueprint(profile_bp)   # Profile routes (/profile)
    app.register_blueprint(rec_bp)       # Recommendation API (/api/recommend)
    app.register_blueprint(assistant_bp) # Career Chat API (/api/career-chat)
    return app
```
* **Why it matters:** Entry point of the web app. Initializes DB tables and registers blueprints.

---

### 2. `src/services/recommendation_service.py` — The Pipeline Orchestrator
```python
def execute_recommendation_pipeline(self, profile_data, student_id=None, top_k=6):
    # Step 1: Save or synchronize student profile
    student_id = ProfileService.save_or_update_student(profile_data)
    
    # Step 2: Retrieve candidate occupations from SQLite
    candidates = OccupationalRetriever.retrieve_candidates_for_profile(...)
    
    # Step 3: Pure LLM Evaluation & Ranking (Agent 4)
    ranked_recs, rec_resp = self.recommendation_agent.evaluate_and_rank(...)
    
    # Step 4: Skill Gap & Roadmap for Top Ranked Role (Agents 5 & 6)
    gap_data, _ = self.gap_agent.analyze_gap(...)
    road_data, _ = self.roadmap_agent.generate_roadmap(...)
    
    # Step 5: Persist run and return structured result
    run_id = self._persist_recommendation_run(...)
    return {"run_id": run_id, "recommendations": ranked_recs, ...}
```
* **Why it matters:** Connects all agents together. This is the heart of the backend workflow.

---

### 3. `src/agents/recommendation_agent.py` — Agent 4 (Evaluation Agent)
* Formats candidate occupations into standardized text blocks.
* Injects student skills, degree, and projects into the prompt.
* Calls `provider.generate_json(...)` with `temperature=0.2`.
* Validates output with `validate_recommendation_output(...)`.

---

### 4. `src/llm/llm_factory.py` — LLM Factory Pattern
```python
def get_llm_provider(provider_type: str = None) -> BaseLLMProvider:
    if provider_type == "openai" and cfg.OPENAI_API_KEY:
        return OpenAIProvider(api_key=cfg.OPENAI_API_KEY, model=cfg.OPENAI_MODEL)
    elif provider_type == "groq" and cfg.GROQ_API_KEY:
        return GroqProvider(api_key=cfg.GROQ_API_KEY, model=cfg.GROQ_MODEL)
    elif provider_type == "ollama":
        return OllamaProvider(base_url=cfg.OLLAMA_BASE_URL, model=cfg.OLLAMA_MODEL)
    return DemoProvider(model="demo-agent-v1")
```
* **Why it matters:** Implements the Factory Design Pattern. Switching providers is completely decoupled from agent code.

---

### 5. `src/llm/demo_provider.py` — Intelligent Simulation Engine
* Contains the mathematical implementation of the 6-dimension rubric for offline mode:
  * Normalized exact skill matching (e.g. `HTML` matches `HTML` and `HTML5`, but never `React` or `TailwindCSS`).
  * Computes honest match scores:
    * `HTML, CSS` only ➔ **46%–52% Foundational Fit**
    * Multi-skill + projects ➔ **80%+ Strong Fit**
  * Direct, concise Career Assistant responses for `"what is my role"` and `"skills needed"`.

---

## 6. High-Yield Viva / Presentation Questions & Answers

### Q1: Why did you use Pure LLM reasoning instead of TF-IDF or Vector Embeddings?
> **Answer:**  
> *"Traditional methods like TF-IDF or cosine similarity rely on exact keyword frequencies. A student who writes 'built a web layout using Flexbox' might get a 0 score from TF-IDF because the word 'CSS' wasn't typed. Vector embeddings measure textual distance, but fail at qualitative logical reasoning—such as understanding that having Java OOP skills makes learning Go easy, or knowing that markup skills alone are insufficient for full-stack engineering. Pure LLM reasoning allows PathMatch AI to evaluate transferable capabilities, prerequisite dependencies, and project context across a documented 6-dimension rubric."*

---

### Q2: How do you prevent the LLM from hallucinating skills the student does not have?
> **Answer:**  
> *"We implement a multi-layered guardrail:  
> 1. In Agent 1 & 2 prompts, the LLM is explicitly instructed to distinguish 'confirmed skills' from 'related skills' and never promote related skills to confirmed.  
> 2. In the recommendation and gap agents, matching skills are computed as a strict intersection between verified student skills and target requirements.  
> 3. All outputs are strictly validated against JSON schemas before database storage."*

---

### Q3: What happens if a student only knows basic HTML and CSS?
> **Answer:**  
> *"Unlike naive matchers that give inflated 90%+ scores, PathMatch AI gives an honest, grounded **46%–52% Foundational Fit** for Web Developer roles. It credits HTML/CSS as verified foundational markup skills, but explicitly flags JavaScript, React, and Git as essential missing prerequisites needed to qualify for professional internships."*

---

### Q4: How is O*NET used and how does the platform link to it?
> **Answer:**  
> *"We ingested 72 specialized technical occupations from the official U.S. Department of Labor O*NET 2018 SOC taxonomy into SQLite. Every recommended role card and dashboard item includes a direct link using the official O*NET syntax: `https://www.onetonline.org/link/summary/<soc_code>` (e.g., `15-1254.00` for Web Developer), allowing students and recruiters to inspect official government occupational standards with one click."*

---

### Q5: How can this system run on Google Colab?
> **Answer:**  
> *"We provided `notebooks/PathMatch_AI_Colab.ipynb`. Colab users can run it with Groq Cloud (fastest, free API key), OpenAI, or run Ollama locally on Colab's GPU without any external API keys."*

---

## 7. Verification & Live Server Status

* **Pytest Test Suite:** All **31 automated tests** are passing (`31 passed in 2.67s`).
* **Active Host Link:** **`http://127.0.0.1:5000`** (or LAN: `http://172.22.18.230:5000`).
* **GitHub Repository:** **`https://github.com/Akashkopalli/pathmatchAi`** (Branch: `main`).

---
*Report compiled for Akash Kopalli — PathMatch AI (SIH25034)*
