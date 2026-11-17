<p align="center">
  <img src="static/images/logo.svg" width="340" alt="PathMatch AI Logo" />
</p>

<h2 align="center">PathMatch AI</h2>
<p align="center">
  <b>Intelligent LLM-Powered Internship Role Recommendation & Career Guidance System</b><br>
  <i>Smart India Hackathon Innovation (SIH25034)</i><br>
  <b>Developed & Created by <a href="https://github.com/Akashkopalli">Akash Kopalli</a></b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue?logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Framework-Flask%203.1-black?logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Tests-31%20Passed-brightgreen?logo=pytest&logoColor=white" alt="Pytest Tests" />
  <img src="https://img.shields.io/badge/O*NET-2018%20SOC%20Taxonomy-orange" alt="O*NET 2018 SOC" />
  <img src="https://img.shields.io/badge/Architecture-Pure%20LLM%20Multi--Agent-purple" alt="Pure LLM" />
  <img src="https://img.shields.io/badge/Colab-Ready%20to%20Run-yellow?logo=googlecolab&logoColor=white" alt="Google Colab" />
</p>

---

## 1. Project Overview

**PathMatch AI** is a state-of-the-art, multi-agent AI career guidance and internship role recommendation platform built for the **Smart India Hackathon (SIH25034)**. College students frequently struggle to bridge the gap between classroom coding, personal projects, and standardized industry job roles.

PathMatch AI solves this challenge through **Pure Large Language Model (LLM) Reasoning** across an orchestrated 7-agent pipeline. The system audits student profiles against **72 verified technical occupations** from the official **U.S. Department of Labor O*NET 2018 SOC database**, computes honest suitability match percentages across 6 qualitative dimensions, pinpoints exact prerequisite skill gaps, and generates structured 30-60-90 day milestone roadmaps.

> [!IMPORTANT]
> **CRITICAL OCCUPATIONAL POLICY:**  
> PathMatch AI strictly evaluates and recommends **standardized occupational role categories and career readiness pathways**, NOT live commercial job postings or corporate hiring vacancies. O*NET provides occupational standards, not recruiter listings. Fictional employers, fabricated salaries, and unverified vacancies are strictly prohibited.

---

## 2. Key Capabilities & Innovations

* **Pure LLM Semantic Reasoning:** Zero reliance on legacy statistical keyword matching (TF-IDF, cosine similarity, or Bag-of-Words). Evaluations understand code context, project narratives, and transferable competencies.
* **Strict Grounded Skill Evaluation:** No hallucination of undeclared skills. Entering only foundational markup (e.g., `HTML, CSS`) awards an honest **~46%–52% Foundational Fit** for Frontend roles and accurately identifies `JavaScript, React, Git` as missing priorities. Profiles with verified languages, frameworks, and project code (e.g. Python, SQL dashboards) scale up to **80%+**.
* **Direct Official O\*NET Platform Cross-Linking:** Every recommended role card, dashboard table row, and modal specification includes direct one-click links to the official U.S. Department of Labor O*NET Online profile (`https://www.onetonline.org/link/summary/<soc_code>`).
* **Responsive, Concise Conversational Career Assistant:** Directly answers student inquiries like `"what is my role"`, `"skills needed"`, and `"is html and css enough"` with crisp, actionable advice rather than generic boilerplate essays.
* **Interactive O\*NET Knowledge Base Explorer:** Real-time search and filter interface for 72 official occupations across 10 technology domains, displaying required competencies, tech stacks, knowledge areas, and daily activities.
* **Full Dark & Light Themes with Modern Typography:** Built-in instant theme toggle (persisted via `localStorage` and synchronized with Chart.js analytics) styled with modern geometric **Plus Jakarta Sans**, **Inter**, and **JetBrains Mono** typography.
* **Multi-Provider LLM Flexibility:** Native plug-and-play support for **Groq Cloud API** (`llama-3.3-70b-versatile`), **OpenAI API** (`gpt-4o-mini`), **Ollama Local LLMs** (`llama3`, `mistral`), and an intelligent zero-cost **Demo Provider** for instant offline hackathon demonstration.
* **Google Colab Notebook:** Complete end-to-end execution script and notebook available at [`notebooks/PathMatch_AI_Colab.ipynb`](notebooks/PathMatch_AI_Colab.ipynb).

---

## 3. Strict Development Constraint: Pure LLM Reasoning

In strict compliance with the SIH25034 problem statement, **all traditional ML algorithms, vector distance metrics, and keyword-overlap scoring are strictly excluded** from the active recommendation engine:

