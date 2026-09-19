from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.security import require_hr_or_admin
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import EmployeeResponse, HRAnalyticsResponse, RoleResponse, SkillGapResponse, SkillResponse
from app.services.analytics_service import analytics_service
from app.services.employee_service import employee_service
from app.services.gap_service import gap_service
from app.services.skill_service import skill_service

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get("/analytics", response_model=HRAnalyticsResponse)
def get_hr_analytics(
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """Retrieve complete organization-wide talent analytics."""
    return analytics_service.get_hr_analytics(db)


@router.get("/skills", response_model=List[Dict[str, Any]])
def get_hr_skill_analytics(
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """Retrieve skill distribution and coverage across organization."""
    analytics = analytics_service.get_hr_analytics(db)
    return analytics.skill_distribution


@router.get("/skill-gaps", response_model=List[Dict[str, Any]])
def get_hr_skill_gaps(
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """Retrieve organization-wide skill gap hotspots."""
    analytics = analytics_service.get_hr_analytics(db)
    return analytics.skill_gaps


@router.get("/roles", response_model=List[Dict[str, Any]])
def get_hr_role_demand(
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """Retrieve bench readiness and candidate fulfillment by role."""
    analytics = analytics_service.get_hr_analytics(db)
    return analytics.role_demand


@router.get("/employees", response_model=List[EmployeeResponse])
def get_hr_employees(
    department: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """HR view of all employees with department filtering."""
    return employee_service.list_employees(db, skip=skip, limit=limit, department=department)
