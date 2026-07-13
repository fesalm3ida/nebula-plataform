from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus


def make_session() -> Session:
    started_at = datetime.now(timezone.utc)

    return Session(
        device_id=uuid4(),
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )


def test_should_initialize_last_seen_with_started_at() -> None:
    session = make_session()

    assert session.last_seen == session.started_at


def test_should_update_last_seen_when_touch_is_called() -> None:
    session = make_session()
    heartbeat_time = session.started_at + timedelta(seconds=30)

    session.touch(heartbeat_time)

    assert session.last_seen == heartbeat_time


def test_should_keep_session_active_after_touch() -> None:
    session = make_session()
    heartbeat_time = session.started_at + timedelta(seconds=30)

    session.touch(heartbeat_time)

    assert session.status == SessionStatus.ACTIVE


def test_should_not_change_expiration_when_touch_is_called() -> None:
    session = make_session()
    original_expiration = session.expires_at
    heartbeat_time = session.started_at + timedelta(seconds=30)

    session.touch(heartbeat_time)

    assert session.expires_at == original_expiration


def test_should_not_change_session_id_when_touch_is_called() -> None:
    session = make_session()
    original_session_id = session.session_id
    heartbeat_time = session.started_at + timedelta(seconds=30)

    session.touch(heartbeat_time)

    assert session.session_id == original_session_id


def test_should_reject_touch_on_ended_session() -> None:
    session = make_session()
    session.end()

    with pytest.raises(
        ValueError,
        match="Only an active Session can receive a heartbeat",
    ):
        session.touch()


def test_should_reject_touch_on_expired_session() -> None:
    session = make_session()
    session.expire()

    with pytest.raises(
        ValueError,
        match="Only an active Session can receive a heartbeat",
    ):
        session.touch()


def test_should_reject_naive_heartbeat_time() -> None:
    session = make_session()

    with pytest.raises(
        ValueError,
        match="heartbeat time must be timezone-aware",
    ):
        session.touch(datetime.now())


def test_should_reject_heartbeat_before_last_seen() -> None:
    session = make_session()
    first_heartbeat = session.started_at + timedelta(seconds=30)
    earlier_heartbeat = session.started_at + timedelta(seconds=15)

    session.touch(first_heartbeat)

    with pytest.raises(
        ValueError,
        match="cannot be earlier than last_seen",
    ):
        session.touch(earlier_heartbeat)
