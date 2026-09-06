from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.device import Device
from app.domain.entities.playlist import Playlist
from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.playlist_format import PlaylistFormat
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
from app.infrastructure.persistence.mappers.playlist_mapper import (
    PlaylistMapper,
)
from app.infrastructure.persistence.models import (
    DeviceModel,
    PlaylistAssignmentModel,
    PlaylistModel,
    SessionModel,
)
from app.infrastructure.repositories.postgresql_playlist_assignment_repository import (
    PostgreSQLPlaylistAssignmentRepository,
)


@pytest.fixture(scope="module", autouse=True)
def prepare_database_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)

    yield

    with SessionFactory() as database_session:
        database_session.execute(delete(PlaylistAssignmentModel))
        database_session.execute(delete(SessionModel))
        database_session.execute(delete(DeviceModel))
        database_session.execute(delete(PlaylistModel))
        database_session.commit()


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
    database_session.execute(delete(PlaylistAssignmentModel))
    database_session.execute(delete(SessionModel))
    database_session.execute(delete(DeviceModel))
    database_session.execute(delete(PlaylistModel))
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


def make_playlist() -> Playlist:
    return Playlist(
        name="Lista Principal",
        format=PlaylistFormat.M3U,
        source_url="https://example.com/playlist.m3u",
    )


def persist_device(
    database_session: SQLAlchemySession,
    device: Device,
) -> None:
    database_session.add(DeviceMapper.to_model(device))
    database_session.commit()


def persist_playlist(
    database_session: SQLAlchemySession,
    playlist: Playlist,
) -> None:
    database_session.add(PlaylistMapper.to_model(playlist))
    database_session.commit()


def test_should_save_and_find_active_assignment_for_device(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)
    playlist = make_playlist()
    persist_playlist(database_session, playlist)

    repository = PostgreSQLPlaylistAssignmentRepository(database_session)
    assignment = PlaylistAssignment(
        device_id=device.device_id,
        playlist_id=playlist.playlist_id,
    )

    repository.save(assignment)

    restored = repository.find_active_by_device_id(device.device_id)

    assert restored is not None
    assert restored.assignment_id == assignment.assignment_id
    assert restored.device_id == device.device_id
    assert restored.playlist_id == playlist.playlist_id


def test_should_ignore_revoked_assignment_for_device(
    database_session: SQLAlchemySession,
) -> None:
    device = make_device()
    persist_device(database_session, device)
    playlist = make_playlist()
    persist_playlist(database_session, playlist)

    repository = PostgreSQLPlaylistAssignmentRepository(database_session)
    assignment = PlaylistAssignment(
        device_id=device.device_id,
        playlist_id=playlist.playlist_id,
    )
    assignment.revoke()

    repository.save(assignment)

    assert repository.find_active_by_device_id(device.device_id) is None


def test_should_return_none_for_device_without_assignment(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLPlaylistAssignmentRepository(database_session)

    assert repository.find_active_by_device_id(UUID(int=1)) is None
