from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.domain import Skill, EmployeeSkill, SkillEvidence, EmployeeProfile
from app.schemas.common import EmployeeSkillCreate, SkillCreate


class SkillService:
    @staticmethod
    def list_skills(
        db: Session, category: Optional[str] = None, skip: int = 0, limit: int = 200
    ) -> List[Skill]:
        query = db.query(Skill)
        if category:
            query = query.filter(Skill.category.ilike(f"%{category}%"))
        return query.order_by(Skill.name.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_or_create_skill(
        db: Session, name: str, category: str = "General", description: str = ""
    ) -> Skill:
        clean_name = name.strip()
        skill = db.query(Skill).filter(Skill.name.ilike(clean_name)).first()
        if not skill:
            skill = Skill(name=clean_name, category=category, description=description)
            db.add(skill)
            db.commit()
            db.refresh(skill)
        return skill

    @staticmethod
    def create_skill(db: Session, payload: SkillCreate) -> Skill:
        skill = Skill(
            name=payload.name.strip(),
            category=payload.category,
            description=payload.description
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    @staticmethod
    def list_employee_skills(db: Session, employee_id: int) -> List[EmployeeSkill]:
        return (
            db.query(EmployeeSkill)
            .options(
                joinedload(EmployeeSkill.skill),
                joinedload(EmployeeSkill.evidence)
            )
            .filter(EmployeeSkill.employee_id == employee_id)
            .all()
        )

    @staticmethod
    def add_or_update_employee_skill(
        db: Session, employee_id: int, payload: EmployeeSkillCreate
    ) -> EmployeeSkill:
        # Resolve skill
        if payload.skill_id:
            skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
            if not skill:
                raise ValueError("Skill not found")
        elif payload.skill_name:
            skill = SkillService.get_or_create_skill(
                db, payload.skill_name, payload.category or "General"
            )
        else:
            raise ValueError("Either skill_id or skill_name must be provided")

        # Check existing employee skill
        emp_skill = (
            db.query(EmployeeSkill)
            .filter(
                EmployeeSkill.employee_id == employee_id,
                EmployeeSkill.skill_id == skill.id
            )
            .first()
        )

        if emp_skill:
            emp_skill.proficiency = payload.proficiency
            emp_skill.confidence = payload.confidence
            emp_skill.skill_type = payload.skill_type
            emp_skill.source = payload.source
        else:
            emp_skill = EmployeeSkill(
                employee_id=employee_id,
                skill_id=skill.id,
                proficiency=payload.proficiency,
                confidence=payload.confidence,
                skill_type=payload.skill_type,
                source=payload.source
            )
            db.add(emp_skill)
            db.flush()

        # Add evidence if provided
        if payload.evidence_text:
            evidence = SkillEvidence(
                employee_skill_id=emp_skill.id,
                source_type=payload.source,
                source_reference="manual-entry",
                evidence_text=payload.evidence_text,
                confidence=payload.confidence
            )
            db.add(evidence)

        # Update profile completion score
        employee = db.query(EmployeeProfile).filter(EmployeeProfile.id == employee_id).first()
        if employee:
            from app.services.employee_service import employee_service
            employee.profile_completion = employee_service.calculate_profile_completion(employee)

        db.commit()
        db.refresh(emp_skill)
        return emp_skill


skill_service = SkillService()
