from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CorePlaylist:
    """Subconjunto do contrato de Playlist do Core consumido pelo Admin."""

    playlist_id: UUID
    name: str
    format: str
    source_url: str
    status: str


@dataclass(frozen=True)
class CoreDevice:
    """Subconjunto do contrato de Device do Core consumido pelo Admin."""

    device_id: UUID
    platform: str
    status: str
    app_version: str
    created_at: str


@dataclass(frozen=True)
class CoreDeviceStatus:
    """Resultado de uma transição de estado de Device no Core."""

    device_id: UUID
    status: str


@dataclass(frozen=True)
class CorePlaylistAssignment:
    """Subconjunto do contrato de PlaylistAssignment do Core."""

    assignment_id: UUID
    device_id: UUID
    playlist_id: UUID
    status: str


@dataclass(frozen=True)
class CorePortalSession:
    """Sessão do **usuário** no portal (token do Device emitido pelo Core)."""

    access_token: str
    token_type: str
    expires_at: str
    device_id: UUID
    device_status: str


@dataclass(frozen=True)
class CorePlan:
    """Plano de licença vendido no portal."""

    product: str
    title: str
    description: str
    price_cents: int
    price_label: str


@dataclass(frozen=True)
class CorePurchase:
    """Compra iniciada (checkout) no Core."""

    payment_id: UUID
    checkout_url: str


@dataclass(frozen=True)
class CoreLicense:
    """Estado de licença de um Device."""

    device_id: UUID
    status: str
    license_type: str | None
    activated_at: str | None
    expires_at: str | None
    days_remaining: int | None
    expired: bool


class NebulaCoreGateway(ABC):
    """Porta de comunicação com o Nebula Core (único dono do domínio/persistência)."""

    @abstractmethod
    async def list_playlists(self) -> list[CorePlaylist]:
        """List playlists from the Nebula Core."""

    @abstractmethod
    async def create_playlist(
        self,
        name: str,
        format: str,
        source_url: str,
    ) -> CorePlaylist:
        """Create a playlist in the Nebula Core."""

    @abstractmethod
    async def list_devices(self) -> list[CoreDevice]:
        """List devices from the Nebula Core (admin)."""

    @abstractmethod
    async def set_device_status(
        self,
        device_id: UUID,
        action: str,
    ) -> CoreDeviceStatus:
        """Apply a lifecycle action to a device in the Nebula Core (admin).

        ``action`` is one of ``activate``, ``block`` or ``revoke``.
        """

    # --- Portal do usuario (autenticado pelo token do Device) ---------------

    @abstractmethod
    async def authenticate_portal(
        self,
        mac_address: str,
        activation_code: str,
    ) -> CorePortalSession:
        """Autentica o usuario no portal (MAC + codigo de ativacao)."""

    @abstractmethod
    async def get_device_license(self, token: str) -> CoreLicense:
        """Estado de licenca do Device autenticado."""

    @abstractmethod
    async def activate_device(self, token: str) -> CoreLicense:
        """Primeira ativacao (gratuita, concede o trial de 7 dias)."""

    @abstractmethod
    async def get_own_playlist(self, token: str) -> CorePlaylist | None:
        """Lista atualmente associada ao Device."""

    @abstractmethod
    async def register_own_playlist(
        self,
        token: str,
        name: str,
        source_url: str,
        format: str,
    ) -> CorePlaylist:
        """Cadastra a lista do usuario e a associa ao Device dele."""

    @abstractmethod
    async def sync_payments(self, token: str) -> CoreLicense:
        """Confirma pagamentos pendentes e devolve a licenca atualizada."""

    @abstractmethod
    async def list_plans(self, token: str) -> list[CorePlan]:
        """Lista os planos de licenca disponiveis."""

    @abstractmethod
    async def create_purchase(
        self,
        token: str,
        product: str,
    ) -> CorePurchase:
        """Inicia a compra de uma licenca e devolve o checkout."""

    @abstractmethod
    async def assign_playlist_to_device(
        self,
        device_id: UUID,
        playlist_id: UUID,
    ) -> CorePlaylistAssignment:
        """Assign a playlist to a device in the Nebula Core (admin)."""
