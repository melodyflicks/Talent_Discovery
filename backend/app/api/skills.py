from fastapi import APIRouter
router = APIRouter(prefix="/skills", tags=["skills"])
@router.get("")
def list_skills(): return []
