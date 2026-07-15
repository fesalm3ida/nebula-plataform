from collections.abc import Generator

import pytest

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.api.dependencies.session_repository import (
    get_session_repository,
)
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from app.main import app


@pytest.fixture
def device_repository() -> InMemoryDeviceRepository:
    return InMemoryDeviceRepository()


@pytest.fixture
def session_repository() -> InMemorySessionRepository:
    return InMemorySessionRepository()


@pytest.fixture(autouse=True)
def override_repositories(
    device_repository: InMemoryDeviceRepository,
    session_repository: InMemorySessionRepository,
) -> Generator[None, None, None]:
    app.dependency_overrides[get_device_repository] = (
        lambda: device_repository
    )
    app.dependency_overrides[get_session_repository] = (
        lambda: session_repository
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
