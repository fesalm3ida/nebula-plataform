from dataclasses import dataclass
from secrets import token_urlsafe


@dataclass(frozen=True)
class DeviceKey:
    value: str

    MIN_LENGTH = 32

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Device key must be a string.")

        if len(self.value) < self.MIN_LENGTH:
            raise ValueError(
                f"Device key must contain at least {self.MIN_LENGTH} characters."
            )

    @classmethod
    def generate(cls) -> "DeviceKey":
        return cls(token_urlsafe(32))

    def __str__(self) -> str:
        return self.value
