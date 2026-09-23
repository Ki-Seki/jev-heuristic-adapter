"""OpenAI implementation. Install with `uv sync --extra openai`."""

from dataclasses import dataclass
from typing import Any, cast

from openai import OpenAI
from openai.types.responses import ResponseInputParam
from openai.types.shared import ReasoningEffort

from . import ProviderResult


@dataclass
class OpenAIProvider:
    """The caller owns the SDK client, including retries and lifetime."""

    client: OpenAI
    model: str
    reasoning_effort: ReasoningEffort = "high"
    max_output_tokens: int = 24_000

    def cache_identity(self) -> dict[str, Any]:
        url = self.client.base_url
        if url.username or url.password or url.query:
            raise ValueError(
                "Cache identity requires a base URL without credentials or query"
            )
        return {
            "provider": "openai",
            "api": "responses",
            "base_url": str(url.copy_with(fragment=None)),
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "max_output_tokens": self.max_output_tokens,
        }

    def request(self, messages: list[dict[str, str]]) -> ProviderResult:
        response = self.client.responses.create(
            model=self.model,
            input=cast(ResponseInputParam, messages),
            reasoning={"effort": self.reasoning_effort},
            max_output_tokens=self.max_output_tokens,
            text={"format": {"type": "text"}},
            store=False,
        )
        usage = response.usage
        return ProviderResult(
            text=response.output_text,
            complete=response.status == "completed",
            input_tokens=usage.input_tokens if usage else None,
            output_tokens=usage.output_tokens if usage else None,
            raw=response.model_dump(mode="json"),
        )
