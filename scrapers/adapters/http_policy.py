from __future__ import annotations

import email.utils
import logging
import random
import time
from datetime import datetime, timezone
from typing import Any

import httpx

USER_AGENT = "VZLA_DEDUP_Scraper/0.3 (+public-interest emergency-data-cleanup)"
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
}

DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_BASE = 1.0
DEFAULT_BACKOFF_MAX = 60.0
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

log = logging.getLogger(__name__)


def backoff_delay(attempt: int) -> float:
    """Exponential backoff con jitter para reintentos HTTP."""
    exp = DEFAULT_BACKOFF_BASE * (2 ** (attempt - 1))
    capped = min(exp, DEFAULT_BACKOFF_MAX)
    return float(capped + random.random())


def retry_after_delay(response: httpx.Response) -> float | None:
    """Devuelve el delay de Retry-After si viene en segundos o HTTP-date."""
    value = response.headers.get("retry-after")
    if not value:
        return None

    try:
        return max(0.0, float(value))
    except ValueError:
        pass

    try:
        retry_at = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None

    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())


def get_with_retry(
    client: httpx.Client,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout: float | None = None,
) -> httpx.Response:
    """Ejecuta GET con política común de retry/backoff para adapters."""
    last_exc: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            request_kwargs: dict[str, Any] = {"params": params or {}}
            if timeout is not None:
                request_kwargs["timeout"] = timeout

            response = client.get(url, **request_kwargs)

            if response.status_code in RETRYABLE_STATUS:
                last_exc = httpx.HTTPStatusError(
                    f"HTTP {response.status_code}",
                    request=response.request,
                    response=response,
                )
                if attempt < max_retries:
                    delay = retry_after_delay(response) or backoff_delay(attempt)
                    log.warning(
                        "HTTP %s en intento %d/%d — reintento en %.1fs",
                        response.status_code,
                        attempt,
                        max_retries,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    log.warning(
                        "HTTP %s en intento %d/%d — sin más reintentos",
                        response.status_code,
                        attempt,
                        max_retries,
                    )
                continue

            response.raise_for_status()
            return response

        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_exc = exc
            if attempt < max_retries:
                delay = backoff_delay(attempt)
                log.warning(
                    "%s en intento %d/%d — reintento en %.1fs",
                    type(exc).__name__,
                    attempt,
                    max_retries,
                    delay,
                )
                time.sleep(delay)
            else:
                log.warning(
                    "%s en intento %d/%d — sin más reintentos",
                    type(exc).__name__,
                    attempt,
                    max_retries,
                )

    raise RuntimeError(
        f"Máximo de reintentos ({max_retries}) alcanzado para {url}"
    ) from last_exc
