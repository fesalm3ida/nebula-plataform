from collections.abc import Generator

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
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
from app.infrastructure.persistence.models import (
    DeviceModel,
    SessionModel,
)
from app.infrastructure.repositories.postgresql_device_repository import (
    PostgreSQLDeviceRepository,
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


def make_device(
    fingerprint: str = "a" * 64,
    mac_address: str = "AA:BB:CC:DD:EE:FF",
) -> Device:
    return Device(
        fingerprint=DeviceFingerprint(fingerprint),
        mac_address=MacAddress(mac_address),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )


def test_should_save_and_find_device_by_id(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )
    device = make_device()

    repository.save(device)

    restored = repository.find_by_id(device.device_id)

    assert restored is not None
    assert restored.device_id == device.device_id
    assert restored.fingerprint == device.fingerprint
    assert restored.mac_address == device.mac_address
    assert restored.device_key == device.device_key
    assert restored.status == DeviceStatus.PENDING


def test_should_update_existing_device(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )
    device = make_device()

    repository.save(device)

    device.activate()
    repository.save(device)

    restored = repository.find_by_id(device.device_id)

    assert restored is not None
    assert restored.status == DeviceStatus.ACTIVE


def test_should_find_device_by_mac_address(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )
    device = make_device()

    repository.save(device)

    restored = repository.find_by_mac_address(
        MacAddress("AA:BB:CC:DD:EE:FF")
    )

    assert restored is not None
    assert restored.device_id == device.device_id


def test_should_find_device_by_fingerprint(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )
    device = make_device()

    repository.save(device)

    restored = repository.find_by_fingerprint(
        DeviceFingerprint("a" * 64)
    )

    assert restored is not None
    assert restored.device_id == device.device_id


def test_should_find_device_by_device_key(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )
    device = make_device()

    repository.save(device)

    restored = repository.find_by_device_key(
        device.device_key
    )

    assert restored is not None
    assert restored.device_id == device.device_id


def test_should_confirm_existing_fingerprint(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )
    device = make_device()

    repository.save(device)

    assert repository.exists_by_fingerprint(
        device.fingerprint
    ) is True


def test_should_report_missing_fingerprint(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )

    assert repository.exists_by_fingerprint(
        DeviceFingerprint("b" * 64)
    ) is False


def test_should_return_none_when_device_does_not_exist(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLDeviceRepository(
        database_session
    )
    device = make_device()

    assert repository.find_by_id(device.device_id) is None
    assert (
        repository.find_by_mac_address(device.mac_address)
        is None
    )
    assert (
        repository.find_by_fingerprint(device.fingerprint)
        is None
    )
    assert (
        repository.find_by_device_key(device.device_key)
        is None
    )
