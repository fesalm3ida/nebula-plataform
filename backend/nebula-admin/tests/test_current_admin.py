import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.security.current_admin import get_current_admin
from app.domain.entities.admin import Admin
from app.domain.enums.admin_role import AdminRole
from app.infrastructure.security.jwt_admin_token_service import (
    JWTAdminTokenService,
)


def make_token_service() -> JWTAdminTokenService:
    return JWTAdminTokenService(
        secret_key="test-secret-key-0123456789abcdef",
        issuer="nebula-admin",
        audience="nebula-admin-ui",
    )


def bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_should_return_principal_for_valid_token() -> None:
    service = make_token_service()
    admin = Admin(
        email="admin@nebula.local",
        password_hash="unused",
        role=AdminRole.ADMIN,
    )
    token = service.create_admin_access_token(
        admin.admin_id,
        admin.role,
    ).value

    principal = get_current_admin(bearer(token), service)

    assert principal.admin_id == admin.admin_id
    assert principal.role == AdminRole.ADMIN


def test_should_reject_missing_credentials() -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_admin(None, make_token_service())

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


def test_should_reject_invalid_scheme() -> None:
    credentials = HTTPAuthorizationCredentials(
        scheme="basic",
        credentials="x",
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_admin(credentials, make_token_service())

    assert exc_info.value.status_code == 401


def test_should_reject_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_admin(bearer("invalid-token"), make_token_service())

    assert exc_info.value.status_code == 401
