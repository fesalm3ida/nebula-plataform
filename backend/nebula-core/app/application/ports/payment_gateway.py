from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutRequest:
    """Dados para criar um checkout no provedor de pagamento."""

    title: str
    unit_price_cents: int
    external_reference: str
    notification_url: str | None = None
    back_url: str | None = None


@dataclass(frozen=True)
class CheckoutResult:
    """Checkout criado no provedor."""

    provider_reference: str
    checkout_url: str


@dataclass(frozen=True)
class PaymentConfirmation:
    """Estado de um pagamento consultado no provedor."""

    status: str
    provider_payment_id: str
    external_reference: str | None = None

    @property
    def is_approved(self) -> bool:
        return self.status == "approved"


class PaymentGateway(ABC):
    """Porta para o provedor de pagamento (Mercado Pago)."""

    @abstractmethod
    async def create_checkout(
        self,
        request: CheckoutRequest,
    ) -> CheckoutResult:
        """Cria o checkout e devolve o link de pagamento."""

    @abstractmethod
    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> PaymentConfirmation:
        """Consulta o estado de um pagamento pelo id do provedor."""

    @abstractmethod
    async def find_payment(
        self,
        external_reference: str,
    ) -> PaymentConfirmation | None:
        """Busca o pagamento pela referência externa (nosso Payment)."""
