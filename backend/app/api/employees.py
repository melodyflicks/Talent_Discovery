from fastapi import APIRouter
router = APIRouter(prefix="/employees", tags=["employees"])
@router.get("")
def list_employees(): return []
