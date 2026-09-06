import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.enums.admin_role import AdminRole


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Admin:
    """Identidade administrativa do Nebula Admin (separada da identidade de Device)."""

    email: str
    password_hash: str
    role: AdminRole = AdminRole.ADMIN
    admin_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        self.email = self._normalize_email(self.email)
        self._validate_password_hash(self.password_hash)
        self._validate_role(self.role)

    def is_super_admin(self) -> bool:
        return self.role == AdminRole.SUPER_ADMIN

    @staticmethod
    def _normalize_email(value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("email must be a string")

        normalized = value.strip().lower()

        if not normalized or not EMAIL_PATTERN.match(normalized):
            raise ValueError("email must be a valid email address")

        return normalized

    @staticmethod
    def _validate_password_hash(value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("password_hash cannot be empty")

    @staticmethod
    def _validate_role(value: AdminRole) -> None:
        if not isinstance(value, AdminRole):
            raise ValueError("role must be a valid AdminRole")
