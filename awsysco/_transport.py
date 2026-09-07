"""Shared error parsing and retry/backoff logic used by both the sync and async transports.

Kept in one module so the two transports (``_http.py`` / ``_async_http.py``) cannot drift —
previously each had its own byte-for-byte copy of this logic.
"""

from __future__ import annotations

import math
import random
from email.utils import parsedate_to_datetime
from time import time as _now
from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    AwsysAuthError,
    AwsysConflictError,
    AwsysError,
    AwsysForbiddenError,
    AwsysNotFoundError,
    AwsysRateLimitError,
    AwsysServerError,
    AwsysValidationError,
)

DEFAULT_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds
_RETRY_MAX_DELAY = 30.0  # seconds

# Quota-class 429s cannot be helped by waiting a few seconds — never retry these.
QUOTA_ERROR_CODES = {"HOURLY_LIMIT_EXCEEDED", "MONTHLY_LIMIT_EXCEEDED", "DAILY_LIMIT_EXCEEDED"}

RETRYABLE_SERVER_STATUSES = {502, 503, 504}
IDEMPOTENT_METHODS = {"GET", "PUT", "DELETE"}


def is_idempotent(method: str) -> bool:
    """Whether ``method`` is safe to retry without an idempotency key."""
    return method.upper() in IDEMPOTENT_METHODS


def _parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Parse a ``Retry-After`` header value — either delta-seconds or an HTTP-date."""
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(value)
        return max(0.0, dt.timestamp() - _now())
    except (TypeError, ValueError):
        return None


def parse_error(response: "httpx.Response") -> AwsysError:
    """Parse an HTTP error response into the matching :class:`AwsysError` subclass.

    Tolerates every error-body shape observed on the platform:
    ``{error: true, code, message}``, ``{error: "<string>", code}`` (the string is the
    message), ``{error: true, code}`` with no message (synthesized from ``code``),
    ``{success: false, message, code}``, and non-JSON bodies (falls back to the response
    text, then to the HTTP status line).
    """
    status = response.status_code
    raw: Any = None
    message: Optional[str] = None
    code: Optional[str] = None

    try:
        data = response.json()
    except Exception:
        data = None

    if isinstance(data, dict):
        raw = data
        code = data.get("code") if isinstance(data.get("code"), str) else None
        error_field = data.get("error")
        msg_field = data.get("message")
        if isinstance(msg_field, str) and msg_field:
            message = msg_field
        elif isinstance(error_field, str) and error_field:
            # e.g. agentlink.js: {error: "<string>", code}
            message = error_field
        elif code:
            # {error: true, code} with no message — synthesize a readable message
            message = code.replace("_", " ").capitalize()
    else:
        text = response.text
        raw = text or None
        if text:
            message = text

    if not message:
        message = f"HTTP {status} {response.reason_phrase}".strip()

    kwargs: Dict[str, Any] = {"code": code, "status": status, "raw": raw}

    if status in (400, 422):
        return AwsysValidationError(message, **kwargs)
    if status == 401:
        return AwsysAuthError(message, **kwargs)
    if status == 403:
        return AwsysForbiddenError(message, **kwargs)
    if status == 404:
        return AwsysNotFoundError(message, **kwargs)
    if status == 409:
        return AwsysConflictError(message, **kwargs)
    if status == 429:
        resets_at = data.get("resetsAt") if isinstance(data, dict) else None
        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
        return AwsysRateLimitError(
            message, retry_after=retry_after, resets_at=resets_at, **kwargs
        )
    if 500 <= status < 600:
        return AwsysServerError(message, **kwargs)

    return AwsysError(message, **kwargs)


def is_quota_rate_limit(exc: AwsysRateLimitError) -> bool:
    """Whether a 429 is a quota exhaustion (never worth retrying) vs. a transient IP limit."""
    return (exc.code in QUOTA_ERROR_CODES) or exc.resets_at is not None


def is_retry_after_excessive(retry_after: Optional[float]) -> bool:
    """Whether a parsed ``Retry-After`` value is too large (or non-finite) to wait out.

    A `Retry-After` beyond the retry cap (or ``inf``/``nan``) means retrying can't
    plausibly help within this call — raise immediately instead of sleeping.
    """
    if retry_after is None:
        return False
    return (not math.isfinite(retry_after)) or retry_after > _RETRY_MAX_DELAY


def compute_delay(response: Optional["httpx.Response"], attempt: int) -> float:
    """Backoff delay for retry ``attempt`` (0-indexed), with full jitter.

    Uses the ``Retry-After`` header when present, otherwise ``1s * 2^attempt`` capped at
    30s. Full jitter: the actual sleep is a random value in ``[0, computed_delay]``.
    """
    retry_after = _parse_retry_after(response.headers.get("Retry-After")) if response is not None else None
    if retry_after is not None:
        base = retry_after
    else:
        base = min(_RETRY_BASE_DELAY * (2**attempt), _RETRY_MAX_DELAY)
    return random.uniform(0, base)
