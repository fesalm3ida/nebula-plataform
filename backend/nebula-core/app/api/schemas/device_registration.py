from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums.device_status import DeviceStatus


class DeviceRegistrationRequest(BaseModel):
    fingerprint: str = Field(min_length=64, max_length=64)
    mac_address: str
    platform: str
    app_version: str


class DeviceRegistrationResponse(BaseModel):
    device_id: UUID
    device_key: str
    activation_code: str
    mac_address: str
    status: DeviceStatus
