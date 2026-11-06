# PathMatch AI
### Intelligent LLM-Powered Internship Role Recommendation and Career Guidance System
**Smart India Hackathon Innovation (SIH25034)**

---

## 1. Project Introduction
**PathMatch AI** is an intelligent, multi-agent AI career guidance and internship role recommendation platform. College students often struggle to identify suitable internship roles because they do not understand how their technical skills, academic coursework, and portfolio projects map to standardized occupational requirements.

PathMatch AI solves this challenge by leveraging **Pure Large Language Model (LLM) Reasoning** across a 7-agent pipeline. The system evaluates a student's profile against the official **U.S. Department of Labor O*NET occupational database**, ranks suitable occupational categories, conducts detailed skill-gap audits, and creates actionable 30-, 60-, and 90-day learning roadmaps.

> [!IMPORTANT]
> **CRITICAL OCCUPATIONAL POLICY:**  
> PathMatch AI recommends **occupational role categories and career readiness pathways**, NOT live hiring vacancies or corporate postings. O*NET provides occupational standards, not live job listings. Fictional employers, fake salaries, and unverified vacancy numbers are strictly prohibited.

---

## 2. Problem Statement & Solution

### The Problem
- **Ambiguous Role Titles:** Students struggle to differentiate between roles such as *Data Scientist* vs. *Business Intelligence Analyst* or *DevOps Engineer* vs. *SRE*.
- **Overreliance on Keyword Overlap:** Traditional recruitment algorithms look for exact word matches (TF-IDF, Bag-of-Words), penalizing students who describe projects in natural language.
- **Unclear Skill Gaps:** Students know what they know, but lack clarity on what prerequisite tools they are missing for their target internship.
- **Lack of Actionable Roadmaps:** Generic online advice does not provide structured, timeline-based learning milestones.

### The Solution
PathMatch AI implements a **Pure LLM Multi-Agent System**:
1. **Understands Natural-Language Resumes & Profiles:** Parses technical stacks and infers project competencies without exaggerating capabilities.
2. **Identifies Transferable Skills:** Recognizes how foundational strengths (e.g., OOP in Java) bridge into adjacent domains (e.g., Go microservices or C++ systems).
3. **Applies a 6-Dimension Suitability Rubric:** Synthesizes comparative suitability scores from 0 to 100 based on verified occupational requirements.
4. **Delivers Concrete 30-60-90 Day Roadmaps:** Outlines specific topics, practical drills, mini-projects, and verified educational resources.
5. **Provides Conversational Career Guidance:** Offers interactive chat where students can discuss role fit and interview readiness with an empathetic AI mentor.

---

## 3. Core Development Principle: Pure LLM Recommendation

In strict accordance with SIH25034 guidelines, **traditional ML and statistical vector distance algorithms are strictly excluded** from the recommendation engine:

| Strictly Prohibited in Active Engine | Performed Exclusively by LLMs |
| :--- | :--- |
| ❌ TF-IDF / `TfidfVectorizer` | ✅ Natural language student profile parsing |
| ❌ Cosine similarity matrices | ✅ Skill extraction and canonical normalization |
| ❌ Sentence Transformers / Vector Embeddings | ✅ Transferable skill identification without exaggeration |
| ❌ Random Forest, SVM, Logistic Regression | ✅ O*NET occupational requirement interpretation |
| ❌ Hardcoded weighted similarity formulas | ✅ 6-dimension semantic role suitability evaluation |
| ❌ Traditional keyword overlap ranking | ✅ Comparative role ranking, skill gaps & roadmaps |

**Python Role:** Acts strictly as the orchestrator handling data retrieval from SQLite, prompt formatting, JSON validation, rate limiting, token tracking, and web persistence.

---

## 4. Multi-Agent Architecture (PathMatch Agent System)

The system consists of seven specialized AI agents:

