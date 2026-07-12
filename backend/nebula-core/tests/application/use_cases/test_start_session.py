from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.application.exceptions import (
    ActiveSessionAlreadyExistsError,
    DeviceNotActiveError,
    DeviceNotFoundError,
)
from app.application.use_cases.start_session import (
    StartSessionCommand,
    StartSessionUseCase,
)
from app.domain.entities.device import Device
from app.domain.entities.session import Session
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.session_status import SessionStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
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


def test_should_start_session_for_active_device() -> None:
    device_repository = InMemoryDeviceRepository()
    session_repository = InMemorySessionRepository()

    device = make_active_device()
    device_repository.save(device)

    use_case = StartSessionUseCase(
        device_repository,
        session_repository,
    )

    result = use_case.execute(
        StartSessionCommand(device_id=device.device_id)
    )

    assert result.session_id is not None
    assert result.device_id == device.device_id
    assert result.status == SessionStatus.ACTIVE
    assert result.started_at is not None
    assert result.expires_at > result.started_at


def test_should_persist_started_session() -> None:
    device_repository = InMemoryDeviceRepository()
    session_repository = InMemorySessionRepository()

    device = make_active_device()
    device_repository.save(device)

    use_case = StartSessionUseCase(
        device_repository,
        session_repository,
    )

    result = use_case.execute(
        StartSessionCommand(device_id=device.device_id)
    )

    stored_session = session_repository.find_by_id(
        result.session_id
    )

    assert stored_session is not None
    assert stored_session.device_id == device.device_id
    assert stored_session.status == SessionStatus.ACTIVE


def test_should_reject_unknown_device() -> None:
    use_case = StartSessionUseCase(
        InMemoryDeviceRepository(),
        InMemorySessionRepository(),
    )

    with pytest.raises(DeviceNotFoundError, match="not found"):
        use_case.execute(
            StartSessionCommand(device_id=uuid4())
        )


def test_should_reject_pending_device() -> None:
    device_repository = InMemoryDeviceRepository()
    session_repository = InMemorySessionRepository()

    device = make_active_device()
    device.status = DeviceStatus.PENDING
    device_repository.save(device)

    use_case = StartSessionUseCase(
        device_repository,
        session_repository,
    )

    with pytest.raises(DeviceNotActiveError, match="pending"):
        use_case.execute(
            StartSessionCommand(device_id=device.device_id)
        )


def test_should_reject_second_active_session() -> None:
    device_repository = InMemoryDeviceRepository()
    session_repository = InMemorySessionRepository()

    device = make_active_device()
    device_repository.save(device)

    existing_session = Session(
    device_id=device.device_id,
    expires_at=datetime.now(timezone.utc)
    + timedelta(minutes=30),
    )
    session_repository.save(existing_session)

    use_case = StartSessionUseCase(
        device_repository,
        session_repository,
    )

    with pytest.raises(
        ActiveSessionAlreadyExistsError,
        match="active Session",
    ):
        use_case.execute(
            StartSessionCommand(device_id=device.device_id)
        )
