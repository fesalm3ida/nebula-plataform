from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.admin_repository import get_admin_repository
from app.api.dependencies.admin_token_service import get_admin_token_service
from app.api.dependencies.nebula_core_gateway import get_nebula_core_gateway
from app.application.ports.nebula_core_gateway import (
    CorePlaylist,
    NebulaCoreGateway,
)
from app.application.security.admin_token_service import AdminTokenService
from app.application.security.password_hasher import hash_password
from app.domain.entities.admin import Admin
from app.domain.enums.admin_role import AdminRole
from app.infrastructure.admin_store import InMemoryAdminRepository
from app.infrastructure.security.jwt_admin_token_service import (
    JWTAdminTokenService,
)
from app.main import app


ADMIN_EMAIL = "admin@nebula.local"
ADMIN_PASSWORD = "correct-horse-battery-staple"
ADMIN_ROLE = AdminRole.SUPER_ADMIN
TEST_SECRET = "test-admin-secret-key-0123456789abcdef"


class FakeNebulaCoreGateway(NebulaCoreGateway):
    def __init__(self) -> None:
        self._playlists: list[CorePlaylist] = []

    async def list_playlists(self) -> list[CorePlaylist]:
        return list(self._playlists)

    async def create_playlist(
        self,
        name: str,
        format: str,
        source_url: str,
    ) -> CorePlaylist:
        playlist = CorePlaylist(
            playlist_id=uuid4(),
            name=name,
            format=format,
            source_url=source_url,
            status="active",
        )
        self._playlists.append(playlist)

        return playlist


@pytest.fixture
def admin_repository() -> InMemoryAdminRepository:
    return InMemoryAdminRepository(
        [
            Admin(
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                role=ADMIN_ROLE,
            )
        ]
    )


@pytest.fixture
def admin_token_service() -> AdminTokenService:
    return JWTAdminTokenService(
        secret_key=TEST_SECRET,
        issuer="nebula-admin",
        audience="nebula-admin-ui",
        expiration_minutes=60,
    )


@pytest.fixture
def fake_core_gateway() -> FakeNebulaCoreGateway:
    return FakeNebulaCoreGateway()


@pytest.fixture(autouse=True)
def override_dependencies(
    admin_repository: InMemoryAdminRepository,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> Generator[None, None, None]:
    app.dependency_overrides[get_admin_repository] = lambda: admin_repository
    app.dependency_overrides[get_admin_token_service] = (
        lambda: admin_token_service
    )
    app.dependency_overrides[get_nebula_core_gateway] = (
        lambda: fake_core_gateway
    )

    try:
        yield
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def admin_token_value(service: AdminTokenService) -> str:
    admin = Admin(
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        role=ADMIN_ROLE,
    )

    return service.create_admin_access_token(
        admin.admin_id,
        admin.role,
    ).value
