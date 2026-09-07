"""Internal HTTP client wrapper with config validation, retries, and error mapping."""

from __future__ import annotations

import platform as _platform
import time
import warnings
from typing import Any, Dict, Optional

import httpx

from ._transport import (
    DEFAULT_MAX_RETRIES,
    RETRYABLE_SERVER_STATUSES,
    compute_delay,
    get_retry_after,
    is_idempotent,
    is_quota_rate_limit,
    is_retry_after_excessive,
    parse_error,
)
from ._version import __version__
from .exceptions import (
    AwsysConfigurationError,
    AwsysNetworkError,
    AwsysRateLimitError,
    AwsysServerError,
    AwsysTimeoutError,
)


_warned_http_base_url = False


def resolve_base_url(base_url: str) -> str:
    """Validate and normalize a base URL, per the cross-SDK behavior contract.

    Raises :class:`AwsysConfigurationError` for a missing scheme; warns once per
    process (not once per call) on a non-``https`` scheme.
    """
    global _warned_http_base_url
    normalized = base_url.rstrip("/")
    if not normalized.startswith(("http://", "https://")):
        raise AwsysConfigurationError(
            f"base_url must start with 'http://' or 'https://', got {base_url!r}."
        )
    if normalized.startswith("http://") and not _warned_http_base_url:
        _warned_http_base_url = True
        warnings.warn(
            "AWSYS base_url is using plain HTTP — API keys will be sent unencrypted.",
            stacklevel=3,
        )
    return normalized


def build_user_agent() -> str:
    return f"awsysco-python-sdk/{__version__} (python/{_platform.python_version()})"


def redact_key(api_key: Optional[str]) -> str:
    """A safe-to-print form of an API key: ``awsys_...<last4>`` (or a placeholder if absent)."""
    if not api_key:
        return "<unset>"
    if len(api_key) <= 4:
        return "awsys_****"
    return f"awsys_...{api_key[-4:]}"


class HttpClient:
    """Thin wrapper around httpx.Client with auth, retries, and error mapping."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._api_key = api_key
        self._base_url = resolve_base_url(base_url)
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": build_user_agent(),
            },
            timeout=timeout,
        )

    @property
    def base_url(self) -> str:
        """The (validated, trailing-slash-stripped) base URL this client talks to."""
        return self._base_url

    @property
    def redacted_key(self) -> str:
        """A safe-to-print form of the configured API key (``awsys_...last4``)."""
        return redact_key(self._api_key)

    def __repr__(self) -> str:
        return f"HttpClient(base_url={self._base_url!r}, api_key={self.redacted_key!r})"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Execute an HTTP request, retrying per the cross-SDK retry policy."""
        attempt = 0
        while True:
            try:
                response = self._client.request(
                    method, path, params=params, json=json, timeout=timeout
                )
            except httpx.TimeoutException as exc:
                if is_idempotent(method) and attempt < self._max_retries:
                    time.sleep(compute_delay(None, attempt))
                    attempt += 1
                    continue
                raise AwsysTimeoutError(str(exc) or "Request timed out.") from exc
            except httpx.TransportError as exc:
                if is_idempotent(method) and attempt < self._max_retries:
                    time.sleep(compute_delay(None, attempt))
                    attempt += 1
                    continue
                raise AwsysNetworkError(str(exc) or "Network error.") from exc

            if response.status_code == 429:
                rate_limit_exc = parse_error(response)
                assert isinstance(rate_limit_exc, AwsysRateLimitError)
                if (
                    is_quota_rate_limit(rate_limit_exc)
                    or is_retry_after_excessive(rate_limit_exc.retry_after)
                    or attempt >= self._max_retries
                ):
                    raise rate_limit_exc
                time.sleep(compute_delay(response, attempt))
                attempt += 1
                continue

            if (
                response.status_code in RETRYABLE_SERVER_STATUSES
                and is_idempotent(method)
                and attempt < self._max_retries
                and not is_retry_after_excessive(get_retry_after(response))
            ):
                time.sleep(compute_delay(response, attempt))
                attempt += 1
                continue

            if response.is_error:
                raise parse_error(response)

            # 204 No Content
            if response.status_code == 204 or not response.content:
                return None

            try:
                return response.json()
            except ValueError as exc:
                # A 2xx with a non-JSON body (e.g. an interstitial HTML page) is a
                # platform-side anomaly — surface it as a typed SDK error, never a
                # raw JSON-decode exception.
                raise AwsysServerError(
                    f"Expected a JSON response but got non-JSON content: {response.text[:200]!r}",
                    status=response.status_code,
                    raw=response.text,
                ) from exc

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        return self._request("GET", path, params=params, timeout=timeout)

    def get_text(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """Like get() but returns response.text instead of response.json()."""
        attempt = 0
        while True:
            try:
                response = self._client.request("GET", path, params=params, timeout=timeout)
            except httpx.TimeoutException as exc:
                if attempt < self._max_retries:
                    time.sleep(compute_delay(None, attempt))
                    attempt += 1
                    continue
                raise AwsysTimeoutError(str(exc) or "Request timed out.") from exc
            except httpx.TransportError as exc:
                if attempt < self._max_retries:
                    time.sleep(compute_delay(None, attempt))
                    attempt += 1
                    continue
                raise AwsysNetworkError(str(exc) or "Network error.") from exc

            if response.status_code == 429:
                rate_limit_exc = parse_error(response)
                assert isinstance(rate_limit_exc, AwsysRateLimitError)
                if (
                    is_quota_rate_limit(rate_limit_exc)
                    or is_retry_after_excessive(rate_limit_exc.retry_after)
                    or attempt >= self._max_retries
                ):
                    raise rate_limit_exc
                time.sleep(compute_delay(response, attempt))
                attempt += 1
                continue

            if (
                response.status_code in RETRYABLE_SERVER_STATUSES
                and attempt < self._max_retries
                and not is_retry_after_excessive(get_retry_after(response))
            ):
                time.sleep(compute_delay(response, attempt))
                attempt += 1
                continue

            if response.is_error:
                raise parse_error(response)

            return response.text

    def post(
        self, path: str, *, json: Optional[Any] = None, timeout: Optional[float] = None
    ) -> Any:
        return self._request("POST", path, json=json, timeout=timeout)

    def patch(
        self, path: str, *, json: Optional[Any] = None, timeout: Optional[float] = None
    ) -> Any:
        return self._request("PATCH", path, json=json, timeout=timeout)

    def put(
        self, path: str, *, json: Optional[Any] = None, timeout: Optional[float] = None
    ) -> Any:
        return self._request("PUT", path, json=json, timeout=timeout)

    def delete(self, path: str, *, timeout: Optional[float] = None) -> Any:
        return self._request("DELETE", path, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
