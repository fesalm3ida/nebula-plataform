from uuid import UUID

import httpx

from app.application.exceptions import CoreCommunicationError
from app.application.ports.nebula_core_gateway import (
    CorePlaylist,
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
                response.raise_for_status()
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
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as error:
            raise CoreCommunicationError(
                "Failed to reach the Nebula Core."
            ) from error

        return self._to_core_playlist(payload)

    @staticmethod
    def _to_core_playlist(payload: dict) -> CorePlaylist:
        return CorePlaylist(
            playlist_id=UUID(payload["playlist_id"]),
            name=payload["name"],
            format=payload["format"],
            source_url=payload["source_url"],
            status=payload["status"],
        )
