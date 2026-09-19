from fastapi import APIRouter
router = APIRouter(prefix="/profiles", tags=["profiles"])
@router.get("")
def list_profiles(): return []
