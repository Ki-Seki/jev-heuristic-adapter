"""Exercise the real SDK through an in-memory HTTP transport, never the API."""

import json

import httpx2
import pytest

openai = pytest.importorskip("openai")
OpenAIProvider = pytest.importorskip(
    "jev_heuristic_adapter.providers.openai", exc_type=ModuleNotFoundError
).OpenAIProvider


@pytest.fixture
def sdk_factory():
    clients = []

    def create(handler=None, **overrides):
        def unexpected_request(request):
            # Identity-only tests must never reach the transport.
            raise AssertionError("Unexpected HTTP request")  # pragma: no cover

        options = {
            "api_key": "unit-test-key",
            "base_url": "https://api.example.invalid/v1",
            "max_retries": 0,
            "http_client": httpx2.Client(
                transport=httpx2.MockTransport(handler or unexpected_request),
                trust_env=False,
            ),
        }
        options.update(overrides)
        sdk = openai.OpenAI(**options)
        clients.append(sdk)
        return sdk

    yield create
    for sdk in clients:
        sdk.close()


def response_body(status="completed", usage=True):
    body = {
        "id": "resp_fixture",
        "object": "response",
        "created_at": 0,
        "model": "test-model",
        "status": status,
        "output": [
            {
                "id": "msg_fixture",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": 'def predict(state): return {"answer": True}',
                        "annotations": [],
                    }
                ],
            }
        ],
    }
    if usage:
        body["usage"] = {
            "input_tokens": 0,
            "output_tokens": 7,
            "total_tokens": 7,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 2},
        }
    return body


@pytest.mark.parametrize("status", ["completed", "incomplete", "failed"])
@pytest.mark.parametrize(
    "usage", [True, False], ids=["reported-usage", "missing-usage"]
)
def test_request_uses_plain_text_generation_and_preserves_status_usage_and_raw_data(
    sdk_factory, status, usage
):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx2.Response(200, json=response_body(status, usage))

    sdk = sdk_factory(respond)
    provider = OpenAIProvider(
        sdk, "test-model", reasoning_effort="high", max_output_tokens=321
    )
    messages = [
        {"role": "system", "content": "Write Python."},
        {"role": "user", "content": "判断"},
    ]
    result = provider.request(messages)
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/v1/responses"
    request = json.loads(requests[0].content)
    assert request["input"] == messages
    assert request["model"] == "test-model"
    assert request["reasoning"] == {"effort": "high"}
    assert request["max_output_tokens"] == 321
    assert request["text"] == {"format": {"type": "text"}}
    assert request["store"] is False
    assert result.text == 'def predict(state): return {"answer": True}'
    assert result.complete is (status == "completed")
    assert result.input_tokens == (0 if usage else None)
    assert result.output_tokens == (7 if usage else None)
    assert result.raw["id"] == "resp_fixture"
    assert result.raw["status"] == status
    assert not sdk.is_closed()


def test_identity_uses_generation_settings_and_excludes_credentials_and_retries(
    sdk_factory,
):
    first = OpenAIProvider(
        sdk_factory(api_key="secret-a", timeout=1.0, max_retries=0), "test-model"
    )
    second = OpenAIProvider(
        sdk_factory(api_key="secret-b", timeout=30.0, max_retries=5), "test-model"
    )
    identity = first.cache_identity()
    assert identity == second.cache_identity()
    assert identity == {
        "provider": "openai",
        "api": "responses",
        "base_url": "https://api.example.invalid/v1/",
        "model": "test-model",
        "reasoning_effort": "high",
        "max_output_tokens": 24_000,
    }
    assert "secret" not in json.dumps(identity)


@pytest.mark.parametrize(
    "overrides",
    [
        {"model": "another-model"},
        {"reasoning_effort": "low"},
        {"max_output_tokens": 100},
    ],
)
def test_generation_settings_change_identity(sdk_factory, overrides):
    sdk = sdk_factory()
    baseline = OpenAIProvider(sdk, "test-model").cache_identity()
    options = {"model": "test-model", **overrides}
    assert OpenAIProvider(sdk, **options).cache_identity() != baseline


def test_endpoint_participates_in_identity_but_fragment_does_not(sdk_factory):
    def identity(url):
        return OpenAIProvider(sdk_factory(base_url=url), "test-model").cache_identity()

    baseline = identity("https://api.example.invalid/v1")
    assert identity("https://api.example.invalid/v1#first") == baseline
    assert identity("https://api.example.invalid/v1#second") == baseline
    assert identity("https://other.example.invalid/v1") != baseline


@pytest.mark.parametrize(
    "url",
    [
        "https://user@api.example.invalid/v1",
        "https://user:password@api.example.invalid/v1",
        "https://:password@api.example.invalid/v1",
        "https://api.example.invalid/v1?api_key=secret",
    ],
)
def test_credentials_and_queries_in_base_urls_are_rejected(sdk_factory, url):
    provider = OpenAIProvider(sdk_factory(base_url=url), "test-model")
    with pytest.raises(ValueError, match="without credentials or query"):
        provider.cache_identity()


def test_sdk_errors_propagate_and_retry_policy_remains_caller_owned(sdk_factory):
    requests = []

    def rate_limited(request):
        requests.append(request)
        return httpx2.Response(
            429, json={"error": {"message": "limited", "type": "rate_limit_error"}}
        )

    sdk = sdk_factory(rate_limited, max_retries=0)
    with pytest.raises(openai.RateLimitError):
        OpenAIProvider(sdk, "test-model").request([])
    assert len(requests) == 1
    assert not sdk.is_closed()
