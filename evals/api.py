"""Recorded API calls, explicit high effort, and a shared spend ceiling."""

import json
import math
import time
from threading import Lock

from .data import read, write

# Standard USD / 1M tokens: input, cached input, 30-minute cache write, output.
# https://developers.openai.com/api/docs/pricing (2026-11-25)
# Jev input-only fallback: https://openrouter.ai/provider/typesafe (2026-11-25).
PRICES = {
    "gpt-6-astra": (10, 1, 12.5, 50),
    "gpt-6-sol": (2, 0.2, 2.5, 10),
    "gpt-6-luna": (0.1, 0.01, 0.125, 0.5),
    "gpt-6.1-sol": (2, 0.1, 2.5, 10),
    "gpt-6.1-terra": (1, 0.05, 1.25, 5),
    "gpt-6.2-astra": (8, 0.4, 10, 40),
    "gpt-6.2-sol": (2, 0.1, 2.5, 10),
    "typesafe/jev-1.13": (0.042, 0.042, 0.042, 0),
    "typesafe/jev-1.14": (0.042, 0.042, 0.042, 0),
}


class BudgetExceeded(RuntimeError):
    pass


class CallError(RuntimeError):
    def __init__(self, receipt):
        self.receipt = receipt
        super().__init__(receipt["error"])

    @property
    def retryable(self):
        status = self.receipt.get("http_status")
        return status is None or status in (408, 409, 429) or status >= 500


def cost(raw, model, method, reserve):
    """Missing usage stays unknown; absent cache-write detail gets a range."""
    usage = raw.get("usage") if raw else None
    if method == "jev" and usage and usage.get("cost") is not None:
        billed = usage["cost"]
        if isinstance(billed, (int, float)) and math.isfinite(billed) and billed >= 0:
            return billed, billed
        return None, reserve
    if not usage or usage.get("input_tokens") is None:
        return None, reserve
    if method == "compile" and usage.get("output_tokens") is None:
        return None, reserve
    pi, pc, pw, po = PRICES[model]
    details = usage.get("input_tokens_details") or {}
    cached, written = (
        details.get("cached_tokens", 0) or 0,
        details.get("cache_write_tokens", 0) or 0,
    )
    ordinary = usage["input_tokens"] - cached - written
    if ordinary < 0:
        return None, reserve
    output = usage.get("output_tokens", 0) or 0
    billed = (
        ordinary * pi
        + cached * pc
        + written * pw
        + (output * po if method == "compile" else 0)
    ) / 1e6
    upper = billed + (
        ordinary * (pw - pi) / 1e6 if details.get("cache_write_tokens") is None else 0
    )
    return billed, upper


