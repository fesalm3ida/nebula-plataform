from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    DeviceHasPaymentsError,
    DeviceNotFoundError,
)
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.payment_repository import PaymentRepository


@dataclass(frozen=True)
class DeleteDeviceCommand:
    device_id: UUID


class DeleteDeviceUseCase:
    """Remove um Device do cadastro.

    Regra: um aparelho **com pagamentos registrados** nao pode ser excluido —
    o pagamento e registro financeiro. Para encerrar o acesso, use
    revogar/bloquear. Aparelhos sem pagamento (tipicamente registros orfaos
    de instalacoes de teste) podem ser removidos.

    Sessoes, associacoes de playlist e telemetria caem em cascata.
    """

    def __init__(
        self,
        device_repository: DeviceRepository,
        payment_repository: PaymentRepository,
    ) -> None:
        self._devices = device_repository
        self._payments = payment_repository

    def execute(self, command: DeleteDeviceCommand) -> None:
        device = self._devices.find_by_id(command.device_id)

        if device is None:
            raise DeviceNotFoundError(
                f"Device {command.device_id} does not exist."
            )

        payments = self._payments.find_all_by_device_id(command.device_id)

        if payments:
            raise DeviceHasPaymentsError(
                "A device with registered payments cannot be deleted. "
                "Revoke or block it instead."
            )

        self._devices.delete(command.device_id)
