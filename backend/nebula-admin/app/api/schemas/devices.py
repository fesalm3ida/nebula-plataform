from uuid import UUID

from pydantic import BaseModel


class DeviceOut(BaseModel):
    device_id: UUID
    platform: str
    status: str
    app_version: str
    created_at: str
    mac_address: str = ""
    activation_code: str | None = None


class DeviceListResponse(BaseModel):
    devices: list[DeviceOut]


class DeviceStatusResponse(BaseModel):
    device_id: UUID
    status: str
