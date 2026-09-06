from app.application.security.admin_token_service import AdminTokenService
from app.core.config import get_settings
from app.infrastructure.security.jwt_admin_token_service import (
    JWTAdminTokenService,
)


def get_admin_token_service() -> AdminTokenService:
    """Fornece a implementação concreta do AdminTokenService."""

    settings = get_settings()

    return JWTAdminTokenService(
        secret_key=settings.admin_jwt_secret_key,
        issuer=settings.admin_jwt_issuer,
        audience=settings.admin_jwt_audience,
        algorithm=settings.admin_jwt_algorithm,
        expiration_minutes=settings.admin_jwt_access_token_expire_minutes,
    )
