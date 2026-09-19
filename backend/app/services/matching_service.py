from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.domain import Role, RoleSkill, RoleMatch, EmployeeSkill, EmployeeProfile, SkillGap, Skill


class MatchingService:
    IMPORTANCE_WEIGHTS = {
        "critical": 1.5,
        "high": 1.2,
        "medium": 1.0,
        "nice-to-have": 0.8,
        "low": 0.8
    }

    @staticmethod
    def get_matches_for_employee(db: Session, employee_id: int) -> List[RoleMatch]:
        return (
            db.query(RoleMatch)
            .options(
                joinedload(RoleMatch.role).joinedload(Role.required_skills).joinedload(RoleSkill.skill)
            )
            .filter(RoleMatch.employee_id == employee_id)
            .order_by(RoleMatch.match_score.desc())
            .all()
        )

    @staticmethod
    def generate_matches_for_employee(
        db: Session, employee_id: int, role_ids: Optional[List[int]] = None
    ) -> List[RoleMatch]:
        # 1. Fetch employee and their skills
        employee = db.query(EmployeeProfile).filter(EmployeeProfile.id == employee_id).first()
        if not employee:
            raise ValueError("Employee not found")

        emp_skills = (
            db.query(EmployeeSkill)
            .options(joinedload(EmployeeSkill.skill))
            .filter(EmployeeSkill.employee_id == employee_id)
            .all()
        )
        emp_skill_map = {es.skill.name.lower(): es for es in emp_skills if es.skill}

        # 2. Fetch roles to evaluate
        role_query = db.query(Role).options(
            joinedload(Role.required_skills).joinedload(RoleSkill.skill)
        ).filter(Role.is_active == True)
        if role_ids:
            role_query = role_query.filter(Role.id.in_(role_ids))
        roles = role_query.all()

        results = []
        for role in roles:
            if not role.required_skills:
                continue

            total_weight = 0.0
            earned_weight = 0.0
            matching = []
            missing = []

            for rs in role.required_skills:
                skill_name = rs.skill.name if rs.skill else "Unknown"
                weight = MatchingService.IMPORTANCE_WEIGHTS.get(rs.importance.lower(), 1.0)
                total_weight += weight

                es = emp_skill_map.get(skill_name.lower())
                if es:
                    ratio = min(es.proficiency / max(rs.required_proficiency, 1), 1.2)
                    earned_weight += weight * min(ratio, 1.0)
                    matching.append({
                        "skill_id": rs.skill_id,
                        "skill_name": skill_name,
                        "current_proficiency": es.proficiency,
                        "required_proficiency": rs.required_proficiency,
                        "importance": rs.importance
                    })
                else:
                    missing.append({
                        "skill_id": rs.skill_id,
                        "skill_name": skill_name,
                        "required_proficiency": rs.required_proficiency,
                        "importance": rs.importance
                    })

            score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0.0

            explanation = (
                f"Candidate matches {len(matching)} of {len(role.required_skills)} required skills "
                f"for {role.title} ({role.level}) with an overall suitability score of {score}%."
            )

            # Check if record exists
            match_rec = (
                db.query(RoleMatch)
                .filter(RoleMatch.employee_id == employee_id, RoleMatch.role_id == role.id)
                .first()
            )
            if match_rec:
                match_rec.match_score = score
                match_rec.matching_skills = matching
                match_rec.missing_skills = missing
                match_rec.explanation = explanation
            else:
                match_rec = RoleMatch(
                    employee_id=employee_id,
                    role_id=role.id,
                    match_score=score,
                    matching_skills=matching,
                    missing_skills=missing,
                    explanation=explanation
                )
                db.add(match_rec)

            results.append(match_rec)

        db.commit()
        return MatchingService.get_matches_for_employee(db, employee_id)


matching_service = MatchingService()
