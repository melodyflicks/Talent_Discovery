from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.schemas.common import ChatRequest, ChatResponse
from app.services.assistant_service import assistant_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
def assistant_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Career Assistant conversation endpoint."""
    return assistant_service.process_chat(
        db, current_user, message=payload.message, context=payload.context
    )
