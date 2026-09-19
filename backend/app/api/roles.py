from fastapi import APIRouter
router = APIRouter(prefix="/roles", tags=["roles"])
@router.get("")
def list_roles(): return []
