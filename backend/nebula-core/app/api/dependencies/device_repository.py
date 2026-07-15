from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db
from app.domain.repositories.device_repository import DeviceRepository
from app.infrastructure.repositories.postgresql_device_repository import (
    PostgreSQLDeviceRepository,
)


def get_device_repository(
    database_session: Annotated[
        SQLAlchemySession,
        Depends(get_db),
    ],
) -> DeviceRepository:
    return PostgreSQLDeviceRepository(database_session)
