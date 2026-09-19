from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="employee", nullable=False)  # admin, hr, employee
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profile: Mapped[Optional["EmployeeProfile"]] = relationship("EmployeeProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class EmployeeProfile(Base, TimestampMixin):
    __tablename__ = "employee_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    employee_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    years_of_experience: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    education: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    location: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    resume_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    profile_completion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="profile")
    skills: Mapped[List["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    external_profiles: Mapped[List["ExternalProfile"]] = relationship("ExternalProfile", back_populates="employee", cascade="all, delete-orphan")
    role_matches: Mapped[List["RoleMatch"]] = relationship("RoleMatch", back_populates="employee", cascade="all, delete-orphan")
    skill_gaps: Mapped[List["SkillGap"]] = relationship("SkillGap", back_populates="employee", cascade="all, delete-orphan")
    course_recommendations: Mapped[List["CourseRecommendation"]] = relationship("CourseRecommendation", back_populates="employee", cascade="all, delete-orphan")
    roadmaps: Mapped[List["LearningRoadmap"]] = relationship("LearningRoadmap", back_populates="employee", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    employee_skills: Mapped[List["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="skill")
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="skill")


class EmployeeSkill(Base, TimestampMixin):
    __tablename__ = "employee_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    proficiency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1 - 5
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 0.0 - 1.0
    skill_type: Mapped[str] = mapped_column(String(30), default="explicit", nullable=False)  # explicit, inferred, transferable
    source: Mapped[str] = mapped_column(String(100), default="self-reported", nullable=False)

    employee: Mapped[EmployeeProfile] = relationship("EmployeeProfile", back_populates="skills")
    skill: Mapped[Skill] = relationship("Skill", back_populates="employee_skills")
    evidence: Mapped[List["SkillEvidence"]] = relationship("SkillEvidence", back_populates="employee_skill", cascade="all, delete-orphan")


class SkillEvidence(Base):
    __tablename__ = "skill_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_skill_id: Mapped[int] = mapped_column(ForeignKey("employee_skills.id", ondelete="CASCADE"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    employee_skill: Mapped[EmployeeSkill] = relationship("EmployeeSkill", back_populates="evidence")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    level: Mapped[str] = mapped_column(String(60), default="Mid-Level", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    required_skills: Mapped[List["RoleSkill"]] = relationship("RoleSkill", back_populates="role", cascade="all, delete-orphan")


class RoleSkill(Base):
    __tablename__ = "role_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    required_proficiency: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    importance: Mapped[str] = mapped_column(String(30), default="high", nullable=False)  # critical, high, medium, nice-to-have

    role: Mapped[Role] = relationship("Role", back_populates="required_skills")
    skill: Mapped[Skill] = relationship("Skill")


class RoleMatch(Base, TimestampMixin):
    __tablename__ = "role_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    matching_skills: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    missing_skills: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)

    employee: Mapped[EmployeeProfile] = relationship("EmployeeProfile", back_populates="role_matches")
    role: Mapped[Role] = relationship("Role")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    current_proficiency: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    required_proficiency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    gap_level: Mapped[str] = mapped_column(String(30), default="medium", nullable=False)  # none, low, medium, high, critical
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    employee: Mapped[EmployeeProfile] = relationship("EmployeeProfile", back_populates="skill_gaps")
    role: Mapped[Role] = relationship("Role")
    skill: Mapped[Skill] = relationship("Skill")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    skill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="Intermediate", nullable=False)  # Beginner, Intermediate, Advanced
    duration: Mapped[str] = mapped_column(String(50), default="4 weeks", nullable=False)
    url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    skill: Mapped[Optional[Skill]] = relationship("Skill", back_populates="courses")


class CourseRecommendation(Base):
    __tablename__ = "course_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    priority: Mapped[str] = mapped_column(String(30), default="medium", nullable=False)  # high, medium, low
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    employee: Mapped[EmployeeProfile] = relationship("EmployeeProfile", back_populates="course_recommendations")
    course: Mapped[Course] = relationship("Course")


class LearningRoadmap(Base, TimestampMixin):
    __tablename__ = "learning_roadmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    target_role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, index=True)
    roadmap_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    employee: Mapped[EmployeeProfile] = relationship("EmployeeProfile", back_populates="roadmaps")
    target_role: Mapped[Optional[Role]] = relationship("Role")


class ExternalProfile(Base, TimestampMixin):
    __tablename__ = "external_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # github, lms, competitive, linkedin, other
    profile_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    username: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    employee: Mapped[EmployeeProfile] = relationship("EmployeeProfile", back_populates="external_profiles")
