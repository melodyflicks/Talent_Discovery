import pytest
from ai.skills.normalizer import normalize_skill, normalize_skill_detailed
from ai.skills.inference import infer_transferable_skills
from ai.matching.scoring import score_match
from ai.recommendations.course_recommender import recommend_courses_for_gaps


def test_skill_normalization_alias_taxonomy_semantic():
    # Alias test
    norm_alias, conf_alias, cat_alias = normalize_skill_detailed("py")
    assert norm_alias == "Python"
    assert conf_alias >= 0.9

    # Taxonomy direct test
    norm_tax, conf_tax, cat_tax = normalize_skill_detailed("Docker")
    assert norm_tax == "Docker"
    assert cat_tax == "DevOps"

    # Semantic similarity difflib test
    norm_sem, conf_sem, _ = normalize_skill_detailed("postgre")
    assert norm_sem == "PostgreSQL"
    assert conf_sem > 0.6


def test_inferred_skill_evidence_and_types():
    explicit = ["Docker", "AWS", "FastAPI", "PostgreSQL", "Python"]
    results = infer_transferable_skills(explicit, experience_years=4)
    
    assert len(results) >= 2
    for item in results:
        assert item.skill_type in ["inferred", "transferable"]
        assert len(item.evidence) > 0
        assert item.confidence >= 0.8


def test_match_calculation_configurable_weights():
    candidate_skills = [
        {"name": "Python", "proficiency": 4, "type": "explicit"},
        {"name": "Docker", "proficiency": 3, "type": "explicit"},
        {"name": "REST API Development", "proficiency": 4, "type": "inferred"},
    ]
    required_skills = [
        {"name": "Python", "required_proficiency": 4, "importance": "critical"},
        {"name": "Docker", "required_proficiency": 4, "importance": "high"},
        {"name": "Kubernetes", "required_proficiency": 3, "importance": "high"},
    ]

    weights = {
        "direct_skills": 0.45,
        "proficiency_align": 0.25,
        "transferable_skills": 0.20,
        "experience_align": 0.10,
    }

    res = score_match(
        candidate_skills=candidate_skills,
        required_role_skills=required_skills,
        candidate_experience_years=5,
        role_level="Senior",
        weights=weights,
    )

    assert 0.0 <= res.match_score <= 100.0
    assert len(res.matching_skills) == 2
    assert len(res.missing_skills) == 1
    assert "weighted_breakdown" in res.model_dump()
    assert res.weighted_breakdown["direct_skills"] > 0


def test_gap_calculation_levels():
    candidate_skills = [
        {"name": "Python", "proficiency": 1, "type": "explicit"},
    ]
    required_skills = [
        {"name": "Python", "required_proficiency": 5, "importance": "critical"},
    ]
    res = score_match(candidate_skills, required_skills)
    assert len(res.gaps) == 1
    assert res.gaps[0]["gap_level"] == "critical"
    assert res.gaps[0]["gap_size"] == 4


def test_course_filtering_and_ranking():
    gaps = [
        {"skill_name": "Kubernetes", "gap_size": 3, "gap_level": "critical"},
        {"skill_name": "Python", "gap_size": 1, "gap_level": "medium"},
    ]
    catalog = [
        {"id": 1, "title": "Python Basics", "target_skill": "Python", "rating": 4.5},
        {"id": 2, "title": "Kubernetes Deep Dive", "target_skill": "Kubernetes", "rating": 4.8},
        {"id": 3, "title": "Java Fundamentals", "target_skill": "Java", "rating": 4.2},
    ]

    recommended = recommend_courses_for_gaps(gaps, catalog)
    assert len(recommended) == 2
    assert recommended[0]["course"]["target_skill"] == "Kubernetes"
