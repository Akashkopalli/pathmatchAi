import os
import sys
import time
import subprocess
import threading
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from src.services.profile_service import ProfileService

SCREENSHOTS_DIR = BASE_DIR / "Project_Screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print(f"Using browser at: {CHROME_PATH}")

app = create_app()

def run_server():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait for server to come up
time.sleep(2)
for i in range(15):
    try:
        res = urllib.request.urlopen("http://127.0.0.1:5000/")
        if res.status == 200:
            print("Flask server is up and responsive on http://127.0.0.1:5000!")
            break
    except Exception as e:
        time.sleep(1)

# Seed student profile
sample_profile = {
    "name": "Akash Kopalli",
    "email": "kopalliakash45@gmail.com",
    "education_level": "Undergraduate",
    "degree_major": "Computer Science & Engineering",
    "institution": "Lovely Professional University",
    "graduation_year": 2026,
    "skills": ["Python", "SQL", "Flask", "Machine Learning", "Git", "REST APIs", "Data Structures"],
    "courses": ["Data Structures & Algorithms", "Database Management Systems", "Artificial Intelligence", "Web Development"],
    "projects": [
        {
            "title": "PathMatch AI - Multi-Agent Career Recommendation Engine",
            "description": "Architected an intelligent 7-agent LLM reasoning pipeline to audit student profiles against 72 O*NET occupations without statistical keyword matching.",
            "technologies": ["Python", "Flask", "SQLite", "LLMs", "Prompt Engineering"]
        }
    ],
    "experience": [],
    "preferred_roles": ["Machine Learning Engineer", "Software Developer", "Data Scientist"],
    "target_domains": ["Artificial Intelligence", "Software Engineering"],
    "natural_input": "3rd-year CSE undergraduate with hands-on expertise in Python, SQL, REST APIs, machine learning concepts, and multi-agent system design."
}

student_id = ProfileService.save_or_update_student(sample_profile)
print(f"Seeded student profile with ID: {student_id}")

pages = [
    {
        "url": "http://127.0.0.1:5000/",
        "output": SCREENSHOTS_DIR / "FIG_1_Homepage.png",
        "name": "FIG. 1: Main Landing & System Gateway"
    },
    {
        "url": "http://127.0.0.1:5000/profile",
        "output": SCREENSHOTS_DIR / "FIG_2_Profile_Input.png",
        "name": "FIG. 2: Comprehensive Student Profile & Competency Ingestion Interface"
    },
    {
        "url": f"http://127.0.0.1:5000/recommendations?student_id={student_id}",
        "output": SCREENSHOTS_DIR / "FIG_3_Role_Recommendations.png",
        "name": "FIG. 3: Pure LLM Occupational Recommendation & Match Evaluation Cards"
    },
    {
        "url": "http://127.0.0.1:5000/dashboard",
        "output": SCREENSHOTS_DIR / "FIG_4_ONET_Analytics_Dashboard.png",
        "name": "FIG. 4: O*NET 2018 SOC Intelligence Dashboard & Knowledge Base Explorer"
    }
]

for p in pages:
    abs_out = str(p["output"].resolve())
    print(f"Capturing screenshot: {p['name']} -> {p['output'].name}")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--screenshot={abs_out}",
        "--window-size=1400,900",
        "--hide-scrollbars",
        "--virtual-time-budget=6000",
        p["url"]
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        time.sleep(1)
        if p["output"].exists() and p["output"].stat().st_size > 1000:
            print(f"  [SUCCESS] Captured: {p['output'].name} ({p['output'].stat().st_size} bytes)")
        else:
            print(f"  [WARNING] Retrying with legacy --headless flag for {p['output'].name}...")
            cmd[1] = "--headless"
            subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            time.sleep(1)
            if p["output"].exists() and p["output"].stat().st_size > 1000:
                print(f"  [SUCCESS] Captured: {p['output'].name} ({p['output'].stat().st_size} bytes)")
            else:
                print(f"  [ERROR] Could not capture {p['output'].name}")
    except Exception as exc:
        print(f"  [ERROR] {exc}")

print("\nScreenshot capture process finished.")
