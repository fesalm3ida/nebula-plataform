from app.domain.repositories.device_repository import DeviceRepository
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)


_device_repository = InMemoryDeviceRepository()


def get_device_repository() -> DeviceRepository:
    return _device_repository
