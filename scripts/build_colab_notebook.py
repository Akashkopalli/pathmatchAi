"""Build Google Colab Notebook for PathMatch AI.

Generates notebooks/PathMatch_AI_Colab.ipynb with complete multi-LLM execution code.
"""

import json
from pathlib import Path


def create_notebook():
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# PathMatch AI — Google Colab Notebook\n",
                    "## SIH25034 — Intelligent LLM-Powered Internship Role Recommendation & Career Guidance System\n",
                    "\n",
                    "This notebook runs **PathMatch AI** end-to-end on Google Colab with all supported LLM providers:\n",
                    "1. **Groq Cloud API** (`llama-3.3-70b-versatile`) — Fast inference (~300 tokens/sec)\n",
                    "2. **OpenAI API** (`gpt-4o-mini`, `gpt-4o`) — Structured JSON reasoning\n",
                    "3. **Ollama / Local LLM** (`llama3:8b`, `mistral`) — Offline local model on Colab GPU/CPU\n",
                    "4. **Intelligent Demo Provider** (`demo-agent-v1`) — Zero-cost deterministic multi-agent simulation\n",
                    "\n",
                    "---\n",
                    "### How to use this notebook:\n",
                    "1. **Step 1:** Run Setup to install dependencies and initialize project files.\n",
                    "2. **Step 2:** Configure your API keys (OpenAI / Groq) or choose Demo mode.\n",
                    "3. **Step 3:** Initialize the SQLite database containing 72 official O*NET 2018 SOC occupations.\n",
                    "4. **Step 4:** Execute the multi-agent LLM recommendation pipeline.\n",
                    "5. **Step 5 (Optional):** Launch the interactive Flask Web UI with a public tunnel link directly from Colab!"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 1: Environment Setup & Dependencies\n",
                    "import os, sys\n",
                    "\n",
                    "# Install required Python packages\n",
                    "!pip install -q flask flask-cors pandas pytest requests\n",
                    "\n",
                    "print('[OK] Python dependencies installed successfully.')\n",
                    "print(f'[OK] Python version: {sys.version}')\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Step 2: Configure LLM Credentials & Provider\n",
                    "Set the provider to `groq`, `openai`, `ollama`, or `demo`.\n",
                    "- Free Groq API Key: [https://console.groq.com/keys](https://console.groq.com/keys)\n",
                    "- OpenAI API Key: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 2: Configure LLM Credentials\n",
                    "import getpass\n",
                    "import os\n",
                    "\n",
                    "print('=== PathMatch AI - LLM Provider Configuration ===')\n",
                    "\n",
                    "# 1. Groq API Key (Recommended for Colab - ultra fast & free)\n",
                    "groq_key = os.environ.get('GROQ_API_KEY', '')\n",
                    "if not groq_key:\n",
                    "    groq_key = getpass.getpass('Enter Groq API Key (press Enter to skip): ').strip()\n",
                    "if groq_key:\n",
                    "    os.environ['GROQ_API_KEY'] = groq_key\n",
                    "    os.environ['GROQ_MODEL'] = 'llama-3.3-70b-versatile'\n",
                    "\n",
                    "# 2. OpenAI API Key\n",
                    "openai_key = os.environ.get('OPENAI_API_KEY', '')\n",
                    "if not openai_key:\n",
                    "    openai_key = getpass.getpass('Enter OpenAI API Key (press Enter to skip): ').strip()\n",
                    "if openai_key:\n",
                    "    os.environ['OPENAI_API_KEY'] = openai_key\n",
                    "    os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'\n",
                    "\n",
                    "# 3. Select Active Provider: 'groq', 'openai', 'ollama', or 'demo'\n",
                    "ACTIVE_PROVIDER = 'groq' if groq_key else ('openai' if openai_key else 'demo')\n",
                    "os.environ['LLM_PROVIDER'] = ACTIVE_PROVIDER\n",
                    "\n",
                    "print(f'\\n[+] Active LLM Provider set to: {ACTIVE_PROVIDER.upper()}')\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Step 3 (Optional): Running Local Ollama inside Google Colab\n",
                    "If you wish to run a 100% local open-source LLM (e.g. `llama3` or `mistral`) inside Colab GPU without any API keys, uncomment and run the cell below."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 3 (Optional): Install and Run Ollama in Colab\n",
                    "\"\"\"\n",
                    "!curl -fsSL https://ollama.com/install.sh | sh\n",
                    "import subprocess, time\n",
                    "subprocess.Popen(['ollama', 'serve'])\n",
                    "time.sleep(3)\n",
                    "!ollama pull llama3:8b\n",
                    "os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'\n",
                    "os.environ['OLLAMA_MODEL'] = 'llama3:8b'\n",
                    "os.environ['LLM_PROVIDER'] = 'ollama'\n",
                    "print('[OK] Ollama initialized with llama3:8b model on localhost:11434')\n",
                    "\"\"\"\n",
                    "print('Ollama cell ready (uncomment to activate local Ollama in Colab).')\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Step 4: Initialize O*NET Occupational Knowledge Base\n",
                    "Loads the verified U.S. DOL O*NET 2018 SOC taxonomy dataset (72 technical occupations across 10 career domains)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 4: Initialize SQLite Database & Knowledge Base\n",
                    "from src.database.db import init_db\n",
                    "from src.services.occupation_retriever import OccupationalRetriever\n",
                    "\n",
                    "init_db('data/pathmatch.db')\n",
                    "occupations = OccupationalRetriever.get_all_occupations(limit=100)\n",
                    "print(f'[OK] Database initialized: {len(occupations)} O*NET standard occupations loaded.')\n",
                    "\n",
                    "# Display sample occupations\n",
                    "for occ in occupations[:5]:\n",
                    "    print(f'  - SOC {occ.soc_code}: {occ.title} ({occ.domain})')\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Step 5: End-to-End Multi-Agent Pipeline Execution\n",
                    "Demonstrates the 4 sequential agents:\n",
                    "1. **Profile Understanding Agent:** Converts unstructured natural language into structured skills.\n",
                    "2. **Occupational Retrieval Agent:** Queries relevant candidate roles from SQLite.\n",
                    "3. **LLM Role Evaluation & Recommendation Agent:** Evaluates candidate roles using the 6-dimension rubric ($0-100$ match score).\n",
                    "4. **Conversational Career Assistant:** Contextual interview and portfolio guidance."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 5: Multi-Agent Recommendation Engine\n",
                    "from src.llm.llm_factory import get_llm_provider\n",
                    "from src.agents.profile_agent import ProfileUnderstandingAgent\n",
                    "from src.agents.recommendation_agent import RoleRecommendationAgent\n",
                    "from src.agents.career_assistant_agent import CareerAssistantAgent\n",
                    "\n",
                    "# Sample student input (natural language)\n",
                    "sample_input = \"\"\"\n",
                    "I am an undergraduate Computer Science student proficient in Python, SQL, REST APIs, Git, and Docker.\n",
                    "I built a full-stack sales analytics microservice using Flask, PostgreSQL, and Pandas.\n",
                    "I am interested in Data Science, Machine Learning, and Backend Engineering.\n",
                    "\"\"\"\n",
                    "\n",
                    "def run_full_pipeline(provider_name):\n",
                    "    print(f'\\n{\"=\" * 75}')\n",
                    "    print(f'EVALUATING WITH LLM PROVIDER: {provider_name.upper()}')\n",
                    "    print(f'{\"=\" * 75}')\n",
                    "    \n",
                    "    provider = get_llm_provider(provider_name)\n",
                    "    print(f'[+] Active Provider: {provider.__class__.__name__} | Model: {provider.model}')\n",
                    "    \n",
                    "    # Agent 1: Profile Understanding\n",
                    "    print('\\n--- [Agent 1: Profile Understanding Agent] ---')\n",
                    "    profile_agent = ProfileUnderstandingAgent(llm_provider=provider)\n",
                    "    parsed_profile = profile_agent.analyze_natural_language(sample_input)\n",
                    "    skills = [s['name'] for s in parsed_profile.get('skills', [])]\n",
                    "    print('Extracted Verified Skills:', skills)\n",
                    "    print('Extracted Career Goals:', parsed_profile.get('career_goals', []))\n",
                    "    \n",
                    "    # Agent 3: Occupational Knowledge Retrieval\n",
                    "    print('\\n--- [Agent 3: Occupational Retrieval Agent] ---')\n",
                    "    candidates = OccupationalRetriever.retrieve_candidates_for_profile(\n",
                    "        skills=skills,\n",
                    "        interests=parsed_profile.get('interests', []),\n",
                    "        career_goals=parsed_profile.get('career_goals', []),\n",
                    "        limit=10\n",
                    "    )\n",
                    "    print(f'Retrieved {len(candidates)} candidate O*NET occupations for LLM scoring.')\n",
                    "    \n",
                    "    # Agent 4: LLM Role Evaluation & Recommendation\n",
                    "    print('\\n--- [Agent 4: LLM Role Evaluation Agent (6-Dimension Rubric)] ---')\n",
                    "    rec_agent = RoleRecommendationAgent(llm_provider=provider)\n",
                    "    eval_result = rec_agent.evaluate_and_rank_roles(\n",
                    "        student_profile={\n",
                    "            'name': 'Student Candidate',\n",
                    "            'degree': 'Computer Science',\n",
                    "            'skills': parsed_profile.get('skills', []),\n",
                    "            'projects': parsed_profile.get('projects', []),\n",
                    "            'interests': parsed_profile.get('interests', []),\n",
                    "            'career_goals': parsed_profile.get('career_goals', [])\n",
                    "        },\n",
                    "        candidate_occupations=[occ.to_dict() for occ in candidates],\n",
                    "        top_k=4\n",
                    "    )\n",
                    "    \n",
                    "    recommendations = eval_result.get('recommendations', [])\n",
                    "    for rec in recommendations:\n",
                    "        print(f'\\n[Role #{rec.get(\"rank_order\")}] {rec.get(\"occupation_title\")} (SOC: {rec.get(\"soc_code\")})')\n",
                    "        print(f'  Match Score: {rec.get(\"match_score\")}/100 [{rec.get(\"confidence\")} Fit]')\n",
                    "        print(f'  Matching Skills: {rec.get(\"matching_skills\")}')\n",
                    "        print(f'  Missing Upskilling Gaps: {rec.get(\"missing_skills\")}')\n",
                    "        print(f'  Rationale: {rec.get(\"reason\")}')\n",
                    "        \n",
                    "    # Agent 7: Conversational Career Mentor\n",
                    "    if recommendations:\n",
                    "        top_title = recommendations[0].get('occupation_title')\n",
                    "        print(f'\\n--- [Agent 7: Conversational Career Mentor for {top_title}] ---')\n",
                    "        mentor = CareerAssistantAgent(llm_provider=provider)\n",
                    "        mentor_resp = mentor.generate_response(\n",
                    "            message=f'What are the top 3 interview questions I should prepare for {top_title}?',\n",
                    "            student_profile={'name': 'Student Candidate', 'skills': parsed_profile.get('skills', [])},\n",
                    "            recommendations=recommendations,\n",
                    "            conversation_history=[]\n",
                    "        )\n",
                    "        print(mentor_resp.get('reply'))\n",
                    "\n",
                    "# Execute with active provider\n",
                    "run_full_pipeline(os.environ.get('LLM_PROVIDER', 'demo'))\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Step 6: Side-by-Side Comparison of All Supported LLMs\n",
                    "Compares output between available providers (`groq`, `openai`, `ollama`, `demo`)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 6: Benchmark Multiple Providers Side-by-Side\n",
                    "providers = ['demo']\n",
                    "if os.environ.get('GROQ_API_KEY'):\n",
                    "    providers.append('groq')\n",
                    "if os.environ.get('OPENAI_API_KEY'):\n",
                    "    providers.append('openai')\n",
                    "if os.environ.get('OLLAMA_BASE_URL'):\n",
                    "    providers.append('ollama')\n",
                    "\n",
                    "print(f'Available LLM Providers: {providers}')\n",
                    "for p in providers:\n",
                    "    run_full_pipeline(p)\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Step 7: Launch Full Web UI with Public Tunnel from Colab\n",
                    "Starts the Flask server inside Colab and exposes it via `localtunnel` so you can open the complete PathMatch AI website in your browser!"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 7: Launch Web App with Public Tunnel\n",
                    "import subprocess, time, urllib.request\n",
                    "\n",
                    "# 1. Install localtunnel\n",
                    "!npm install -g localtunnel > /dev/null 2>&1\n",
                    "\n",
                    "# 2. Get Tunnel Password (Colab public IP)\n",
                    "public_ip = urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip()\n",
                    "print('=' * 65)\n",
                    "print(f'LOCALTUNNEL PASSWORD: {public_ip}')\n",
                    "print('(Enter this IP if prompted on the tunnel URL)')\n",
                    "print('=' * 65)\n",
                    "\n",
                    "# 3. Start Flask app\n",
                    "flask_p = subprocess.Popen(['python', 'app.py'])\n",
                    "time.sleep(3)\n",
                    "\n",
                    "# 4. Start localtunnel on port 5000\n",
                    "tunnel_p = subprocess.Popen(['lt', '--port', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)\n",
                    "for line in tunnel_p.stdout:\n",
                    "    if 'your url is:' in line.lower():\n",
                    "        print(f'\\n[+] LIVE PUBLIC URL: {line.strip()}')\n",
                    "        print(f'    Password: {public_ip}\\n')\n",
                    "        break\n"
                ]
            }
        ],
        "metadata": {
            "accelerator": "GPU",
            "colab": {
                "provenance": []
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }

    out_path = Path("notebooks/PathMatch_AI_Colab.ipynb")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    print(f"Successfully generated {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    create_notebook()

