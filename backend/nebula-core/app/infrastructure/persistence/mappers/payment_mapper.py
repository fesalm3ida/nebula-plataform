from app.domain.entities.payment import Payment
from app.domain.enums.license_product import LicenseProduct
from app.domain.enums.payment_status import PaymentStatus
from app.infrastructure.persistence.models.payment_model import (
    PaymentModel,
)


class PaymentMapper:
    @staticmethod
    def to_model(payment: Payment) -> PaymentModel:
        return PaymentModel(
            payment_id=payment.payment_id,
            device_id=payment.device_id,
            product=payment.product.value,
            amount_cents=payment.amount_cents,
            status=payment.status.value,
            provider=payment.provider,
            provider_reference=payment.provider_reference,
            provider_payment_id=payment.provider_payment_id,
            checkout_url=payment.checkout_url,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            approved_at=payment.approved_at,
        )

    @staticmethod
    def to_domain(model: PaymentModel) -> Payment:
        payment = Payment(
            device_id=model.device_id,
            product=LicenseProduct(model.product),
            amount_cents=model.amount_cents,
        )

        payment.payment_id = model.payment_id
        payment.status = PaymentStatus(model.status)
        payment.provider = model.provider
        payment.provider_reference = model.provider_reference
        payment.provider_payment_id = model.provider_payment_id
        payment.checkout_url = model.checkout_url
        payment.created_at = model.created_at
        payment.updated_at = model.updated_at
        payment.approved_at = model.approved_at

        return payment
