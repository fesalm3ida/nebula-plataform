from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus
from app.infrastructure.persistence.models.session_model import (
    SessionModel,
)


class SessionMapper:
    @staticmethod
    def to_model(session: Session) -> SessionModel:
        if session.last_seen is None:
            raise ValueError(
                "Session cannot be persisted without last_seen."
            )

        return SessionModel(
            session_id=session.session_id,
            device_id=session.device_id,
            status=session.status.value,
            started_at=session.started_at,
            last_seen=session.last_seen,
            expires_at=session.expires_at,
            ended_at=session.ended_at,
        )

    @staticmethod
    def to_domain(model: SessionModel) -> Session:
        return Session(
            device_id=model.device_id,
            expires_at=model.expires_at,
            session_id=model.session_id,
            status=SessionStatus(model.status),
            started_at=model.started_at,
            last_seen=model.last_seen,
            ended_at=model.ended_at,
        )
