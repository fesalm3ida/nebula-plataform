from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.application.exceptions import (
    SessionNotActiveError,
    SessionNotFoundError,
)
from app.application.use_cases.heartbeat_session import (
    HeartbeatSessionCommand,
    HeartbeatSessionUseCase,
)
from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)


def make_active_session() -> Session:
    started_at = datetime.now(timezone.utc)

    return Session(
        device_id=uuid4(),
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )


def test_should_update_last_seen() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()
    original_last_seen = session.last_seen

    repository.save(session)

    use_case = HeartbeatSessionUseCase(repository)

    result = use_case.execute(
        HeartbeatSessionCommand(
            session_id=session.session_id,
        )
    )

    assert result.session_id == session.session_id
    assert result.status == SessionStatus.ACTIVE
    assert result.last_seen > original_last_seen


def test_should_persist_updated_last_seen() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()

    repository.save(session)

    use_case = HeartbeatSessionUseCase(repository)

    result = use_case.execute(
        HeartbeatSessionCommand(
            session_id=session.session_id,
        )
    )

    stored_session = repository.find_by_id(
        session.session_id
    )

    assert stored_session is not None
    assert stored_session.last_seen == result.last_seen


def test_should_keep_session_active_after_heartbeat() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()

    repository.save(session)

    use_case = HeartbeatSessionUseCase(repository)

    result = use_case.execute(
        HeartbeatSessionCommand(
            session_id=session.session_id,
        )
    )

    assert result.status == SessionStatus.ACTIVE

    stored_session = repository.find_by_id(
        session.session_id
    )

    assert stored_session is not None
    assert stored_session.status == SessionStatus.ACTIVE


def test_should_reject_unknown_session() -> None:
    repository = InMemorySessionRepository()
    use_case = HeartbeatSessionUseCase(repository)

    with pytest.raises(
        SessionNotFoundError,
        match="not found",
    ):
        use_case.execute(
            HeartbeatSessionCommand(
                session_id=uuid4(),
            )
        )


def test_should_reject_ended_session() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()
    session.end()

    repository.save(session)

    use_case = HeartbeatSessionUseCase(repository)

    with pytest.raises(
        SessionNotActiveError,
        match="ended",
    ):
        use_case.execute(
            HeartbeatSessionCommand(
                session_id=session.session_id,
            )
        )


def test_should_reject_expired_session() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()
    session.expire()

    repository.save(session)

    use_case = HeartbeatSessionUseCase(repository)

    with pytest.raises(
        SessionNotActiveError,
        match="expired",
    ):
        use_case.execute(
            HeartbeatSessionCommand(
                session_id=session.session_id,
            )
        )


def test_should_expire_session_when_expiration_time_has_passed() -> None:
    repository = InMemorySessionRepository()

    started_at = datetime.now(timezone.utc) - timedelta(
        minutes=31
    )

    session = Session(
        device_id=uuid4(),
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )

    repository.save(session)

    use_case = HeartbeatSessionUseCase(repository)

    with pytest.raises(
        SessionNotActiveError,
        match="has expired",
    ):
        use_case.execute(
            HeartbeatSessionCommand(
                session_id=session.session_id,
            )
        )

    stored_session = repository.find_by_id(
        session.session_id
    )

    assert stored_session is not None
    assert stored_session.status == SessionStatus.EXPIRED
    assert stored_session.ended_at is not None
