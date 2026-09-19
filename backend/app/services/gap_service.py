from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.domain import SkillGap, Role, RoleSkill, EmployeeSkill, EmployeeProfile, Skill


class GapService:
    @staticmethod
    def get_skill_gaps(
        db: Session, employee_id: int, role_id: Optional[int] = None
    ) -> List[SkillGap]:
        query = (
            db.query(SkillGap)
            .options(
                joinedload(SkillGap.skill),
                joinedload(SkillGap.role)
            )
            .filter(SkillGap.employee_id == employee_id)
        )
        if role_id:
            query = query.filter(SkillGap.role_id == role_id)
        return query.all()

    @staticmethod
    def calculate_and_sync_gaps(db: Session, employee_id: int, role_id: int) -> List[SkillGap]:
        role = db.query(Role).options(joinedload(Role.required_skills)).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Role not found")

        emp_skills = db.query(EmployeeSkill).filter(EmployeeSkill.employee_id == employee_id).all()
        emp_skill_map = {es.skill_id: es.proficiency for es in emp_skills}

        gaps = []
        for rs in role.required_skills:
            curr_prof = emp_skill_map.get(rs.skill_id, 0)
            req_prof = rs.required_proficiency
            diff = req_prof - curr_prof

            if diff <= 0:
                gap_level = "none"
            elif diff == 1:
                gap_level = "low"
            elif diff == 2:
                gap_level = "medium"
            elif diff >= 3 and rs.importance in ("critical", "high"):
                gap_level = "critical"
            else:
                gap_level = "high"

            # Check if record exists
            gap_rec = (
                db.query(SkillGap)
                .filter(
                    SkillGap.employee_id == employee_id,
                    SkillGap.role_id == role_id,
                    SkillGap.skill_id == rs.skill_id
                )
                .first()
            )

            if gap_rec:
                gap_rec.current_proficiency = curr_prof
                gap_rec.required_proficiency = req_prof
                gap_rec.gap_level = gap_level
            else:
                gap_rec = SkillGap(
                    employee_id=employee_id,
                    role_id=role_id,
                    skill_id=rs.skill_id,
                    current_proficiency=curr_prof,
                    required_proficiency=req_prof,
                    gap_level=gap_level
                )
                db.add(gap_rec)
            gaps.append(gap_rec)

        db.commit()
        return GapService.get_skill_gaps(db, employee_id, role_id)


gap_service = GapService()
