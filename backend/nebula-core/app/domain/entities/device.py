from dataclasses import dataclass, field
from datetime import timezone, datetime
from uuid import UUID, uuid4

from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion


@dataclass
class Device:
    fingerprint: DeviceFingerprint
    mac_address: MacAddress
    platform: DevicePlatform
    app_version: AppVersion
    device_id: UUID = field(default_factory=uuid4)
    device_key: DeviceKey = field(default_factory=DeviceKey.generate)
    status: DeviceStatus = DeviceStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def activate(self) -> None:
        self.status = DeviceStatus.ACTIVE

    def block(self) -> None:
        self.status = DeviceStatus.BLOCKED

    def revoke(self) -> None:
        self.status = DeviceStatus.REVOKED

    def expire(self) -> None:
        self.status = DeviceStatus.EXPIRED
