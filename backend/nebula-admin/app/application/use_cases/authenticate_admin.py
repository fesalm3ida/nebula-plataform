from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.exceptions import InvalidCredentialsError
from app.application.security.admin_token_service import (
    AdminTokenService,
)
from app.application.security.password_hasher import verify_password
from app.domain.enums.admin_role import AdminRole
from app.domain.repositories.admin_repository import AdminRepository


@dataclass(frozen=True)
class AuthenticateAdminCommand:
    email: str
    password: str


@dataclass(frozen=True)
class AuthenticateAdminResult:
    admin_id: UUID
    email: str
    role: AdminRole
    access_token: str
    token_type: str
    issued_at: datetime
    expires_at: datetime


class AuthenticateAdminUseCase:
    def __init__(
        self,
        admin_repository: AdminRepository,
        token_service: AdminTokenService,
    ) -> None:
        self._admin_repository = admin_repository
        self._token_service = token_service

    def execute(
        self,
        command: AuthenticateAdminCommand,
    ) -> AuthenticateAdminResult:
        admin = self._admin_repository.find_by_email(command.email)

        if admin is None or not verify_password(
            command.password,
            admin.password_hash,
        ):
            raise InvalidCredentialsError(
                "Invalid administrative credentials."
            )

        token = self._token_service.create_admin_access_token(
            admin.admin_id,
            admin.role,
        )

        return AuthenticateAdminResult(
            admin_id=admin.admin_id,
            email=admin.email,
            role=admin.role,
            access_token=token.value,
            token_type=token.token_type,
            issued_at=token.issued_at,
            expires_at=token.expires_at,
        )
