from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Auth & User Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "employee"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Skill Schemas ---
class SkillBase(BaseModel):
    name: str
    category: str
    description: str = ""


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Skill Evidence Schemas ---
class SkillEvidenceCreate(BaseModel):
    source_type: str = "self-reported"
    source_reference: str = ""
    evidence_text: str
    confidence: float = 1.0


class SkillEvidenceResponse(BaseModel):
    id: int
    employee_skill_id: int
    source_type: str
    source_reference: str
    evidence_text: str
    confidence: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Employee Skill Schemas ---
class EmployeeSkillCreate(BaseModel):
    skill_name: Optional[str] = None
    skill_id: Optional[int] = None
    category: Optional[str] = "General"
    proficiency: int = Field(ge=1, le=5, default=3)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    skill_type: str = "explicit"  # explicit, inferred, transferable
    source: str = "self-reported"
    evidence_text: Optional[str] = None


class EmployeeSkillResponse(BaseModel):
    id: int
    employee_id: int
    skill_id: int
    proficiency: int
    confidence: float
    skill_type: str
    source: str
    skill: Optional[SkillResponse] = None
    evidence: List[SkillEvidenceResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- External Profile Schemas ---
class ExternalProfileResponse(BaseModel):
    id: int
    employee_id: int
    platform: str
    profile_url: str
    username: str
    raw_data: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- Employee Profile Schemas ---
class EmployeeResponse(BaseModel):
    id: int
    user_id: int
    employee_code: str
    department: str
    designation: str
    years_of_experience: float
    education: str = ""
    location: str = ""
    bio: str = ""
    resume_url: str = ""
    profile_completion: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)


class EmployeeDetailResponse(EmployeeResponse):
    skills: List[EmployeeSkillResponse] = []
    external_profiles: List[ExternalProfileResponse] = []
    model_config = ConfigDict(from_attributes=True)


class EmployeeCreate(BaseModel):
    email: str
    password: str
    full_name: str
    employee_code: str
    department: str
    designation: str
    years_of_experience: float = 0.0
    education: str = ""
    location: str = ""
    bio: str = ""


class EmployeeUpdate(BaseModel):
    department: Optional[str] = None
    designation: Optional[str] = None
    years_of_experience: Optional[float] = None
    education: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    resume_url: Optional[str] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    designation: Optional[str] = None
    years_of_experience: Optional[float] = None
    education: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    resume_url: Optional[str] = None


# --- Role Schemas ---
class RoleSkillResponse(BaseModel):
    id: int
    role_id: int
    skill_id: int
    required_proficiency: int
    importance: str
    skill: Optional[SkillResponse] = None
    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: int
    title: str
    department: str
    description: str
    level: str
    is_active: bool
    required_skills: List[RoleSkillResponse] = []
    model_config = ConfigDict(from_attributes=True)


class RoleSkillCreate(BaseModel):
    skill_name: Optional[str] = None
    skill_id: Optional[int] = None
    required_proficiency: int = Field(ge=1, le=5, default=3)
    importance: str = "high"


class RoleCreate(BaseModel):
    title: str
    department: str
    description: str = ""
    level: str = "Mid-Level"
    required_skills: List[RoleSkillCreate] = []


# --- Role Match Schemas ---
class RoleMatchResponse(BaseModel):
    id: int
    employee_id: int
    role_id: int
    match_score: float
    matching_skills: List[Any] = []
    missing_skills: List[Any] = []
    explanation: str = ""
    role: Optional[RoleResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class GenerateMatchRequest(BaseModel):
    role_ids: Optional[List[int]] = None


# --- Skill Gap Schemas ---
class SkillGapResponse(BaseModel):
    id: int
    employee_id: int
    role_id: int
    skill_id: int
    current_proficiency: int
    required_proficiency: int
    gap_level: str
    skill: Optional[SkillResponse] = None
    role: Optional[RoleResponse] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- Course Schemas ---
class CourseResponse(BaseModel):
    id: int
    title: str
    provider: str
    description: str
    skill_id: Optional[int] = None
    difficulty: str
    duration: str
    url: str
    is_active: bool
    skill: Optional[SkillResponse] = None
    model_config = ConfigDict(from_attributes=True)


class CourseRecommendationResponse(BaseModel):
    id: int
    employee_id: int
    course_id: int
    reason: str
    priority: str
    course: Optional[CourseResponse] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- Roadmap Schemas ---
class RoadmapResponse(BaseModel):
    id: int
    employee_id: int
    target_role_id: Optional[int] = None
    roadmap_data: Dict[str, Any] = {}
    target_role: Optional[RoleResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class RoadmapCreate(BaseModel):
    target_role_id: Optional[int] = None
    roadmap_data: Optional[Dict[str, Any]] = None


# --- Career Assistant Schemas ---
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: List[str] = []


# --- HR Analytics Schemas ---
class HRAnalyticsResponse(BaseModel):
    total_employees: int
    profile_completion_rate: float
    total_skills: int
    emerging_skill_gaps: int
    total_role_matches: int
    learning_recommendations: int
    skill_distribution: List[Dict[str, Any]] = []
    department_skills: List[Dict[str, Any]] = []
    skill_gaps: List[Dict[str, Any]] = []
    role_demand: List[Dict[str, Any]] = []
    learning_categories: List[Dict[str, Any]] = []
