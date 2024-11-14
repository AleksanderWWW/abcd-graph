__all__ = ["Edge"]

from dataclasses import dataclass
from typing import Any


@dataclass
class Edge:
    __slots__ = ["v1", "v2"]

    v1: int
    v2: int

    def __post_init__(self) -> None:
        self.to_ordered()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return self.v1 == other.v1 and self.v2 == other.v2

    def __hash__(self) -> int:
        return hash((self.v1, self.v2))

    def to_ordered(self) -> None:
        if self.v1 < self.v2:
            self.v1, self.v2 = self.v2, self.v1

    @property
    def is_loop(self) -> bool:
        return self.v1 == self.v2
