import asyncio
import json

import httpx
import pytest

from app.application.exceptions import PaymentGatewayError
from app.application.ports.payment_gateway import CheckoutRequest
from app.infrastructure.payments.mercadopago_client import (
    MercadoPagoClient,
)


def _client(handler) -> MercadoPagoClient:
    return MercadoPagoClient(
        "TEST-TOKEN",
        transport=httpx.MockTransport(handler),
    )


def test_should_send_auto_return_with_https_back_url() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)

        return httpx.Response(
            201,
            json={"id": "pref-1", "init_point": "https://mp/checkout"},
        )

    result = asyncio.run(
        _client(handler).create_checkout(
            CheckoutRequest(
                title="Licença anual",
                unit_price_cents=9900,
                external_reference="pay-1",
                back_url="https://portal.ngrok-free.app",
            )
        )
    )

    assert result.checkout_url == "https://mp/checkout"
    assert captured["body"]["auto_return"] == "approved"
    assert (
        captured["body"]["back_urls"]["success"]
        == "https://portal.ngrok-free.app"
    )


def test_should_omit_auto_return_for_http_back_url() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)

        return httpx.Response(
            201,
            json={"id": "pref-1", "init_point": "https://mp/checkout"},
        )

    asyncio.run(
        _client(handler).create_checkout(
            CheckoutRequest(
                title="Licença anual",
                unit_price_cents=9900,
                external_reference="pay-1",
                back_url="http://172.18.88.46:3000",
            )
        )
    )

    # O Mercado Pago rejeita auto_return quando a back_url nao e HTTPS.
    assert "auto_return" not in captured["body"]
    assert (
        captured["body"]["back_urls"]["success"]
        == "http://172.18.88.46:3000"
    )


def test_should_not_send_auto_return_without_back_url() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)

        return httpx.Response(
            201,
            json={"id": "pref-1", "init_point": "https://mp/checkout"},
        )

    asyncio.run(
        _client(handler).create_checkout(
            CheckoutRequest(
                title="Licença anual",
                unit_price_cents=9900,
                external_reference="pay-1",
            )
        )
    )

    # O Mercado Pago rejeita auto_return sem back_urls.
    assert "auto_return" not in captured["body"]
    assert "back_urls" not in captured["body"]


def test_should_forward_notification_url() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)

        return httpx.Response(
            201,
            json={"id": "pref-1", "init_point": "https://mp/checkout"},
        )

    asyncio.run(
        _client(handler).create_checkout(
            CheckoutRequest(
                title="Licença vitalícia",
                unit_price_cents=29900,
                external_reference="pay-2",
                notification_url="https://ngrok/webhooks/mercadopago",
            )
        )
    )

    assert (
        captured["body"]["notification_url"]
        == "https://ngrok/webhooks/mercadopago"
    )


def test_should_raise_payment_gateway_error_on_provider_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"message": "auto_return invalid"},
        )

    with pytest.raises(PaymentGatewayError):
        asyncio.run(
            _client(handler).create_checkout(
                CheckoutRequest(
                    title="Licença anual",
                    unit_price_cents=9900,
                    external_reference="pay-1",
                )
            )
        )
