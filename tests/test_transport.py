"""Unit tests for the shared error-parsing and retry/backoff logic in _transport.py,
and the retry loop wiring in the sync/async HTTP clients (mocked clock, no real sleeps).
"""

from __future__ import annotations

import asyncio
import http.client
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from awsysco._async_http import AsyncHttpClient
from awsysco._http import HttpClient
from awsysco._transport import (
    compute_delay,
    is_idempotent,
    is_quota_rate_limit,
    is_retry_after_excessive,
    parse_error,
)
from awsysco.exceptions import (
    AwsysAuthError,
    AwsysConflictError,
    AwsysForbiddenError,
    AwsysNetworkError,
    AwsysNotFoundError,
    AwsysRateLimitError,
    AwsysServerError,
    AwsysTimeoutError,
    AwsysValidationError,
)


class _FakeResponse:
    def __init__(self, status_code, *, json_body=None, text_body=None, headers=None):
        self.status_code = status_code
        self._json_body = json_body
        self._text_body = text_body if text_body is not None else ""
        self.headers = headers or {}
        self.is_error = status_code >= 400
        self.reason_phrase = http.client.responses.get(status_code, "")

    def json(self):
        if self._json_body is None:
            raise ValueError("no JSON body")
        return self._json_body

    @property
    def text(self):
        return self._text_body

    @property
    def content(self):
        if self._json_body is not None:
            return b"{}"  # non-empty stand-in; parse_error/success paths use .json()/.text, not this
        return self._text_body.encode() if self._text_body else b""


# ---------------------------------------------------------------------------
# parse_error — the four documented body shapes + non-JSON + status mapping
# ---------------------------------------------------------------------------


class TestParseErrorBodyShapes:
    def test_shape_error_true_code_message(self):
        resp = _FakeResponse(401, json_body={"error": True, "code": "UNAUTHORIZED", "message": "Invalid key."})
        exc = parse_error(resp)
        assert isinstance(exc, AwsysAuthError)
        assert exc.message == "Invalid key."
        assert exc.code == "UNAUTHORIZED"

    def test_shape_error_string_no_message(self):
        resp = _FakeResponse(
            403, json_body={"error": "AgentLink analytics require Pro or higher", "code": "TIER_INSUFFICIENT"}
        )
        exc = parse_error(resp)
        assert isinstance(exc, AwsysForbiddenError)
        assert exc.message == "AgentLink analytics require Pro or higher"
        assert exc.code == "TIER_INSUFFICIENT"

    def test_shape_error_true_code_no_message_synthesizes(self):
        resp = _FakeResponse(404, json_body={"error": True, "code": "IMPORT_JOB_NOT_FOUND"})
        exc = parse_error(resp)
        assert isinstance(exc, AwsysNotFoundError)
        assert exc.message == "Import job not found"
        assert exc.code == "IMPORT_JOB_NOT_FOUND"

    def test_shape_success_false(self):
        resp = _FakeResponse(400, json_body={"success": False, "message": "Bad password", "code": "BAD_PASSWORD"})
        exc = parse_error(resp)
        assert isinstance(exc, AwsysValidationError)
        assert exc.message == "Bad password"

    def test_non_json_body_falls_back_to_text(self):
        resp = _FakeResponse(404, text_body="Cannot PATCH /api/v1/folders/x")
        exc = parse_error(resp)
        assert isinstance(exc, AwsysNotFoundError)
        assert exc.message == "Cannot PATCH /api/v1/folders/x"

    def test_no_body_falls_back_to_status_line(self):
        resp = _FakeResponse(409)
        exc = parse_error(resp)
        assert isinstance(exc, AwsysConflictError)
        assert "409" in exc.message

    def test_5xx_maps_to_server_error(self):
        resp = _FakeResponse(502, json_body={"error": True, "message": "Bad gateway"})
        exc = parse_error(resp)
        assert isinstance(exc, AwsysServerError)
        assert exc.status == 502

    def test_raw_never_includes_request_headers(self):
        resp = _FakeResponse(400, json_body={"error": True, "message": "x"})
        exc = parse_error(resp)
        assert "Authorization" not in str(exc.raw)


