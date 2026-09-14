from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.device_status import DeviceStatus
from app.domain.enums.license_type import LicenseType
from app.domain.value_objects.activation_code import ActivationCode
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.device_key import DeviceKey
from app.domain.value_objects.mac_address import MacAddress


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Device:
    """Device registrado no Nebula.

    Licenciamento: a **primeira ativação concede um trial** de
    [TRIAL_DURATION_DAYS] dias. Ao vencer, o Device passa a
    ``DeviceStatus.EXPIRED`` e só volta a operar com uma licença
    ``ANNUAL`` renovável ou ``LIFETIME``.
    """

    TRIAL_DURATION_DAYS = 7
    ANNUAL_DURATION_DAYS = 365

    fingerprint: DeviceFingerprint
    mac_address: MacAddress
    platform: DevicePlatform
    app_version: AppVersion
    device_id: UUID = field(default_factory=uuid4)
    device_key: DeviceKey = field(default_factory=DeviceKey.generate)
    activation_code: ActivationCode = field(
        default_factory=ActivationCode.generate
    )
    status: DeviceStatus = DeviceStatus.PENDING
    created_at: datetime = field(default_factory=_utcnow)
    activated_at: datetime | None = None
    license_type: LicenseType | None = None
    license_expires_at: datetime | None = None

    def activate(self, now: datetime | None = None) -> None:
        """Ativa o Device.

        A **primeira** ativação concede o trial; reativações preservam a
        licença já concedida.
        """
        reference = now or _utcnow()

        self.status = DeviceStatus.ACTIVE

        if self.activated_at is None:
            self.activated_at = reference

        if self.license_type is None:
            self.license_type = LicenseType.TRIAL
            self.license_expires_at = reference + timedelta(
                days=self.TRIAL_DURATION_DAYS
            )

    def grant_license(
        self,
        license_type: LicenseType,
        now: datetime | None = None,
    ) -> None:
        """Concede ou renova uma licença paga (annual/lifetime)."""
        if license_type == LicenseType.TRIAL:
            raise ValueError(
                "Use activate() para conceder o trial."
            )

        reference = now or _utcnow()

        if license_type == LicenseType.LIFETIME:
            self.license_expires_at = None
        else:
            # Renovação: soma a partir do vencimento, se ainda estiver válido.
            base = reference
            if (
                self.license_expires_at is not None
                and self.license_expires_at > reference
            ):
                base = self.license_expires_at

            self.license_expires_at = base + timedelta(
                days=self.ANNUAL_DURATION_DAYS
            )

        self.license_type = license_type
        self.status = DeviceStatus.ACTIVE

    def is_license_expired(self, now: datetime | None = None) -> bool:
        if self.license_type is None:
            return False

        if self.license_type == LicenseType.LIFETIME:
            return False

        if self.license_expires_at is None:
            return False

        return (now or _utcnow()) >= self.license_expires_at

    def license_days_remaining(self, now: datetime | None = None) -> int | None:
        """Dias restantes de licença; ``None`` para vitalícia/sem licença."""
        if self.license_type == LicenseType.LIFETIME:
            return None

        if self.license_expires_at is None:
            return None

        remaining = self.license_expires_at - (now or _utcnow())

        return max(remaining.days, 0)

    def block(self) -> None:
        self.status = DeviceStatus.BLOCKED

    def revoke(self) -> None:
        self.status = DeviceStatus.REVOKED

    def expire(self) -> None:
        self.status = DeviceStatus.EXPIRED
