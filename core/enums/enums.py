from enum import Enum
from functools import cached_property


class DisplayEnum(Enum):
    @cached_property
    def display(self) -> str:
        return " ".join(w.capitalize() for w in self.name.split("_"))
