from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.application.exceptions import (
    SessionNotActiveError,
    SessionNotFoundError,
    SessionOwnershipError,
)
from app.domain.entities.log import Log
from app.domain.enums.log_level import LogLevel
from app.domain.enums.session_status import SessionStatus
from app.domain.repositories.log_repository import LogRepository
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class IngestLogCommand:
    device_id: UUID
    session_id: UUID
    level: LogLevel
    message: str
    occurred_at: datetime | None = None


@dataclass(frozen=True)
class IngestLogResult:
    log_id: UUID
    occurred_at: datetime
    received_at: datetime


class IngestLogUseCase:
    def __init__(
        self,
        log_repository: LogRepository,
        session_repository: SessionRepository,
    ) -> None:
        self._log_repository = log_repository
        self._session_repository = session_repository

    def execute(
        self,
        command: IngestLogCommand,
    ) -> IngestLogResult:
        session = self._session_repository.find_by_id(command.session_id)

        if session is None:
            raise SessionNotFoundError(
                f"Session {command.session_id} does not exist."
            )

        if session.device_id != command.device_id:
            raise SessionOwnershipError(
                "Session does not belong to the authenticated Device."
            )

        if session.status != SessionStatus.ACTIVE:
            raise SessionNotActiveError(
                "Session is not active."
            )

        log = Log(
            session_id=command.session_id,
            device_id=command.device_id,
            level=command.level,
            message=command.message,
            occurred_at=command.occurred_at
            or datetime.now(timezone.utc),
        )

        self._log_repository.save(log)

        return IngestLogResult(
            log_id=log.log_id,
            occurred_at=log.occurred_at,
            received_at=log.received_at,
        )
