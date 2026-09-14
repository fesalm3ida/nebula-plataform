from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.license_product import LicenseProduct


class LicensePlanResponse(BaseModel):
    product: LicenseProduct
    title: str
    description: str
    price_cents: int
    price_label: str


class PlansResponse(BaseModel):
    plans: list[LicensePlanResponse]


class PurchaseRequest(BaseModel):
    product: LicenseProduct


class PurchaseResponse(BaseModel):
    payment_id: UUID
    checkout_url: str


class WebhookPayload(BaseModel):
    id: str | None = None
    type: str | None = None
    data: dict | None = None
