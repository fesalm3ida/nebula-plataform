from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    DeviceAlreadyBlockedError,
    DeviceNotFoundError,
)
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


@dataclass(frozen=True)
class BlockDeviceCommand:
    device_id: UUID


@dataclass(frozen=True)
class BlockDeviceResult:
    device_id: UUID
    status: DeviceStatus


class BlockDeviceUseCase:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: BlockDeviceCommand,
    ) -> BlockDeviceResult:
        device = self._repository.find_by_id(command.device_id)

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        if device.status == DeviceStatus.BLOCKED:
            raise DeviceAlreadyBlockedError(
                "Device is already blocked."
            )

        device.block()
        self._repository.save(device)

        return BlockDeviceResult(
            device_id=device.device_id,
            status=device.status,
        )
