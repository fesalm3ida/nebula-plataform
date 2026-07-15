from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db


def test_should_provide_database_session() -> None:
    dependency = get_db()
    database_session = next(dependency)

    try:
        assert isinstance(
            database_session,
            SQLAlchemySession,
        )
        assert database_session.is_active is True
    finally:
        dependency.close()


def test_should_close_database_session_after_dependency_finishes() -> None:
    dependency = get_db()
    database_session = next(dependency)

    dependency.close()

    assert database_session.in_transaction() is False
