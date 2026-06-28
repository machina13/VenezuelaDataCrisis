from __future__ import annotations

import httpx

from scrapers.adapters.http_policy import DEFAULT_HEADERS, USER_AGENT, get_with_retry


_CLIENT = httpx.Client(headers=DEFAULT_HEADERS, follow_redirects=True)


def fetch_url(url: str, timeout: int = 25) -> tuple[str, str]:
    response = get_with_retry(_CLIENT, url, timeout=float(timeout))
    content_type = response.headers.get("content-type", "")
    return response.text, content_type
