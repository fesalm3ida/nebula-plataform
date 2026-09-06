from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.device import Device
from app.domain.entities.log import Log
from app.domain.entities.session import Session
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.log_level import LogLevel
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.database import (
    SessionFactory,
    engine,
)
from app.infrastructure.persistence.mappers.device_mapper import (
    DeviceMapper,
)
from app.infrastructure.persistence.mappers.session_mapper import (
    SessionMapper,
)
from app.infrastructure.persistence.models import (
    DeviceModel,
    LogModel,
    SessionModel,
    TelemetryEventModel,
)
from app.infrastructure.repositories.postgresql_log_repository import (
    PostgreSQLLogRepository,
)


@pytest.fixture(scope="module", autouse=True)
def prepare_database_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)

    yield

    with SessionFactory() as database_session:
        _clean(database_session)


@pytest.fixture
def database_session() -> Generator[SQLAlchemySession, None, None]:
    session = SessionFactory()
    _clean(session)

    try:
        yield session
    finally:
        _clean(session)
        session.close()


def _clean(database_session: SQLAlchemySession) -> None:
    database_session.execute(delete(TelemetryEventModel))
    database_session.execute(delete(LogModel))
    database_session.execute(delete(SessionModel))
    database_session.execute(delete(DeviceModel))
    database_session.commit()


def make_device() -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )
    device.activate()

    return device


def make_session(device: Device) -> Session:
    started_at = datetime.now(timezone.utc)

    return Session(
        device_id=device.device_id,
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )


def persist_device(
    database_session: SQLAlchemySession,
    device: Device,
) -> None:
    database_session.add(DeviceMapper.to_model(device))
    database_session.commit()


def persist_session(
    database_session: SQLAlchemySession,
    session: Session,
) -> None:
    database_session.add(SessionMapper.to_model(session))
    database_session.commit()


def test_should_save_and_find_log_by_id(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)
    session = make_session(device)
    persist_session(database_session, session)

    repository = PostgreSQLLogRepository(database_session)
    log = Log(
        session_id=session.session_id,
        device_id=device.device_id,
        level=LogLevel.WARNING,
        message="Buffer underrun detected",
    )

    repository.save(log)

    restored = repository.find_by_id(log.log_id)

    assert restored is not None
    assert restored.log_id == log.log_id
    assert restored.device_id == device.device_id
    assert restored.level == LogLevel.WARNING
    assert restored.message == "Buffer underrun detected"


def test_should_return_none_when_log_does_not_exist(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLLogRepository(database_session)

    log = Log(
        session_id=uuid4(),
        device_id=uuid4(),
        level=LogLevel.ERROR,
        message="not persisted",
    )

    assert repository.find_by_id(log.log_id) is None
