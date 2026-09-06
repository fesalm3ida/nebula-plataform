from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums.playlist_assignment_status import (
    PlaylistAssignmentStatus,
)
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus


class PlaylistCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    format: PlaylistFormat
    source_url: str = Field(min_length=1, max_length=2048)


class PlaylistUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    source_url: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048,
    )


class PlaylistStatusRequest(BaseModel):
    status: PlaylistStatus


class PlaylistResponse(BaseModel):
    playlist_id: UUID
    name: str
    format: PlaylistFormat
    source_url: str
    status: PlaylistStatus
    created_at: datetime
    updated_at: datetime


class PlaylistListResponse(BaseModel):
    playlists: list[PlaylistResponse]


class PlaylistAssignmentRequest(BaseModel):
    device_id: UUID
    playlist_id: UUID


class PlaylistAssignmentResponse(BaseModel):
    assignment_id: UUID
    device_id: UUID
    playlist_id: UUID
    status: PlaylistAssignmentStatus
