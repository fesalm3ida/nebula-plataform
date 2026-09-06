import pytest

from app.application.exceptions import InvalidCredentialsError
from app.application.security.password_hasher import hash_password
from app.application.use_cases.authenticate_admin import (
    AuthenticateAdminCommand,
    AuthenticateAdminUseCase,
)
from app.domain.entities.admin import Admin
from app.domain.enums.admin_role import AdminRole
from app.infrastructure.admin_store import InMemoryAdminRepository
from app.infrastructure.security.jwt_admin_token_service import (
    JWTAdminTokenService,
)


ADMIN_EMAIL = "admin@nebula.local"
ADMIN_PASSWORD = "correct-horse-battery-staple"


def make_token_service() -> JWTAdminTokenService:
    return JWTAdminTokenService(
        secret_key="test-secret-key-0123456789abcdef",
        issuer="nebula-admin",
        audience="nebula-admin-ui",
    )


def make_repository() -> InMemoryAdminRepository:
    return InMemoryAdminRepository(
        [
            Admin(
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                role=AdminRole.SUPER_ADMIN,
            )
        ]
    )


def test_should_authenticate_admin() -> None:
    use_case = AuthenticateAdminUseCase(
        admin_repository=make_repository(),
        token_service=make_token_service(),
    )

    result = use_case.execute(
        AuthenticateAdminCommand(
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
        )
    )

    assert result.email == ADMIN_EMAIL
    assert result.role == AdminRole.SUPER_ADMIN
    assert result.access_token
    assert result.token_type == "bearer"


def test_should_reject_wrong_password() -> None:
    use_case = AuthenticateAdminUseCase(
        admin_repository=make_repository(),
        token_service=make_token_service(),
    )

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(
            AuthenticateAdminCommand(
                email=ADMIN_EMAIL,
                password="wrong-password",
            )
        )


def test_should_reject_unknown_email() -> None:
    use_case = AuthenticateAdminUseCase(
        admin_repository=InMemoryAdminRepository(),
        token_service=make_token_service(),
    )

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(
            AuthenticateAdminCommand(
                email="nobody@nebula.local",
                password=ADMIN_PASSWORD,
            )
        )


def test_should_normalize_email() -> None:
    admin = Admin(
        email="  ADMIN@NEBULA.LOCAL  ",
        password_hash=hash_password(ADMIN_PASSWORD),
        role=AdminRole.ADMIN,
    )

    assert admin.email == "admin@nebula.local"
