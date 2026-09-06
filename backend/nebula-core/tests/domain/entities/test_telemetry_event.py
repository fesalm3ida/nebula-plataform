from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.enums.telemetry_event_type import TelemetryEventType


def make_event(
    *,
    event_type: TelemetryEventType = TelemetryEventType.PLAYBACK_STARTED,
    payload: dict | None = None,
    occurred_at: datetime | None = None,
    received_at: datetime | None = None,
) -> TelemetryEvent:
    now = datetime.now(timezone.utc)

    return TelemetryEvent(
        session_id=uuid4(),
        device_id=uuid4(),
        event_type=event_type,
        payload=payload if payload is not None else {"duration_ms": 100},
        occurred_at=occurred_at or now,
        received_at=received_at or now,
    )


def test_should_create_telemetry_event() -> None:
    event = make_event()

    assert isinstance(event.event_id, UUID)
    assert event.event_type == TelemetryEventType.PLAYBACK_STARTED
    assert event.payload == {"duration_ms": 100}


def test_should_reject_invalid_event_type() -> None:
    with pytest.raises(
        ValueError,
        match="event_type must be a valid TelemetryEventType",
    ):
        make_event(event_type="playback_started")  # type: ignore[arg-type]


def test_should_reject_non_dict_payload() -> None:
    with pytest.raises(
        ValueError,
        match="payload must be a dictionary",
    ):
        make_event(payload=["not", "a", "dict"])  # type: ignore[arg-type]


def test_should_reject_naive_occurred_at() -> None:
    with pytest.raises(
        ValueError,
        match="occurred_at must include timezone information",
    ):
        make_event(occurred_at=datetime.now())


def test_should_reject_received_at_before_occurred_at() -> None:
    occurred_at = datetime.now(timezone.utc)
    received_at = occurred_at - timedelta(seconds=1)

    with pytest.raises(
        ValueError,
        match="received_at cannot be earlier than occurred_at",
    ):
        make_event(
            occurred_at=occurred_at,
            received_at=received_at,
        )
