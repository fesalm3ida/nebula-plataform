from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.device_status import DeviceStatus


class DeviceActivationResponse(BaseModel):
    device_id: UUID
    status: DeviceStatus
