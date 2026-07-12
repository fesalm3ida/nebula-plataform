from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)


_session_repository = InMemorySessionRepository()


def get_session_repository() -> SessionRepository:
    return _session_repository
