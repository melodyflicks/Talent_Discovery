from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user, verify_employee_access
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import GenerateMatchRequest, RoleMatchResponse
from app.services.matching_service import matching_service

router = APIRouter(tags=["matching"])


@router.get("/employees/{employee_id}/matches", response_model=List[RoleMatchResponse])
def get_employee_matches(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve evaluated role matches for an employee."""
    verify_employee_access(employee_id, current_user, db)
    matches = matching_service.get_matches_for_employee(db, employee_id)
    if not matches:
        matches = matching_service.generate_matches_for_employee(db, employee_id)
    return matches


@router.post("/employees/{employee_id}/matches/generate", response_model=List[RoleMatchResponse])
def generate_employee_matches(
    employee_id: int,
    payload: GenerateMatchRequest = GenerateMatchRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger role match recalculation for an employee."""
    verify_employee_access(employee_id, current_user, db)
    try:
        return matching_service.generate_matches_for_employee(
            db, employee_id, role_ids=payload.role_ids
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
