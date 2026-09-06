from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.domain.entities.playlist import Playlist
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus


def make_playlist(
    *,
    name: str = "Lista Principal",
    format: PlaylistFormat = PlaylistFormat.M3U,
    source_url: str = "https://example.com/playlist.m3u",
    status: PlaylistStatus = PlaylistStatus.ACTIVE,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> Playlist:
    now = datetime.now(timezone.utc)

    return Playlist(
        name=name,
        format=format,
        source_url=source_url,
        status=status,
        created_at=created_at or now,
        updated_at=updated_at or now,
    )


def test_should_create_active_playlist() -> None:
    playlist = make_playlist()

    assert isinstance(playlist.playlist_id, UUID)
    assert playlist.name == "Lista Principal"
    assert playlist.format == PlaylistFormat.M3U
    assert (
        playlist.source_url
        == "https://example.com/playlist.m3u"
    )
    assert playlist.status == PlaylistStatus.ACTIVE
    assert playlist.is_available_for_provisioning is True


def test_should_normalize_name_and_source_url() -> None:
    playlist = make_playlist(
        name="  Lista Principal  ",
        source_url="  https://example.com/playlist.m3u  ",
    )

    assert playlist.name == "Lista Principal"
    assert (
        playlist.source_url
        == "https://example.com/playlist.m3u"
    )


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        " ",
        "     ",
    ],
)
def test_should_reject_empty_name(invalid_name: str) -> None:
    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):
        make_playlist(name=invalid_name)


def test_should_reject_non_string_name() -> None:
    with pytest.raises(
        ValueError,
        match="name must be a string",
    ):
        make_playlist(name=None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_source_url",
    [
        "",
        " ",
        "     ",
    ],
)
def test_should_reject_empty_source_url(
    invalid_source_url: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="source_url cannot be empty",
    ):
        make_playlist(source_url=invalid_source_url)


def test_should_reject_non_string_source_url() -> None:
    with pytest.raises(
        ValueError,
        match="source_url must be a string",
    ):
        make_playlist(source_url=None)  # type: ignore[arg-type]


def test_should_reject_invalid_format() -> None:
    with pytest.raises(
        ValueError,
        match="format must be a valid PlaylistFormat",
    ):
        make_playlist(format="m3u")  # type: ignore[arg-type]


def test_should_reject_invalid_status() -> None:
    with pytest.raises(
        ValueError,
        match="status must be a valid PlaylistStatus",
    ):
        make_playlist(status="active")  # type: ignore[arg-type]


def test_should_reject_created_at_without_timezone() -> None:
    naive_datetime = datetime.now()

    with pytest.raises(
        ValueError,
        match="created_at must include timezone information",
    ):
        make_playlist(created_at=naive_datetime)


def test_should_reject_updated_at_without_timezone() -> None:
    naive_datetime = datetime.now()

    with pytest.raises(
        ValueError,
        match="updated_at must include timezone information",
    ):
        make_playlist(updated_at=naive_datetime)


def test_should_reject_updated_at_before_created_at() -> None:
    created_at = datetime.now(timezone.utc)
    updated_at = created_at - timedelta(seconds=1)

    with pytest.raises(
        ValueError,
        match="updated_at cannot be earlier than created_at",
    ):
        make_playlist(
            created_at=created_at,
            updated_at=updated_at,
        )


def test_should_update_name() -> None:
    playlist = make_playlist()
    previous_updated_at = playlist.updated_at

    playlist.update_name("Lista Secundária")

    assert playlist.name == "Lista Secundária"
    assert playlist.updated_at > previous_updated_at


def test_should_normalize_name_when_updating() -> None:
    playlist = make_playlist()

    playlist.update_name("  Lista Secundária  ")

    assert playlist.name == "Lista Secundária"


def test_should_not_change_updated_at_when_name_is_unchanged() -> None:
    playlist = make_playlist()
    previous_updated_at = playlist.updated_at

    playlist.update_name("Lista Principal")

    assert playlist.updated_at == previous_updated_at


def test_should_reject_empty_name_when_updating() -> None:
    playlist = make_playlist()

    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):
        playlist.update_name("   ")


def test_should_update_source_url() -> None:
    playlist = make_playlist()
    previous_updated_at = playlist.updated_at

    playlist.update_source_url(
        "https://example.com/new-playlist.m3u"
    )

    assert (
        playlist.source_url
        == "https://example.com/new-playlist.m3u"
    )
    assert playlist.updated_at > previous_updated_at


def test_should_normalize_source_url_when_updating() -> None:
    playlist = make_playlist()

    playlist.update_source_url(
        "  https://example.com/new-playlist.m3u  "
    )

    assert (
        playlist.source_url
        == "https://example.com/new-playlist.m3u"
    )


def test_should_not_change_updated_at_when_source_url_is_unchanged() -> None:
    playlist = make_playlist()
    previous_updated_at = playlist.updated_at

    playlist.update_source_url(
        "https://example.com/playlist.m3u"
    )

    assert playlist.updated_at == previous_updated_at


def test_should_reject_empty_source_url_when_updating() -> None:
    playlist = make_playlist()

    with pytest.raises(
        ValueError,
        match="source_url cannot be empty",
    ):
        playlist.update_source_url("   ")


def test_should_disable_playlist() -> None:
    playlist = make_playlist()
    previous_updated_at = playlist.updated_at

    playlist.disable()

    assert playlist.status == PlaylistStatus.DISABLED
    assert playlist.is_available_for_provisioning is False
    assert playlist.updated_at > previous_updated_at


def test_should_not_change_updated_at_when_already_disabled() -> None:
    playlist = make_playlist(
        status=PlaylistStatus.DISABLED,
    )
    previous_updated_at = playlist.updated_at

    playlist.disable()

    assert playlist.status == PlaylistStatus.DISABLED
    assert playlist.updated_at == previous_updated_at


def test_should_activate_disabled_playlist() -> None:
    playlist = make_playlist(
        status=PlaylistStatus.DISABLED,
    )
    previous_updated_at = playlist.updated_at

    playlist.activate()

    assert playlist.status == PlaylistStatus.ACTIVE
    assert playlist.is_available_for_provisioning is True
    assert playlist.updated_at > previous_updated_at


def test_should_not_change_updated_at_when_already_active() -> None:
    playlist = make_playlist()
    previous_updated_at = playlist.updated_at

    playlist.activate()

    assert playlist.status == PlaylistStatus.ACTIVE
    assert playlist.updated_at == previous_updated_at


@pytest.mark.parametrize(
    "playlist_format",
    [
        PlaylistFormat.M3U,
        PlaylistFormat.XTREAM_CODES,
        PlaylistFormat.STALKER,
    ],
)
def test_should_accept_supported_playlist_formats(
    playlist_format: PlaylistFormat,
) -> None:
    playlist = make_playlist(format=playlist_format)

    assert playlist.format == playlist_format
