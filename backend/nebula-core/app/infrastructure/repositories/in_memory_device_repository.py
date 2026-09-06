from uuid import UUID

from app.domain.entities.device import Device
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress


class InMemoryDeviceRepository(DeviceRepository):
    def __init__(self) -> None:
        self._devices: dict[UUID, Device] = {}

    def save(self, device: Device) -> None:
        self._devices[device.device_id] = device

    def find_by_id(self, device_id: UUID) -> Device | None:
        return self._devices.get(device_id)

    def find_by_mac_address(
        self,
        mac_address: MacAddress,
    ) -> Device | None:
        return next(
            (
                device
                for device in self._devices.values()
                if device.mac_address == mac_address
            ),
            None,
        )

    def find_by_fingerprint(
        self,
        fingerprint: DeviceFingerprint,
    ) -> Device | None:
        return next(
            (
                device
                for device in self._devices.values()
                if device.fingerprint == fingerprint
            ),
            None,
        )

    def find_by_device_key(
        self,
        device_key: DeviceKey,
    ) -> Device | None:
        return next(
            (
                device
                for device in self._devices.values()
                if device.device_key == device_key
            ),
            None,
        )

    def find_all(self) -> list[Device]:
        return sorted(
            self._devices.values(),
            key=lambda device: device.created_at,
        )
