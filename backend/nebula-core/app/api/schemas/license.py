from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.license_type import LicenseType


class LicenseResponse(BaseModel):
    device_id: UUID
    status: DeviceStatus
    license_type: LicenseType | None
    activated_at: datetime | None
    expires_at: datetime | None
    days_remaining: int | None
    expired: bool
