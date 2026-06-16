from abc import ABC, abstractmethod
from typing import Any


class IExtractionService(ABC):
    @abstractmethod
    async def classify(self, file_key: str) -> str: ...

    @abstractmethod
    async def extract(self, file_key: str, schema: dict[str, Any]) -> dict[str, Any]: ...
