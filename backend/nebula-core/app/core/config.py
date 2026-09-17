from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, make_url


NEBULA_CORE_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = NEBULA_CORE_ROOT / ".env"
SECRETS_DIRECTORY = NEBULA_CORE_ROOT / ".secrets"


class Settings(BaseSettings):
    app_name: str = Field(
        default="Nebula Core",
        validation_alias=AliasChoices(
            "APP_NAME",
            "app_name",
        ),
    )

    app_version: str = Field(
        default="0.3.0-dev",
        validation_alias=AliasChoices(
            "APP_VERSION",
            "app_version",
        ),
    )

    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices(
            "APP_ENV",
            "app_env",
        ),
    )

    app_debug: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "APP_DEBUG",
            "app_debug",
        ),
    )

    postgres_host: str = Field(
        default="localhost",
        validation_alias=AliasChoices(
            "POSTGRES_HOST",
            "PGHOST",
            "postgres_host",
        ),
    )

    postgres_port: int = Field(
        default=5434,
        validation_alias=AliasChoices(
            "POSTGRES_PORT",
            "PGPORT",
            "postgres_port",
        ),
    )

    postgres_db: str = Field(
        default="nebula",
        validation_alias=AliasChoices(
            "POSTGRES_DB",
            "PGDATABASE",
            "postgres_db",
        ),
    )

    postgres_user: str = Field(
        default="nebula",
        validation_alias=AliasChoices(
            "POSTGRES_USER",
            "PGUSER",
            "postgres_user",
        ),
    )

    postgres_password: str = Field(
        default="",
        validation_alias=AliasChoices(
            "POSTGRES_PASSWORD",
            "PGPASSWORD",
            "postgres_password",
        ),
    )

    # Provedores gerenciados (Railway/Render/Heroku) entregam uma URL unica.
    database_url_value: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "DATABASE_URL",
            "database_url_value",
        ),
    )

    database_echo: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "DATABASE_ECHO",
            "database_echo",
        ),
    )

    jwt_secret_key: str = Field(
        validation_alias=AliasChoices(
            "JWT_SECRET_KEY",
            "jwt_secret_key",
        ),
    )

    jwt_issuer: str = Field(
        default="nebula-core",
        validation_alias=AliasChoices(
            "JWT_ISSUER",
            "jwt_issuer",
        ),
    )

    jwt_audience: str = Field(
        default="nebula-player",
        validation_alias=AliasChoices(
            "JWT_AUDIENCE",
            "jwt_audience",
        ),
    )

    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices(
            "JWT_ALGORITHM",
            "jwt_algorithm",
        ),
    )

    jwt_access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        validation_alias=AliasChoices(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "jwt_access_token_expire_minutes",
        ),
    )

    admin_api_key: str = Field(
        default="dev-admin-key",
        validation_alias=AliasChoices(
            "ADMIN_API_KEY",
            "admin_api_key",
        ),
    )

    mercadopago_access_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "MERCADOPAGO_ACCESS_TOKEN",
            "mercadopago_access_token",
        ),
    )

    mercadopago_webhook_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "MERCADOPAGO_WEBHOOK_SECRET",
            "mercadopago_webhook_secret",
        ),
    )

    payment_provider: str = Field(
        default="mercadopago",
        validation_alias=AliasChoices(
            "PAYMENT_PROVIDER",
            "payment_provider",
        ),
    )

    mercadopago_notification_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "MERCADOPAGO_NOTIFICATION_URL",
            "mercadopago_notification_url",
        ),
    )

    mercadopago_back_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "MERCADOPAGO_BACK_URL",
            "mercadopago_back_url",
        ),
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        secrets_dir=SECRETS_DIRECTORY,
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def _validate_database(self) -> "Settings":
        """Garante que exista uma forma de conectar ao banco."""
        if not self.database_url_value and not self.postgres_password:
            raise ValueError(
                "Provide DATABASE_URL or POSTGRES_PASSWORD "
                "(the password may also come from "
                ".secrets/postgres_password)."
            )

        return self

    @property
    def database_url(self) -> URL:
        """URL do banco: usa DATABASE_URL quando presente."""
        if self.database_url_value:
            raw = self.database_url_value

            # Railway/Heroku usam postgres:// ou postgresql://; aqui o driver
            # e o psycopg 3 (postgresql+psycopg://).
            for prefix in ("postgres://", "postgresql://"):
                if raw.startswith(prefix):
                    raw = "postgresql+psycopg://" + raw[len(prefix):]
                    break

            return make_url(raw)

        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
