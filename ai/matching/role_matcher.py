from typing import Any, Dict, List, Optional
from .scoring import DetailedMatchScore, score_match


class RoleMatcher:
    """Matcher engine utilizing deterministic weighted formula scoring."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights

    def evaluate_role_match(
        self,
        candidate_skills: List[Dict[str, Any]],
        required_role_skills: List[Dict[str, Any]],
        candidate_experience_years: int = 0,
        role_level: str = "Mid",
    ) -> DetailedMatchScore:
        return score_match(
            candidate_skills=candidate_skills,
            required_role_skills=required_role_skills,
            candidate_experience_years=candidate_experience_years,
            role_level=role_level,
            weights=self.weights,
        )
