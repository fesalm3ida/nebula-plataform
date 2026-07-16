from sqlalchemy import text

from app.infrastructure.persistence.database import engine


def test_should_connect_to_postgresql() -> None:
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    current_database() AS database_name,
                    current_user AS database_user
                """
            )
        ).mappings().one()

    assert result["database_name"] == "nebula"
    assert result["database_user"] == "nebula"
