from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.enums.license_product import LicenseProduct
from app.domain.enums.payment_status import PaymentStatus


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Payment:
    """Pagamento de uma licença feito pelo usuário no portal."""

    device_id: UUID
    product: LicenseProduct
    amount_cents: int
    payment_id: UUID = field(default_factory=uuid4)
    status: PaymentStatus = PaymentStatus.PENDING
    provider: str = "mercadopago"
    provider_reference: str | None = None
    provider_payment_id: str | None = None
    checkout_url: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    approved_at: datetime | None = None

    @property
    def is_approved(self) -> bool:
        return self.status == PaymentStatus.APPROVED

    @property
    def is_pending(self) -> bool:
        return self.status == PaymentStatus.PENDING

    def approve(
        self,
        provider_payment_id: str | None = None,
        now: datetime | None = None,
    ) -> None:
        if self.status == PaymentStatus.APPROVED:
            return

        reference = now or _utcnow()

        self.status = PaymentStatus.APPROVED
        self.approved_at = reference
        self.updated_at = reference

        if provider_payment_id:
            self.provider_payment_id = provider_payment_id

    def reject(
        self,
        provider_payment_id: str | None = None,
        now: datetime | None = None,
    ) -> None:
        self.status = PaymentStatus.REJECTED
        self.updated_at = now or _utcnow()

        if provider_payment_id:
            self.provider_payment_id = provider_payment_id

    def cancel(self, now: datetime | None = None) -> None:
        self.status = PaymentStatus.CANCELLED
        self.updated_at = now or _utcnow()
