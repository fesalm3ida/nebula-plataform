from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from app.application.exceptions import (
    SessionNotActiveError,
    SessionNotFoundError,
    SessionOwnershipError,
)
from app.application.use_cases.ingest_log import (
    IngestLogCommand,
    IngestLogUseCase,
)
from app.domain.entities.session import Session
from app.domain.enums.log_level import LogLevel
from app.infrastructure.repositories.in_memory_log_repository import (
    InMemoryLogRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)


def make_session(
    device_id: UUID,
    *,
    active: bool = True,
) -> Session:
    started_at = datetime.now(timezone.utc)
    session = Session(
        device_id=device_id,
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )

    if not active:
        session.end()

    return session


def test_should_ingest_log_for_owned_active_session() -> None:
    session_repository = InMemorySessionRepository()
    log_repository = InMemoryLogRepository()

    device_id = uuid4()
    session = make_session(device_id)
    session_repository.save(session)

    use_case = IngestLogUseCase(
        log_repository=log_repository,
        session_repository=session_repository,
    )

    result = use_case.execute(
        IngestLogCommand(
            device_id=device_id,
            session_id=session.session_id,
            level=LogLevel.WARNING,
            message="Buffer underrun detected",
        )
    )

    assert isinstance(result.log_id, UUID)
    assert log_repository.find_by_id(result.log_id) is not None


def test_should_raise_when_session_does_not_exist() -> None:
    session_repository = InMemorySessionRepository()
    log_repository = InMemoryLogRepository()

    use_case = IngestLogUseCase(
        log_repository=log_repository,
        session_repository=session_repository,
    )

    with pytest.raises(SessionNotFoundError):
        use_case.execute(
            IngestLogCommand(
                device_id=uuid4(),
                session_id=uuid4(),
                level=LogLevel.ERROR,
                message="boom",
            )
        )


def test_should_raise_when_session_not_owned() -> None:
    session_repository = InMemorySessionRepository()
    log_repository = InMemoryLogRepository()

    other_device_id = uuid4()
    session = make_session(other_device_id)
    session_repository.save(session)

    use_case = IngestLogUseCase(
        log_repository=log_repository,
        session_repository=session_repository,
    )

    with pytest.raises(SessionOwnershipError):
        use_case.execute(
            IngestLogCommand(
                device_id=uuid4(),
                session_id=session.session_id,
                level=LogLevel.ERROR,
                message="boom",
            )
        )


def test_should_raise_when_session_not_active() -> None:
    session_repository = InMemorySessionRepository()
    log_repository = InMemoryLogRepository()

    device_id = uuid4()
    session = make_session(device_id, active=False)
    session_repository.save(session)

    use_case = IngestLogUseCase(
        log_repository=log_repository,
        session_repository=session_repository,
    )

    with pytest.raises(SessionNotActiveError):
        use_case.execute(
            IngestLogCommand(
                device_id=device_id,
                session_id=session.session_id,
                level=LogLevel.INFO,
                message="info",
            )
        )
