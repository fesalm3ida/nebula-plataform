from dataclasses import dataclass
from uuid import UUID

from app.application.ports.payment_gateway import (
    PaymentConfirmation,
    PaymentGateway,
)
from app.domain.entities.payment import Payment
from app.domain.licensing.catalog import get_plan
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.payment_repository import PaymentRepository


@dataclass(frozen=True)
class ConfirmPaymentCommand:
    provider_payment_id: str


@dataclass(frozen=True)
class ConfirmPaymentResult:
    payment_id: UUID | None
    approved: bool


class ConfirmPaymentUseCase:
    """Confirma um pagamento (webhook) e concede a licença, se aprovado."""

    def __init__(
        self,
        payment_repository: PaymentRepository,
        device_repository: DeviceRepository,
        gateway: PaymentGateway,
    ) -> None:
        self._payment_repository = payment_repository
        self._device_repository = device_repository
        self._gateway = gateway

    async def execute(
        self,
        command: ConfirmPaymentCommand,
    ) -> ConfirmPaymentResult:
        confirmation = await self._gateway.get_payment(
            command.provider_payment_id
        )

        payment = self._resolve_payment(
            confirmation,
            command.provider_payment_id,
        )

        if payment is None:
            return ConfirmPaymentResult(payment_id=None, approved=False)

        if payment.is_approved:
            return ConfirmPaymentResult(
                payment_id=payment.payment_id,
                approved=True,
            )

        if not confirmation.is_approved:
            return ConfirmPaymentResult(
                payment_id=payment.payment_id,
                approved=False,
            )

        self._approve_and_grant(payment, confirmation)

        return ConfirmPaymentResult(
            payment_id=payment.payment_id,
            approved=True,
        )

    def _resolve_payment(
        self,
        confirmation: PaymentConfirmation,
        provider_payment_id: str,
    ) -> Payment | None:
        if confirmation.external_reference:
            try:
                payment = self._payment_repository.find_by_id(
                    UUID(confirmation.external_reference)
                )

                if payment is not None:
                    return payment
            except ValueError:
                pass

        return self._payment_repository.find_by_provider_payment_id(
            provider_payment_id
        )

    def _approve_and_grant(
        self,
        payment: Payment,
        confirmation: PaymentConfirmation,
    ) -> None:
        payment.approve(
            provider_payment_id=confirmation.provider_payment_id
        )
        self._payment_repository.save(payment)

        device = self._device_repository.find_by_id(payment.device_id)

        if device is None:
            return

        plan = get_plan(payment.product)
        device.grant_license(plan.license_type)
        self._device_repository.save(device)
