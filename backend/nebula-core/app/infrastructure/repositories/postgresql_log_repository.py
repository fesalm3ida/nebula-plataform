from uuid import UUID

from sqlalchemy import select
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
