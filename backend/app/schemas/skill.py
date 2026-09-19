from pydantic import BaseModel, Field

class SkillEvidence(BaseModel):
    skill: str
    proficiency: str = "unknown"
    confidence: float = Field(ge=0, le=1)
    source: str
    evidence: str
