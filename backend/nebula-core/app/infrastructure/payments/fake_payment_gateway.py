from uuid import uuid4

from app.application.ports.payment_gateway import (
    CheckoutRequest,
    CheckoutResult,
    PaymentConfirmation,
    PaymentGateway,
)


class FakePaymentGateway(PaymentGateway):
    """Provedor fake para desenvolvimento/testes (sem chamadas reais).

    Cria um checkout simulado e considera qualquer pagamento como aprovado,
    retornando o `external_reference` do último checkout (simula o fluxo do
    Mercado Pago, onde o pagamento carrega a referência da preferência).
    """

    def __init__(self) -> None:
        self._external_reference: str | None = None

    async def create_checkout(
        self,
        request: CheckoutRequest,
    ) -> CheckoutResult:
        self._external_reference = request.external_reference

        reference = f"fake-{uuid4()}"

        return CheckoutResult(
            provider_reference=reference,
            checkout_url=f"https://checkout.mercadopago.fake/{reference}",
        )

    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> PaymentConfirmation:
        return PaymentConfirmation(
            status="approved",
            provider_payment_id=provider_payment_id,
            external_reference=self._external_reference,
        )

    async def find_payment(
        self,
        external_reference: str,
    ) -> PaymentConfirmation | None:
        if external_reference != self._external_reference:
            return None

        return PaymentConfirmation(
            status="approved",
            provider_payment_id=f"fake-payment-{external_reference}",
            external_reference=external_reference,
        )
