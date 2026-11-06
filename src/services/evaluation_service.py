"""PathMatch AI - Recommendation Evaluation and Benchmark Service.

Provides benchmarking against predefined ground-truth domain alignments for the 5 sample profiles.
Calculates Precision@k, Recall@k, Mean Reciprocal Rank (MRR), and generates reports.
"""

from typing import Dict, Any, List
from src.services.recommendation_service import RecommendationService
from src.utils.logging_config import logger

# Ground truth expected target domains and role keywords for the 5 sample profiles
GROUND_TRUTH_BENCHMARKS = {
    "Rahul": {
        "expected_domains": ["Data Science & AI", "Systems & Business Analysis"],
        "expected_role_keywords": ["data", "analyst", "intelligence", "statistician", "visualization"],
        "top_expected_role": "Data Scientist"
    },
    "Ananya": {
        "expected_domains": ["Web & Mobile Development"],
        "expected_role_keywords": ["web", "frontend", "ui", "ux", "designer", "mobile"],
        "top_expected_role": "Web Developer (Frontend)"
    },
    "Mohit": {
        "expected_domains": ["Software Engineering"],
        "expected_role_keywords": ["java", "backend", "software developer", "api", "spring"],
        "top_expected_role": "Backend Java Engineer"
    },
    "Sneha": {
        "expected_domains": ["Data Science & AI"],
        "expected_role_keywords": ["machine learning", "data scientist", "ai", "deep learning"],
        "top_expected_role": "Machine Learning Engineer"
    },
    "Arjun": {
        "expected_domains": ["Cybersecurity & Networking"],
        "expected_role_keywords": ["security", "network", "analyst", "systems", "forensics"],
        "top_expected_role": "Information Security Analyst"
    }
}


class EvaluationService:
    """Computes academic evaluation metrics across sample profiles."""

    def __init__(self, provider_name: str = None):
        self.rec_service = RecommendationService(provider_name=provider_name)

    def evaluate_sample_profiles(self, sample_profiles: List[Dict[str, Any]], k: int = 5) -> Dict[str, Any]:
        """Run evaluation pipeline on sample profiles and calculate Precision@k, Recall@k, MRR."""
        results = []
        precision_scores = []
        reciprocal_ranks = []

        for profile in sample_profiles:
            name = profile.get("name", "Unknown")
            benchmark = GROUND_TRUTH_BENCHMARKS.get(name)
            if not benchmark:
                continue

            # Run recommendation pipeline
            run_result = self.rec_service.execute_recommendation_pipeline(profile, top_k=k)
            recommendations = run_result.get("recommendations", [])

            # Compute precision@k: proportion of recommended roles matching target domain / keywords
            relevant_count = 0
            first_relevant_rank = None

            for rank_idx, rec in enumerate(recommendations, 1):
                title_low = rec.get("occupation_title", "").lower()
                is_relevant = any(kw in title_low for kw in benchmark["expected_role_keywords"])
                if is_relevant:
                    relevant_count += 1
                    if first_relevant_rank is None:
                        first_relevant_rank = rank_idx

            p_at_k = relevant_count / max(1, len(recommendations))
            rr = (1.0 / first_relevant_rank) if first_relevant_rank else 0.0

            precision_scores.append(p_at_k)
            reciprocal_ranks.append(rr)

            results.append({
                "student_name": name,
                "degree": profile.get("degree"),
                "interests": profile.get("interests"),
                "precision_at_k": round(p_at_k, 3),
                "mrr": round(rr, 3),
                "top_recommended_role": recommendations[0].get("occupation_title") if recommendations else "None",
                "top_score": recommendations[0].get("match_score") if recommendations else 0,
                "recommended_roles": [r.get("occupation_title") for r in recommendations],
                "expected_domain": benchmark["expected_domains"],
                "run_id": run_result.get("run_id")
            })

        mean_precision = sum(precision_scores) / max(1, len(precision_scores))
        mrr = sum(reciprocal_ranks) / max(1, len(reciprocal_ranks))

        return {
            "k": k,
            "profiles_evaluated": len(results),
            "mean_precision_at_k": round(mean_precision, 3),
            "mean_reciprocal_rank": round(mrr, 3),
            "detailed_results": results,
            "provider": self.rec_service.provider.provider_name,
            "is_demo_mode": self.rec_service.provider.is_demo_mode
        }

