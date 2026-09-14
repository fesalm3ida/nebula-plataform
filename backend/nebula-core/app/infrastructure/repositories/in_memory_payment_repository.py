from uuid import UUID

from app.domain.entities.payment import Payment
from app.domain.repositories.payment_repository import PaymentRepository


class InMemoryPaymentRepository(PaymentRepository):
    def __init__(self) -> None:
        self._payments: dict[UUID, Payment] = {}

    def save(self, payment: Payment) -> None:
        self._payments[payment.payment_id] = payment

    def find_by_id(self, payment_id: UUID) -> Payment | None:
        return self._payments.get(payment_id)

    def find_by_provider_reference(
        self,
        provider_reference: str,
    ) -> Payment | None:
        return next(
            (
                payment
                for payment in self._payments.values()
                if payment.provider_reference == provider_reference
            ),
            None,
        )

    def find_by_provider_payment_id(
        self,
        provider_payment_id: str,
    ) -> Payment | None:
        return next(
            (
                payment
                for payment in self._payments.values()
                if payment.provider_payment_id == provider_payment_id
            ),
            None,
        )

    def find_all_by_device_id(self, device_id: UUID) -> list[Payment]:
        return [
            payment
            for payment in self._payments.values()
            if payment.device_id == device_id
        ]
