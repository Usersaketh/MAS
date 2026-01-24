from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.query import router as query_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(query_router)
app.include_router(documents_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
