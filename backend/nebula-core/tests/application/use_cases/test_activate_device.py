from uuid import uuid4

import pytest

from app.application.exceptions import (
    DeviceAlreadyActiveError,
    DeviceNotFoundError,
)
from app.application.use_cases.activate_device import (
    ActivateDeviceCommand,
    ActivateDeviceUseCase,
)
from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)


def make_pending_device() -> Device:
    return Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )


def test_should_activate_pending_device() -> None:
    repository = InMemoryDeviceRepository()
    device = make_pending_device()
    repository.save(device)

    use_case = ActivateDeviceUseCase(repository)

    result = use_case.execute(
        ActivateDeviceCommand(device_id=device.device_id)
    )

    assert result.device_id == device.device_id
    assert result.status == DeviceStatus.ACTIVE

    stored_device = repository.find_by_id(device.device_id)

    assert stored_device is not None
    assert stored_device.status == DeviceStatus.ACTIVE


def test_should_reject_unknown_device() -> None:
    repository = InMemoryDeviceRepository()
    use_case = ActivateDeviceUseCase(repository)

    with pytest.raises(DeviceNotFoundError, match="not found"):
        use_case.execute(
            ActivateDeviceCommand(device_id=uuid4())
        )


def test_should_reject_already_active_device() -> None:
    repository = InMemoryDeviceRepository()
    device = make_pending_device()
    device.activate()
    repository.save(device)

    use_case = ActivateDeviceUseCase(repository)

    with pytest.raises(
        DeviceAlreadyActiveError,
        match="already active",
    ):
        use_case.execute(
            ActivateDeviceCommand(device_id=device.device_id)
        )
