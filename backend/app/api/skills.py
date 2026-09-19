from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user, require_hr_or_admin, verify_employee_access
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import EmployeeSkillCreate, EmployeeSkillResponse, SkillCreate, SkillResponse
from app.services.skill_service import skill_service

router = APIRouter(tags=["skills"])


@router.get("/skills", response_model=List[SkillResponse])
def list_skills(
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all available skills from the catalog/taxonomy."""
    return skill_service.list_skills(db, category=category, skip=skip, limit=limit)


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    payload: SkillCreate,
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """Add a new skill to the taxonomy (HR/Admin only)."""
    return skill_service.create_skill(db, payload)


@router.get("/employees/{employee_id}/skills", response_model=List[EmployeeSkillResponse])
def get_employee_skills(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all skills for a specific employee."""
    verify_employee_access(employee_id, current_user, db)
    return skill_service.list_employee_skills(db, employee_id)


@router.post("/employees/{employee_id}/skills", response_model=EmployeeSkillResponse, status_code=status.HTTP_201_CREATED)
def add_employee_skill(
    employee_id: int,
    payload: EmployeeSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add or update a skill for an employee."""
    verify_employee_access(employee_id, current_user, db)
    try:
        return skill_service.add_or_update_employee_skill(db, employee_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
