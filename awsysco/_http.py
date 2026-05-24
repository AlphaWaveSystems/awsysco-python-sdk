"""Internal HTTP client wrapper with retry logic and error mapping."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    AwsysAuthError,
    AwsysConflictError,
    AwsysError,
    AwsysForbiddenError,
    AwsysNotFoundError,
    AwsysRateLimitError,
    AwsysValidationError,
)

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds


def _parse_error(response: httpx.Response) -> AwsysError:
    """Parse an HTTP error response and return the appropriate exception."""
    status = response.status_code
    raw: Any = None
    message: str = f"HTTP {status}"
    code: Optional[str] = None

    try:
        data = response.json()
        raw = data
        # API returns { error: true, message: "...", code: "..." }
        # The "error" field is a boolean, the human-readable text is in "message"
        msg_field = data.get("message")
        if msg_field and isinstance(msg_field, str):
            message = msg_field
        elif isinstance(data.get("error"), str):
            message = data["error"]
        code = data.get("code")
    except Exception:
        raw = response.text
        if raw:
            message = raw

    kwargs: Dict[str, Any] = {"code": code, "status": status, "raw": raw}

    if status == 400:
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
        retry_after: Optional[float] = None
        ra_header = response.headers.get("Retry-After")
        if ra_header:
            try:
                retry_after = float(ra_header)
            except ValueError:
                pass
        return AwsysRateLimitError(message, retry_after=retry_after, **kwargs)

    return AwsysError(message, **kwargs)


class HttpClient:
    """Thin wrapper around httpx.Client with auth, retries, and error mapping."""

    def __init__(self, api_key: str, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "awsysco-python-sdk/0.1.0",
            },
            timeout=timeout,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
    ) -> Any:
        """Execute an HTTP request with 429-retry logic."""
        attempt = 0
        while True:
            response = self._client.request(method, path, params=params, json=json)

            if response.status_code == 429 and attempt < _MAX_RETRIES:
                exc = _parse_error(response)
                assert isinstance(exc, AwsysRateLimitError)
                delay = exc.retry_after or (_RETRY_BASE_DELAY * (2 ** attempt))
                time.sleep(delay)
                attempt += 1
                continue

            if response.is_error:
                raise _parse_error(response)

            # 204 No Content
            if response.status_code == 204 or not response.content:
                return None

            return response.json()

    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, *, json: Optional[Any] = None) -> Any:
        return self._request("POST", path, json=json)

    def patch(self, path: str, *, json: Optional[Any] = None) -> Any:
        return self._request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
