from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import EmployeeDetailResponse, EmployeeResponse, ProfileUpdate
from app.services.employee_service import employee_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=EmployeeDetailResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve currently authenticated employee's profile."""
    profile = employee_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user account"
        )
    return profile


@router.put("/me", response_model=EmployeeResponse)
def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update currently authenticated employee's profile."""
    profile = employee_service.update_my_profile(db, current_user, payload)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user account"
        )
    return profile
