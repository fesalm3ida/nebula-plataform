from uuid import uuid4

from app.domain.entities.payment import Payment
from app.domain.enums.license_product import LicenseProduct
from app.domain.enums.license_type import LicenseType
from app.domain.enums.payment_status import PaymentStatus
from app.domain.licensing.catalog import PLANS, get_plan, list_plans


def make_payment() -> Payment:
    return Payment(
        device_id=uuid4(),
        product=LicenseProduct.ANNUAL,
        amount_cents=9900,
    )


def test_should_create_payment_as_pending() -> None:
    payment = make_payment()

    assert payment.status == PaymentStatus.PENDING
    assert payment.is_pending is True
    assert payment.is_approved is False
    assert payment.approved_at is None
    assert payment.provider == "mercadopago"


def test_should_approve_payment() -> None:
    payment = make_payment()

    payment.approve(provider_payment_id="123456")

    assert payment.status == PaymentStatus.APPROVED
    assert payment.is_approved is True
    assert payment.approved_at is not None
    assert payment.provider_payment_id == "123456"


def test_should_keep_first_approval() -> None:
    payment = make_payment()

    payment.approve(provider_payment_id="1")
    first = payment.approved_at

    payment.approve(provider_payment_id="2")

    assert payment.approved_at == first
    assert payment.provider_payment_id == "1"


def test_should_reject_payment() -> None:
    payment = make_payment()

    payment.reject()

    assert payment.status == PaymentStatus.REJECTED


def test_should_cancel_payment() -> None:
    payment = make_payment()

    payment.cancel()

    assert payment.status == PaymentStatus.CANCELLED


def test_should_map_products_to_license_types() -> None:
    assert (
        get_plan(LicenseProduct.ANNUAL).license_type
        == LicenseType.ANNUAL
    )
    assert (
        get_plan(LicenseProduct.LIFETIME).license_type
        == LicenseType.LIFETIME
    )


def test_should_list_plans_with_prices() -> None:
    plans = list_plans()

    assert len(plans) == 2

    for plan in plans:
        assert plan.price_cents > 0
        assert plan.title
        assert plan.price_label.startswith("R$")


def test_should_only_sell_annual_and_lifetime() -> None:
    assert set(PLANS.keys()) == {
        LicenseProduct.ANNUAL,
        LicenseProduct.LIFETIME,
    }
