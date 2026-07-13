from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.application.exceptions import (
    ActiveSessionAlreadyExistsError,
    DeviceNotActiveError,
    DeviceNotFoundError,
)
from app.domain.entities.session import Session
from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.session_status import SessionStatus
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class StartSessionCommand:
    device_id: UUID


@dataclass(frozen=True)
class StartSessionResult:
    session_id: UUID
    device_id: UUID
    status: SessionStatus
    started_at: datetime
    expires_at: datetime
    last_seen: datetime


class StartSessionUseCase:
    SESSION_DURATION_MINUTES = 30

    def __init__(
        self,
        device_repository: DeviceRepository,
        session_repository: SessionRepository,
    ) -> None:
        self._device_repository = device_repository
        self._session_repository = session_repository

    def execute(
        self,
        command: StartSessionCommand,
    ) -> StartSessionResult:
        device = self._device_repository.find_by_id(
            command.device_id
        )

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        if device.status != DeviceStatus.ACTIVE:
            raise DeviceNotActiveError(
                f"Device cannot start a Session while status is "
                f"{device.status.value}."
            )

        active_session = (
            self._session_repository.find_active_by_device_id(
                command.device_id
            )
        )

        if active_session is not None:
            raise ActiveSessionAlreadyExistsError(
                "Device already has an active Session."
            )

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.SESSION_DURATION_MINUTES
        )

        session = Session(
            device_id=device.device_id,
            expires_at=expires_at,
        )

        self._session_repository.save(session)

        if session.last_seen is None:
            raise RuntimeError(
                "Session created without a last_seen timestamp."
            )

        return StartSessionResult(
            session_id=session.session_id,
            device_id=session.device_id,
            status=session.status,
            started_at=session.started_at,
            expires_at=session.expires_at,
            last_seen=session.last_seen,
        )

