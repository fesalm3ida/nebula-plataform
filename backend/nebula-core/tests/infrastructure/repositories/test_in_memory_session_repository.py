from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.entities.session import Session
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)


def make_session() -> Session:
    return Session(
        device_id=uuid4(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )


def test_should_save_and_find_session_by_id() -> None:
    repository = InMemorySessionRepository()
    session = make_session()

    repository.save(session)

    assert repository.find_by_id(session.session_id) == session


def test_should_update_existing_session() -> None:
    repository = InMemorySessionRepository()
    session = make_session()

    repository.save(session)
    session.end()
    repository.save(session)

    stored_session = repository.find_by_id(session.session_id)

    assert stored_session is not None
    assert stored_session.status == session.status


def test_should_find_active_session_by_device_id() -> None:
    repository = InMemorySessionRepository()
    session = make_session()

    repository.save(session)

    found_session = repository.find_active_by_device_id(
        session.device_id
    )

    assert found_session == session


def test_should_ignore_ended_session_when_searching_active_session() -> None:
    repository = InMemorySessionRepository()
    session = make_session()

    session.end()
    repository.save(session)

    found_session = repository.find_active_by_device_id(
        session.device_id
    )

    assert found_session is None


def test_should_return_none_when_session_does_not_exist() -> None:
    repository = InMemorySessionRepository()

    assert repository.find_by_id(uuid4()) is None
    assert repository.find_active_by_device_id(uuid4()) is None
