from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import routers
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(
    title="AI-Powered Talent Discovery & Employee Profiling API",
    description="Backend API for employee skill tracking, role matching, skill gap analysis, learning roadmaps, and HR analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
if not origins:
    origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["system"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that safely verifies database connectivity
    without exposing connection strings, credentials, or internal details.
    """
    db_status = "unavailable"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "unavailable"

    return {
        "status": "ok",
        "database": db_status
    }


# Include all modular API routers
for router in routers:
    app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
