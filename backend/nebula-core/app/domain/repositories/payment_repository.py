from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    def save(self, payment: Payment) -> None:
        """Persist a Payment."""

    @abstractmethod
    def find_by_id(self, payment_id: UUID) -> Payment | None:
        """Find a Payment by its identifier."""

    @abstractmethod
    def find_by_provider_reference(
        self,
        provider_reference: str,
    ) -> Payment | None:
        """Find a Payment by the checkout reference from the provider."""

    @abstractmethod
    def find_by_provider_payment_id(
        self,
        provider_payment_id: str,
    ) -> Payment | None:
        """Find a Payment by the provider payment identifier."""

    @abstractmethod
    def find_all_by_device_id(self, device_id: UUID) -> list[Payment]:
        """List the Payments of a Device."""
