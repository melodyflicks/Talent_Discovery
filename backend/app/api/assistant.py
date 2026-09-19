from fastapi import APIRouter
router = APIRouter(prefix="/assistant", tags=["assistant"])
@router.get("/status")
def status(): return {"status": "not-implemented"}
