from dataclasses import dataclass
from datetime import datetime
from hmac import compare_digest
from uuid import UUID

from app.application.exceptions import (
    DeviceNotActiveError,
    DeviceNotFoundError,
    InvalidDeviceCredentialsError,
)
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress


@dataclass(frozen=True)
class AuthenticatePortalCommand:
    mac_address: str
    device_key: str


@dataclass(frozen=True)
class AuthenticatePortalResult:
    access_token: str
    token_type: str
    expires_at: datetime
    device_id: UUID
    device_status: DeviceStatus


class AuthenticatePortalUseCase:
    """Autentica o **dono** do Device no portal web (MAC + Device Key).

    Diferente da autenticação do app, aceita Devices que ainda não estão
    ativos (o dono entra no portal para ativar/licenciar), bloqueando apenas
    Devices revogados.
    """

    def __init__(
        self,
        repository: DeviceRepository,
        access_token_service: AccessTokenService,
    ) -> None:
        self._repository = repository
        self._access_token_service = access_token_service

    def execute(
        self,
        command: AuthenticatePortalCommand,
    ) -> AuthenticatePortalResult:
        mac_address = MacAddress(command.mac_address)

        device = self._repository.find_by_mac_address(mac_address)

        if device is None:
            raise DeviceNotFoundError("Device not found.")

        submitted_key = DeviceKey(command.device_key)

        if not compare_digest(
            str(device.device_key),
            str(submitted_key),
        ):
            raise InvalidDeviceCredentialsError(
                "Invalid Device credentials."
            )

        if device.status == DeviceStatus.REVOKED:
            raise DeviceNotActiveError("Device is revoked.")

        access_token = (
            self._access_token_service.create_device_access_token(
                device.device_id
            )
        )

        return AuthenticatePortalResult(
            access_token=access_token.value,
            token_type=access_token.token_type,
            expires_at=access_token.expires_at,
            device_id=device.device_id,
            device_status=device.status,
        )
