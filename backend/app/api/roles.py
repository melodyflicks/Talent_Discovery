from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.core.security import get_current_user, require_hr_or_admin
from app.db.session import get_db
from app.models.domain import Role, RoleSkill, User
from app.schemas.common import RoleCreate, RoleResponse
from app.services.skill_service import skill_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=List[RoleResponse])
def list_roles(
    department: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active roles with required skills."""
    query = db.query(Role).options(
        joinedload(Role.required_skills).joinedload(RoleSkill.skill)
    ).filter(Role.is_active == True)
    if department:
        query = query.filter(Role.department.ilike(f"%{department}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get single role details with required skills."""
    role = (
        db.query(Role)
        .options(joinedload(Role.required_skills).joinedload(RoleSkill.skill))
        .filter(Role.id == role_id)
        .first()
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    current_user: User = Depends(require_hr_or_admin),
    db: Session = Depends(get_db),
):
    """Create a new role with required skills (HR/Admin only)."""
    role = Role(
        title=payload.title,
        department=payload.department,
        description=payload.description,
        level=payload.level,
        is_active=True
    )
    db.add(role)
    db.flush()

    for item in payload.required_skills:
        if item.skill_id:
            s_id = item.skill_id
        elif item.skill_name:
            sk = skill_service.get_or_create_skill(db, item.skill_name)
            s_id = sk.id
        else:
            continue

        rs = RoleSkill(
            role_id=role.id,
            skill_id=s_id,
            required_proficiency=item.required_proficiency,
            importance=item.importance
        )
        db.add(rs)

    db.commit()
    db.refresh(role)
    return role
