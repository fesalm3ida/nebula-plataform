from app.application.exceptions import (
    DeviceNotActiveError,
    LicenseExpiredError,
)
from app.domain.entities.device import Device
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


class ActivateOwnDeviceUseCase:
    """Primeira ativação feita pelo **dono** no portal.

    A primeira ativação é gratuita e concede o **trial de 7 dias**. Se o
    trial (ou a licença anual) já venceu, a reativação é recusada: é preciso
    adquirir uma licença.
    """

    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def execute(self, device: Device) -> Device:
        if device.status == DeviceStatus.REVOKED:
            raise DeviceNotActiveError("Device is revoked.")

        if device.license_type is not None and device.is_license_expired():
            raise LicenseExpiredError(
                "Device license has expired. A license is required."
            )

        device.activate()
        self._repository.save(device)

        return device
