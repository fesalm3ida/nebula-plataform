from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.application.exceptions import (
    SessionNotActiveError,
    SessionNotFoundError,
)
from app.domain.enums.session_status import SessionStatus
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class HeartbeatSessionCommand:
    session_id: UUID


@dataclass(frozen=True)
class HeartbeatSessionResult:
    session_id: UUID
    status: SessionStatus
    last_seen: datetime


class HeartbeatSessionUseCase:
    def __init__(
        self,
        repository: SessionRepository,
    ) -> None:
        self._repository = repository

    def execute(
        self,
        command: HeartbeatSessionCommand,
    ) -> HeartbeatSessionResult:
        session = self._repository.find_by_id(
            command.session_id
        )

        if session is None:
            raise SessionNotFoundError("Session not found.")

        if session.status != SessionStatus.ACTIVE:
            raise SessionNotActiveError(
                f"Session cannot receive a heartbeat while status is "
                f"{session.status.value}."
            )

        current_time = datetime.now(timezone.utc)

        if session.is_expired(current_time):
            session.expire()
            self._repository.save(session)

            raise SessionNotActiveError(
                "Session cannot receive a heartbeat because it has expired."
            )

        session.touch(current_time)
        self._repository.save(session)

        if session.last_seen is None:
            raise RuntimeError(
                "Session heartbeat completed without a last_seen timestamp."
            )

        return HeartbeatSessionResult(
            session_id=session.session_id,
            status=session.status,
            last_seen=session.last_seen,
        )
