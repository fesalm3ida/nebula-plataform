from app.application.ports.payment_gateway import PaymentGateway
from app.core.config import get_settings
from app.infrastructure.payments.fake_payment_gateway import (
    FakePaymentGateway,
)
from app.infrastructure.payments.mercadopago_client import (
    MercadoPagoClient,
)


def get_payment_gateway() -> PaymentGateway:
    """Resolve o provedor de pagamento.

    Usa o Mercado Pago quando `MERCADOPAGO_ACCESS_TOKEN` está definido; caso
    contrário, usa o provedor fake (desenvolvimento/testes).
    """
    settings = get_settings()

    token = settings.mercadopago_access_token

    if not token:
        return FakePaymentGateway()

    return MercadoPagoClient(access_token=token)
