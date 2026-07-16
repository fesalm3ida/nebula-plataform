from collections.abc import Generator
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.device import Device
from app.domain.entities.session import Session
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.session_status import SessionStatus
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.database import (
    SessionFactory,
    engine,
)
from app.infrastructure.persistence.mappers.device_mapper import (
    DeviceMapper,
)
from app.infrastructure.persistence.models import (
    DeviceModel,
    SessionModel,
)
from app.infrastructure.repositories.postgresql_session_repository import (
    PostgreSQLSessionRepository,
)


@pytest.fixture(scope="module", autouse=True)
def prepare_database_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)

    yield

    with SessionFactory() as database_session:
        database_session.execute(delete(SessionModel))
        database_session.execute(delete(DeviceModel))
        database_session.commit()


@pytest.fixture
def database_session() -> Generator[
    SQLAlchemySession,
    None,
    None,
]:
    session = SessionFactory()

    session.execute(delete(SessionModel))
    session.execute(delete(DeviceModel))
    session.commit()

    try:
        yield session
    finally:
        session.execute(delete(SessionModel))
        session.execute(delete(DeviceModel))
        session.commit()
        session.close()


def make_device() -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )
    device.activate()

    return device


def persist_device(
    database_session: SQLAlchemySession,
    device: Device,
) -> None:
    database_session.add(
        DeviceMapper.to_model(device)
    )
    database_session.commit()


def make_session(device: Device) -> Session:
    started_at = datetime.now(timezone.utc)

    return Session(
        device_id=device.device_id,
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )


def test_should_save_and_find_session_by_id(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)

    repository = PostgreSQLSessionRepository(
        database_session
    )
    session = make_session(device)

    repository.save(session)

    restored = repository.find_by_id(
        session.session_id
    )

    assert restored is not None
    assert restored.session_id == session.session_id
    assert restored.device_id == device.device_id
    assert restored.status == SessionStatus.ACTIVE
    assert restored.started_at == session.started_at
    assert restored.last_seen == session.last_seen
    assert restored.expires_at == session.expires_at
    assert restored.ended_at is None


def test_should_update_existing_session(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)

    repository = PostgreSQLSessionRepository(
        database_session
    )
    session = make_session(device)

    repository.save(session)

    heartbeat_time = (
        session.started_at + timedelta(seconds=30)
    )
    session.touch(heartbeat_time)

    repository.save(session)

    restored = repository.find_by_id(
        session.session_id
    )

    assert restored is not None
    assert restored.last_seen == heartbeat_time
    assert restored.status == SessionStatus.ACTIVE


def test_should_persist_ended_session(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)

    repository = PostgreSQLSessionRepository(
        database_session
    )
    session = make_session(device)

    repository.save(session)

    session.end()
    repository.save(session)

    restored = repository.find_by_id(
        session.session_id
    )

    assert restored is not None
    assert restored.status == SessionStatus.ENDED
    assert restored.ended_at is not None


def test_should_find_active_session_by_device_id(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)

    repository = PostgreSQLSessionRepository(
        database_session
    )
    session = make_session(device)

    repository.save(session)

    restored = repository.find_active_by_device_id(
        device.device_id
    )

    assert restored is not None
    assert restored.session_id == session.session_id
    assert restored.status == SessionStatus.ACTIVE


def test_should_ignore_ended_session_when_searching_active(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)

    repository = PostgreSQLSessionRepository(
        database_session
    )
    session = make_session(device)
    session.end()

    repository.save(session)

    restored = repository.find_active_by_device_id(
        device.device_id
    )

    assert restored is None


def test_should_ignore_expired_session_when_searching_active(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)

    repository = PostgreSQLSessionRepository(
        database_session
    )
    session = make_session(device)
    session.expire()

    repository.save(session)

    restored = repository.find_active_by_device_id(
        device.device_id
    )

    assert restored is None


def test_should_return_none_when_session_does_not_exist(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)

    repository = PostgreSQLSessionRepository(
        database_session
    )
    unknown_session = make_session(device)

    assert (
        repository.find_by_id(
            unknown_session.session_id
        )
        is None
    )

    assert (
        repository.find_active_by_device_id(
            device.device_id
        )
        is None
    )
