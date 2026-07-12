from app.api.dependencies.session_repository import (
    get_session_repository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)


def test_should_return_same_session_repository_instance() -> None:
    first_repository = get_session_repository()
    second_repository = get_session_repository()

    assert isinstance(
        first_repository,
        InMemorySessionRepository,
    )
    assert first_repository is second_repository
