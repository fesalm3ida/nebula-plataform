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
    # Identificacao publica exibida no Player (usada pelo usuario no portal).
    mac_address: str
    activation_code: str | None = None


class DeviceListResponse(BaseModel):
    devices: list[DeviceSummaryResponse]
