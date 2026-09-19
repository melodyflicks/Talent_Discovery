from fastapi import APIRouter
router = APIRouter(prefix="/skill-gaps", tags=["skill-gaps"])
@router.get("/status")
def status(): return {"status": "not-implemented"}
