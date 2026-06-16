from dataclasses import dataclass


@dataclass(frozen=True)
class RunID:
    value: str
