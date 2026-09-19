from typing import Any, Dict, List
from pydantic import BaseModel
from .normalizer import normalize_skill


class InferredSkillResult(BaseModel):
    skill_name: str
    skill_type: str  # "inferred" or "transferable"
    proficiency: int
    confidence: float
    evidence: str


INFERENCE_RULES = [
    {
        "prereqs": {"FastAPI", "PostgreSQL", "Python"},
        "inferred_skill": "REST API Development",
        "type": "inferred",
        "proficiency": 4,
        "confidence": 0.90,
        "evidence": "Inferred from strong proficiency in FastAPI, PostgreSQL, and Python backend stack.",
    },
    {
        "prereqs": {"Docker", "AWS"},
        "inferred_skill": "Cloud Infrastructure",
        "type": "transferable",
        "proficiency": 3,
        "confidence": 0.85,
        "evidence": "Transferable competency inferred from Docker container management and AWS cloud experience.",
    },
    {
        "prereqs": {"React", "TypeScript"},
        "inferred_skill": "Frontend Architecture",
        "type": "inferred",
        "proficiency": 4,
        "confidence": 0.88,
        "evidence": "Inferred from combined React and TypeScript component design experience.",
    },
    {
        "prereqs": {"Machine Learning", "Python"},
        "inferred_skill": "Data Science",
        "type": "transferable",
        "proficiency": 3,
        "confidence": 0.82,
        "evidence": "Transferable data analytical skills inferred from Machine Learning and Python experience.",
    },
    {
        "prereqs": {"Kubernetes", "Docker"},
        "inferred_skill": "Microservices Architecture",
        "type": "inferred",
        "proficiency": 4,
        "confidence": 0.86,
        "evidence": "Inferred from containerization (Docker) and orchestration (Kubernetes) expertise.",
    },
    {
        "prereqs": {"Agile Methodology", "Team Leadership"},
        "inferred_skill": "Project Management",
        "type": "transferable",
        "proficiency": 4,
        "confidence": 0.85,
        "evidence": "Transferable leadership competency inferred from Agile practices and Team Leadership.",
    },
]


def infer_transferable_skills(
    explicit_skills: List[str],
    experience_years: int = 0,
    department: str = "",
) -> List[InferredSkillResult]:
    """
    Infers implicit or transferable skills backed by concrete evidence.
    """
    normalized_explicit = {normalize_skill(s).lower() for s in explicit_skills}
    results: List[InferredSkillResult] = []

    for rule in INFERENCE_RULES:
        prereqs_lower = {p.lower() for p in rule["prereqs"]}
        # Check if candidate has at least 2 or all prereqs
        matching = prereqs_lower.intersection(normalized_explicit)
        if len(matching) >= 2 or matching == prereqs_lower:
            target_skill = normalize_skill(rule["inferred_skill"])
            if target_skill.lower() not in normalized_explicit:
                results.append(
                    InferredSkillResult(
                        skill_name=target_skill,
                        skill_type=rule["type"],
                        proficiency=rule["proficiency"],
                        confidence=rule["confidence"],
                        evidence=rule["evidence"],
                    )
                )

    return results
