from uuid import UUID

from pydantic import BaseModel


class PlaylistAssignmentRequest(BaseModel):
    device_id: UUID
    playlist_id: UUID


class PlaylistAssignmentResponse(BaseModel):
    assignment_id: UUID
    device_id: UUID
    playlist_id: UUID
    status: str
