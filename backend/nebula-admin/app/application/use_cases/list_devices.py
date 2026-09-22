from dataclasses import dataclass
from uuid import UUID

from app.application.ports.nebula_core_gateway import NebulaCoreGateway


@dataclass(frozen=True)
class DeviceSummary:
    device_id: UUID
    platform: str
    status: str
    app_version: str
    created_at: str
    # Identificacao publica exibida no Player (o usuario usa no portal).
    mac_address: str = ""
    activation_code: str | None = None


@dataclass(frozen=True)
class ListDevicesResult:
    devices: list[DeviceSummary]


class ListDevicesUseCase:
    def __init__(self, gateway: NebulaCoreGateway) -> None:
        self._gateway = gateway

    async def execute(self) -> ListDevicesResult:
        core_devices = await self._gateway.list_devices()

        return ListDevicesResult(
            devices=[
                DeviceSummary(
                    device_id=device.device_id,
                    platform=device.platform,
                    status=device.status,
                    app_version=device.app_version,
                    created_at=device.created_at,
                    mac_address=device.mac_address,
                    activation_code=device.activation_code,
                )
                for device in core_devices
            ]
        )
