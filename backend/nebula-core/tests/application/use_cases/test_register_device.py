import pytest

from app.application.exceptions import DeviceAlreadyRegisteredError
from app.application.use_cases.register_device import (
    RegisterDeviceCommand,
    RegisterDeviceUseCase,
)
from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)


def make_command() -> RegisterDeviceCommand:
    return RegisterDeviceCommand(
        fingerprint="a" * 64,
        mac_address="AA:BB:CC:DD:EE:FF",
        platform="android_tv",
        app_version="0.1.0",
    )


def test_should_register_device_as_pending() -> None:
    repository = InMemoryDeviceRepository()
    use_case = RegisterDeviceUseCase(repository)

    result = use_case.execute(make_command())

    assert result.device_id is not None
    assert len(result.device_key) >= 32
    assert result.status == DeviceStatus.PENDING


def test_should_persist_registered_device() -> None:
    repository = InMemoryDeviceRepository()
    use_case = RegisterDeviceUseCase(repository)

    result = use_case.execute(make_command())

    stored_device = repository.find_by_id(result.device_id)

    assert stored_device is not None
    assert stored_device.device_id == result.device_id
    assert stored_device.status == DeviceStatus.PENDING


def test_should_reject_duplicate_fingerprint() -> None:
    repository = InMemoryDeviceRepository()
    use_case = RegisterDeviceUseCase(repository)
    command = make_command()

    use_case.execute(command)

    with pytest.raises(
        DeviceAlreadyRegisteredError,
        match="fingerprint",
    ):
        use_case.execute(command)


def test_should_reject_duplicate_mac_address() -> None:
    repository = InMemoryDeviceRepository()
    use_case = RegisterDeviceUseCase(repository)

    use_case.execute(make_command())

    duplicate_mac_command = RegisterDeviceCommand(
        fingerprint="b" * 64,
        mac_address="AA:BB:CC:DD:EE:FF",
        platform="android",
        app_version="0.1.0",
    )

    with pytest.raises(
        DeviceAlreadyRegisteredError,
        match="MAC address",
    ):
        use_case.execute(duplicate_mac_command)


def test_should_reject_invalid_registration_data() -> None:
    repository = InMemoryDeviceRepository()
    use_case = RegisterDeviceUseCase(repository)

    invalid_command = RegisterDeviceCommand(
        fingerprint="invalid",
        mac_address="banana",
        platform="unsupported",
        app_version="version-one",
    )

    with pytest.raises(ValueError):
        use_case.execute(invalid_command)


def test_should_find_registered_device_by_fingerprint() -> None:
    repository = InMemoryDeviceRepository()
    use_case = RegisterDeviceUseCase(repository)

    use_case.execute(make_command())

    stored_device = repository.find_by_fingerprint(
        DeviceFingerprint("a" * 64)
    )

    assert stored_device is not None
