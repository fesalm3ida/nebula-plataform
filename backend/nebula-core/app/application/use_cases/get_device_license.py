from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.device import Device
from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.license_type import LicenseType


@dataclass(frozen=True)
class DeviceLicense:
    device_id: UUID
    status: DeviceStatus
    license_type: LicenseType | None
    activated_at: datetime | None
    expires_at: datetime | None
    days_remaining: int | None
    expired: bool


class GetDeviceLicenseUseCase:
    """Estado de licença do Device autenticado."""

    def execute(self, device: Device) -> DeviceLicense:
        return DeviceLicense(
            device_id=device.device_id,
            status=device.status,
            license_type=device.license_type,
            activated_at=device.activated_at,
            expires_at=device.license_expires_at,
            days_remaining=device.license_days_remaining(),
            expired=device.is_license_expired(),
        )
