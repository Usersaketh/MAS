from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.documents import router as documents_router
from app.api.routes.observability import router as observability_router
from app.api.routes.query import router as query_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router)
app.include_router(documents_router)
app.include_router(observability_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
