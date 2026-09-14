from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db
from app.domain.repositories.payment_repository import PaymentRepository
from app.infrastructure.repositories.postgresql_payment_repository import (
    PostgreSQLPaymentRepository,
)


def get_payment_repository(
    database_session: Annotated[
        SQLAlchemySession,
        Depends(get_db),
    ],
) -> PaymentRepository:
    return PostgreSQLPaymentRepository(database_session)
