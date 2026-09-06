from uuid import uuid4

from app.domain.entities.log import Log
from app.domain.enums.log_level import LogLevel
from app.infrastructure.repositories.in_memory_log_repository import (
    InMemoryLogRepository,
)


def make_log() -> Log:
    return Log(
        session_id=uuid4(),
        device_id=uuid4(),
        level=LogLevel.WARNING,
        message="Buffer underrun detected",
    )


def test_should_save_and_find_log_by_id() -> None:
    repository = InMemoryLogRepository()
    log = make_log()

    repository.save(log)

    restored = repository.find_by_id(log.log_id)

    assert restored is not None
    assert restored.log_id == log.log_id
    assert restored.level == LogLevel.WARNING


def test_should_return_none_for_unknown_log() -> None:
    repository = InMemoryLogRepository()

    assert repository.find_by_id(make_log().log_id) is None
