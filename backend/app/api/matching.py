from fastapi import APIRouter
router = APIRouter(prefix="/matching", tags=["matching"])
@router.get("/status")
def status(): return {"status": "not-implemented"}
