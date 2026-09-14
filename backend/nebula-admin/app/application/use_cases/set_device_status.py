from dataclasses import dataclass
from uuid import UUID

from app.application.ports.nebula_core_gateway import (
    CoreDeviceStatus,
    NebulaCoreGateway,
)


@dataclass(frozen=True)
class SetDeviceStatusCommand:
    device_id: UUID
    action: str


class SetDeviceStatusUseCase:
    """Aplica uma ação de ciclo de vida ao Device (executada pelo Core)."""

    ALLOWED_ACTIONS = ("activate", "block", "revoke")

    def __init__(self, gateway: NebulaCoreGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        command: SetDeviceStatusCommand,
    ) -> CoreDeviceStatus:
        if command.action not in self.ALLOWED_ACTIONS:
            raise ValueError(
                f"Unsupported device action: {command.action}"
            )

        return await self._gateway.set_device_status(
            device_id=command.device_id,
            action=command.action,
        )