```
                      +-----------------------------+
                      |   Student Profile Input     |
                      | (Natural Text or Form Data) |
                      +--------------+--------------+
                                     |
                                     v
                  +-----------------------------------+
                  | AGENT 1: Student Profile Agent   |
                  | (Skill Extraction & Normalization)|
                  +------------------+----------------+
                                     |
                                     v
                  +-----------------------------------+
                  | AGENT 2: Skill Intelligence Agent|
                  |  (Confirmed vs. Transferable)    |
                  +------------------+----------------+
                                     |
                                     v
                  +-----------------------------------+
                  | AGENT 3: Occupational Retrieval   |
                  | (Queries SQLite for O*NET records)|
                  +------------------+----------------+
                                     |
                                     v
                  +-----------------------------------+
                  | AGENT 4: LLM Evaluation & Ranking |
                  |  (Pure LLM 6-Dimension Rubric)    |
                  +------------------+----------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
    +-------------------------------+ +-------------------------------+
    | AGENT 5: Skill Gap Agent     | | AGENT 6: Learning Roadmap     |
    | (Missing Prerequisite Audit) | | (30-60-90 Day Milestone Plan) |
    +-------------------------------+ +-------------------------------+
                    |                                 |
                    +----------------+----------------+
                                     |
                                     v
                  +-----------------------------------+
                  | AGENT 7: Conversational Assistant |
                  | (Context-Aware Mentorship Chat)  |
                  +-----------------------------------+
```

1. **Agent 1: Student Profile Understanding Agent:** Converts unstructured student descriptions into structured JSON. Distinguishes explicit skills from inferred skills without fabricating proficiency levels.
2. **Agent 2: Skill Intelligence Agent:** Classifies skills into *confirmed*, *related*, *transferable*, *requiring verification*, and *skills to learn*. Related skills are **never** automatically promoted to confirmed student skills.
3. **Agent 3: Occupational Knowledge Retrieval Agent:** Queries SQLite database for candidate O*NET records based on domains and tags, supplying candidates as prompt context to prevent context window flooding.
4. **Agent 4: LLM Role Evaluation and Recommendation Agent:** Evaluates candidate occupations against the 6-dimension rubric, generates comparative suitability scores (0–100), and ranks top occupations.
5. **Agent 5: Skill Gap Analysis Agent:** Identifies missing essential tools, additional frameworks, and transferable capabilities with explicit prioritization.
6. **Agent 6: Learning Roadmap Agent:** Synthesizes tailored 30-, 60-, and 90-day milestone roadmaps with concrete exercises, portfolio mini-projects, and verified educational resources.
7. **Agent 7: Conversational Career Assistant:** Interactive conversational mentor retaining profile, recommendation history, and skill gaps in the database.

---

## 5. Six-Dimension Evaluation Rubric

Every candidate occupation is evaluated by the LLM across six documented dimensions:

1. **Required Skill Alignment (~30%):** Direct overlap with core occupational requirements in O*NET.
2. **Transferable Skill Alignment (~20%):** Foundational competencies (e.g. OOP, algorithms) that facilitate learning.
3. **Project Relevance (~20%):** Tangible evidence demonstrated in portfolio projects.
4. **Interest Alignment (~15%):** Synergy with declared career domains and daily work activities.
5. **Educational Suitability (~10%):** Degree program and specialization match with entry requirements.
6. **Experience Suitability (~5%):** Realistic scope for an internship / entry-level role.

> [!NOTE]
> **Scoring Clarification:** A match score of 88/100 represents an AI-generated comparative suitability ranking. It is **not** a statistically validated hiring probability or guaranteed offer.

---

## 6. Technology Stack

- **Backend:** Python 3.11+ / 3.14+, Flask 3.1+, SQLite3 (standard library), Jinja2
- **LLM Integrations:**
  - OpenAI API (`gpt-4o`, `gpt-4o-mini`)
  - Groq API (`llama-3.3-70b-versatile`, `mixtral-8x7b-32768`)
  - Ollama Local (`llama3`, `mistral`)
  - Built-in High-Fidelity **Demo Provider** (clearly labeled offline simulation for zero-credential hackathon presentation)
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Vanilla JavaScript, Chart.js, Font Awesome 6
- **Data Source:** Official U.S. Department of Labor O*NET 2018 SOC Taxonomy
- **Testing:** Pytest (100% automated offline suite, no paid API tokens required)

---

## 7. Five Built-in Sample Student Profiles

PathMatch AI includes five pre-configured profiles for instant demonstration:

1. **Rahul:** Computer Science (Data Analytics) &bull; Skills: Python, SQL, Excel, Data Visualization, Statistics &bull; Interests: Data Analysis, Business Insights &bull; *Top Match: Business Intelligence Analyst / Data Scientist*
2. **Ananya:** Computer Science (Web & UI Design) &bull; Skills: HTML, CSS, JavaScript, React, Figma, Git &bull; Interests: Frontend Development, UI Design &bull; *Top Match: Web Developer (Frontend) / UI/UX Designer*
3. **Mohit:** Computer Science (Software Systems) &bull; Skills: Java, OOP, MySQL, Spring Boot, REST API &bull; Interests: Backend Development &bull; *Top Match: Backend Java Engineer / Enterprise Spring Boot Engineer*
4. **Sneha:** Computer Science / AI &bull; Skills: Python, Machine Learning, Pandas, NumPy, Scikit-learn, Matplotlib &bull; Interests: Artificial Intelligence, Data Science &bull; *Top Match: Machine Learning Engineer / Data Scientist*
5. **Arjun:** Computer Science (Network Security) &bull; Skills: C, C++, Computer Networks, Linux, Cybersecurity Basics, Wireshark &bull; Interests: Networking, Cybersecurity &bull; *Top Match: Information Security Analyst / Network Security Engineer*

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.11 or higher installed on your machine.
- Git (optional).

