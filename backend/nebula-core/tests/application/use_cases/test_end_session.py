from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.application.exceptions import (
    SessionAlreadyClosedError,
    SessionNotFoundError,
)
from app.application.use_cases.end_session import (
    EndSessionCommand,
    EndSessionUseCase,
)
from app.domain.entities.session import Session
from app.domain.enums.session_status import SessionStatus
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)


def make_active_session() -> Session:
    return Session(
        device_id=uuid4(),
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=30),
    )


def test_should_end_active_session() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()
    repository.save(session)

    use_case = EndSessionUseCase(repository)

    result = use_case.execute(
        EndSessionCommand(session_id=session.session_id)
    )

    assert result.session_id == session.session_id
    assert result.status == SessionStatus.ENDED
    assert result.ended_at is not None


def test_should_persist_ended_session() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()
    repository.save(session)

    use_case = EndSessionUseCase(repository)

    use_case.execute(
        EndSessionCommand(session_id=session.session_id)
    )

    stored_session = repository.find_by_id(session.session_id)

    assert stored_session is not None
    assert stored_session.status == SessionStatus.ENDED
    assert stored_session.ended_at is not None


def test_should_reject_unknown_session() -> None:
    repository = InMemorySessionRepository()
    use_case = EndSessionUseCase(repository)

    with pytest.raises(SessionNotFoundError, match="not found"):
        use_case.execute(
            EndSessionCommand(session_id=uuid4())
        )


def test_should_reject_already_ended_session() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()
    session.end()
    repository.save(session)

    use_case = EndSessionUseCase(repository)

    with pytest.raises(
        SessionAlreadyClosedError,
        match="ended",
    ):
        use_case.execute(
            EndSessionCommand(session_id=session.session_id)
        )


def test_should_reject_expired_session() -> None:
    repository = InMemorySessionRepository()
    session = make_active_session()
    session.expire()
    repository.save(session)

    use_case = EndSessionUseCase(repository)

    with pytest.raises(
        SessionAlreadyClosedError,
        match="expired",
    ):
        use_case.execute(
            EndSessionCommand(session_id=session.session_id)
        )