class TestRateLimitParsing:
    def test_quota_error_carries_code_and_resets_at(self):
        resp = _FakeResponse(
            429,
            json_body={
                "error": True,
                "code": "HOURLY_LIMIT_EXCEEDED",
                "message": "Hourly limit exceeded",
                "resetsAt": "2026-09-06T23:00:00Z",
            },
        )
        exc = parse_error(resp)
        assert isinstance(exc, AwsysRateLimitError)
        assert exc.code == "HOURLY_LIMIT_EXCEEDED"
        assert exc.resets_at == "2026-09-06T23:00:00Z"
        assert is_quota_rate_limit(exc) is True

    def test_ip_rate_limit_is_not_quota(self):
        resp = _FakeResponse(
            429,
            json_body={"error": True, "message": "Too many requests"},
            headers={"Retry-After": "2"},
        )
        exc = parse_error(resp)
        assert is_quota_rate_limit(exc) is False
        assert exc.retry_after == 2.0

    def test_retry_after_http_date(self):
        from datetime import datetime, timedelta, timezone
        from email.utils import format_datetime

        future = datetime.now(timezone.utc) + timedelta(seconds=10)
        resp = _FakeResponse(
            429, json_body={"error": True, "message": "x"}, headers={"Retry-After": format_datetime(future)}
        )
        exc = parse_error(resp)
        assert exc.retry_after is not None
        assert 0 <= exc.retry_after <= 15


# ---------------------------------------------------------------------------
# Retry/backoff primitives
# ---------------------------------------------------------------------------


class TestIsIdempotent:
    @pytest.mark.parametrize("method", ["GET", "get", "PUT", "DELETE"])
    def test_idempotent_methods(self, method):
        assert is_idempotent(method) is True

    @pytest.mark.parametrize("method", ["POST", "PATCH"])
    def test_non_idempotent_methods(self, method):
        assert is_idempotent(method) is False


class TestComputeDelay:
    def test_full_jitter_bounds(self):
        for attempt in range(4):
            delay = compute_delay(None, attempt)
            assert 0 <= delay <= min(1.0 * (2**attempt), 30.0)

    def test_capped_at_30s(self):
        delay = compute_delay(None, attempt=10)
        assert delay <= 30.0

    def test_uses_retry_after_header(self):
        resp = _FakeResponse(429, headers={"Retry-After": "5"})
        delay = compute_delay(resp, attempt=0)
        assert 0 <= delay <= 5.0


# ---------------------------------------------------------------------------
# Retry-loop wiring (mocked httpx.Client/AsyncClient, mocked sleep — no real waits)
# ---------------------------------------------------------------------------


class TestSyncRetryLoop:
    def _client_with_responses(self, responses, monkeypatch):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=3)
        mock_request = MagicMock(side_effect=responses)
        monkeypatch.setattr(client._client, "request", mock_request)
        monkeypatch.setattr("awsysco._http.time.sleep", lambda _: None)
        return client, mock_request

    def test_quota_429_is_never_retried(self, monkeypatch):
        resp = _FakeResponse(429, json_body={"error": True, "code": "HOURLY_LIMIT_EXCEEDED", "message": "x"})
        client, mock_request = self._client_with_responses([resp], monkeypatch)
        with pytest.raises(AwsysRateLimitError):
            client.get("/api/v1/links")
        assert mock_request.call_count == 1

    def test_ip_429_is_retried_then_succeeds(self, monkeypatch):
        rate_limited = _FakeResponse(429, json_body={"error": True, "message": "slow down"})
        ok = _FakeResponse(200, json_body={"ok": True})
        client, mock_request = self._client_with_responses([rate_limited, ok], monkeypatch)
        result = client.get("/api/v1/links")
        assert result == {"ok": True}
        assert mock_request.call_count == 2

    def test_502_retried_for_get(self, monkeypatch):
        bad_gateway = _FakeResponse(502, json_body={"error": True, "message": "bad gateway"})
        ok = _FakeResponse(200, json_body={"ok": True})
        client, mock_request = self._client_with_responses([bad_gateway, ok], monkeypatch)
        result = client.get("/api/v1/links")
        assert result == {"ok": True}
        assert mock_request.call_count == 2

    def test_502_not_retried_for_post(self, monkeypatch):
        bad_gateway = _FakeResponse(502, json_body={"error": True, "message": "bad gateway"})
        client, mock_request = self._client_with_responses([bad_gateway], monkeypatch)
        with pytest.raises(AwsysServerError):
            client.post("/api/v1/links", json={"url": "https://example.com"})
        assert mock_request.call_count == 1

    def test_timeout_wrapped_and_retried_for_get(self, monkeypatch):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=1)
        ok = _FakeResponse(200, json_body={"ok": True})
        mock_request = MagicMock(side_effect=[httpx.ConnectTimeout("timed out"), ok])
        monkeypatch.setattr(client._client, "request", mock_request)
        monkeypatch.setattr("awsysco._http.time.sleep", lambda _: None)
        result = client.get("/api/v1/links")
        assert result == {"ok": True}

    def test_timeout_raises_after_retries_exhausted(self, monkeypatch):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=0)
        mock_request = MagicMock(side_effect=httpx.ConnectTimeout("timed out"))
        monkeypatch.setattr(client._client, "request", mock_request)
        with pytest.raises(AwsysTimeoutError):
            client.get("/api/v1/links")

    def test_transport_error_on_post_not_retried(self, monkeypatch):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=3)
        mock_request = MagicMock(side_effect=httpx.ConnectError("refused"))
        monkeypatch.setattr(client._client, "request", mock_request)
        with pytest.raises(AwsysNetworkError):
            client.post("/api/v1/links", json={"url": "https://example.com"})
        assert mock_request.call_count == 1