class API:
    def __init__(self, client, output, budget, openrouter=None):
        self.client, self.output, self.budget = client, output, budget
        self.openrouter = openrouter
        self.lock = Lock()
        self.used = 0.0
        for path in output.glob("calls/**/request.json"):
            receipt = path.with_name("receipt.json")
            self.used += (
                read(receipt)["cost_upper_usd"]
                if receipt.exists()
                else read(path)["reserve_usd"]
            )

    def call(self, method, model, payload, folder):
        if method == "jev" and self.openrouter is None:
            raise ValueError("An OpenRouter client is required for Jev")
        request = {"method": method, "model": model, "payload": payload}
        input_bound = len(json.dumps(payload, ensure_ascii=False).encode()) + 4096
        reserve = (
            input_bound * PRICES[model][2]
            + payload.get("max_output_tokens", 0) * PRICES[model][3]
        ) / 1e6
        path = folder / "request.json"
        if path.exists():
            previous = read(path)
            if {k: previous[k] for k in request} != request:
                raise ValueError(f"Refusing to reuse a different API request: {folder}")
            if (folder / "receipt.json").exists():
                receipt = read(folder / "receipt.json")
                if receipt["error"]:
                    raise CallError(receipt)
                return read(folder / "response.json"), receipt
            # A process interruption consumes an attempt; never send it again.
            raw = (
                read(folder / "response.json")
                if (folder / "response.json").exists()
                else None
            )
            return self.finish(
                folder,
                method,
                model,
                raw,
                previous["reserve_usd"],
                None,
                None if raw else "InterruptedCall",
            )
        with self.lock:
            if self.used + reserve > self.budget:
                raise BudgetExceeded(
                    f"Spend ceiling ${self.budget:.2f}; accounted/reserved ${self.used:.2f}"
                )
            write(path, {**request, "reserve_usd": reserve, "started_at": time.time()})
            self.used += reserve
        started = time.perf_counter()
        try:
            if method == "compile":
                raw = self.generate(payload, folder)
            elif method == "jev":
                raw = self.openrouter.post(
                    "/alpha/decisions", cast_to=dict, body=payload
                )
            else:
                # Public low-level SDK method also works before a typed Decisions client ships.
                raw = self.client.post("/decisions", cast_to=dict, body=payload)
            write(folder / "response.json", raw)
        except Exception as exc:
            return self.finish(
                folder,
                method,
                model,
                None,
                reserve,
                time.perf_counter() - started,
                type(exc).__name__,
                getattr(exc, "status_code", None),
            )
        return self.finish(
            folder, method, model, raw, reserve, time.perf_counter() - started, None
        )

    def generate(self, payload, folder):
        partial, last_save = "", 0.0
        try:
            with self.client.responses.create(**payload, stream=True) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        partial += event.delta
                        if time.monotonic() - last_save >= 10:
                            (folder / "partial.py").write_text(
                                partial, encoding="utf-8"
                            )
                            last_save = time.monotonic()
                    if event.type in (
                        "response.completed",
                        "response.incomplete",
                        "response.failed",
                    ):
                        return event.response.model_dump(mode="json")
            raise RuntimeError("Stream ended without a terminal response")
        finally:
            (folder / "partial.py").write_text(partial, encoding="utf-8")

    def finish(self, folder, method, model, raw, reserve, seconds, error, status=None):
        billed, upper = cost(raw, model, method, reserve)
        receipt = {
            "seconds": seconds,
            "cost_usd": billed,
            "cost_upper_usd": upper,
            "error": error,
            "http_status": status,
        }
        write(folder / "receipt.json", receipt)
        with self.lock:
            self.used += upper - reserve
        if error:
            raise CallError(receipt)
        return raw, receipt


def generation_payload(model, messages, cap):
    return {
        "model": model,
        "input": messages,
        "reasoning": {"effort": "high"},
        "max_output_tokens": cap,
        "service_tier": "default",
        "store": False,
        "text": {"format": {"type": "text"}},
    }


def output_text(raw):
    return "".join(
        part["text"]
        for item in raw.get("output", [])
        for part in item.get("content", [])
        if part.get("type") == "output_text"
    )


def decision_payload(question, examples, state):
    context = (
        [
            {
                "role": "developer",
                "content": "Classify the final input. Labeled examples:\n"
                + json.dumps(examples, ensure_ascii=False),
            }
        ]
        if examples
        else []
    )
    return {
        "model": "gpt-6-luna",
        "input": context + [{"role": "user", "content": state}],
        "questions": [
            {
                "type": "choice",
                "name": "label",
                "instructions": question["instructions"],
                "choices": [
                    {"value": k, "description": v}
                    for k, v in question["criteria"].items()
                ],
            }
        ],
    }


def jev_payload(model, question, examples, state):
    instructions = question["instructions"]
    if examples:
        instructions += (
            "\nUse the labeled examples as guidance for classifying only the current input. Examples:\n"
            + json.dumps(examples, ensure_ascii=False)
        )
    return {
        "model": model,
        "state": state,
        "questions": {"label": {**question, "instructions": instructions}},
    }


def decision_answer(raw, method):
    answers = raw.get("answers")
    if method == "jev":
        answer = answers.get("label") if isinstance(answers, dict) else None
        if isinstance(answer, dict) and answer.get("type") == "choice":
            return answer.get("choice")
    elif isinstance(answers, list):
        matches = [
            a for a in answers if isinstance(a, dict) and a.get("name") == "label"
        ]
        if len(matches) == 1:
            return matches[0].get("choice")
    return None
