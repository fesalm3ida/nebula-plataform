from enum import Enum


class PaymentStatus(str, Enum):
    """Situação de um pagamento de licença."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
