from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.device_status import DeviceStatus


class DeviceSummaryResponse(BaseModel):
    device_id: UUID
    platform: str
    status: DeviceStatus
    app_version: str
    created_at: datetime


class DeviceListResponse(BaseModel):
    devices: list[DeviceSummaryResponse]
