from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import DeviceAlreadyRegisteredError
from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress


@dataclass(frozen=True)
class RegisterDeviceCommand:
    fingerprint: str
    mac_address: str
    platform: str
    app_version: str


@dataclass(frozen=True)
class RegisterDeviceResult:
    device_id: UUID
    device_key: str
    status: DeviceStatus


class RegisterDeviceUseCase:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: RegisterDeviceCommand,
    ) -> RegisterDeviceResult:
        fingerprint = DeviceFingerprint(command.fingerprint)
        mac_address = MacAddress(command.mac_address)
        platform = DevicePlatform(command.platform)
        app_version = AppVersion(command.app_version)

        if self._repository.find_by_fingerprint(fingerprint) is not None:
            raise DeviceAlreadyRegisteredError(
                "A Device with this fingerprint is already registered."
            )

        if self._repository.find_by_mac_address(mac_address) is not None:
            raise DeviceAlreadyRegisteredError(
                "A Device with this MAC address is already registered."
            )

        device = Device(
            fingerprint=fingerprint,
            mac_address=mac_address,
            platform=platform,
            app_version=app_version,
        )

        self._repository.save(device)

        return RegisterDeviceResult(
            device_id=device.device_id,
            device_key=str(device.device_key),
            status=device.status,
        )
