from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user, require_admin, require_hr_or_admin, verify_employee_access
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import EmployeeCreate, EmployeeDetailResponse, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import employee_service

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=List[EmployeeResponse])
def list_employees(
    department: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """List all employees (HR and Admin only)."""
    return employee_service.list_employees(db, skip=skip, limit=limit, department=department)


@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
def get_employee(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get employee details. Employees can only access their own profile; HR/Admin can access any."""
    employee = verify_employee_access(employee_id, current_user, db)
    return employee


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new employee profile and user account (Admin only)."""
    return employee_service.create_employee(db, payload)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update employee details. Employees can only update their own profile; HR/Admin can update any."""
    verify_employee_access(employee_id, current_user, db)
    updated = employee_service.update_employee(db, employee_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated
