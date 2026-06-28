from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from scrapers.adapters import http_client
from scrapers.adapters.http_policy import DEFAULT_HEADERS, get_with_retry


def _response(
    request: httpx.Request,
    status_code: int = 200,
    text: str = "ok",
    content_type: str = "text/plain",
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    response_headers = {"content-type": content_type, **(headers or {})}
    return httpx.Response(
        status_code=status_code,
        text=text,
        headers=response_headers,
        request=request,
    )


def _client_with_transport(transport: httpx.BaseTransport) -> httpx.Client:
    return httpx.Client(
        transport=transport,
        headers=DEFAULT_HEADERS,
        follow_redirects=True,
    )


def test_fetch_url_returns_text_and_content_type(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _response(request, text="contenido demo", content_type="text/html")

    client = _client_with_transport(httpx.MockTransport(handler))
    monkeypatch.setattr(http_client, "_CLIENT", client)

    text, content_type = http_client.fetch_url("https://example.test/page")

    assert text == "contenido demo"
    assert content_type == "text/html"
    client.close()


def test_fetch_url_retries_retryable_status(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return _response(request, status_code=503, text="temporal")
        return _response(request, status_code=200, text="recuperado")

    client = _client_with_transport(httpx.MockTransport(handler))
    monkeypatch.setattr(http_client, "_CLIENT", client)

    with patch("scrapers.adapters.http_policy.time.sleep"):
        text, _ = http_client.fetch_url("https://example.test/page")

    assert text == "recuperado"
    assert calls == 2
    client.close()


def test_get_with_retry_respects_retry_after_header() -> None:
    calls = 0
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return _response(
                request,
                status_code=429,
                text="rate limited",
                headers={"retry-after": "2"},
            )
        return _response(request, status_code=200)

    client = _client_with_transport(httpx.MockTransport(handler))

    with patch("scrapers.adapters.http_policy.time.sleep", side_effect=sleeps.append):
        response = get_with_retry(
            client,
            "https://example.test/page",
            max_retries=2,
        )

    assert response.status_code == 200
    assert sleeps == [2.0]
    client.close()


def test_fetch_url_raises_after_retry_exhaustion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _response(request, status_code=500, text="error")

    client = _client_with_transport(httpx.MockTransport(handler))
    monkeypatch.setattr(http_client, "_CLIENT", client)

    with patch("scrapers.adapters.http_policy.time.sleep"):
        with pytest.raises(RuntimeError, match="Máximo de reintentos"):
            http_client.fetch_url("https://example.test/page")

    client.close()
