from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    DeviceAlreadyActiveError,
    DeviceNotFoundError,
)
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


@dataclass(frozen=True)
class ActivateDeviceCommand:
    device_id: UUID


@dataclass(frozen=True)
class ActivateDeviceResult:
    device_id: UUID
    status: DeviceStatus


class ActivateDeviceUseCase:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: ActivateDeviceCommand,
    ) -> ActivateDeviceResult:
        device = self._repository.find_by_id(command.device_id)

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        if device.status == DeviceStatus.ACTIVE:
            raise DeviceAlreadyActiveError(
                "Device is already active."
            )

        device.activate()
        self._repository.save(device)

        return ActivateDeviceResult(
            device_id=device.device_id,
            status=device.status,
        )
