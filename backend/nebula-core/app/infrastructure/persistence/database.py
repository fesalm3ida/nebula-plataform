from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


settings = get_settings()


engine: Engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)


SessionFactory = sessionmaker(
    bind=engine,
    class_=SQLAlchemySession,
    autoflush=False,
    expire_on_commit=False,
)


def create_database_session() -> SQLAlchemySession:
    """Create a new SQLAlchemy database session."""

    return SessionFactory()


def get_database_session() -> Generator[
    SQLAlchemySession,
    None,
    None,
]:
    """Provide one database session for a request lifecycle."""

    database_session = create_database_session()

    try:
        yield database_session
    except Exception:
        database_session.rollback()
        raise
    finally:
        database_session.close()
