from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus


def make_session() -> Session:
    return Session(
        device_id=uuid4(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )


def test_should_create_active_session() -> None:
    session = make_session()

    assert session.session_id is not None
    assert session.status == SessionStatus.ACTIVE
    assert session.started_at is not None
    assert session.last_seen == session.started_at
    assert session.ended_at is None


def test_should_end_active_session() -> None:
    session = make_session()

    session.end()

    assert session.status == SessionStatus.ENDED
    assert session.ended_at is not None


def test_should_expire_active_session() -> None:
    session = make_session()

    session.expire()

    assert session.status == SessionStatus.EXPIRED
    assert session.ended_at is not None


def test_should_detect_expired_session() -> None:
    session = make_session()
    future = session.expires_at + timedelta(seconds=1)

    assert session.is_expired(future) is True


def test_should_detect_non_expired_session() -> None:
    session = make_session()
    before_expiration = session.expires_at - timedelta(seconds=1)

    assert session.is_expired(before_expiration) is False


def test_should_reject_expiration_before_start() -> None:
    with pytest.raises(
        ValueError,
        match="later than its start time",
    ):
        Session(
            device_id=uuid4(),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )


def test_should_reject_naive_expiration_datetime() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        Session(
            device_id=uuid4(),
            expires_at=datetime.now() + timedelta(minutes=30),
        )


def test_should_reject_naive_start_datetime() -> None:
    started_at = datetime.now()

    with pytest.raises(
        ValueError,
        match="start time must be timezone-aware",
    ):
        Session(
            device_id=uuid4(),
            started_at=started_at,
            expires_at=started_at + timedelta(minutes=30),
        )


def test_should_reject_last_seen_before_start() -> None:
    started_at = datetime.now(timezone.utc)

    with pytest.raises(
        ValueError,
        match="last_seen cannot be earlier",
    ):
        Session(
            device_id=uuid4(),
            started_at=started_at,
            last_seen=started_at - timedelta(seconds=1),
            expires_at=started_at + timedelta(minutes=30),
        )


def test_should_reject_naive_last_seen_datetime() -> None:
    started_at = datetime.now(timezone.utc)

    with pytest.raises(
        ValueError,
        match="last_seen must be timezone-aware",
    ):
        Session(
            device_id=uuid4(),
            started_at=started_at,
            last_seen=datetime.now(),
            expires_at=started_at + timedelta(minutes=30),
        )


def test_should_reject_naive_expiration_reference() -> None:
    session = make_session()

    with pytest.raises(
        ValueError,
        match="expiration reference must be timezone-aware",
    ):
        session.is_expired(datetime.now())


def test_should_reject_ending_session_twice() -> None:
    session = make_session()
    session.end()

    with pytest.raises(
        ValueError,
        match="Only an active Session",
    ):
        session.end()



