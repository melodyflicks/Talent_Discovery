from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from ..skills.normalizer import normalize_skill

DEFAULT_MATCH_WEIGHTS = {
    "direct_skills": 0.45,
    "proficiency_align": 0.25,
    "transferable_skills": 0.20,
    "experience_align": 0.10,
}

LEVEL_EXPERIENCE_REQUIREMENTS = {
    "Junior": 1,
    "Mid": 3,
    "Senior": 5,
    "Lead": 7,
    "Principal": 8,
}


class SkillMatchDetail(BaseModel):
    skill_name: str
    required_proficiency: int
    current_proficiency: int
    importance: str
    match_status: str  # "met", "partially_met", "missing"


class DetailedMatchScore(BaseModel):
    match_score: float  # 0.0 - 100.0
    matching_skills: List[Dict[str, Any]]
    missing_skills: List[Dict[str, Any]]
    gaps: List[Dict[str, Any]]
    explanation: str
    weighted_breakdown: Dict[str, float]


def score_match(
    candidate_skills: List[Dict[str, Any]],  # list of dicts: {"name": str, "proficiency": int, "type": str}
    required_role_skills: List[Dict[str, Any]],  # list of dicts: {"name": str, "required_proficiency": int, "importance": str}
    candidate_experience_years: int = 0,
    role_level: str = "Mid",
    weights: Optional[Dict[str, float]] = None,
) -> DetailedMatchScore:
    """
    Computes deterministic match score using configurable weights.
    LLM NEVER decides or hallucinates the match score.
    """
    if weights is None:
        weights = DEFAULT_MATCH_WEIGHTS

    # Normalize weights to sum to 1.0
    total_w = sum(weights.values())
    w_direct = weights.get("direct_skills", 0.45) / total_w
    w_prof = weights.get("proficiency_align", 0.25) / total_w
    w_trans = weights.get("transferable_skills", 0.20) / total_w
    w_exp = weights.get("experience_align", 0.10) / total_w

    if not required_role_skills:
        return DetailedMatchScore(
            match_score=100.0,
            matching_skills=[],
            missing_skills=[],
            gaps=[],
            explanation="Role has no specific skill requirements.",
            weighted_breakdown={"direct_skills": 1.0, "proficiency_align": 1.0, "transferable_skills": 1.0, "experience_align": 1.0},
        )

    # Build map of candidate skills
    explicit_map = {}
    transferable_map = {}
    for s in candidate_skills:
        norm_name = normalize_skill(s.get("name") or s.get("skill_name") or "").lower()
        stype = s.get("type") or s.get("skill_type") or "explicit"
        prof = int(s.get("proficiency", 1))
        if stype == "explicit":
            explicit_map[norm_name] = prof
        else:
            transferable_map[norm_name] = prof

    matching_list = []
    missing_list = []
    gaps_list = []

    direct_matches_count = 0
    transferable_matches_count = 0
    total_required = len(required_role_skills)
    prof_ratio_sum = 0.0

    for rs in required_role_skills:
        rname = rs.get("name") or rs.get("skill_name") or ""
        rnorm = normalize_skill(rname).lower()
        req_prof = int(rs.get("required_proficiency", 3))
        importance = rs.get("importance", "medium")

        if rnorm in explicit_map:
            curr_prof = explicit_map[rnorm]
            direct_matches_count += 1
            prof_ratio = min(curr_prof / max(req_prof, 1), 1.2)
            prof_ratio_sum += min(prof_ratio, 1.0)
            matching_list.append({
                "skill_name": rname,
                "current_proficiency": curr_prof,
                "required_proficiency": req_prof,
                "importance": importance,
                "type": "explicit",
            })
            if curr_prof < req_prof:
                gap_size = req_prof - curr_prof
                level = "critical" if gap_size >= 3 else "high" if gap_size == 2 else "medium"
                gaps_list.append({
                    "skill_name": rname,
                    "current_proficiency": curr_prof,
                    "required_proficiency": req_prof,
                    "gap_size": gap_size,
                    "gap_level": level,
                })
        elif rnorm in transferable_map:
            curr_prof = transferable_map[rnorm]
            transferable_matches_count += 1
            prof_ratio = min((curr_prof * 0.8) / max(req_prof, 1), 1.0)
            prof_ratio_sum += prof_ratio
            matching_list.append({
                "skill_name": rname,
                "current_proficiency": curr_prof,
                "required_proficiency": req_prof,
                "importance": importance,
                "type": "inferred",
            })
            if curr_prof < req_prof:
                gaps_list.append({
                    "skill_name": rname,
                    "current_proficiency": curr_prof,
                    "required_proficiency": req_prof,
                    "gap_size": req_prof - curr_prof,
                    "gap_level": "medium",
                })
        else:
            missing_list.append({
                "skill_name": rname,
                "required_proficiency": req_prof,
                "importance": importance,
            })
            gaps_list.append({
                "skill_name": rname,
                "current_proficiency": 0,
                "required_proficiency": req_prof,
                "gap_size": req_prof,
                "gap_level": "critical" if req_prof >= 4 else "high",
            })

    # Component Scores (0.0 to 1.0)
    score_direct = direct_matches_count / total_required
    score_prof = prof_ratio_sum / total_required
    score_trans = (direct_matches_count + transferable_matches_count) / total_required
    
    target_exp = LEVEL_EXPERIENCE_REQUIREMENTS.get(role_level, 3)
    score_exp = min(candidate_experience_years / max(target_exp, 1), 1.0)

    # Total Weighted Formula Score
    final_score = (
        (w_direct * score_direct) +
        (w_prof * score_prof) +
        (w_trans * score_trans) +
        (w_exp * score_exp)
    ) * 100.0

    final_score_rounded = round(final_score, 1)

    explanation = (
        f"Matched {len(matching_list)} of {total_required} required skills "
        f"({direct_matches_count} direct, {transferable_matches_count} inferred/transferable). "
        f"Formulaic compatibility score: {final_score_rounded}%."
    )

    return DetailedMatchScore(
        match_score=final_score_rounded,
        matching_skills=matching_list,
        missing_skills=missing_list,
        gaps=gaps_list,
        explanation=explanation,
        weighted_breakdown={
            "direct_skills": round(score_direct * 100, 1),
            "proficiency_align": round(score_prof * 100, 1),
            "transferable_skills": round(score_trans * 100, 1),
            "experience_align": round(score_exp * 100, 1),
        },
    )
