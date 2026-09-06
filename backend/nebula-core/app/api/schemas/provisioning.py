from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus


class ProvisioningResponse(BaseModel):
    playlist_id: UUID
    name: str
    format: PlaylistFormat
    source_url: str
    status: PlaylistStatus
