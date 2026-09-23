from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.device import Device
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress


class DeviceRepository(ABC):
    @abstractmethod
    def save(self, device: Device) -> None:
        """Create or update a Device."""

    @abstractmethod
    def find_by_id(self, device_id: UUID) -> Device | None:
        """Find a Device by its unique identifier."""

    @abstractmethod
    def find_by_mac_address(
        self,
        mac_address: MacAddress,
    ) -> Device | None:
        """Find a Device by its MAC address."""

    @abstractmethod
    def find_by_fingerprint(
        self,
        fingerprint: DeviceFingerprint,
    ) -> Device | None:
        """Find a Device by its fingerprint."""

    @abstractmethod
    def find_by_device_key(
        self,
        device_key: DeviceKey,
    ) -> Device | None:
        """Find a Device by its DeviceKey."""

    @abstractmethod
    def find_all(self) -> list[Device]:
        """Return all registered Devices (ordered by creation)."""

    def delete(self, device_id: UUID) -> None:
        """Remove o Device. Sessoes, associacoes e telemetria caem em
        cascata pelas chaves estrangeiras."""
        raise NotImplementedError
