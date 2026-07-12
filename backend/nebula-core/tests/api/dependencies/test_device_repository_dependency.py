from app.api.dependencies.device_repository import get_device_repository
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)


def test_should_return_same_device_repository_instance() -> None:
    first_repository = get_device_repository()
    second_repository = get_device_repository()

    assert isinstance(first_repository, InMemoryDeviceRepository)
    assert first_repository is second_repository
