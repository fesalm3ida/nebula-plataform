from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db
from app.domain.repositories.telemetry_event_repository import (
    TelemetryEventRepository,
)
from app.infrastructure.repositories.postgresql_telemetry_event_repository import (
    PostgreSQLTelemetryEventRepository,
)


def get_telemetry_event_repository(
    database_session: Annotated[
        SQLAlchemySession,
        Depends(get_db),
    ],
) -> TelemetryEventRepository:
    return PostgreSQLTelemetryEventRepository(database_session)
