from uuid import UUID

from pydantic import BaseModel, Field


class PortalLoginRequest(BaseModel):
    mac_address: str = Field(min_length=1)
    activation_code: str = Field(min_length=1)


class PortalLoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str
    device_id: UUID
    device_status: str


class PortalLicenseOut(BaseModel):
    status: str
    license_type: str | None
    activated_at: str | None
    expires_at: str | None
    days_remaining: int | None
    expired: bool


class PortalPlaylistOut(BaseModel):
    playlist_id: UUID
    name: str
    format: str
    source_url: str
    status: str


class PortalPlaylistRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    source_url: str = Field(min_length=1)
    format: str = "m3u"


class PortalDeviceResponse(BaseModel):
    device_id: UUID
    license: PortalLicenseOut
    playlist: PortalPlaylistOut | None = None


class PortalPlanOut(BaseModel):
    product: str
    title: str
    description: str
    price_cents: int
    price_label: str


class PortalPlansResponse(BaseModel):
    plans: list[PortalPlanOut]


class PortalPurchaseRequest(BaseModel):
    product: str = Field(min_length=1)


class PortalPurchaseResponse(BaseModel):
    payment_id: UUID
    checkout_url: str
