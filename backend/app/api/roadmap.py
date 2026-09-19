from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user, verify_employee_access
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import RoadmapCreate, RoadmapResponse
from app.services.roadmap_service import roadmap_service

router = APIRouter(tags=["roadmap"])


@router.get("/employees/{employee_id}/roadmap", response_model=RoadmapResponse)
def get_employee_roadmap(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve personalized learning and career acceleration roadmap for an employee."""
    verify_employee_access(employee_id, current_user, db)
    roadmap = roadmap_service.get_roadmap_for_employee(db, employee_id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found for this employee"
        )
    return roadmap


@router.post("/employees/{employee_id}/roadmap", response_model=RoadmapResponse)
def create_or_update_employee_roadmap(
    employee_id: int,
    payload: RoadmapCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update or initialize custom roadmap milestones."""
    verify_employee_access(employee_id, current_user, db)
    return roadmap_service.create_or_update_roadmap(
        db, employee_id, target_role_id=payload.target_role_id, roadmap_data=payload.roadmap_data
    )
