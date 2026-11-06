"""PathMatch AI - Interactive CLI Demonstration Runner.

Executes the pure LLM recommendation pipeline across all 5 standard student profiles.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.db import init_db
from src.services.recommendation_service import RecommendationService
from src.services.profile_service import ProfileService

BANNER = """
================================================================================
       PATHMATCH AI — LLM INTERNSHIP ROLE RECOMMENDATION ENGINE
                      SIH25034 Innovation Showcase
================================================================================
"""


def run_demo():
    print(BANNER)
    init_db()

    data_path = Path(__file__).resolve().parent.parent / "data" / "sample_profiles.json"
    if not data_path.exists():
        print("[!] Sample profiles not found. Run 'python scripts/prepare_dataset.py' first.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    rec_service = RecommendationService()
    print(f"[*] Active LLM Provider: {rec_service.provider.provider_name.upper()}")
    print(f"[*] Active Model: {rec_service.provider.model}")
    print(f"[*] Demo Mode Flag: {rec_service.provider.is_demo_mode}\n")

    for idx, profile in enumerate(profiles, 1):
        name = profile["name"]
        degree = profile["degree"]
        skills = [s["name"] for s in profile.get("skills", [])]

        print(f"--------------------------------------------------------------------------------")
        print(f"STUDENT PROFILE {idx}/5: {name.upper()}")
        print(f"Degree: {degree} ({profile.get('specialization', 'General')})")
        print(f"Declared Skills: {', '.join(skills)}")
        print(f"Interests: {', '.join(profile.get('interests', []))}")
        print(f"Executing Multi-Agent Reasoning Pipeline...")

        result = rec_service.execute_recommendation_pipeline(profile, top_k=4)
        recs = result.get("recommendations", [])

        print(f"\n[+] TOP RECOMMENDED O*NET OCCUPATIONAL ROLES:")
        for r in recs:
            print(f"    #{r['rank_order']} | {r['occupation_title']} (SOC: {r['soc_code']})")
            print(f"        Match Score: {r['match_score']}/100 [{r['confidence']} Confidence]")
            print(f"        Matching Skills: {', '.join(r['matching_skills'])}")
            print(f"        Upskilling Gaps: {', '.join(r['missing_skills'])}")
            print(f"        Suitability Rationale: {r['reason'][:120]}...\n")

        # Roadmap highlights for top role
        roadmap = result.get("roadmap", {})
        if roadmap and roadmap.get("roadmap_30_days"):
            first_milestone = roadmap["roadmap_30_days"][0]
            print(f"    [30-Day Milestone Priority]: {first_milestone.get('skill_to_learn')}")
            print(f"    [Mini-Project]: {first_milestone.get('mini_project')}\n")

    print("================================================================================")
    print("DEMO EXECUTION COMPLETED SUCCESSFULLY!")
    print("Start the Web Interface with: python app.py")
    print("================================================================================")


if __name__ == "__main__":
    run_demo()

