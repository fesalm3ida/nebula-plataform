import re
from dataclasses import dataclass


_MAC_ADDRESS_PATTERN = re.compile(
    r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
)


@dataclass(frozen=True)
class MacAddress:
    value: str

    def __post_init__(self) -> None:
        normalized_value = self.value.upper()

        if not _MAC_ADDRESS_PATTERN.fullmatch(normalized_value):
            raise ValueError("Invalid MAC address format.")

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
