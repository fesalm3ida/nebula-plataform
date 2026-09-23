from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.log import Log
from app.domain.repositories.log_repository import LogRepository
from app.infrastructure.persistence.mappers.log_mapper import LogMapper
from app.infrastructure.persistence.models.log_model import LogModel


class PostgreSQLLogRepository(LogRepository):
    def __init__(
        self,
        database_session: SQLAlchemySession,
    ) -> None:
        self._database_session = database_session

    def save(self, log: Log) -> None:
        model = LogMapper.to_model(log)

        self._database_session.add(model)
        self._database_session.commit()

    def find_by_id(self, log_id: UUID) -> Log | None:
        statement = select(LogModel).where(
            LogModel.log_id == log_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return LogMapper.to_domain(model)

    def list_logs(
        self,
        *,
        device_id: UUID | None = None,
        level: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Log]:
        statement = select(LogModel)

        if device_id is not None:
            statement = statement.where(LogModel.device_id == device_id)

        if level is not None:
            statement = statement.where(LogModel.level == level)

        if since is not None:
            statement = statement.where(LogModel.occurred_at >= since)

        statement = statement.order_by(
            LogModel.occurred_at.desc()
        ).limit(limit)

        models = self._database_session.execute(statement).scalars().all()

        return [LogMapper.to_entity(model) for model in models]

    def count_by_level(
        self,
        *,
        since: datetime | None = None,
        device_id: UUID | None = None,
    ) -> dict[str, int]:
        statement = select(LogModel.level, func.count(LogModel.log_id))

        if since is not None:
            statement = statement.where(LogModel.occurred_at >= since)

        if device_id is not None:
            statement = statement.where(LogModel.device_id == device_id)

        statement = statement.group_by(LogModel.level)

        rows = self._database_session.execute(statement).all()

        return {row[0]: int(row[1]) for row in rows}
