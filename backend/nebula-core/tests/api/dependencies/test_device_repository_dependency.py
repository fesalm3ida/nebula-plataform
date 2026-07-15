from unittest.mock import Mock

from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.infrastructure.repositories.postgresql_device_repository import (
    PostgreSQLDeviceRepository,
)


def test_should_create_postgresql_device_repository() -> None:
    database_session = Mock(spec=SQLAlchemySession)

    repository = get_device_repository(database_session)

    assert isinstance(
        repository,
        PostgreSQLDeviceRepository,
    )


def test_should_use_injected_database_session() -> None:
    database_session = Mock(spec=SQLAlchemySession)

    repository = get_device_repository(database_session)

    assert repository._database_session is database_session
