from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    DeviceAlreadyExpiredError,
    DeviceNotFoundError,
)
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


@dataclass(frozen=True)
class ExpireDeviceCommand:
    device_id: UUID


@dataclass(frozen=True)
class ExpireDeviceResult:
    device_id: UUID
    status: DeviceStatus


class ExpireDeviceUseCase:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: ExpireDeviceCommand,
    ) -> ExpireDeviceResult:
        device = self._repository.find_by_id(command.device_id)

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        if device.status == DeviceStatus.EXPIRED:
            raise DeviceAlreadyExpiredError(
                "Device is already expired."
            )

        device.expire()
        self._repository.save(device)

        return ExpireDeviceResult(
            device_id=device.device_id,
            status=device.status,
        )
