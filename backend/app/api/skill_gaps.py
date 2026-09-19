from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user, verify_employee_access
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import SkillGapResponse
from app.services.gap_service import gap_service

router = APIRouter(tags=["skill-gaps"])


@router.get("/employees/{employee_id}/skill-gaps", response_model=List[SkillGapResponse])
def get_employee_skill_gaps(
    employee_id: int,
    role_id: Optional[int] = Query(None, description="Filter by target role ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve skill gaps identified for an employee."""
    verify_employee_access(employee_id, current_user, db)
    return gap_service.get_skill_gaps(db, employee_id, role_id=role_id)
