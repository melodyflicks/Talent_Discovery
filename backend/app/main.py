from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routers

app = FastAPI(title="Talent Discovery API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "talent-discovery-api"}

for router in routers:
    app.include_router(router, prefix="/api/v1")
