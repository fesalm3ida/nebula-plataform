from uuid import UUID

import httpx

from app.application.exceptions import (
    CoreCommunicationError,
    CoreConflictError,
    CoreResourceNotFoundError,
)
from app.application.ports.nebula_core_gateway import (
    CoreDevice,
    CoreDeviceStatus,
    CorePlaylist,
    CorePlaylistAssignment,
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

    @staticmethod
    def _ensure_success(response: httpx.Response) -> None:
        """Traduz erros do Core em erros do Admin quando possível."""
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
