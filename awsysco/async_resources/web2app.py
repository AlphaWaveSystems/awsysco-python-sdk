"""Async Web2App resource."""

from __future__ import annotations

from urllib.parse import quote

from .._async_http import AsyncHttpClient
from ..models import Web2AppSession


class AsyncWeb2AppResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def consume_session(self, token: str) -> Web2AppSession:
        """Consume a single-use Web2App deep-link session by its token.

        Sessions are single-use (consumed on read) with a 24-hour TTL.
        Unknown/expired/consumed tokens raise ``AwsysNotFoundError`` (404);
        malformed tokens raise ``AwsysValidationError`` (400), mapped by the
        underlying transport.
        """
        encoded = quote(token, safe="")
        data = await self._http.get(f"/api/v1/web2app/{encoded}")
        return Web2AppSession.model_validate(data)
