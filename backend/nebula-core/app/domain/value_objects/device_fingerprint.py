import re
from dataclasses import dataclass


_FINGERPRINT_PATTERN = re.compile(r"^[a-f0-9]{64}$")


@dataclass(frozen=True)
class DeviceFingerprint:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Device fingerprint must be a string.")

        normalized_value = self.value.strip().lower()

        if not _FINGERPRINT_PATTERN.fullmatch(normalized_value):
            raise ValueError(
                "Device fingerprint must be a 64-character hexadecimal string."
            )

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
