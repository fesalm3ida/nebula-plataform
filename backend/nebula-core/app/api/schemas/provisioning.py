from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus


class ProvisionedContentEndpointResponse(BaseModel):
    playlist_id: UUID
    name: str
    format: PlaylistFormat
    source_url: str
    status: PlaylistStatus


class ProvisioningResponse(BaseModel):
    device_id: UUID
    device_status: DeviceStatus
    content_endpoints: list[ProvisionedContentEndpointResponse]
