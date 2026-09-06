from uuid import UUID

from pydantic import BaseModel, Field


class PlaylistCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    format: str
    source_url: str = Field(min_length=1, max_length=2048)


class PlaylistOut(BaseModel):
    playlist_id: UUID
    name: str
    format: str
    source_url: str
    status: str


class PlaylistListResponse(BaseModel):
    playlists: list[PlaylistOut]
