from app.application.ports.nebula_core_gateway import NebulaCoreGateway
from app.core.config import get_settings
from app.infrastructure.clients.httpx_nebula_core_client import (
    HTTPXNebulaCoreClient,
)


def get_nebula_core_gateway() -> NebulaCoreGateway:
    """Fornece o gateway de comunicação com o Nebula Core."""

    settings = get_settings()

    return HTTPXNebulaCoreClient(
        base_url=settings.nebula_core_base_url,
        service_token=settings.nebula_core_service_token,
    )
