"""Azure OpenAI lease extractor — stub."""

from typing import Any

from app.domain.interfaces.extraction_service import IExtractionService


class AzureOpenAIExtractor(IExtractionService):
    async def classify(self, file_key: str) -> str:
        raise NotImplementedError

    async def extract(self, file_key: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
