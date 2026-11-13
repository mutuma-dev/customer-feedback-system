"""Database plumbing (Spring equivalent: DataSource + EntityManager + @Entity base)."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

# The engine owns the connection pool. pool_pre_ping tests a connection before using it.
engine = create_engine(get_settings().database_url, pool_pre_ping=True)

# A session is one unit of work with the database. We open a fresh one per request.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent of every entity class (like putting @Entity on each model)."""


def get_db() -> Iterator[Session]:
    """Open a session for one request and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Use `db: DbSession` as a route parameter and FastAPI injects a session (like @Autowired).
DbSession = Annotated[Session, Depends(get_db)]
