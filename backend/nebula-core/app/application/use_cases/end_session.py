from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.exceptions import (
    SessionAlreadyClosedError,
    SessionNotFoundError,
)
from app.domain.enums.session_status import SessionStatus
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class EndSessionCommand:
    session_id: UUID


@dataclass(frozen=True)
class EndSessionResult:
    session_id: UUID
    status: SessionStatus
    ended_at: datetime


class EndSessionUseCase:
    def __init__(self, repository: SessionRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: EndSessionCommand,
    ) -> EndSessionResult:
        session = self._repository.find_by_id(command.session_id)

        if session is None:
            raise SessionNotFoundError("Session not found.")

        if session.status != SessionStatus.ACTIVE:
            raise SessionAlreadyClosedError(
                f"Session cannot be ended while status is "
                f"{session.status.value}."
            )

        session.end()
        self._repository.save(session)

        if session.ended_at is None:
            raise RuntimeError(
                "Session ended without an ending timestamp."
            )

        return EndSessionResult(
            session_id=session.session_id,
            status=session.status,
            ended_at=session.ended_at,
        )
