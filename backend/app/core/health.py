"""Health check used by Docker and the CI pipeline."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import DbSession

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))  # proves the database answers
    return {"status": "ok"}
