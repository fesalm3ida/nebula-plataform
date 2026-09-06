from uuid import uuid4

from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.enums.telemetry_event_type import TelemetryEventType
from app.infrastructure.repositories.in_memory_telemetry_event_repository import (
    InMemoryTelemetryEventRepository,
)


def make_event() -> TelemetryEvent:
    return TelemetryEvent(
        session_id=uuid4(),
        device_id=uuid4(),
        event_type=TelemetryEventType.PLAYBACK_STARTED,
        payload={"duration_ms": 100},
    )


def test_should_save_and_find_event_by_id() -> None:
    repository = InMemoryTelemetryEventRepository()
    event = make_event()

    repository.save(event)

    restored = repository.find_by_id(event.event_id)

    assert restored is not None
    assert restored.event_id == event.event_id
    assert restored.event_type == TelemetryEventType.PLAYBACK_STARTED


def test_should_return_none_for_unknown_event() -> None:
    repository = InMemoryTelemetryEventRepository()

    assert repository.find_by_id(make_event().event_id) is None
