import difflib
from typing import Tuple
from .taxonomy import CANONICAL_SKILLS, SKILL_ALIASES


def normalize_skill_detailed(skill: str) -> Tuple[str, float, str]:
    """
    Normalizes a skill name through Alias -> Taxonomy -> Semantic Match.
    Returns (normalized_name, confidence_score, category).
    """
    if not skill or not skill.strip():
        return ("", 0.0, "General")

    raw = skill.strip()
    raw_lower = raw.lower()

    # 1. Alias lookup
    if raw_lower in SKILL_ALIASES:
        canon_name = SKILL_ALIASES[raw_lower]
        category = CANONICAL_SKILLS.get(canon_name, "General")
        return (canon_name, 0.98, category)

    # 2. Exact taxonomy lookup (case insensitive)
    for canon_name, category in CANONICAL_SKILLS.items():
        if canon_name.lower() == raw_lower:
            return (canon_name, 1.0, category)

    # 3. Semantic / String similarity lookup against canonical taxonomy
    canon_names_list = list(CANONICAL_SKILLS.keys())
    matches = difflib.get_close_matches(raw, canon_names_list, n=1, cutoff=0.6)
    if matches:
        canon_name = matches[0]
        # compute exact ratio
        ratio = difflib.SequenceMatcher(None, raw_lower, canon_name.lower()).ratio()
        category = CANONICAL_SKILLS.get(canon_name, "General")
        return (canon_name, round(ratio, 2), category)

    # 4. Fallback: Clean title case
    formatted = " ".join(word.capitalize() for word in raw.split())
    return (formatted, 0.70, "General")


def normalize_skill(skill: str) -> str:
    """Helper returning normalized skill name string."""
    norm_name, _, _ = normalize_skill_detailed(skill)
    return norm_name
