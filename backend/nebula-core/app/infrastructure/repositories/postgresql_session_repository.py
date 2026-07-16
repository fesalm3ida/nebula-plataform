from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.persistence.mappers.session_mapper import (
    SessionMapper,
)
from app.infrastructure.persistence.models.session_model import (
    SessionModel,
)


class PostgreSQLSessionRepository(SessionRepository):
    def __init__(
        self,
        database_session: SQLAlchemySession,
    ) -> None:
        self._database_session = database_session

    def save(self, session: Session) -> None:
        model = SessionMapper.to_model(session)

        self._database_session.merge(model)
        self._database_session.commit()

    def find_by_id(
        self,
        session_id: UUID,
    ) -> Session | None:
        statement = select(SessionModel).where(
            SessionModel.session_id == session_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return SessionMapper.to_domain(model)

    def find_active_by_device_id(
        self,
        device_id: UUID,
    ) -> Session | None:
        statement = select(SessionModel).where(
            SessionModel.device_id == device_id,
            SessionModel.status == SessionStatus.ACTIVE.value,
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return SessionMapper.to_domain(model)
