from fastapi import APIRouter
router = APIRouter(prefix="/hr", tags=["hr"])
@router.get("/status")
def status(): return {"status": "not-implemented"}