class TestAsyncRetryLoop:
    def test_quota_429_is_never_retried(self, monkeypatch):
        async def _run():
            client = AsyncHttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=3)
            resp = _FakeResponse(429, json_body={"error": True, "code": "MONTHLY_LIMIT_EXCEEDED", "message": "x"})

            async def fake_request(*args, **kwargs):
                return resp

            monkeypatch.setattr(client._client, "request", fake_request)
            monkeypatch.setattr("awsysco._async_http.asyncio.sleep", AsyncNoop())
            with pytest.raises(AwsysRateLimitError):
                await client.get("/api/v1/links")

        asyncio.run(_run())

    def test_502_retried_then_succeeds(self, monkeypatch):
        async def _run():
            client = AsyncHttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=3)
            responses = iter(
                [
                    _FakeResponse(502, json_body={"error": True, "message": "bad gateway"}),
                    _FakeResponse(200, json_body={"ok": True}),
                ]
            )

            async def fake_request(*args, **kwargs):
                return next(responses)

            monkeypatch.setattr(client._client, "request", fake_request)
            monkeypatch.setattr("awsysco._async_http.asyncio.sleep", AsyncNoop())
            result = await client.get("/api/v1/links")
            assert result == {"ok": True}

        asyncio.run(_run())


class AsyncNoop:
    """A callable that returns a completed coroutine — stands in for asyncio.sleep."""

    async def __call__(self, *args, **kwargs):
        return None


# ---------------------------------------------------------------------------
# Retry-After capping — a value beyond the retry cap (or non-finite) must raise
# immediately rather than sleep.
# ---------------------------------------------------------------------------


