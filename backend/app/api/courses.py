from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user, verify_employee_access
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import CourseRecommendationResponse, CourseResponse
from app.services.recommendation_service import recommendation_service

router = APIRouter(tags=["courses"])


@router.get("/courses", response_model=List[CourseResponse])
def list_courses(
    skill_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List curated courses from catalog."""
    return recommendation_service.list_courses(
        db, skill_id=skill_id, difficulty=difficulty, skip=skip, limit=limit
    )


@router.get("/employees/{employee_id}/recommendations", response_model=List[CourseRecommendationResponse])
def get_employee_recommendations(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve course recommendations for an employee."""
    verify_employee_access(employee_id, current_user, db)
    return recommendation_service.get_recommendations_for_employee(db, employee_id)
