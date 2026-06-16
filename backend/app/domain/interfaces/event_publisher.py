from abc import ABC, abstractmethod
from typing import Any


class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event_type: str, payload: dict[str, Any]) -> None: ...
