from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums.device_status import DeviceStatus


class DeviceAuthenticationRequest(BaseModel):
    device_id: UUID
    device_key: str = Field(min_length=32)
    fingerprint: str = Field(min_length=64, max_length=64)


class DeviceAuthenticationResponse(BaseModel):
    access_token: str
    expires_at: datetime
    device_status: DeviceStatus
