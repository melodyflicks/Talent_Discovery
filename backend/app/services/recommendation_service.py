from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.domain import Course, CourseRecommendation, SkillGap, EmployeeSkill, EmployeeProfile


class RecommendationService:
    @staticmethod
    def list_courses(
        db: Session, skill_id: Optional[int] = None, difficulty: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        query = db.query(Course).options(joinedload(Course.skill)).filter(Course.is_active == True)
        if skill_id:
            query = query.filter(Course.skill_id == skill_id)
        if difficulty:
            query = query.filter(Course.difficulty.ilike(difficulty))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_recommendations_for_employee(db: Session, employee_id: int) -> List[CourseRecommendation]:
        recs = (
            db.query(CourseRecommendation)
            .options(
                joinedload(CourseRecommendation.course).joinedload(Course.skill)
            )
            .filter(CourseRecommendation.employee_id == employee_id)
            .order_by(CourseRecommendation.created_at.desc())
            .all()
        )
        if not recs:
            # Dynamically auto-generate initial recommendations based on skill gaps or courses
            return RecommendationService.generate_recommendations_for_employee(db, employee_id)
        return recs

    @staticmethod
    def generate_recommendations_for_employee(db: Session, employee_id: int) -> List[CourseRecommendation]:
        employee = db.query(EmployeeProfile).filter(EmployeeProfile.id == employee_id).first()
        if not employee:
            raise ValueError("Employee not found")

        # Check existing skill gaps
        gaps = db.query(SkillGap).filter(SkillGap.employee_id == employee_id).all()
        target_skill_ids = {g.skill_id for g in gaps if g.gap_level in ("critical", "high", "medium")}

        if not target_skill_ids:
            # Fallback to available courses
            courses = db.query(Course).filter(Course.is_active == True).limit(5).all()
        else:
            courses = db.query(Course).filter(
                Course.is_active == True,
                Course.skill_id.in_(target_skill_ids)
            ).all()
            if len(courses) < 3:
                additional = db.query(Course).filter(
                    Course.is_active == True,
                    ~Course.id.in_([c.id for c in courses])
                ).limit(3).all()
                courses.extend(additional)

        results = []
        for course in courses:
            existing = (
                db.query(CourseRecommendation)
                .filter(
                    CourseRecommendation.employee_id == employee_id,
                    CourseRecommendation.course_id == course.id
                )
                .first()
            )
            if not existing:
                priority = "high" if course.skill_id in target_skill_ids else "medium"
                skill_name = course.skill.name if course.skill else "Key Competencies"
                rec = CourseRecommendation(
                    employee_id=employee_id,
                    course_id=course.id,
                    priority=priority,
                    reason=f"Strengthen your proficiency in {skill_name} to accelerate career progression."
                )
                db.add(rec)
                results.append(rec)
            else:
                results.append(existing)

        db.commit()
        return (
            db.query(CourseRecommendation)
            .options(joinedload(CourseRecommendation.course).joinedload(Course.skill))
            .filter(CourseRecommendation.employee_id == employee_id)
            .all()
        )


recommendation_service = RecommendationService()
