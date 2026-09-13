from app.application.exceptions import (
    DeviceNotActiveError,
)
from app.application.use_cases.start_session import (
    StartSessionCommand,
    StartSessionUseCase,
)
from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.session_status import SessionStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)

import pytest


def make_device(
    active: bool = True,
) -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress(
            "AA:BB:CC:DD:EE:FF"
        ),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )

    if active:
        device.activate()

    return device


def make_use_case(
    repository: InMemorySessionRepository,
) -> StartSessionUseCase:
    return StartSessionUseCase(
        session_repository=repository,
    )


def test_should_start_session_for_active_device() -> None:
    repository = InMemorySessionRepository()
    device = make_device()

    use_case = make_use_case(repository)

    result = use_case.execute(
        StartSessionCommand(device=device)
    )

    assert result.device_id == device.device_id
    assert result.status == SessionStatus.ACTIVE
    assert result.started_at.tzinfo is not None
    assert result.expires_at > result.started_at
    assert result.last_seen == result.started_at


def test_should_persist_started_session() -> None:
    repository = InMemorySessionRepository()
    device = make_device()

    use_case = make_use_case(repository)

    result = use_case.execute(
        StartSessionCommand(device=device)
    )

    persisted_session = repository.find_by_id(
        result.session_id
    )

    assert persisted_session is not None
    assert persisted_session.device_id == device.device_id
    assert persisted_session.status == SessionStatus.ACTIVE


def test_should_use_authenticated_device_identity() -> None:
    repository = InMemorySessionRepository()
    device = make_device()

    use_case = make_use_case(repository)

    result = use_case.execute(
        StartSessionCommand(device=device)
    )

    assert result.device_id == device.device_id


def test_should_reject_pending_device() -> None:
    repository = InMemorySessionRepository()
    device = make_device(active=False)

    use_case = make_use_case(repository)

    with pytest.raises(
        DeviceNotActiveError,
        match="pending",
    ):
        use_case.execute(
            StartSessionCommand(device=device)
        )


def test_should_resume_existing_active_session() -> None:
    repository = InMemorySessionRepository()
    device = make_device()

    use_case = make_use_case(repository)
    command = StartSessionCommand(device=device)

    first = use_case.execute(command)
    second = use_case.execute(command)

    assert second.session_id == first.session_id
