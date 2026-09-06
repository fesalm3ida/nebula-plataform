from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from app.domain.entities.log import Log
from app.domain.enums.log_level import LogLevel


def make_log(
    *,
    level: LogLevel = LogLevel.INFO,
    message: str = "Application started",
    occurred_at: datetime | None = None,
    received_at: datetime | None = None,
) -> Log:
    now = datetime.now(timezone.utc)

    return Log(
        session_id=uuid4(),
        device_id=uuid4(),
        level=level,
        message=message,
        occurred_at=occurred_at or now,
        received_at=received_at or now,
    )


def test_should_create_log() -> None:
    log = make_log()

    assert isinstance(log.log_id, UUID)
    assert log.level == LogLevel.INFO
    assert log.message == "Application started"


def test_should_reject_invalid_level() -> None:
    with pytest.raises(
        ValueError,
        match="level must be a valid LogLevel",
    ):
        make_log(level="info")  # type: ignore[arg-type]


def test_should_reject_empty_message() -> None:
    with pytest.raises(
        ValueError,
        match="message cannot be empty",
    ):
        make_log(message="   ")


def test_should_reject_naive_occurred_at() -> None:
    with pytest.raises(
        ValueError,
        match="occurred_at must include timezone information",
    ):
        make_log(occurred_at=datetime.now())


def test_should_reject_received_at_before_occurred_at() -> None:
    occurred_at = datetime.now(timezone.utc)
    received_at = occurred_at - timedelta(seconds=1)

    with pytest.raises(
        ValueError,
        match="received_at cannot be earlier than occurred_at",
    ):
        make_log(
            occurred_at=occurred_at,
            received_at=received_at,
        )
