from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CashFlowLine:
    id: str
    run_id: str
    period: int
    amount: Decimal
    category: str
