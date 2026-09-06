from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.admin_repository import get_admin_repository
from app.api.dependencies.admin_token_service import get_admin_token_service
from app.api.schemas.auth import AdminLoginRequest, AdminLoginResponse
from app.application.exceptions import InvalidCredentialsError
from app.application.security.admin_token_service import AdminTokenService
from app.application.use_cases.authenticate_admin import (
    AuthenticateAdminCommand,
    AuthenticateAdminUseCase,
)
from app.domain.repositories.admin_repository import AdminRepository


router = APIRouter(
    prefix="/admin/auth",
    tags=["Admin Auth"],
)


@router.post(
    "/login",
    response_model=AdminLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin Login",
)
def login(
    payload: AdminLoginRequest,
    admin_repository: AdminRepository = Depends(get_admin_repository),
    token_service: AdminTokenService = Depends(get_admin_token_service),
) -> AdminLoginResponse:
    use_case = AuthenticateAdminUseCase(
        admin_repository=admin_repository,
        token_service=token_service,
    )

    try:
        result = use_case.execute(
            AuthenticateAdminCommand(
                email=payload.email,
                password=payload.password,
            )
        )

    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    return AdminLoginResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        expires_at=result.expires_at,
        admin_id=result.admin_id,
        email=result.email,
        role=result.role,
    )
