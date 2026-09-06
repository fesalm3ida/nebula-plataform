from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


@dataclass(frozen=True)
class DeviceSummary:
    device_id: UUID
    platform: str
    status: DeviceStatus
    app_version: str
    created_at: datetime


@dataclass(frozen=True)
class ListDevicesResult:
    devices: list[DeviceSummary]


class ListDevicesUseCase:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(self) -> ListDevicesResult:
        devices = self._repository.find_all()

        return ListDevicesResult(
            devices=[
                DeviceSummary(
                    device_id=device.device_id,
                    platform=device.platform.value,
                    status=device.status,
                    app_version=device.app_version.value,
                    created_at=device.created_at,
                )
                for device in devices
            ]
        )
