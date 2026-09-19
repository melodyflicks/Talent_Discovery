from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.domain import (
    User,
    EmployeeProfile,
    EmployeeSkill,
    RoleMatch,
    Role,
    SkillGap,
    CourseRecommendation,
    Course,
)
from app.schemas.common import ChatResponse
from ai.llm.llm_service import LLMService


class AssistantService:
    def __init__(self):
        self.llm_service = LLMService()

    def process_chat(
        self, db: Session, user: User, message: str, context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Career Assistant service grounding responses in real DB context.
        Never invents facts.
        """
        employee = (
            db.query(EmployeeProfile)
            .filter(EmployeeProfile.user_id == user.id)
            .first()
        )
        if not employee:
            return ChatResponse(
                reply="User profile not found. Please ensure your profile is created.",
                suggestions=["Contact HR support"],
            )

        # 1. Fetch DB records
        skills = (
            db.query(EmployeeSkill)
            .options(joinedload(EmployeeSkill.skill))
            .filter(EmployeeSkill.employee_id == employee.id)
            .all()
        )

        matches = (
            db.query(RoleMatch)
            .options(joinedload(RoleMatch.role))
            .filter(RoleMatch.employee_id == employee.id)
            .order_by(RoleMatch.match_score.desc())
            .all()
        )

        gaps = (
            db.query(SkillGap)
            .options(joinedload(SkillGap.skill))
            .filter(SkillGap.employee_id == employee.id)
            .all()
        )

        courses = (
            db.query(CourseRecommendation)
            .options(joinedload(CourseRecommendation.course))
            .filter(CourseRecommendation.employee_id == employee.id)
            .all()
        )

        # 2. Format Real DB Context
        name = user.full_name or "Employee"
        dept = employee.department or "N/A"
        designation = employee.designation or "Staff"
        exp = employee.years_of_experience

        explicit_skills = [f"{es.skill.name} ({es.proficiency}/5)" for es in skills if es.skill and es.skill_type == "explicit"]
        inferred_skills = [
            f"{es.skill.name} (Inferred, source: {es.source})"
            for es in skills
            if es.skill and es.skill_type in ["inferred", "transferable"]
        ]

        match_summaries = []
        for m in matches[:5]:
            missing_names = [ms.get("skill_name") for ms in (m.missing_skills or [])]
            match_summaries.append(
                f"- {m.role.title if m.role else 'Role'}: {m.match_score}% match. Missing: {', '.join(missing_names) if missing_names else 'None'}"
            )

        gap_summaries = [
            f"- {g.skill.name if g.skill else 'Skill'}: gap of {g.required_proficiency - g.current_proficiency} ({g.gap_level})"
            for g in gaps
        ]

        course_summaries = [
            f"- {c.course.title if c.course else 'Course'} ({c.course.provider if c.course else ''})"
            for c in courses
        ]

        db_context = f"""
Employee Profile:
Name: {name}
Designation: {designation}
Department: {dept}
Experience: {exp} years
Profile Completion: {employee.profile_completion}%

Verified Skills: {', '.join(explicit_skills) if explicit_skills else 'None'}
Inferred & Transferable Skills: {', '.join(inferred_skills) if inferred_skills else 'None'}

Top Role Matches:
{chr(10).join(match_summaries) if match_summaries else 'No role matches calculated yet.'}

Skill Gaps:
{chr(10).join(gap_summaries) if gap_summaries else 'No critical skill gaps identified.'}

Recommended Courses:
{chr(10).join(course_summaries) if course_summaries else 'No active course recommendations.'}
"""

        msg_lower = message.lower()

        # If LLM key is configured, generate via LLM with strict grounding prompt
        if self.llm_service.is_available():
            system_prompt = (
                "You are an AI Career & Talent Advisor for the organization. "
                "Answer the employee's query using strictly the real profile and organizational context provided below. "
                "Never invent fake facts, non-existent roles, or unverified skills. "
                "If information is not present in the context, state so directly.\n\n"
                f"Context Data:\n{db_context}"
            )
            llm_reply = self.llm_service.generate(message, system_prompt=system_prompt)
            if llm_reply:
                suggestions = [
                    "What are my highest priority skill gaps?",
                    "How can I reach 100% match for my top role?",
                    "Recommend a learning path for career advancement",
                ]
                return ChatResponse(reply=llm_reply.strip(), suggestions=suggestions)

        # Factual Fallback Response directly from DB Context
        if "skill" in msg_lower or "gap" in msg_lower:
            reply = (
                f"Hello {name.split()[0]}! Based on your profile as {designation} in {dept}, "
                f"you currently have {len(explicit_skills)} verified skills logged. "
            )
            if gap_summaries:
                reply += f"Your top identified skill gaps are:\n" + "\n".join(gap_summaries[:3])
            else:
                reply += "You have no critical skill gaps recorded."
            suggestions = [
                "Which courses help close these gaps?",
                "Show my top role matches",
                "How do I log new skill evidence?",
            ]
        elif "role" in msg_lower or "match" in msg_lower or "career" in msg_lower:
            reply = f"Hi {name.split()[0]}, here is your real-time role compatibility assessment:\n"
            if match_summaries:
                reply += "\n".join(match_summaries[:3])
            else:
                reply += "No role evaluations found."
            suggestions = [
                "What skills am I missing for senior roles?",
                "Recommend courses to close my skill gaps",
                "How is my match score calculated?",
            ]
        elif "course" in msg_lower or "learn" in msg_lower:
            reply = f"Here are your assigned learning recommendations:\n"
            if course_summaries:
                reply += "\n".join(course_summaries)
            else:
                reply += "No course recommendations currently assigned."
            suggestions = [
                "Show my top role matches",
                "Analyze my skill gaps",
                "What certifications should I pursue?",
            ]
        else:
            reply = (
                f"Hello {name.split()[0]}! I am your AI Career Advisor. "
                f"Your profile ({designation}, {dept}) has {len(explicit_skills)} verified skills "
                f"and {len(matches)} role compatibility evaluations on record. "
                "How can I assist your career growth today?"
            )
            suggestions = [
                "Analyze my skill gaps",
                "Show my top role matches",
                "Recommend courses for my career progression",
            ]

        return ChatResponse(reply=reply, suggestions=suggestions)


assistant_service = AssistantService()
