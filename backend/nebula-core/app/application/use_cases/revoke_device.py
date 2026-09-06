from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    DeviceAlreadyRevokedError,
    DeviceNotFoundError,
)
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


@dataclass(frozen=True)
class RevokeDeviceCommand:
    device_id: UUID


@dataclass(frozen=True)
class RevokeDeviceResult:
    device_id: UUID
    status: DeviceStatus


class RevokeDeviceUseCase:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: RevokeDeviceCommand,
    ) -> RevokeDeviceResult:
        device = self._repository.find_by_id(command.device_id)

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        if device.status == DeviceStatus.REVOKED:
            raise DeviceAlreadyRevokedError(
                "Device is already revoked."
            )

        device.revoke()
        self._repository.save(device)

        return RevokeDeviceResult(
            device_id=device.device_id,
            status=device.status,
        )
