from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
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

    def list_events(
        self,
        *,
        device_id: UUID | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[TelemetryEvent]:
        statement = select(TelemetryEventModel)

        if device_id is not None:
            statement = statement.where(
                TelemetryEventModel.device_id == device_id
            )

        if event_type is not None:
            statement = statement.where(
                TelemetryEventModel.event_type == event_type
            )

        if since is not None:
            statement = statement.where(
                TelemetryEventModel.occurred_at >= since
            )

        statement = statement.order_by(
            TelemetryEventModel.occurred_at.desc()
        ).limit(limit)

        models = self._database_session.execute(statement).scalars().all()

        return [TelemetryEventMapper.to_entity(model) for model in models]

    def count_by_type(
        self,
        *,
        since: datetime | None = None,
        device_id: UUID | None = None,
    ) -> dict[str, int]:
        statement = select(
            TelemetryEventModel.event_type,
            func.count(TelemetryEventModel.event_id),
        )

        if since is not None:
            statement = statement.where(
                TelemetryEventModel.occurred_at >= since
            )

        if device_id is not None:
            statement = statement.where(
                TelemetryEventModel.device_id == device_id
            )

        statement = statement.group_by(TelemetryEventModel.event_type)

        rows = self._database_session.execute(statement).all()

        return {row[0]: int(row[1]) for row in rows}

    def count_per_hour(
        self,
        *,
        since: datetime,
        device_id: UUID | None = None,
    ) -> list[tuple[datetime, int]]:
        bucket = func.date_trunc(
            "hour",
            TelemetryEventModel.occurred_at,
        )

        statement = select(bucket, func.count(TelemetryEventModel.event_id))

        statement = statement.where(
            TelemetryEventModel.occurred_at >= since
        )

        if device_id is not None:
            statement = statement.where(
                TelemetryEventModel.device_id == device_id
            )

        statement = statement.group_by(bucket).order_by(bucket)

        rows = self._database_session.execute(statement).all()

        return [(row[0], int(row[1])) for row in rows]
