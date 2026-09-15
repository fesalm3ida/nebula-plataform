from uuid import UUID

import httpx

from app.application.exceptions import (
    CoreAuthenticationError,
    CoreCommunicationError,
    CoreConflictError,
    CoreResourceNotFoundError,
)
from app.application.ports.nebula_core_gateway import (
    CoreDevice,
    CoreDeviceStatus,
    CoreLicense,
    CorePlan,
    CorePlaylist,
    CorePlaylistAssignment,
    CorePortalSession,
    CorePurchase,
    NebulaCoreGateway,
)


class HTTPXNebulaCoreClient(NebulaCoreGateway):
    """Cliente HTTP para o Nebula Core.

    Centraliza toda a comunicação Admin -> Core. Nenhuma outra camada do
    Admin deve usar HTTP diretamente. Permite injetar um ``transport``
    (ex.: ``httpx.MockTransport``) para testes em isolamento.
    """

    def __init__(
        self,
        base_url: str,
        service_token: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_token = service_token
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        return {"X-Admin-Token": self._service_token}

    async def list_playlists(self) -> list[CorePlaylist]:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.get(
                    f"{self._base_url}/playlists",
                    headers=self._headers(),
                )
                self._ensure_success(response)
                data = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return [
            self._to_core_playlist(payload)
            for payload in data.get("playlists", [])
        ]

    async def create_playlist(
        self,
        name: str,
        format: str,
        source_url: str,
    ) -> CorePlaylist:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/playlists",
                    headers=self._headers(),
                    json={
                        "name": name,
                        "format": format,
                        "source_url": source_url,
                    },
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return self._to_core_playlist(payload)

    async def list_devices(self) -> list[CoreDevice]:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.get(
                    f"{self._base_url}/devices",
                    headers=self._headers(),
                )
                self._ensure_success(response)
                data = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return [
            self._to_core_device(payload)
            for payload in data.get("devices", [])
        ]

    async def set_device_status(
        self,
        device_id: UUID,
        action: str,
    ) -> CoreDeviceStatus:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/devices/{device_id}/{action}",
                    headers=self._headers(),
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return CoreDeviceStatus(
            device_id=UUID(payload["device_id"]),
            status=payload["status"],
        )

    async def assign_playlist_to_device(
        self,
        device_id: UUID,
        playlist_id: UUID,
    ) -> CorePlaylistAssignment:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/playlists/assignments",
                    headers=self._headers(),
                    json={
                        "device_id": str(device_id),
                        "playlist_id": str(playlist_id),
                    },
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return self._to_core_assignment(payload)

    # --- Portal do usuario ---------------------------------------------------

    @staticmethod
    def _bearer(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    async def authenticate_portal(
        self,
        mac_address: str,
        activation_code: str,
    ) -> CorePortalSession:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/auth/portal",
                    json={
                        "mac_address": mac_address,
                        "activation_code": activation_code,
                    },
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return CorePortalSession(
            access_token=payload["access_token"],
            token_type=payload["token_type"],
            expires_at=payload["expires_at"],
            device_id=UUID(payload["device_id"]),
            device_status=payload["device_status"],
        )

    async def get_device_license(self, token: str) -> CoreLicense:
        return await self._license_request("GET", "/me/license", token)

    async def activate_device(self, token: str) -> CoreLicense:
        return await self._license_request("POST", "/me/activation", token)

    async def _license_request(
        self,
        method: str,
        path: str,
        token: str,
    ) -> CoreLicense:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.request(
                    method,
                    f"{self._base_url}{path}",
                    headers=self._bearer(token),
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return CoreLicense(
            device_id=UUID(payload["device_id"]),
            status=payload["status"],
            license_type=payload.get("license_type"),
            activated_at=payload.get("activated_at"),
            expires_at=payload.get("expires_at"),
            days_remaining=payload.get("days_remaining"),
            expired=payload["expired"],
        )

    async def get_own_playlist(self, token: str) -> CorePlaylist | None:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.get(
                    f"{self._base_url}/me/playlist",
                    headers=self._bearer(token),
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        playlist = payload.get("playlist")

        if not playlist:
            return None

        return self._to_core_playlist(playlist)

    async def register_own_playlist(
        self,
        token: str,
        name: str,
        source_url: str,
        format: str,
    ) -> CorePlaylist:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/me/playlist",
                    headers=self._bearer(token),
                    json={
                        "name": name,
                        "source_url": source_url,
                        "format": format,
                    },
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return self._to_core_playlist(payload)

    async def sync_payments(self, token: str) -> CoreLicense:
        return await self._license_request(
            "POST",
            "/me/payments/sync",
            token,
        )

    async def list_plans(self, token: str) -> list[CorePlan]:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.get(
                    f"{self._base_url}/me/plans",
                    headers=self._bearer(token),
                )
                self._ensure_success(response)
                data = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return [
            CorePlan(
                product=item["product"],
                title=item["title"],
                description=item["description"],
                price_cents=item["price_cents"],
                price_label=item["price_label"],
            )
            for item in data.get("plans", [])
        ]

    async def create_purchase(
        self,
        token: str,
        product: str,
    ) -> CorePurchase:
        try:
            async with httpx.AsyncClient(transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/me/purchase",
                    headers=self._bearer(token),
                    json={"product": product},
                )
                self._ensure_success(response)
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return CorePurchase(
            payment_id=UUID(payload["payment_id"]),
            checkout_url=payload["checkout_url"],
        )

    @staticmethod
    def _ensure_success(response: httpx.Response) -> None:
        """Traduz erros do Core em erros do Admin quando possível."""
        if response.status_code == 401:
            raise CoreAuthenticationError(
                "Invalid credentials."
            )

        if response.status_code == 404:
            raise CoreResourceNotFoundError(
                "Resource not found in the Nebula Core."
            )

        if response.status_code in (400, 409):
            raise CoreConflictError(
                "Nebula Core rejected the operation "
                f"({response.status_code})."
            )

        response.raise_for_status()

    @staticmethod
    def _to_core_playlist(payload: dict) -> CorePlaylist:
        return CorePlaylist(
            playlist_id=UUID(payload["playlist_id"]),
            name=payload["name"],
            format=payload["format"],
            source_url=payload["source_url"],
            status=payload["status"],
        )

    @staticmethod
    def _to_core_device(payload: dict) -> CoreDevice:
        return CoreDevice(
            device_id=UUID(payload["device_id"]),
            platform=payload["platform"],
            status=payload["status"],
            app_version=payload["app_version"],
            created_at=payload["created_at"],
        )

    @staticmethod
    def _to_core_assignment(payload: dict) -> CorePlaylistAssignment:
        return CorePlaylistAssignment(
            assignment_id=UUID(payload["assignment_id"]),
            device_id=UUID(payload["device_id"]),
            playlist_id=UUID(payload["playlist_id"]),
            status=payload["status"],
        )
