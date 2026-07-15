from collections.abc import Generator

from sqlalchemy.orm import Session as SQLAlchemySession

from app.infrastructure.persistence.database import (
    get_database_session,
)


def get_db() -> Generator[
    SQLAlchemySession,
    None,
    None,
]:
    """Expose the SQLAlchemy session as a FastAPI dependency."""

    yield from get_database_session()
