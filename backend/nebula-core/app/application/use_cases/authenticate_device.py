from dataclasses import dataclass
from datetime import datetime
from hmac import compare_digest
from uuid import UUID

from app.application.exceptions import (
    DeviceNotActiveError,
    DeviceNotFoundError,
    InvalidDeviceCredentialsError,
)
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey


@dataclass(frozen=True)
class AuthenticateDeviceCommand:
    device_id: UUID
    device_key: str
    fingerprint: str


@dataclass(frozen=True)
class AuthenticateDeviceResult:
    access_token: str
    token_type: str
    expires_at: datetime
    device_status: DeviceStatus


class AuthenticateDeviceUseCase:
    def __init__(
        self,
        repository: DeviceRepository,
        access_token_service: AccessTokenService,
    ) -> None:
        self._repository = repository
        self._access_token_service = access_token_service

    def execute(
        self,
        command: AuthenticateDeviceCommand,
    ) -> AuthenticateDeviceResult:
        device = self._repository.find_by_id(
            command.device_id
        )

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        submitted_key = DeviceKey(command.device_key)
        submitted_fingerprint = DeviceFingerprint(
            command.fingerprint
        )

        if not compare_digest(
            str(device.device_key),
            str(submitted_key),
        ):
            raise InvalidDeviceCredentialsError(
                "Invalid Device credentials."
            )

        if not compare_digest(
            str(device.fingerprint),
            str(submitted_fingerprint),
        ):
            raise InvalidDeviceCredentialsError(
                "Invalid Device credentials."
            )

        if device.status != DeviceStatus.ACTIVE:
            raise DeviceNotActiveError(
                f"Device cannot authenticate while status is "
                f"{device.status.value}."
            )

        access_token = (
            self._access_token_service.create_device_access_token(
                device.device_id
            )
        )

        return AuthenticateDeviceResult(
            access_token=access_token.value,
            token_type=access_token.token_type,
            expires_at=access_token.expires_at,
            device_status=device.status,
        )
