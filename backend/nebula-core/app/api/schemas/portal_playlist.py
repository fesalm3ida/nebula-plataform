from uuid import UUID

from pydantic import BaseModel, Field


class PortalPlaylistRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    source_url: str = Field(min_length=1)
    format: str = "m3u"


class PortalPlaylistResponse(BaseModel):
    assignment_id: UUID
    playlist_id: UUID
    name: str
    format: str
    source_url: str
    status: str


class PortalPlaylistEnvelope(BaseModel):
    playlist: PortalPlaylistResponse | None = None


class PortalPlaylistsResponse(BaseModel):
    playlists: list[PortalPlaylistResponse]
