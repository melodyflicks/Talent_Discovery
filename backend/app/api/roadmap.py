from fastapi import APIRouter
router = APIRouter(prefix="/roadmap", tags=["roadmap"])
@router.get("/status")
def status(): return {"status": "not-implemented"}
