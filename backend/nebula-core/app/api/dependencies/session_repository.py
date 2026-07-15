from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.repositories.postgresql_session_repository import (
    PostgreSQLSessionRepository,
)


def get_session_repository(
    database_session: Annotated[
        SQLAlchemySession,
        Depends(get_db),
    ],
) -> SessionRepository:
    return PostgreSQLSessionRepository(database_session)
