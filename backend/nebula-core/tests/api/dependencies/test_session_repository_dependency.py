from unittest.mock import Mock

from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.session_repository import (
    get_session_repository,
)
from app.infrastructure.repositories.postgresql_session_repository import (
    PostgreSQLSessionRepository,
)


def test_should_create_postgresql_session_repository() -> None:
    database_session = Mock(spec=SQLAlchemySession)

    repository = get_session_repository(database_session)

    assert isinstance(
        repository,
        PostgreSQLSessionRepository,
    )


def test_should_use_injected_database_session() -> None:
    database_session = Mock(spec=SQLAlchemySession)

    repository = get_session_repository(database_session)

    assert repository._database_session is database_session
