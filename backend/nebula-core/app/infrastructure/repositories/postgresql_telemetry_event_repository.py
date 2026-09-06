from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.repositories.telemetry_event_repository import (
    TelemetryEventRepository,
)
from app.infrastructure.persistence.mappers.telemetry_event_mapper import (
    TelemetryEventMapper,
)
from app.infrastructure.persistence.models.telemetry_event_model import (
    TelemetryEventModel,
)


class PostgreSQLTelemetryEventRepository(TelemetryEventRepository):
    def __init__(
        self,
        database_session: SQLAlchemySession,
    ) -> None:
        self._database_session = database_session

    def save(self, event: TelemetryEvent) -> None:
        model = TelemetryEventMapper.to_model(event)

        self._database_session.add(model)
        self._database_session.commit()

    def find_by_id(
        self,
        event_id: UUID,
    ) -> TelemetryEvent | None:
        statement = select(TelemetryEventModel).where(
            TelemetryEventModel.event_id == event_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return TelemetryEventMapper.to_domain(model)
