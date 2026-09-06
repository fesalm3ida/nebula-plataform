from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db
from app.domain.repositories.log_repository import LogRepository
from app.infrastructure.repositories.postgresql_log_repository import (
    PostgreSQLLogRepository,
)


def get_log_repository(
    database_session: Annotated[
        SQLAlchemySession,
        Depends(get_db),
    ],
) -> LogRepository:
    return PostgreSQLLogRepository(database_session)
