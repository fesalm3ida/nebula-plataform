from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from app.application.exceptions import (
    SessionNotActiveError,
    SessionNotFoundError,
    SessionOwnershipError,
)
from app.application.use_cases.ingest_telemetry_event import (
    IngestTelemetryEventCommand,
    IngestTelemetryEventUseCase,
)
from app.domain.entities.session import Session
from app.domain.enums.telemetry_event_type import TelemetryEventType
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from app.infrastructure.repositories.in_memory_telemetry_event_repository import (
    InMemoryTelemetryEventRepository,
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


def test_should_ingest_event_for_owned_active_session() -> None:
    session_repository = InMemorySessionRepository()
    telemetry_repository = InMemoryTelemetryEventRepository()

    device_id = uuid4()
    session = make_session(device_id)
    session_repository.save(session)

    use_case = IngestTelemetryEventUseCase(
        telemetry_event_repository=telemetry_repository,
        session_repository=session_repository,
    )

    result = use_case.execute(
        IngestTelemetryEventCommand(
            device_id=device_id,
            session_id=session.session_id,
            event_type=TelemetryEventType.PLAYBACK_STARTED,
            payload={"duration_ms": 100},
        )
    )

    assert isinstance(result.event_id, UUID)
    assert telemetry_repository.find_by_id(result.event_id) is not None


def test_should_raise_when_session_does_not_exist() -> None:
    session_repository = InMemorySessionRepository()
    telemetry_repository = InMemoryTelemetryEventRepository()

    use_case = IngestTelemetryEventUseCase(
        telemetry_event_repository=telemetry_repository,
        session_repository=session_repository,
    )

    with pytest.raises(SessionNotFoundError):
        use_case.execute(
            IngestTelemetryEventCommand(
                device_id=uuid4(),
                session_id=uuid4(),
                event_type=TelemetryEventType.QOS_REPORT,
                payload={},
            )
        )


def test_should_raise_when_session_not_owned() -> None:
    session_repository = InMemorySessionRepository()
    telemetry_repository = InMemoryTelemetryEventRepository()

    other_device_id = uuid4()
    session = make_session(other_device_id)
    session_repository.save(session)

    use_case = IngestTelemetryEventUseCase(
        telemetry_event_repository=telemetry_repository,
        session_repository=session_repository,
    )

    with pytest.raises(SessionOwnershipError):
        use_case.execute(
            IngestTelemetryEventCommand(
                device_id=uuid4(),
                session_id=session.session_id,
                event_type=TelemetryEventType.QOS_REPORT,
                payload={},
            )
        )


def test_should_raise_when_session_not_active() -> None:
    session_repository = InMemorySessionRepository()
    telemetry_repository = InMemoryTelemetryEventRepository()

    device_id = uuid4()
    session = make_session(device_id, active=False)
    session_repository.save(session)

    use_case = IngestTelemetryEventUseCase(
        telemetry_event_repository=telemetry_repository,
        session_repository=session_repository,
    )

    with pytest.raises(SessionNotActiveError):
        use_case.execute(
            IngestTelemetryEventCommand(
                device_id=device_id,
                session_id=session.session_id,
                event_type=TelemetryEventType.QOS_REPORT,
                payload={},
            )
        )
