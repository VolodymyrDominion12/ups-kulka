from dataclasses import dataclass

from ups_kulka.shared.domain.errors import ValidationError


class InvalidMoney(ValidationError):
    code = "invalid_money"


@dataclass(frozen=True, slots=True)
class Money:
    """Amount in UAH kopecks. Never use float for money."""

    kopecks: int

    def __post_init__(self) -> None:
        if isinstance(self.kopecks, bool) or not isinstance(self.kopecks, int):
            raise InvalidMoney("Money must be an integer number of kopecks")
        if self.kopecks < 0:
            raise InvalidMoney("Money cannot be negative")

    @classmethod
    def uah(cls, hryvnias: int) -> "Money":
        return cls(hryvnias * 100)

    def __add__(self, other: "Money") -> "Money":
        return Money(self.kopecks + other.kopecks)

    def __mul__(self, quantity: int) -> "Money":
        return Money(self.kopecks * quantity)

    @property
    def is_zero(self) -> bool:
        return self.kopecks == 0
