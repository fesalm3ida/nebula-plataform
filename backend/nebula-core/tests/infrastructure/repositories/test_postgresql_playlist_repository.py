from collections.abc import Generator

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.playlist import Playlist
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.database import (
    SessionFactory,
    engine,
)
from app.infrastructure.persistence.models import (
    PlaylistAssignmentModel,
    PlaylistModel,
)
from app.infrastructure.repositories.postgresql_playlist_repository import (
    PostgreSQLPlaylistRepository,
)


@pytest.fixture(scope="module", autouse=True)
def prepare_database_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)

    yield

    with SessionFactory() as database_session:
        database_session.execute(delete(PlaylistAssignmentModel))
        database_session.execute(delete(PlaylistModel))
        database_session.commit()


@pytest.fixture
def database_session() -> Generator[SQLAlchemySession, None, None]:
    session = SessionFactory()

    session.execute(delete(PlaylistAssignmentModel))
    session.execute(delete(PlaylistModel))
    session.commit()

    try:
        yield session
    finally:
        session.execute(delete(PlaylistAssignmentModel))
        session.execute(delete(PlaylistModel))
        session.commit()
        session.close()


def make_playlist(
    name: str = "Lista Principal",
    source_url: str = "https://example.com/playlist.m3u",
) -> Playlist:
    return Playlist(
        name=name,
        format=PlaylistFormat.M3U,
        source_url=source_url,
    )


def test_should_save_and_find_playlist_by_id(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLPlaylistRepository(database_session)
    playlist = make_playlist()

    repository.save(playlist)

    restored = repository.find_by_id(playlist.playlist_id)

    assert restored is not None
    assert restored.playlist_id == playlist.playlist_id
    assert restored.name == playlist.name
    assert restored.format == PlaylistFormat.M3U
    assert restored.source_url == playlist.source_url
    assert restored.status == PlaylistStatus.ACTIVE


def test_should_update_existing_playlist(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLPlaylistRepository(database_session)
    playlist = make_playlist()

    repository.save(playlist)

    playlist.update_name("Lista Secundária")
    repository.save(playlist)

    restored = repository.find_by_id(playlist.playlist_id)

    assert restored is not None
    assert restored.name == "Lista Secundária"


def test_should_list_all_playlists_sorted_by_name(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLPlaylistRepository(database_session)

    repository.save(make_playlist(name="Beta"))
    repository.save(make_playlist(name="Alpha"))

    playlists = repository.find_all()

    assert [playlist.name for playlist in playlists] == [
        "Alpha",
        "Beta",
    ]


def test_should_return_none_when_playlist_does_not_exist(
    database_session: SQLAlchemySession,
) -> None:
    repository = PostgreSQLPlaylistRepository(database_session)

    assert repository.find_by_id(make_playlist().playlist_id) is None
