"""Database plumbing: connection pool, sessions and the injectable DbSession.
"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

# The engine owns the pool of connections to PostgreSQL.
# pool_pre_ping=True tests a connection before using it, so a restarted database
# does not cause a random error on the next request.
engine = create_engine(get_settings().database_url, pool_pre_ping=True)

# A "session" is one unit of work with the database (like a JPA EntityManager).
# autoflush=False       -> we decide when SQL is sent.
# expire_on_commit=False -> objects stay readable after commit(); we return them in responses.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class of every entity (table) class. Alembic reads its metadata."""


def get_db() -> Iterator[Session]:
    """Give ONE request its own session, and always close it afterwards.

    `yield` hands the session to the route function; the code after `yield`
    runs when the request is finished, even if an error happened (the finally block).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI dependency injection (like @Autowired): write `db: DbSession` as a route
# parameter and FastAPI calls get_db() and passes the session in.
DbSession = Annotated[Session, Depends(get_db)]
