from dataclasses import dataclass
from secrets import randbelow


@dataclass(frozen=True)
class ActivationCode:
    """Código curto de ativação (6 dígitos) exibido pelo Player.

    É usado pelo **usuário** para entrar no portal web junto com o MAC
    Address. Não substitui a ``DeviceKey`` (segredo longo usado pelo app).
    """

    value: str

    LENGTH = 6

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Activation code must be a string.")

        if len(self.value) != self.LENGTH or not self.value.isdigit():
            raise ValueError(
                "Activation code must contain exactly 6 digits."
            )

    @classmethod
    def generate(cls) -> "ActivationCode":
        return cls(f"{randbelow(10 ** cls.LENGTH):06d}")

    def __str__(self) -> str:
        return self.value
