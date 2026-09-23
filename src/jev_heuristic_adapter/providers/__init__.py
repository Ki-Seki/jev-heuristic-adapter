"""Provider-neutral contracts; importing these requires no provider SDK."""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ProviderResult:
    text: str
    complete: bool
    input_tokens: int | None
    output_tokens: int | None
    raw: dict[str, Any]


class Provider(Protocol):
    def request(self, messages: list[dict[str, str]]) -> ProviderResult: ...
