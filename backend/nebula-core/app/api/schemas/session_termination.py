from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.session_status import SessionStatus


class EndSessionResponse(BaseModel):
    session_id: UUID
    status: SessionStatus
    ended_at: datetime
