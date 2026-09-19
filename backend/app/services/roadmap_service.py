from typing import Any, Dict, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.domain import LearningRoadmap, EmployeeProfile, Role, SkillGap, Course


class RoadmapService:
    @staticmethod
    def get_roadmap_for_employee(db: Session, employee_id: int) -> Optional[LearningRoadmap]:
        roadmap = (
            db.query(LearningRoadmap)
            .options(
                joinedload(LearningRoadmap.target_role).joinedload(Role.required_skills)
            )
            .filter(LearningRoadmap.employee_id == employee_id)
            .order_by(LearningRoadmap.updated_at.desc())
            .first()
        )
        if not roadmap:
            # Auto-generate a default roadmap structure
            roadmap = RoadmapService.generate_default_roadmap(db, employee_id)
        return roadmap

    @staticmethod
    def generate_default_roadmap(db: Session, employee_id: int) -> LearningRoadmap:
        employee = db.query(EmployeeProfile).filter(EmployeeProfile.id == employee_id).first()
        if not employee:
            raise ValueError("Employee not found")

        # Find target role (e.g. higher level in same department or related)
        target_role = db.query(Role).filter(
            Role.department == employee.department,
            Role.is_active == True
        ).first()

        if not target_role:
            target_role = db.query(Role).filter(Role.is_active == True).first()

        target_role_id = target_role.id if target_role else None
        target_role_title = target_role.title if target_role else "Target Career Progression"

        # Construct structured milestone data
        roadmap_data = {
            "title": f"Career Acceleration to {target_role_title}",
            "estimated_months": 6,
            "phases": [
                {
                    "phase": 1,
                    "title": "Foundation & Skill Gap Closure",
                    "duration": "Weeks 1-6",
                    "status": "in_progress",
                    "objectives": [
                        "Complete foundational certifications",
                        "Address high-priority technical gaps",
                        "Review core role expectations"
                    ]
                },
                {
                    "phase": 2,
                    "title": "Applied Project & Cross-Functional Collaboration",
                    "duration": "Weeks 7-16",
                    "status": "pending",
                    "objectives": [
                        "Lead a department-level initiative",
                        "Demonstrate advanced proficiency in primary toolchain",
                        "Receive mentor endorsement on key deliverables"
                    ]
                },
                {
                    "phase": 3,
                    "title": "Leadership & Role Readiness Assessment",
                    "duration": "Weeks 17-24",
                    "status": "pending",
                    "objectives": [
                        "Conduct internal knowledge sharing sessions",
                        "Complete comprehensive role readiness evaluation",
                        "Formal review with Department Lead and HR"
                    ]
                }
            ],
            "progress_percent": 25
        }

        roadmap = LearningRoadmap(
            employee_id=employee_id,
            target_role_id=target_role_id,
            roadmap_data=roadmap_data
        )
        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)
        return roadmap

    @staticmethod
    def create_or_update_roadmap(
        db: Session, employee_id: int, target_role_id: Optional[int] = None, roadmap_data: Optional[Dict[str, Any]] = None
    ) -> LearningRoadmap:
        roadmap = db.query(LearningRoadmap).filter(LearningRoadmap.employee_id == employee_id).first()
        if not roadmap:
            roadmap = LearningRoadmap(
                employee_id=employee_id,
                target_role_id=target_role_id,
                roadmap_data=roadmap_data or {}
            )
            db.add(roadmap)
        else:
            if target_role_id is not None:
                roadmap.target_role_id = target_role_id
            if roadmap_data is not None:
                roadmap.roadmap_data = roadmap_data

        db.commit()
        db.refresh(roadmap)
        return roadmap


roadmap_service = RoadmapService()
