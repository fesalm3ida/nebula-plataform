from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.admin_role import AdminRole


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
    admin_id: UUID
    email: str
    role: AdminRole
