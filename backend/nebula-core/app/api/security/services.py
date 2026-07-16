from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.core.config import get_settings
from app.infrastructure.security.jwt_access_token_service import (
    JWTAccessTokenService,
)


def get_access_token_service() -> AccessTokenService:
    settings = get_settings()

    return JWTAccessTokenService(
        secret_key=settings.jwt_secret_key,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        algorithm=settings.jwt_algorithm,
        expiration_minutes=(
            settings.jwt_access_token_expire_minutes
        ),
    )
