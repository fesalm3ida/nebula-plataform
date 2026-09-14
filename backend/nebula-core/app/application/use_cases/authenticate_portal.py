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
from app.domain.value_objects.activation_code import ActivationCode
from app.domain.value_objects.mac_address import MacAddress


@dataclass(frozen=True)
class AuthenticatePortalCommand:
    mac_address: str
    activation_code: str


@dataclass(frozen=True)
class AuthenticatePortalResult:
    access_token: str
    token_type: str
    expires_at: datetime
    device_id: UUID
    device_status: DeviceStatus


class AuthenticatePortalUseCase:
    """Autentica o **usuário** no portal web (MAC Address + código de 6 dígitos).

    O código de ativação é exibido pelo Nebula Player. Diferente da
    autenticação do app, aceita Devices que ainda não estão ativos (o usuário
    entra no portal para ativar/licenciar), bloqueando apenas os revogados.
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

        try:
            submitted_code = ActivationCode(command.activation_code)
        except (TypeError, ValueError) as error:
            raise InvalidDeviceCredentialsError(
                "Invalid activation code."
            ) from error

        if not compare_digest(
            str(device.activation_code),
            str(submitted_code),
        ):
            raise InvalidDeviceCredentialsError(
                "Invalid activation code."
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
