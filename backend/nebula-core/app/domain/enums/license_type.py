from enum import Enum


class LicenseType(str, Enum):
    """Tipo de licença concedida a um Device."""

    TRIAL = "trial"
    ANNUAL = "annual"
    LIFETIME = "lifetime"
