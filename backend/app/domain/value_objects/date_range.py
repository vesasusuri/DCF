from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def contains(self, as_of: date) -> bool:
        return self.start <= as_of <= self.end

    def months_until_end(self, as_of: date) -> int:
        if not self.contains(as_of):
            return 0
        return (self.end.year - as_of.year) * 12 + (self.end.month - as_of.month)
