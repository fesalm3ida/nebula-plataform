from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.security.current_session import get_current_session
from app.domain.entities.device import Device
from app.domain.entities.session import Session
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)


def make_device() -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )

    device.activate()

    return device


def make_session(
    device: Device,
) -> Session:
    started_at = datetime.now(timezone.utc)

    return Session(
        device_id=device.device_id,
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )


def test_should_return_session_owned_by_authenticated_device() -> None:
    repository = InMemorySessionRepository()
    device = make_device()
    session = make_session(device)

    repository.save(session)

    current_session = get_current_session(
        session_id=session.session_id,
        current_device=device,
        repository=repository,
    )

    assert current_session.session_id == session.session_id
    assert current_session.device_id == device.device_id


def test_should_reject_unknown_session() -> None:
    repository = InMemorySessionRepository()
    device = make_device()

    with pytest.raises(HTTPException) as raised:
        get_current_session(
            session_id=uuid4(),
            current_device=device,
            repository=repository,
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == "Session not found."


def test_should_reject_session_owned_by_another_device() -> None:
    repository = InMemorySessionRepository()

    authenticated_device = make_device()
    owner_device = make_device()

    session = make_session(owner_device)
    repository.save(session)

    with pytest.raises(HTTPException) as raised:
        get_current_session(
            session_id=session.session_id,
            current_device=authenticated_device,
            repository=repository,
        )

    assert raised.value.status_code == 403
    assert "not authorized" in raised.value.detail


def test_should_not_modify_authorized_session() -> None:
    repository = InMemorySessionRepository()
    device = make_device()
    session = make_session(device)

    original_status = session.status
    original_last_seen = session.last_seen
    original_ended_at = session.ended_at

    repository.save(session)

    current_session = get_current_session(
        session_id=session.session_id,
        current_device=device,
        repository=repository,
    )

    assert current_session.status == original_status
    assert current_session.last_seen == original_last_seen
    assert current_session.ended_at == original_ended_at
