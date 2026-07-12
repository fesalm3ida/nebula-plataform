from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.session_status import SessionStatus


class StartSessionRequest(BaseModel):
    device_id: UUID


class StartSessionResponse(BaseModel):
    session_id: UUID
    device_id: UUID
    status: SessionStatus
    started_at: datetime
    expires_at: datetime
