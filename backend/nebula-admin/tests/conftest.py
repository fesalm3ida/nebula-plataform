from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.admin_repository import get_admin_repository
from app.api.dependencies.admin_token_service import get_admin_token_service
from app.api.dependencies.nebula_core_gateway import get_nebula_core_gateway
from app.application.exceptions import CoreResourceNotFoundError
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
        self._devices: list[CoreDevice] = []
        self._assignments: list[CorePlaylistAssignment] = []
        self._license_type: str | None = None
        self._own_playlist: CorePlaylist | None = None

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

    async def list_devices(self) -> list[CoreDevice]:
        return list(self._devices)

    def add_device(self, status: str = "pending") -> CoreDevice:
        device = CoreDevice(
            device_id=uuid4(),
            platform="android_tv",
            status=status,
            app_version="0.1.0",
            created_at="2026-09-14T00:00:00Z",
        )
        self._devices.append(device)

        return device

    async def set_device_status(
        self,
        device_id: UUID,
        action: str,
    ) -> CoreDeviceStatus:
        status_by_action = {
            "activate": "active",
            "block": "blocked",
            "revoke": "revoked",
        }
        new_status = status_by_action[action]

        if not any(item.device_id == device_id for item in self._devices):
            raise CoreResourceNotFoundError("Device not found.")

        self._devices = [
            CoreDevice(
                device_id=item.device_id,
                platform=item.platform,
                status=(
                    new_status if item.device_id == device_id else item.status
                ),
                app_version=item.app_version,
                created_at=item.created_at,
            )
            for item in self._devices
        ]

        return CoreDeviceStatus(device_id=device_id, status=new_status)

    async def authenticate_portal(
        self,
        mac_address: str,
        activation_code: str,
    ) -> CorePortalSession:
        if not self._devices:
            self.add_device()

        device = self._devices[0]

        return CorePortalSession(
            access_token=f"device-token-{device.device_id}",
            token_type="bearer",
            expires_at="2026-09-14T12:00:00Z",
            device_id=device.device_id,
            device_status=device.status,
        )

    async def get_device_license(self, token: str) -> CoreLicense:
        if not self._devices:
            self.add_device()

        device = self._devices[0]

        return CoreLicense(
            device_id=device.device_id,
            status=device.status,
            license_type=self._license_type,
            activated_at=None,
            expires_at=None,
            days_remaining=7 if self._license_type else None,
            expired=False,
        )

    async def activate_device(self, token: str) -> CoreLicense:
        self._license_type = "trial"

        return await self.get_device_license(token)

    async def get_own_playlist(self, token: str) -> CorePlaylist | None:
        return self._own_playlist

    async def register_own_playlist(
        self,
        token: str,
        name: str,
        source_url: str,
        format: str,
    ) -> CorePlaylist:
        playlist = CorePlaylist(
            playlist_id=uuid4(),
            name=name,
            format=format,
            source_url=source_url,
            status="active",
        )
        self._own_playlist = playlist

        return playlist

    async def sync_payments(self, token: str) -> CoreLicense:
        self._license_type = self._license_type or "trial"

        return await self.get_device_license(token)

    async def list_plans(self, token: str) -> list[CorePlan]:
        return [
            CorePlan(
                product="annual",
                title="Licença anual",
                description="12 meses de acesso, renovável.",
                price_cents=9900,
                price_label="R$ 99,00",
            ),
            CorePlan(
                product="lifetime",
                title="Licença vitalícia",
                description="Acesso para sempre, sem renovação.",
                price_cents=29900,
                price_label="R$ 299,00",
            ),
        ]

    async def create_purchase(
        self,
        token: str,
        product: str,
    ) -> CorePurchase:
        return CorePurchase(
            payment_id=uuid4(),
            checkout_url="https://checkout.mercadopago.fake/abc",
        )

    async def assign_playlist_to_device(
        self,
        device_id: UUID,
        playlist_id: UUID,
    ) -> CorePlaylistAssignment:
        assignment = CorePlaylistAssignment(
            assignment_id=uuid4(),
            device_id=device_id,
            playlist_id=playlist_id,
            status="active",
        )
        self._assignments.append(assignment)

        return assignment


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
