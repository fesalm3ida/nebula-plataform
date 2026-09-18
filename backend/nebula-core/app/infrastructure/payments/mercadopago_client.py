import httpx

from app.application.exceptions import PaymentGatewayError
from app.application.ports.payment_gateway import (
    CheckoutRequest,
    CheckoutResult,
    PaymentConfirmation,
    PaymentGateway,
)



# A API do Mercado Pago pode demorar; 20s evita falhas intermitentes.
_TIMEOUT = httpx.Timeout(20.0, connect=10.0)

class MercadoPagoClient(PaymentGateway):
    """Cliente do Mercado Pago (Checkout Pro)."""

    BASE_URL = "https://api.mercadopago.com"

    def __init__(
        self,
        access_token: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._access_token = access_token
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    async def create_checkout(
        self,
        request: CheckoutRequest,
    ) -> CheckoutResult:
        payload = {
            "items": [
                {
                    "title": request.title,
                    "unit_price": request.unit_price_cents / 100,
                    "quantity": 1,
                    "currency_id": "BRL",
                }
            ],
            "external_reference": request.external_reference,
        }

        if request.notification_url:
            payload["notification_url"] = request.notification_url

        if request.back_url:
            payload["back_urls"] = {
                "success": request.back_url,
                "pending": request.back_url,
                "failure": request.back_url,
            }

            # O Mercado Pago so aceita `auto_return` com back_url HTTPS;
            # com HTTP local enviamos apenas as back_urls.
            if request.back_url.startswith("https://"):
                payload["auto_return"] = "approved"

        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=_TIMEOUT) as client:
                response = await client.post(
                    f"{self.BASE_URL}/checkout/preferences",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as error:
            raise PaymentGatewayError(
                "Falha ao criar o checkout no Mercado Pago."
            ) from error

        return CheckoutResult(
            provider_reference=data["id"],
            checkout_url=data["init_point"],
        )

    async def find_merchant_order(
        self,
        merchant_order_id: str,
    ) -> PaymentConfirmation | None:
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=_TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/merchant_orders/{merchant_order_id}",
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as error:
            raise PaymentGatewayError(
                "Falha ao consultar a ordem no Mercado Pago."
            ) from error

        payments = data.get("payments") or []

        approved = next(
            (
                item
                for item in payments
                if item.get("status") == "approved"
            ),
            None,
        )

        if approved is not None:
            return PaymentConfirmation(
                status="approved",
                provider_payment_id=str(approved.get("id", "")),
                external_reference=data.get("external_reference"),
            )

        if data.get("order_status") == "paid":
            return PaymentConfirmation(
                status="approved",
                provider_payment_id="",
                external_reference=data.get("external_reference"),
            )

        if payments:
            return PaymentConfirmation(
                status=payments[0].get("status", "pending"),
                provider_payment_id=str(payments[0].get("id", "")),
                external_reference=data.get("external_reference"),
            )

        return PaymentConfirmation(
            status="pending",
            provider_payment_id="",
            external_reference=data.get("external_reference"),
        )

    async def find_payment(
        self,
        external_reference: str,
    ) -> PaymentConfirmation | None:
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=_TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/v1/payments/search",
                    headers=self._headers(),
                    params={"external_reference": external_reference},
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as error:
            raise PaymentGatewayError(
                "Falha ao consultar o pagamento no Mercado Pago."
            ) from error

        results = data.get("results") or []

        if not results:
            return None

        # O mais recente primeiro.
        payment = sorted(
            results,
            key=lambda item: item.get("date_created", ""),
            reverse=True,
        )[0]

        return PaymentConfirmation(
            status=payment.get("status", "unknown"),
            provider_payment_id=str(payment.get("id", "")),
            external_reference=payment.get("external_reference"),
        )

    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> PaymentConfirmation:
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=_TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/v1/payments/{provider_payment_id}",
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as error:
            raise PaymentGatewayError(
                "Falha ao consultar o pagamento no Mercado Pago."
            ) from error

        return PaymentConfirmation(
            status=data.get("status", "unknown"),
            provider_payment_id=str(data.get("id", provider_payment_id)),
            external_reference=data.get("external_reference"),
        )
