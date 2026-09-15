from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies.nebula_core_gateway import (
    get_nebula_core_gateway,
)
from app.api.schemas.portal import (
    PortalDeviceResponse,
    PortalLicenseOut,
    PortalLoginRequest,
    PortalLoginResponse,
    PortalPlanOut,
    PortalPlansResponse,
    PortalPlaylistOut,
    PortalPlaylistRequest,
    PortalPurchaseRequest,
    PortalPurchaseResponse,
)
from app.application.exceptions import (
    CoreAuthenticationError,
    CoreCommunicationError,
    CoreConflictError,
    CoreResourceNotFoundError,
)
from app.application.ports.nebula_core_gateway import (
    CoreLicense,
    CorePlan,
    CorePlaylist,
    CorePortalSession,
    CorePurchase,
    NebulaCoreGateway,
)


router = APIRouter(
    prefix="/portal",
    tags=["User Portal"],
)


def _raise_http_error(error: Exception) -> None:
    if isinstance(error, CoreAuthenticationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MAC Address ou código de ativação inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    if isinstance(error, CoreResourceNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    if isinstance(error, CoreConflictError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(error),
    ) from error


def get_device_token(
    authorization: str | None = Header(default=None),
) -> str:
    """Extrai o token do Device enviado pelo portal."""
    if authorization is None or not authorization.lower().startswith(
        "bearer "
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing device token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return authorization.split(" ", 1)[1].strip()


def _to_license(license: CoreLicense) -> PortalLicenseOut:
    return PortalLicenseOut(
        status=license.status,
        license_type=license.license_type,
        activated_at=license.activated_at,
        expires_at=license.expires_at,
        days_remaining=license.days_remaining,
        expired=license.expired,
    )


def _to_playlist(playlist: CorePlaylist) -> PortalPlaylistOut:
    return PortalPlaylistOut(
        playlist_id=playlist.playlist_id,
        name=playlist.name,
        format=playlist.format,
        source_url=playlist.source_url,
        status=playlist.status,
    )


@router.post(
    "/auth/login",
    response_model=PortalLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Portal Login",
    description=(
        "Login do usuário com o MAC Address e o código de ativação "
        "exibidos pelo Nebula Player."
    ),
)
async def portal_login(
    payload: PortalLoginRequest,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PortalLoginResponse:
    try:
        session: CorePortalSession = await gateway.authenticate_portal(
            mac_address=payload.mac_address,
            activation_code=payload.activation_code,
        )
    except (
        CoreAuthenticationError,
        CoreCommunicationError,
        CoreConflictError,
        CoreResourceNotFoundError,
    ) as error:
        _raise_http_error(error)

    return PortalLoginResponse(
        access_token=session.access_token,
        token_type=session.token_type,
        expires_at=session.expires_at,
        device_id=session.device_id,
        device_status=session.device_status,
    )


@router.get(
    "/device",
    response_model=PortalDeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="User Device Overview",
    description="Licença e lista do aparelho do usuário autenticado.",
)
async def portal_device(
    token: str = Depends(get_device_token),
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PortalDeviceResponse:
    try:
        license = await gateway.get_device_license(token)
        playlist = await gateway.get_own_playlist(token)
    except (
        CoreAuthenticationError,
        CoreCommunicationError,
        CoreConflictError,
        CoreResourceNotFoundError,
    ) as error:
        _raise_http_error(error)

    return PortalDeviceResponse(
        device_id=license.device_id,
        license=_to_license(license),
        playlist=_to_playlist(playlist) if playlist is not None else None,
    )


@router.post(
    "/device/activation",
    response_model=PortalDeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Own Device",
    description=(
        "Primeira ativação feita pelo usuário: gratuita e concede o trial "
        "de 7 dias."
    ),
)
async def activate_device(
    token: str = Depends(get_device_token),
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PortalDeviceResponse:
    try:
        license = await gateway.activate_device(token)
        playlist = await gateway.get_own_playlist(token)
    except (
        CoreAuthenticationError,
        CoreCommunicationError,
        CoreConflictError,
        CoreResourceNotFoundError,
    ) as error:
        _raise_http_error(error)

    return PortalDeviceResponse(
        device_id=license.device_id,
        license=_to_license(license),
        playlist=_to_playlist(playlist) if playlist is not None else None,
    )


@router.post(
    "/playlist",
    response_model=PortalPlaylistOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register Own Playlist",
    description="O usuário cadastra a lista do aparelho dele.",
)
async def register_playlist(
    payload: PortalPlaylistRequest,
    token: str = Depends(get_device_token),
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PortalPlaylistOut:
    try:
        playlist = await gateway.register_own_playlist(
            token=token,
            name=payload.name,
            source_url=payload.source_url,
            format=payload.format,
        )
    except (
        CoreAuthenticationError,
        CoreCommunicationError,
        CoreConflictError,
        CoreResourceNotFoundError,
    ) as error:
        _raise_http_error(error)

    return _to_playlist(playlist)


@router.post(
    "/payments/sync",
    response_model=PortalDeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Sync Payments",
    description=(
        "Confirma os pagamentos pendentes do aparelho consultando o "
        "provedor e devolve o estado atualizado."
    ),
)
async def sync_payments(
    token: str = Depends(get_device_token),
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PortalDeviceResponse:
    try:
        license = await gateway.sync_payments(token)
        playlist = await gateway.get_own_playlist(token)
    except (
        CoreAuthenticationError,
        CoreCommunicationError,
        CoreConflictError,
        CoreResourceNotFoundError,
    ) as error:
        _raise_http_error(error)

    return PortalDeviceResponse(
        device_id=license.device_id,
        license=_to_license(license),
        playlist=_to_playlist(playlist) if playlist is not None else None,
    )


@router.get(
    "/plans",
    response_model=PortalPlansResponse,
    status_code=status.HTTP_200_OK,
    summary="License Plans",
    description="Planos de licença disponíveis para compra.",
)
async def list_plans(
    token: str = Depends(get_device_token),
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PortalPlansResponse:
    try:
        plans: list[CorePlan] = await gateway.list_plans(token)
    except (
        CoreAuthenticationError,
        CoreCommunicationError,
        CoreConflictError,
        CoreResourceNotFoundError,
    ) as error:
        _raise_http_error(error)

    return PortalPlansResponse(
        plans=[
            PortalPlanOut(
                product=plan.product,
                title=plan.title,
                description=plan.description,
                price_cents=plan.price_cents,
                price_label=plan.price_label,
            )
            for plan in plans
        ]
    )


@router.post(
    "/purchase",
    response_model=PortalPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Purchase License",
    description="Inicia a compra e devolve a URL do checkout.",
)
async def purchase_license(
    payload: PortalPurchaseRequest,
    token: str = Depends(get_device_token),
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PortalPurchaseResponse:
    try:
        purchase: CorePurchase = await gateway.create_purchase(
            token=token,
            product=payload.product,
        )
    except (
        CoreAuthenticationError,
        CoreCommunicationError,
        CoreConflictError,
        CoreResourceNotFoundError,
    ) as error:
        _raise_http_error(error)

    return PortalPurchaseResponse(
        payment_id=purchase.payment_id,
        checkout_url=purchase.checkout_url,
    )
