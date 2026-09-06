from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.api.dependencies.playlist_assignment_repository import (
    get_playlist_assignment_repository,
)
from app.api.dependencies.playlist_repository import (
    get_playlist_repository,
)
from app.api.dependencies.log_repository import get_log_repository
from app.api.dependencies.session_repository import (
    get_session_repository,
)
from app.api.dependencies.telemetry_event_repository import (
    get_telemetry_event_repository,
)
from app.api.security.services import (
    get_access_token_service,
)
from app.application.security.access_token_service import (
    AccessToken,
    AccessTokenService,
)
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.infrastructure.repositories.in_memory_log_repository import (
    InMemoryLogRepository,
)
from app.infrastructure.repositories.in_memory_playlist_assignment_repository import (
    InMemoryPlaylistAssignmentRepository,
)
from app.infrastructure.repositories.in_memory_playlist_repository import (
    InMemoryPlaylistRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from app.infrastructure.repositories.in_memory_telemetry_event_repository import (
    InMemoryTelemetryEventRepository,
)
from app.main import app


class FakeAccessTokenService(AccessTokenService):
    def create_device_access_token(
        self,
        device_id: UUID,
    ) -> AccessToken:
        issued_at = datetime.now(timezone.utc)

        return AccessToken(
            value=f"fake-jwt:{device_id}",
            token_type="bearer",
            issued_at=issued_at,
            expires_at=issued_at + timedelta(minutes=30),
        )

    def validate_device_access_token(
        self,
        token: str,
    ) -> UUID:
        prefix = "fake-jwt:"

        if not token.startswith(prefix):
            raise ValueError("Invalid access token.")

        return UUID(token.removeprefix(prefix))


@pytest.fixture
def device_repository() -> InMemoryDeviceRepository:
    return InMemoryDeviceRepository()


@pytest.fixture
def session_repository() -> InMemorySessionRepository:
    return InMemorySessionRepository()


@pytest.fixture
def playlist_repository() -> InMemoryPlaylistRepository:
    return InMemoryPlaylistRepository()


@pytest.fixture
def playlist_assignment_repository() -> InMemoryPlaylistAssignmentRepository:
    return InMemoryPlaylistAssignmentRepository()


@pytest.fixture
def telemetry_event_repository() -> InMemoryTelemetryEventRepository:
    return InMemoryTelemetryEventRepository()


@pytest.fixture
def log_repository() -> InMemoryLogRepository:
    return InMemoryLogRepository()


@pytest.fixture
def access_token_service() -> AccessTokenService:
    return FakeAccessTokenService()


@pytest.fixture(autouse=True)
def override_dependencies(
    device_repository: InMemoryDeviceRepository,
    session_repository: InMemorySessionRepository,
    playlist_repository: InMemoryPlaylistRepository,
    playlist_assignment_repository: InMemoryPlaylistAssignmentRepository,
    telemetry_event_repository: InMemoryTelemetryEventRepository,
    log_repository: InMemoryLogRepository,
    access_token_service: AccessTokenService,
) -> Generator[None, None, None]:
    app.dependency_overrides[get_device_repository] = (
        lambda: device_repository
    )
    app.dependency_overrides[get_session_repository] = (
        lambda: session_repository
    )
    app.dependency_overrides[get_playlist_repository] = (
        lambda: playlist_repository
    )
    app.dependency_overrides[get_playlist_assignment_repository] = (
        lambda: playlist_assignment_repository
    )
    app.dependency_overrides[get_telemetry_event_repository] = (
        lambda: telemetry_event_repository
    )
    app.dependency_overrides[get_log_repository] = (
        lambda: log_repository
    )
    app.dependency_overrides[get_access_token_service] = (
        lambda: access_token_service
    )

    try:
        yield
    finally:
        app.dependency_overrides.pop(
            get_device_repository,
            None,
        )
        app.dependency_overrides.pop(
            get_session_repository,
            None,
        )
        app.dependency_overrides.pop(
            get_playlist_repository,
            None,
        )
        app.dependency_overrides.pop(
            get_playlist_assignment_repository,
            None,
        )
        app.dependency_overrides.pop(
            get_telemetry_event_repository,
            None,
        )
        app.dependency_overrides.pop(
            get_log_repository,
            None,
        )
        app.dependency_overrides.pop(
            get_access_token_service,
            None,
        )
