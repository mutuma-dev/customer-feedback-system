"""Health check endpoint. Docker and the CI pipeline call it to see if the app is alive."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import DbSession

# A router groups related URLs (like a @RestController class). All URLs start with /api.
router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")  # decorator: "when someone sends GET /api/health, call this function"
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))  # if the database is down this line raises an error
    return {"status": "ok"}
