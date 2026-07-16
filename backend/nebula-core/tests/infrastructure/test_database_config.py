from app.core.config import Settings


def test_should_build_postgresql_database_url() -> None:
    settings = Settings(
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5434,
        POSTGRES_DB="nebula",
        POSTGRES_USER="nebula",
        POSTGRES_PASSWORD="secret-password",
    )

    database_url = settings.database_url

    assert database_url.drivername == "postgresql+psycopg"
    assert database_url.host == "localhost"
    assert database_url.port == 5434
    assert database_url.database == "nebula"
    assert database_url.username == "nebula"
    assert database_url.password == "secret-password"


def test_should_hide_password_when_rendering_database_url() -> None:
    settings = Settings(
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5434,
        POSTGRES_DB="nebula",
        POSTGRES_USER="nebula",
        POSTGRES_PASSWORD="super-secret-password",
    )

    rendered_url = settings.database_url.render_as_string(
        hide_password=True
    )

    assert "super-secret-password" not in rendered_url
    assert "***" in rendered_url