### Step 1: Clone or Open Workspace
Open the project directory in VS Code or Terminal:
```powershell
cd C:\Users\kopal\Downloads\pathmatchAi
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Edit `.env` to configure your preferred LLM provider:
```env
# Provider options: 'demo', 'openai', 'groq', or 'ollama'
LLM_PROVIDER=demo

# OpenAI API Key (optional)
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

# Groq API Key (optional)
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama Local (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

> **Note on Demo Mode:** If `LLM_PROVIDER=demo` or API keys are not provided, PathMatch automatically activates **DEMO MODE**. The application displays a visible demo badge and uses realistic multi-agent simulations without failing or making external requests.

### Step 3: Prepare the Dataset & SQLite Database
Run the automated preparation script to populate O*NET occupations and seed sample profiles:
```powershell
python scripts/prepare_dataset.py
```

---

## 9. How to Run the Application

### Option A: Launch Web Interface (Recommended)
Start the Flask web server:
```powershell
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### Option B: Run the CLI Demonstration
Execute the full multi-agent pipeline across all 5 sample profiles directly in your terminal:
```powershell
python scripts/run_demo.py
```

### Option C: Run the Profile Benchmark Report
Compute Precision@5 and MRR evaluation metrics and regenerate `reports/evaluation.md`:
```powershell
python scripts/evaluate_profiles.py
```

---

## 10. REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status and provider metadata |
| `POST` | `/api/profile/analyze` | Parse natural-language text into structured skills & projects |
| `POST` | `/api/recommend` | Execute the full multi-agent recommendation pipeline |
| `POST` | `/api/skill-gap` | On-demand skill-gap audit for a target SOC code |
| `POST` | `/api/learning-roadmap` | Generate 30-60-90 day milestone roadmap |
| `POST` | `/api/career-chat` | Engage in conversational guidance with Career Assistant |
| `GET` | `/api/sample-profiles` | Retrieve the 5 predefined SIH sample student profiles |
| `GET` | `/api/recommendations/history`| List historical recommendation runs |
| `GET` | `/api/recommendations/<id>` | Full details of a specific recommendation run |
| `GET` | `/api/occupations` | Browse the O*NET occupational database |

---

## 11. Testing & Verification

PathMatch AI includes a comprehensive automated test suite with **29 tests** covering database schemas, all 7 agents, API endpoints, SOC validation, prompt injection defense, and the 5 sample profiles.

To run the automated tests:
```powershell
pytest -v
```

Expected output:
```
tests/test_agents.py ...........                                 [ 34%]
tests/test_api.py ..........                                     [ 68%]
tests/test_database.py ...                                       [ 79%]
tests/test_recommendations.py ......                             [100%]

============================= 29 passed in 0.55s ==============================
```

---

## 12. Security & Guardrails

- **Prompt Injection Defense:** Input text is sanitized and passed through delimiter boundaries `<student_input>`. Prompt injection attempts (e.g. "ignore previous instructions") are detected and neutralized.
- **Strict Anti-Hallucination:** Recommended SOC codes are validated strictly against retrieved candidate records.
- **In-Memory Rate Limiting:** Protects endpoints against request flooding.
- **No Stored Credentials:** API keys are read strictly from environment variables and never logged or written to SQLite.

---

## 13. Future Scope

1. **Resume PDF/DOCX Parsing:** Native extraction from uploaded resumes.
2. **Direct LMS Integration:** Connect roadmaps to Coursera, edX, and university LMS progress trackers.
3. **College Administration Analytics:** Multi-tenant dashboard for university placement cells to analyze cohort skill gaps across departments.
4. **Multilingual Guidance:** Conversational career mentorship in regional Indian languages via localized LLM prompts.

---

**Developed for Smart India Hackathon (SIH25034)**  
*Pure LLM Multi-Agent Career Guidance and Internship Role Recommendation System.*