class TestRetryAfterCapping:
    def test_excessive_retry_after_detected(self):
        assert is_retry_after_excessive(31.0) is True
        assert is_retry_after_excessive(30.0) is False
        assert is_retry_after_excessive(29.9) is False
        assert is_retry_after_excessive(None) is False

    def test_non_finite_retry_after_detected(self):
        assert is_retry_after_excessive(float("inf")) is True
        assert is_retry_after_excessive(float("nan")) is True

    def test_sync_client_raises_immediately_on_excessive_retry_after(self, monkeypatch):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=3)
        resp = _FakeResponse(
            429, json_body={"error": True, "message": "slow down"}, headers={"Retry-After": "999"}
        )
        mock_request = MagicMock(return_value=resp)
        monkeypatch.setattr(client._client, "request", mock_request)
        slept = []
        monkeypatch.setattr("awsysco._http.time.sleep", lambda d: slept.append(d))
        with pytest.raises(AwsysRateLimitError) as exc_info:
            client.get("/api/v1/links")
        assert mock_request.call_count == 1  # no retry attempted
        assert slept == []  # never slept
        assert exc_info.value.retry_after == 999.0  # still reported to the caller

    def test_sync_client_raises_immediately_on_excessive_retry_after_503(self, monkeypatch):
        """err_503_retry_after_oversized: a retryable 5xx with an oversized
        Retry-After must raise immediately too, not just 429 — this path had no
        excessiveness check at all before an independent review caught it."""
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=3)
        resp = _FakeResponse(
            503, json_body={"error": True, "message": "unavailable"}, headers={"Retry-After": "3600"}
        )
        mock_request = MagicMock(return_value=resp)
        monkeypatch.setattr(client._client, "request", mock_request)
        slept = []
        monkeypatch.setattr("awsysco._http.time.sleep", lambda d: slept.append(d))
        with pytest.raises(AwsysServerError):
            client.get("/api/v1/links")
        assert mock_request.call_count == 1
        assert slept == []

    def test_async_client_raises_immediately_on_excessive_retry_after_503(self, monkeypatch):
        async def _run():
            client = AsyncHttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=3)
            resp = _FakeResponse(
                503, json_body={"error": True, "message": "unavailable"}, headers={"Retry-After": "3600"}
            )

            async def fake_request(*args, **kwargs):
                return resp

            monkeypatch.setattr(client._client, "request", fake_request)
            sleep_mock = AsyncMock()
            monkeypatch.setattr("awsysco._async_http.asyncio.sleep", sleep_mock)
            with pytest.raises(AwsysServerError):
                await client.get("/api/v1/links")
            sleep_mock.assert_not_awaited()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# 422 → AwsysValidationError; non-JSON 2xx body → typed SDK error, not a raw
# JSONDecodeError; asyncio.CancelledError passes through unmodified.
# ---------------------------------------------------------------------------


class TestAdditionalContractRequirements:
    def test_422_maps_to_validation_error(self):
        resp = _FakeResponse(422, json_body={"error": True, "code": "VALIDATION_FAILED", "message": "bad"})
        exc = parse_error(resp)
        from awsysco.exceptions import AwsysValidationError

        assert isinstance(exc, AwsysValidationError)
        assert exc.status == 422

    def test_non_json_2xx_body_raises_typed_error_not_raw_decode_error(self, monkeypatch):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co")
        resp = _FakeResponse(200, text_body="<html>interstitial</html>")
        monkeypatch.setattr(client._client, "request", MagicMock(return_value=resp))
        with pytest.raises(AwsysServerError):
            client.get("/api/v1/links")

    def test_non_json_2xx_body_raises_typed_error_async(self, monkeypatch):
        async def _run():
            client = AsyncHttpClient(api_key="awsys_x", base_url="https://awsys.co")
            resp = _FakeResponse(200, text_body="<html>interstitial</html>")

            async def fake_request(*args, **kwargs):
                return resp

            monkeypatch.setattr(client._client, "request", fake_request)
            with pytest.raises(AwsysServerError):
                await client.get("/api/v1/links")

        asyncio.run(_run())

    def test_cancelled_error_passes_through_unmodified(self, monkeypatch):
        async def _run():
            client = AsyncHttpClient(api_key="awsys_x", base_url="https://awsys.co")

            async def fake_request(*args, **kwargs):
                raise asyncio.CancelledError()

            monkeypatch.setattr(client._client, "request", fake_request)
            with pytest.raises(asyncio.CancelledError):
                await client.get("/api/v1/links")

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Timeout covers header AND body read — a single float timeout applies to all
# of httpx's connect/read/write/pool phases.
# ---------------------------------------------------------------------------


class TestTimeoutCoversBodyRead:
    def test_sync_client_timeout_covers_read_phase(self):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", timeout=12.5)
        assert client._client.timeout == httpx.Timeout(12.5)
        assert client._client.timeout.read == 12.5

    def test_async_client_timeout_covers_read_phase(self):
        client = AsyncHttpClient(api_key="awsys_x", base_url="https://awsys.co", timeout=12.5)
        assert client._client.timeout == httpx.Timeout(12.5)
        assert client._client.timeout.read == 12.5

    def test_a_stalled_body_read_raises_awsys_timeout_error(self, monkeypatch):
        client = HttpClient(api_key="awsys_x", base_url="https://awsys.co", max_retries=0)
        monkeypatch.setattr(
            client._client, "request", MagicMock(side_effect=httpx.ReadTimeout("body stalled"))
        )
        with pytest.raises(AwsysTimeoutError):
            client.get("/api/v1/links")