| Strictly Excluded in Active Engine | Performed Exclusively via LLMs |
| :--- | :--- |
| ❌ TF-IDF / `TfidfVectorizer` | ✅ Natural language student profile parsing |
| ❌ Cosine similarity matrices | ✅ Skill extraction and canonical normalization |
| ❌ Sentence Transformers / Vector Embeddings | ✅ Transferable skill identification without exaggeration |
| ❌ Random Forest, SVM, Logistic Regression | ✅ O*NET occupational requirement interpretation |
| ❌ Hardcoded weighted similarity formulas | ✅ 6-dimension semantic role suitability evaluation |
| ❌ Keyword frequency matching | ✅ Comparative role ranking, skill gap audits & roadmaps |

**Python Role:** Python acts strictly as the orchestrator handling O*NET candidate retrieval from SQLite, prompt engineering, structured JSON validation, rate limiting, token tracking, and web persistence.

---

## 4. Multi-Agent System Architecture

The recommendation pipeline coordinates **7 specialized AI agents**:

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

1. **Agent 1: Student Profile Agent:** Converts raw student descriptions into verified JSON skills and projects without fabricating proficiency levels.
2. **Agent 2: Skill Intelligence Agent:** Classifies skills into *confirmed*, *related*, and *transferable* categories without artificially inflating the confirmed skills list.
3. **Agent 3: Occupational Retrieval Agent:** Fetches candidate O*NET occupations from SQLite based on domain congruence to prevent context window saturation.
4. **Agent 4: LLM Evaluation & Ranking Agent:** Evaluates candidate occupations against the 6-dimension rubric, generates comparative suitability scores (0–100), and ranks the top roles.
5. **Agent 5: Skill Gap Agent:** Conducts a strict comparative audit between confirmed skills and occupational requirements, identifying high-priority missing prerequisites.
6. **Agent 6: Learning Roadmap Agent:** Synthesizes actionable 30-, 60-, and 90-day learning roadmaps complete with mini-projects, exercises, and verified documentation links.
7. **Agent 7: Conversational Career Assistant:** Provides concise, direct conversational guidance answering specific student queries about role suitability and interview preparation.

---

## 5. Six-Dimension Evaluation Rubric

Every candidate occupation is evaluated by the LLM across six documented dimensions:

1. **Required Skill Alignment (~30%):** Direct coverage of core technical prerequisites cataloged in O*NET.
2. **Transferable Skill Alignment (~20%):** Foundational strengths (e.g. data structures, OOP) that facilitate rapid learning.
3. **Project Relevance (~20%):** Hands-on portfolio evidence and applied code implementations.
4. **Interest & Career Goal Alignment (~15%):** Synergy with declared career domains and work activities.
5. **Educational Suitability (~10%):** Degree program and academic specialization alignment.
6. **Experience Suitability (~5%):** Realistic scope and suitability for an internship or entry-level role.

---

## 6. Technology Stack

* **Backend:** Python 3.11+ / 3.14+, Flask 3.1+, SQLite3, Jinja2
* **LLM Providers Supported:**
  * **Groq Cloud API** (`llama-3.3-70b-versatile`) — Fast inference (~300 tokens/sec)
  * **OpenAI API** (`gpt-4o-mini`, `gpt-4o`) — High-precision structured JSON
  * **Ollama Local LLMs** (`llama3:8b`, `mistral`) — 100% offline local inference
  * **Intelligent Demo Provider** (`demo-agent-v1`) — Built-in deterministic multi-agent simulation
* **Frontend:** HTML5, CSS3, Bootstrap 5.3, Vanilla JavaScript, Chart.js, Font Awesome 6
* **Dataset Standards:** Official U.S. Department of Labor O*NET 2018 SOC Taxonomy (72 Occupations)
* **Testing:** Pytest (31/31 unit & integration tests passing)

---

## 7. Five Built-in Sample Student Profiles

PathMatch AI includes 5 pre-configured student profiles for instant demonstration:

1. **Rahul (Data Analytics):** Computer Science &bull; Skills: Python, SQL, Excel, Data Visualization, Statistics &bull; Project: Sales Performance Dashboard &bull; *Top Fit: Marketing Analytics Specialist / Data Scientist (80% Fit)*
2. **Ananya (Frontend & UI Design):** Computer Science &bull; Skills: HTML, CSS, JavaScript, React, Figma, Git &bull; Project: E-Commerce Web App &bull; *Top Fit: Web Developer (Frontend) / UI/UX Designer (85% Fit)*
3. **Mohit (Backend Development):** Computer Science &bull; Skills: Java, OOP, MySQL, Spring Boot, REST API &bull; Project: Microservice Backend &bull; *Top Fit: Backend Java Engineer / Enterprise Spring Boot Engineer (85% Fit)*
4. **Sneha (AI & Machine Learning):** Computer Science &bull; Skills: Python, Machine Learning, Pandas, NumPy, Scikit-learn, Matplotlib &bull; Project: Predictive Model &bull; *Top Fit: Machine Learning Engineer / Data Scientist (88% Fit)*
5. **Arjun (Network Security):** Computer Science &bull; Skills: C, C++, Computer Networks, Linux, Cybersecurity Basics, Wireshark &bull; Project: Network Packet Analyzer &bull; *Top Fit: Information Security Analyst / Network Security Engineer (85% Fit)*

