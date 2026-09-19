from ai.skills.extractor import extract_skills
from ai.skills.normalizer import normalize_skill
from ai.skills.inference import infer_transferable_skills
from ai.matching.scoring import score_match
from ai.recommendations.course_recommender import recommend_courses_for_gaps


def test_full_talent_discovery_ai_pipeline():
    """
    Real integration pipeline test covering:
    Resume/Bio Text -> Skill Extraction -> Normalization -> Skill Inference -> Weighted Matching -> Gap Calculation -> Course Recommendation.
    """
    # 1. Raw candidate bio text
    sample_text = "Experienced Senior Developer proficient in py, postgres, docker, and aws. Built microservices and rest APIs."

    # 2. Skill Extraction & Normalization
    extracted = extract_skills(sample_text)
    extracted_names = [item.name for item in extracted]
    assert "Python" in extracted_names or "PostgreSQL" in extracted_names or "Docker" in extracted_names

    # 3. Evidence-Backed Skill Inference
    explicit_skills = ["Python", "PostgreSQL", "Docker", "AWS", "FastAPI"]
    inferred = infer_transferable_skills(explicit_skills, experience_years=5, department="Engineering")
    assert len(inferred) > 0
    inferred_names = [item.skill_name for item in inferred]
    assert "Cloud Infrastructure" in inferred_names or "REST API Development" in inferred_names
    assert all(len(item.evidence) > 0 for item in inferred)

    # 4. Role Matching
    candidate_skills = [
        {"name": "Python", "proficiency": 5, "type": "explicit"},
        {"name": "PostgreSQL", "proficiency": 4, "type": "explicit"},
        {"name": "Docker", "proficiency": 4, "type": "explicit"},
        {"name": "AWS", "proficiency": 3, "type": "explicit"},
        {"name": "Cloud Infrastructure", "proficiency": 3, "type": "inferred"},
    ]

    required_role_skills = [
        {"name": "Python", "required_proficiency": 4, "importance": "critical"},
        {"name": "PostgreSQL", "required_proficiency": 4, "importance": "high"},
        {"name": "Docker", "required_proficiency": 4, "importance": "medium"},
        {"name": "Kubernetes", "required_proficiency": 3, "importance": "high"},
    ]

    match_result = score_match(
        candidate_skills=candidate_skills,
        required_role_skills=required_role_skills,
        candidate_experience_years=5,
        role_level="Senior",
        weights={"direct_skills": 0.45, "proficiency_align": 0.25, "transferable_skills": 0.20, "experience_align": 0.10},
    )

    assert match_result.match_score > 0.0
    assert len(match_result.matching_skills) >= 3
    assert len(match_result.missing_skills) == 1
    assert match_result.missing_skills[0]["skill_name"] == "Kubernetes"

    # 5. Course Recommendation
    course_catalog = [
        {"id": 101, "title": "Mastering Kubernetes Operations", "target_skill": "Kubernetes", "provider": "Coursera", "rating": 4.9},
        {"id": 102, "title": "Advanced Python Patterns", "target_skill": "Python", "provider": "Udemy", "rating": 4.7},
    ]

    recommendations = recommend_courses_for_gaps(match_result.gaps, course_catalog)
    assert len(recommendations) > 0
    assert recommendations[0]["course"]["target_skill"] == "Kubernetes"
