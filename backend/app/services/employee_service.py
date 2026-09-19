from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.core.security import hash_password
from app.models.domain import User, EmployeeProfile
from app.schemas.common import EmployeeCreate, EmployeeUpdate, ProfileUpdate


class EmployeeService:
    @staticmethod
    def calculate_profile_completion(employee: EmployeeProfile) -> int:
        score = 0
        if employee.designation:
            score += 15
        if employee.department:
            score += 15
        if employee.years_of_experience > 0:
            score += 10
        if employee.education:
            score += 15
        if employee.location:
            score += 10
        if employee.bio:
            score += 15
        if employee.resume_url:
            score += 10
        if employee.skills and len(employee.skills) > 0:
            score += 10
        return min(score, 100)

    @staticmethod
    def list_employees(
        db: Session, skip: int = 0, limit: int = 100, department: Optional[str] = None
    ) -> List[EmployeeProfile]:
        query = db.query(EmployeeProfile).options(joinedload(EmployeeProfile.user))
        if department:
            query = query.filter(EmployeeProfile.department.ilike(f"%{department}%"))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Optional[EmployeeProfile]:
        return (
            db.query(EmployeeProfile)
            .options(
                joinedload(EmployeeProfile.user),
                joinedload(EmployeeProfile.skills),
                joinedload(EmployeeProfile.external_profiles),
            )
            .filter(EmployeeProfile.id == employee_id)
            .first()
        )

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[EmployeeProfile]:
        return (
            db.query(EmployeeProfile)
            .options(
                joinedload(EmployeeProfile.user),
                joinedload(EmployeeProfile.skills),
                joinedload(EmployeeProfile.external_profiles),
            )
            .filter(EmployeeProfile.user_id == user_id)
            .first()
        )

    @staticmethod
    def create_employee(db: Session, payload: EmployeeCreate) -> EmployeeProfile:
        # Create user account
        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role="employee",
            is_active=True,
        )
        db.add(user)
        db.flush()

        # Create profile
        profile = EmployeeProfile(
            user_id=user.id,
            employee_code=payload.employee_code,
            department=payload.department,
            designation=payload.designation,
            years_of_experience=payload.years_of_experience,
            education=payload.education,
            location=payload.location,
            bio=payload.bio,
            resume_url="",
            profile_completion=0,
        )
        profile.profile_completion = EmployeeService.calculate_profile_completion(profile)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_employee(db: Session, employee_id: int, payload: EmployeeUpdate) -> Optional[EmployeeProfile]:
        profile = db.query(EmployeeProfile).filter(EmployeeProfile.id == employee_id).first()
        if not profile:
            return None

        update_dict = payload.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)

        profile.profile_completion = EmployeeService.calculate_profile_completion(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_my_profile(db: Session, user: User, payload: ProfileUpdate) -> Optional[EmployeeProfile]:
        profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
        if not profile:
            return None

        update_dict = payload.model_dump(exclude_unset=True)
        if "full_name" in update_dict:
            user.full_name = update_dict.pop("full_name")

        for key, value in update_dict.items():
            setattr(profile, key, value)

        profile.profile_completion = EmployeeService.calculate_profile_completion(profile)
        db.commit()
        db.refresh(profile)
        return profile


employee_service = EmployeeService()
