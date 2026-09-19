from typing import Any, Dict, List
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session
from app.models.domain import (
    EmployeeProfile,
    Skill,
    EmployeeSkill,
    Role,
    RoleSkill,
    RoleMatch,
    SkillGap,
    Course,
    CourseRecommendation,
)
from app.schemas.common import HRAnalyticsResponse


class AnalyticsService:
    @staticmethod
    def get_hr_analytics(db: Session) -> HRAnalyticsResponse:
        total_employees = db.query(EmployeeProfile).count()
        avg_completion = db.query(func.avg(EmployeeProfile.profile_completion)).scalar() or 0.0
        total_skills = db.query(Skill).count()
        emerging_skill_gaps = (
            db.query(SkillGap)
            .filter(SkillGap.gap_level.in_(["critical", "high"]))
            .count()
        )
        total_role_matches = db.query(RoleMatch).count()
        learning_recommendations = db.query(CourseRecommendation).count()

        # 1. Skill Distribution (Top skills across org)
        skill_dist_query = (
            db.query(
                Skill.name,
                Skill.category,
                func.count(EmployeeSkill.id).label("employee_count"),
                func.avg(EmployeeSkill.proficiency).label("avg_proficiency")
            )
            .join(EmployeeSkill, Skill.id == EmployeeSkill.skill_id)
            .group_by(Skill.name, Skill.category)
            .order_by(func.count(EmployeeSkill.id).desc())
            .limit(10)
            .all()
        )
        skill_distribution = [
            {
                "skill": row.name,
                "category": row.category,
                "count": row.employee_count,
                "avg_proficiency": round(float(row.avg_proficiency or 0), 1)
            }
            for row in skill_dist_query
        ]

        # 2. Department Skills breakdown
        dept_skills_query = (
            db.query(
                EmployeeProfile.department,
                func.count(distinct(EmployeeProfile.id)).label("headcount"),
                func.count(EmployeeSkill.id).label("total_skills_logged"),
                func.avg(EmployeeProfile.profile_completion).label("avg_completion")
            )
            .outerjoin(EmployeeSkill, EmployeeProfile.id == EmployeeSkill.employee_id)
            .group_by(EmployeeProfile.department)
            .all()
        )
        department_skills = [
            {
                "department": row.department,
                "headcount": row.headcount,
                "total_skills": row.total_skills_logged,
                "avg_completion": round(float(row.avg_completion or 0), 1)
            }
            for row in dept_skills_query
        ]

        # 3. Top Organization Skill Gaps
        gaps_query = (
            db.query(
                Skill.name,
                Skill.category,
                func.count(SkillGap.id).label("gap_count"),
                func.avg(SkillGap.required_proficiency - SkillGap.current_proficiency).label("avg_gap")
            )
            .join(SkillGap, Skill.id == SkillGap.skill_id)
            .filter(SkillGap.gap_level.in_(["critical", "high", "medium"]))
            .group_by(Skill.name, Skill.category)
            .order_by(func.count(SkillGap.id).desc())
            .limit(10)
            .all()
        )
        skill_gaps = [
            {
                "skill": row.name,
                "category": row.category,
                "affected_employees": row.gap_count,
                "avg_gap_size": round(float(row.avg_gap or 0), 1)
            }
            for row in gaps_query
        ]

        # 4. Role Demand / Bench Strength & Organizational Skill Demand Gap
        roles = db.query(Role).filter(Role.is_active == True).all()
        role_demand = []
        for r in roles:
            matches = db.query(RoleMatch).filter(RoleMatch.role_id == r.id).all()
            total_eval = len(matches)
            avg_score = sum(m.match_score for m in matches) / total_eval if total_eval > 0 else 0.0
            ready = sum(1 for m in matches if m.match_score >= 0.80)
            partial = sum(1 for m in matches if 0.50 <= m.match_score < 0.80)
            significant_gap = sum(1 for m in matches if m.match_score < 0.50)
            
            role_demand.append({
                "role": r.title,
                "role_id": r.id,
                "department": r.department,
                "level": r.level,
                "evaluated_candidates": total_eval,
                "avg_match_score": round(float(avg_score * 100), 1) if avg_score <= 1.0 else round(float(avg_score), 1),
                "ready_count": ready,
                "partial_count": partial,
                "gap_count": significant_gap,
                "bench_strength": f"{ready} ready / {partial} partial / {significant_gap} gap",
                "organizational_skill_demand_gap": max(0, total_employees - ready)
            })

        # 5. Learning Categories
        courses_query = (
            db.query(
                Course.provider,
                func.count(Course.id).label("course_count"),
                func.count(CourseRecommendation.id).label("assigned_count")
            )
            .outerjoin(CourseRecommendation, Course.id == CourseRecommendation.course_id)
            .group_by(Course.provider)
            .all()
        )
        learning_categories = [
            {
                "provider": row.provider,
                "course_count": row.course_count,
                "assigned_count": row.assigned_count
            }
            for row in courses_query
        ]

        return HRAnalyticsResponse(
            total_employees=total_employees,
            profile_completion_rate=round(float(avg_completion), 1),
            total_skills=total_skills,
            emerging_skill_gaps=emerging_skill_gaps,
            total_role_matches=total_role_matches,
            learning_recommendations=learning_recommendations,
            skill_distribution=skill_distribution,
            department_skills=department_skills,
            skill_gaps=skill_gaps,
            role_demand=role_demand,
            learning_categories=learning_categories,
        )


analytics_service = AnalyticsService()
