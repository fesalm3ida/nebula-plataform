from dataclasses import dataclass
from uuid import UUID

from app.application.ports.payment_gateway import (
    CheckoutRequest,
    PaymentGateway,
)
from app.domain.entities.device import Device
from app.domain.entities.payment import Payment
from app.domain.enums.license_product import LicenseProduct
from app.domain.licensing.catalog import get_plan
from app.domain.repositories.payment_repository import PaymentRepository


@dataclass(frozen=True)
class CreateLicensePurchaseCommand:
    device: Device
    product: LicenseProduct
    notification_url: str | None = None


@dataclass(frozen=True)
class CreateLicensePurchaseResult:
    payment_id: UUID
    checkout_url: str


class CreateLicensePurchaseUseCase:
    """Inicia a compra de uma licença: cria o Payment e o checkout."""

    def __init__(
        self,
        payment_repository: PaymentRepository,
        gateway: PaymentGateway,
    ) -> None:
        self._payment_repository = payment_repository
        self._gateway = gateway

    async def execute(
        self,
        command: CreateLicensePurchaseCommand,
    ) -> CreateLicensePurchaseResult:
        plan = get_plan(command.product)

        payment = Payment(
            device_id=command.device.device_id,
            product=command.product,
            amount_cents=plan.price_cents,
        )

        checkout = await self._gateway.create_checkout(
            CheckoutRequest(
                title=plan.title,
                unit_price_cents=plan.price_cents,
                external_reference=str(payment.payment_id),
                notification_url=command.notification_url,
            )
        )

        payment.provider_reference = checkout.provider_reference
        payment.checkout_url = checkout.checkout_url
        self._payment_repository.save(payment)

        return CreateLicensePurchaseResult(
            payment_id=payment.payment_id,
            checkout_url=checkout.checkout_url,
        )
