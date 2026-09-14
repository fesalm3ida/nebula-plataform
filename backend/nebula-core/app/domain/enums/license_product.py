from enum import Enum


class LicenseProduct(str, Enum):
    """Produtos de licença vendidos no portal."""

    ANNUAL = "annual"
    LIFETIME = "lifetime"