---

## 8. Installation & Setup

### Prerequisites
* Python 3.11 or higher installed on your machine.
* Git (optional).

### Step 1: Open Workspace
```powershell
cd C:\Users\kopal\Downloads\pathmatchAi
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Configure your preferred LLM provider in `.env`:
```env
# Provider options: 'demo', 'groq', 'openai', or 'ollama'
LLM_PROVIDER=demo

# Groq API Key (Recommended - fast & free: https://console.groq.com/keys)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# OpenAI API Key (optional)
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

# Ollama Local (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

> **Note on Demo Mode:** If `LLM_PROVIDER=demo` or API keys are left unset, PathMatch AI automatically engages **DEMO MODE**. It simulates multi-agent reasoning offline with realistic 6-dimension scoring, zero external cost, and 100% test reliability.

### Step 3: Populate O*NET Dataset & Database
```powershell
python scripts/prepare_dataset.py
```

---

## 9. Running the Application

### Option A: Launch Web Interface (Recommended)
Start the web application:
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Option B: Run CLI End-to-End Demo
```powershell
python scripts/run_demo.py
```

### Option C: Run Google Colab Notebook
Upload [`notebooks/PathMatch_AI_Colab.ipynb`](notebooks/PathMatch_AI_Colab.ipynb) to [Google Colab](https://colab.research.google.com/) and run all cells to execute PathMatch AI in the cloud with Groq, OpenAI, or Ollama.

---

## 10. REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Web application home page |
| `GET` | `/profile` | Interactive student profile builder |
| `GET` | `/recommendations` | View evaluation results, match scores, and O*NET links |
| `GET` | `/career-assistant` | Conversational career guidance mentor |
| `GET` | `/dashboard` | Interactive O*NET Occupational Knowledge Base Explorer |
| `POST` | `/api/recommend` | Execute the full 7-agent LLM recommendation pipeline |
| `POST` | `/api/career-chat` | Interactive conversation with the Career Guidance Assistant |
| `POST` | `/api/skill-gap` | On-demand skill-gap audit for a target SOC code |
| `POST` | `/api/learning-roadmap` | Generate 30-60-90 day milestone roadmap |
| `GET` | `/api/dashboard/stats` | Aggregated dataset analytics and catalog of 72 occupations |
| `GET` | `/api/sample-profiles` | Retrieve the 5 predefined SIH sample student profiles |

---

## 11. Automated Testing & Verification

PathMatch AI includes a comprehensive automated test suite with **31 unit and integration tests** validating agents, API endpoints, SQLite schema integrity, SOC code validation, prompt injection defense, and dynamic scoring.

To run the automated tests:
```powershell
pytest -v
```

Expected output:
```
tests/test_agents.py ..........                                          [ 32%]
tests/test_api.py ...........                                            [ 67%]
tests/test_database.py ....                                              [ 80%]
tests/test_recommendations.py ......                                     [100%]

============================= 31 passed in 2.04s ==============================
```

---

## 12. Security & Guardrails

* **Prompt Injection Interception:** All user input is sanitized and constrained within `<student_input>` tags. Malicious injections (e.g. *"ignore previous instructions"*) are intercepted and rejected.
* **Strict Anti-Hallucination:** Recommended SOC codes are strictly validated against retrieved candidate records from the verified database.
* **Rate Limiting & Abuse Prevention:** In-memory sliding window rate limits protect public endpoints against flooding.
* **Zero Credential Leakage:** API credentials are read strictly from environment variables and never logged or persisted to SQLite.

---

## 13. Author & Creator

* **Developer & Author:** **Akash Kopalli**
* **GitHub Profile:** [@Akashkopalli](https://github.com/Akashkopalli)
* **Repository:** [PathMatch AI](https://github.com/Akashkopalli/pathmatchAi)
* **Email:** [kopallimani45@gmail.com](mailto:kopallimani45@gmail.com)

---

<p align="center">
  <b>PathMatch AI &bull; Smart India Hackathon (SIH25034)</b><br>
  <i>Designed and developed by <b>Akash Kopalli</b> with Pure LLM Multi-Agent Intelligence.</i>
</p>
