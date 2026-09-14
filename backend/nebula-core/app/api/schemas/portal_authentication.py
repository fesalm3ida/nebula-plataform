from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.device_status import DeviceStatus


class PortalAuthenticationRequest(BaseModel):
    mac_address: str
    activation_code: str


class PortalAuthenticationResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
    device_id: UUID
    device_status: DeviceStatus
