from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


NEBULA_ADMIN_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = NEBULA_ADMIN_ROOT / ".env"
SECRETS_DIRECTORY = NEBULA_ADMIN_ROOT / ".secrets"


class Settings(BaseSettings):
    app_name: str = Field(
        default="Nebula Admin",
        validation_alias=AliasChoices("APP_NAME", "app_name"),
    )

    app_version: str = Field(
        default="0.1.0-dev",
        validation_alias=AliasChoices("APP_VERSION", "app_version"),
    )

    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "app_env"),
    )

    # Admin JWT: identidade administrativa (separada da identidade de Device).
    admin_jwt_secret_key: str = Field(
        validation_alias=AliasChoices(
            "ADMIN_JWT_SECRET_KEY",
            "admin_jwt_secret_key",
        ),
    )

    admin_jwt_issuer: str = Field(
        default="nebula-admin",
        validation_alias=AliasChoices(
            "ADMIN_JWT_ISSUER",
            "admin_jwt_issuer",
        ),
    )

    admin_jwt_audience: str = Field(
        default="nebula-admin-ui",
        validation_alias=AliasChoices(
            "ADMIN_JWT_AUDIENCE",
            "admin_jwt_audience",
        ),
    )

    admin_jwt_algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices(
            "ADMIN_JWT_ALGORITHM",
            "admin_jwt_algorithm",
        ),
    )

    admin_jwt_access_token_expire_minutes: int = Field(
        default=60,
        gt=0,
        validation_alias=AliasChoices(
            "ADMIN_JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "admin_jwt_access_token_expire_minutes",
        ),
    )

    # Comunicação service-to-service com o Nebula Core.
    nebula_core_base_url: str = Field(
        validation_alias=AliasChoices(
            "NEBULA_CORE_BASE_URL",
            "nebula_core_base_url",
        ),
    )

    nebula_core_service_token: str = Field(
        validation_alias=AliasChoices(
            "NEBULA_CORE_SERVICE_TOKEN",
            "nebula_core_service_token",
        ),
    )

    # Administrador de bootstrap (primeira identidade administrativa).
    admin_seed_email: str = Field(
        default="admin@nebula.local",
        validation_alias=AliasChoices(
            "ADMIN_SEED_EMAIL",
            "admin_seed_email",
        ),
    )

    admin_seed_password: str = Field(
        validation_alias=AliasChoices(
            "ADMIN_SEED_PASSWORD",
            "admin_seed_password",
        ),
    )

    admin_seed_role: str = Field(
        default="super_admin",
        validation_alias=AliasChoices(
            "ADMIN_SEED_ROLE",
            "admin_seed_role",
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
