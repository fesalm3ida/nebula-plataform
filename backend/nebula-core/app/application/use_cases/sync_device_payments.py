from dataclasses import dataclass

from app.application.ports.payment_gateway import PaymentGateway
from app.domain.entities.device import Device
from app.domain.licensing.catalog import get_plan
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.payment_repository import PaymentRepository


@dataclass(frozen=True)
class SyncDevicePaymentsResult:
    approved: int
    pending: int
    device: Device


class SyncDevicePaymentsUseCase:
    """Confirma os pagamentos pendentes do Device consultando o provedor.

    Complementa o webhook: quando a notificação não chega (ex.: sem URL
    pública configurada), o portal pode pedir a confirmação ativa. Se o
    pagamento estiver aprovado, a licença é concedida na hora.
    """

    def __init__(
        self,
        payment_repository: PaymentRepository,
        device_repository: DeviceRepository,
        gateway: PaymentGateway,
    ) -> None:
        self._payment_repository = payment_repository
        self._device_repository = device_repository
        self._gateway = gateway

    async def execute(self, device: Device) -> SyncDevicePaymentsResult:
        payments = self._payment_repository.find_all_by_device_id(
            device.device_id
        )

        approved = 0
        pending = 0

        for payment in payments:
            if not payment.is_pending:
                continue

            confirmation = await self._gateway.find_payment(
                str(payment.payment_id)
            )

            if confirmation is None or not confirmation.is_approved:
                pending += 1
                continue

            payment.approve(
                provider_payment_id=confirmation.provider_payment_id
            )
            self._payment_repository.save(payment)

            plan = get_plan(payment.product)
            device.grant_license(plan.license_type)
            self._device_repository.save(device)

            approved += 1

        return SyncDevicePaymentsResult(
            approved=approved,
            pending=pending,
            device=device,
        )
