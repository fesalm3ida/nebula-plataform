from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.api.dependencies.payment_gateway import get_payment_gateway
from app.api.dependencies.payment_repository import (
    get_payment_repository,
)
from app.api.schemas.license import LicenseResponse
from app.api.schemas.payment import (
    LicensePlanResponse,
    PlansResponse,
    PurchaseRequest,
    PurchaseResponse,
    WebhookPayload,
)
from app.api.security.current_portal_device import (
    get_current_portal_device,
)
from app.application.exceptions import PaymentGatewayError
from app.application.ports.payment_gateway import PaymentGateway
from app.application.use_cases.confirm_payment import (
    ConfirmPaymentCommand,
    ConfirmPaymentUseCase,
)
from app.application.use_cases.create_license_purchase import (
    CreateLicensePurchaseCommand,
    CreateLicensePurchaseUseCase,
)
from app.application.use_cases.get_device_license import (
    GetDeviceLicenseUseCase,
)
from app.application.use_cases.sync_device_payments import (
    SyncDevicePaymentsUseCase,
)
from app.core.config import get_settings
from app.domain.entities.device import Device
from app.domain.enums.license_product import LicenseProduct
from app.domain.licensing.catalog import list_plans
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.payment_repository import PaymentRepository


router = APIRouter(
    tags=["Payments"],
)


@router.get(
    "/me/plans",
    response_model=PlansResponse,
    status_code=status.HTTP_200_OK,
    summary="License Plans",
    description="Planos de licença disponíveis para compra.",
)
def list_license_plans(
    _: Device = Depends(get_current_portal_device),
) -> PlansResponse:
    return PlansResponse(
        plans=[
            LicensePlanResponse(
                product=plan.product,
                title=plan.title,
                description=plan.description,
                price_cents=plan.price_cents,
                price_label=plan.price_label,
            )
            for plan in list_plans()
        ]
    )


@router.post(
    "/me/purchase",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Purchase License",
    description=(
        "Inicia a compra de uma licença e devolve a URL do checkout do "
        "Mercado Pago."
    ),
)
async def purchase_license(
    payload: PurchaseRequest,
    current_device: Device = Depends(get_current_portal_device),
    payment_repository: PaymentRepository = Depends(
        get_payment_repository
    ),
    gateway: PaymentGateway = Depends(get_payment_gateway),
) -> PurchaseResponse:
    use_case = CreateLicensePurchaseUseCase(
        payment_repository=payment_repository,
        gateway=gateway,
    )

    try:
        result = await use_case.execute(
            CreateLicensePurchaseCommand(
                device=current_device,
                product=LicenseProduct(payload.product),
                notification_url=(
                    get_settings().mercadopago_notification_url
                ),
                back_url=get_settings().mercadopago_back_url,
            )
        )
    except PaymentGatewayError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return PurchaseResponse(
        payment_id=result.payment_id,
        checkout_url=result.checkout_url,
    )


@router.post(
    "/webhooks/mercadopago",
    status_code=status.HTTP_200_OK,
    summary="Mercado Pago Webhook",
    description=(
        "Recebe notificações do Mercado Pago, consulta o pagamento e, se "
        "aprovado, concede a licença."
    ),
)
async def mercadopago_webhook(
    payload: WebhookPayload,
    payment_repository: PaymentRepository = Depends(
        get_payment_repository
    ),
    device_repository: DeviceRepository = Depends(
        get_device_repository
    ),
    gateway: PaymentGateway = Depends(get_payment_gateway),
) -> dict[str, str]:
    provider_payment_id = _extract_payment_id(payload)

    if provider_payment_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Missing payment id.",
        )

    use_case = ConfirmPaymentUseCase(
        payment_repository=payment_repository,
        device_repository=device_repository,
        gateway=gateway,
    )

    try:
        result = await use_case.execute(
            ConfirmPaymentCommand(
                provider_payment_id=provider_payment_id,
            )
        )
    except PaymentGatewayError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return {"status": "ok", "approved": str(result.approved).lower()}


@router.post(
    "/me/payments/sync",
    response_model=LicenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Sync Payments (confirm pending payment)",
    description=(
        "Confirma os pagamentos pendentes do Device consultando o provedor. "
        "Usado pelo portal quando a notificação (webhook) não chega."
    ),
)
async def sync_payments(
    current_device: Device = Depends(get_current_portal_device),
    payment_repository: PaymentRepository = Depends(
        get_payment_repository
    ),
    device_repository: DeviceRepository = Depends(
        get_device_repository
    ),
    gateway: PaymentGateway = Depends(get_payment_gateway),
) -> LicenseResponse:
    use_case = SyncDevicePaymentsUseCase(
        payment_repository=payment_repository,
        device_repository=device_repository,
        gateway=gateway,
    )

    try:
        result = await use_case.execute(current_device)
    except PaymentGatewayError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    license_result = GetDeviceLicenseUseCase().execute(result.device)

    return LicenseResponse(
        device_id=license_result.device_id,
        status=license_result.status,
        license_type=license_result.license_type,
        activated_at=license_result.activated_at,
        expires_at=license_result.expires_at,
        days_remaining=license_result.days_remaining,
        expired=license_result.expired,
    )


def _extract_payment_id(payload: WebhookPayload) -> str | None:
    data = payload.data or {}

    if data.get("id"):
        return str(data["id"])

    if payload.id:
        return payload.id

    return None
