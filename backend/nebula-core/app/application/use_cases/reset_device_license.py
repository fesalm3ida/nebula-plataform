from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import DeviceNotFoundError
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


@dataclass(frozen=True)
class ResetDeviceLicenseCommand:
    device_id: UUID


@dataclass(frozen=True)
class ResetDeviceLicenseResult:
    device_id: UUID
    status: DeviceStatus


class ResetDeviceLicenseUseCase:
    """Operação administrativa: remove a licença do Device.

    O aparelho volta para ``PENDING`` (aguardando ativação), permitindo
    refazer o fluxo de ativação/compra. Útil em suporte e em testes.
    """

    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: ResetDeviceLicenseCommand,
    ) -> ResetDeviceLicenseResult:
        device = self._repository.find_by_id(command.device_id)

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        device.reset_license()
        self._repository.save(device)

        return ResetDeviceLicenseResult(
            device_id=device.device_id,
            status=device.status,
        )
