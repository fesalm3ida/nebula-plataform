from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies.admin_token_service import get_admin_token_service
from app.api.security.bearer import bearer_scheme
from app.application.security.admin_token_service import (
    AdminPrincipal,
    AdminTokenService,
)


AUTHENTICATE_HEADER = {
    "WWW-Authenticate": "Bearer",
}


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Security(
        bearer_scheme
    ),
    token_service: AdminTokenService = Depends(
        get_admin_token_service
    ),
) -> AdminPrincipal:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers=AUTHENTICATE_HEADER,
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers=AUTHENTICATE_HEADER,
        )

    try:
        principal = token_service.validate_admin_access_token(
            credentials.credentials
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin access token.",
            headers=AUTHENTICATE_HEADER,
        ) from error

    return principal
