import re
from dataclasses import dataclass


_APP_VERSION_PATTERN = re.compile(
    r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$"
)


@dataclass(frozen=True)
class AppVersion:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("App version must be a string.")

        normalized_value = self.value.strip()

        if not _APP_VERSION_PATTERN.fullmatch(normalized_value):
            raise ValueError(
                "App version must follow semantic versioning, such as 1.0.0."
            )

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
