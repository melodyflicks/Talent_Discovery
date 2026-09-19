from typing import List, Optional
from pydantic import BaseModel, Field
from ..llm.llm_service import LLMService
from .normalizer import normalize_skill_detailed
from .taxonomy import CANONICAL_SKILLS, SKILL_ALIASES


class ExtractedSkill(BaseModel):
    name: str
    category: str = "General"
    confidence: float = 0.8
    source_snippet: Optional[str] = None


class SkillExtractionOutput(BaseModel):
    skills: List[ExtractedSkill] = Field(default_factory=list)


def extract_skills(text: str, llm_service: Optional[LLMService] = None) -> List[ExtractedSkill]:
    """
    Extracts explicit skills from text. Uses LLM if available; otherwise uses deterministic taxonomy parser.
    """
    if not text or not text.strip():
        return []

    # Try LLM Extraction if LLMService is available
    if llm_service and llm_service.is_available():
        prompt = (
            f"Extract all technical, domain, and professional skills mentioned in the following text:\n\n{text}\n"
        )
        result = llm_service.generate_json(prompt, SkillExtractionOutput)
        if result and result.skills:
            # Normalize extracted skills
            normalized_list = []
            for item in result.skills:
                norm_name, conf, cat = normalize_skill_detailed(item.name)
                normalized_list.append(
                    ExtractedSkill(
                        name=norm_name,
                        category=cat,
                        confidence=min(item.confidence, conf),
                        source_snippet=item.source_snippet or "LLM Extracted",
                    )
                )
            return normalized_list

    # Deterministic Fallback Parser
    found_skills = {}
    text_lower = text.lower()

    # 1. Scan aliases
    for alias, canon_name in SKILL_ALIASES.items():
        if alias in text_lower:
            norm_name, conf, cat = normalize_skill_detailed(canon_name)
            found_skills[norm_name] = ExtractedSkill(
                name=norm_name,
                category=cat,
                confidence=conf,
                source_snippet=f"Matched term '{alias}' in text",
            )

    # 2. Scan canonical skills
    for canon_name in CANONICAL_SKILLS.keys():
        if canon_name.lower() in text_lower:
            norm_name, conf, cat = normalize_skill_detailed(canon_name)
            found_skills[norm_name] = ExtractedSkill(
                name=norm_name,
                category=cat,
                confidence=1.0,
                source_snippet=f"Direct match '{canon_name}'",
            )

    return list(found_skills.values())
