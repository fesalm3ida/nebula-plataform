from uuid import UUID

from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus
from app.domain.repositories.session_repository import SessionRepository


class InMemorySessionRepository(SessionRepository):
    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}

    def save(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def find_by_id(self, session_id: UUID) -> Session | None:
        return self._sessions.get(session_id)

    def find_active_by_device_id(
        self,
        device_id: UUID,
    ) -> Session | None:
        return next(
            (
                session
                for session in self._sessions.values()
                if session.device_id == device_id
                and session.status == SessionStatus.ACTIVE
            ),
            None,
        )
