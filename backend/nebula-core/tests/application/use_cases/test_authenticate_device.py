from uuid import uuid4

import pytest

from app.application.exceptions import (
    DeviceNotActiveError,
    DeviceNotFoundError,
    InvalidDeviceCredentialsError,
)
from app.application.use_cases.authenticate_device import (
    AuthenticateDeviceCommand,
    AuthenticateDeviceUseCase,
)
from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)


def make_active_device() -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )
    device.activate()
    return device


def make_command(device: Device) -> AuthenticateDeviceCommand:
    return AuthenticateDeviceCommand(
        device_id=device.device_id,
        device_key=str(device.device_key),
        fingerprint=str(device.fingerprint),
    )


def test_should_authenticate_active_device() -> None:
    repository = InMemoryDeviceRepository()
    device = make_active_device()
    repository.save(device)

    use_case = AuthenticateDeviceUseCase(repository)
    result = use_case.execute(make_command(device))

    assert result.access_token
    assert len(result.access_token) >= 32
    assert result.device_status == DeviceStatus.ACTIVE
    assert result.expires_at is not None


def test_should_reject_unknown_device() -> None:
    repository = InMemoryDeviceRepository()
    use_case = AuthenticateDeviceUseCase(repository)

    command = AuthenticateDeviceCommand(
        device_id=uuid4(),
        device_key="x" * DeviceKey.MIN_LENGTH,
        fingerprint="a" * 64,
    )

    with pytest.raises(DeviceNotFoundError, match="not found"):
        use_case.execute(command)


def test_should_reject_invalid_device_key() -> None:
    repository = InMemoryDeviceRepository()
    device = make_active_device()
    repository.save(device)

    command = AuthenticateDeviceCommand(
        device_id=device.device_id,
        device_key="x" * DeviceKey.MIN_LENGTH,
        fingerprint=str(device.fingerprint),
    )

    use_case = AuthenticateDeviceUseCase(repository)

    with pytest.raises(
        InvalidDeviceCredentialsError,
        match="Invalid Device credentials",
    ):
        use_case.execute(command)


def test_should_reject_invalid_fingerprint() -> None:
    repository = InMemoryDeviceRepository()
    device = make_active_device()
    repository.save(device)

    command = AuthenticateDeviceCommand(
        device_id=device.device_id,
        device_key=str(device.device_key),
        fingerprint="b" * 64,
    )

    use_case = AuthenticateDeviceUseCase(repository)

    with pytest.raises(
        InvalidDeviceCredentialsError,
        match="Invalid Device credentials",
    ):
        use_case.execute(command)


def test_should_reject_pending_device() -> None:
    repository = InMemoryDeviceRepository()

    device = make_active_device()
    device.status = DeviceStatus.PENDING
    repository.save(device)

    use_case = AuthenticateDeviceUseCase(repository)

    with pytest.raises(DeviceNotActiveError, match="pending"):
        use_case.execute(make_command(device))


@pytest.mark.parametrize(
    "status",
    [
        DeviceStatus.BLOCKED,
        DeviceStatus.REVOKED,
        DeviceStatus.EXPIRED,
    ],
)
def test_should_reject_non_active_device(
    status: DeviceStatus,
) -> None:
    repository = InMemoryDeviceRepository()

    device = make_active_device()
    device.status = status
    repository.save(device)

    use_case = AuthenticateDeviceUseCase(repository)

    with pytest.raises(DeviceNotActiveError):
        use_case.execute(make_command(device))
