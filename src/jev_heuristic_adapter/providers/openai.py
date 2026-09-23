"""OpenAI implementation. Install with `uv sync --extra openai`."""

from dataclasses import dataclass
from typing import cast

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
