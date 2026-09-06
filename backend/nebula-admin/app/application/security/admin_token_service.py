from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.admin_role import AdminRole


@dataclass(frozen=True)
class AdminToken:
    value: str
    token_type: str
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class AdminPrincipal:
    admin_id: UUID
    role: AdminRole


class AdminTokenService(ABC):
    @abstractmethod
    def create_admin_access_token(
        self,
        admin_id: UUID,
        role: AdminRole,
    ) -> AdminToken:
        """Create an access token for an authenticated Admin."""

    @abstractmethod
    def validate_admin_access_token(
        self,
        token: str,
    ) -> AdminPrincipal:
        """Validate an Admin token and return its principal when valid."""
