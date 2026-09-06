from uuid import UUID

from pydantic import BaseModel


class DeviceOut(BaseModel):
    device_id: UUID
    platform: str
    status: str
    app_version: str
    created_at: str


class DeviceListResponse(BaseModel):
    devices: list[DeviceOut]
