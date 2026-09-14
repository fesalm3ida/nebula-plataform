from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.payment import Payment
from app.domain.repositories.payment_repository import PaymentRepository
from app.infrastructure.persistence.mappers.payment_mapper import (
    PaymentMapper,
)
from app.infrastructure.persistence.models.payment_model import (
    PaymentModel,
)


class PostgreSQLPaymentRepository(PaymentRepository):
    def __init__(
        self,
        database_session: SQLAlchemySession,
    ) -> None:
        self._database_session = database_session

    def save(self, payment: Payment) -> None:
        model = PaymentMapper.to_model(payment)

        self._database_session.merge(model)
        self._database_session.commit()

    def find_by_id(self, payment_id: UUID) -> Payment | None:
        statement = select(PaymentModel).where(
            PaymentModel.payment_id == payment_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return PaymentMapper.to_domain(model)

    def find_by_provider_reference(
        self,
        provider_reference: str,
    ) -> Payment | None:
        statement = select(PaymentModel).where(
            PaymentModel.provider_reference == provider_reference
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return PaymentMapper.to_domain(model)

    def find_by_provider_payment_id(
        self,
        provider_payment_id: str,
    ) -> Payment | None:
        statement = select(PaymentModel).where(
            PaymentModel.provider_payment_id == provider_payment_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return PaymentMapper.to_domain(model)

    def find_all_by_device_id(self, device_id: UUID) -> list[Payment]:
        statement = select(PaymentModel).where(
            PaymentModel.device_id == device_id
        )

        models = self._database_session.execute(statement).scalars().all()

        return [PaymentMapper.to_domain(model) for model in models]
