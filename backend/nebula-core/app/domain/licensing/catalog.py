from dataclasses import dataclass

from app.domain.enums.license_product import LicenseProduct
from app.domain.enums.license_type import LicenseType


@dataclass(frozen=True)
class LicensePlan:
    """Plano de licença vendido no portal."""

    product: LicenseProduct
    license_type: LicenseType
    title: str
    description: str
    price_cents: int

    @property
    def price_label(self) -> str:
        reais = self.price_cents / 100

        return f"R$ {reais:,.2f}".replace(",", "X").replace(
            ".", ","
        ).replace("X", ".")


PLANS: dict[LicenseProduct, LicensePlan] = {
    LicenseProduct.ANNUAL: LicensePlan(
        product=LicenseProduct.ANNUAL,
        license_type=LicenseType.ANNUAL,
        title="Licença anual",
        description="12 meses de acesso, renovável.",
        price_cents=9900,
    ),
    LicenseProduct.LIFETIME: LicensePlan(
        product=LicenseProduct.LIFETIME,
        license_type=LicenseType.LIFETIME,
        title="Licença vitalícia",
        description="Acesso para sempre, sem renovação.",
        price_cents=29900,
    ),
}


def get_plan(product: LicenseProduct) -> LicensePlan:
    return PLANS[product]


def list_plans() -> list[LicensePlan]:
    return list(PLANS.values())
