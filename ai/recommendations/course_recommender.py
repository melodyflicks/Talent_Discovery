from typing import Any, Dict, List
from ..skills.normalizer import normalize_skill


def recommend_courses_for_gaps(
    skill_gaps: List[Dict[str, Any]],  # e.g., [{"skill_name": "Docker", "gap_size": 2, "gap_level": "critical"}]
    course_catalog: List[Dict[str, Any]],  # e.g., [{"id": 1, "title": "...", "target_skill": "Docker", "rating": 4.8}]
) -> List[Dict[str, Any]]:
    """
    Filters and ranks course catalog items according to candidate skill gaps.
    """
    if not skill_gaps or not course_catalog:
        return []

    # Map target skills from gaps
    gap_skills_map = {}
    for g in skill_gaps:
        sname = normalize_skill(g.get("skill_name") or g.get("skill") or "").lower()
        gap_size = g.get("gap_size", 1)
        gap_level = g.get("gap_level", "medium")
        priority = 3 if gap_level == "critical" else 2 if gap_level == "high" else 1
        gap_skills_map[sname] = priority * 10 + gap_size

    recommended = []
    for course in course_catalog:
        target = normalize_skill(course.get("target_skill") or course.get("skill_name") or "").lower()
        if target in gap_skills_map:
            score = gap_skills_map[target] + float(course.get("rating", 4.0))
            recommended.append({
                "course": course,
                "relevance_score": round(score, 2),
                "matched_gap_skill": course.get("target_skill"),
            })

    # Sort by relevance score descending
    recommended.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommended
