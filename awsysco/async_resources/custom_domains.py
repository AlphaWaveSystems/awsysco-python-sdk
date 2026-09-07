"""Async Custom Domains resource."""

from __future__ import annotations

import warnings
from typing import Any, Dict, Optional

from .._async_http import AsyncHttpClient
from ..exceptions import AwsysForbiddenError
from ..models import CustomDomain


class AsyncCustomDomainsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self) -> dict:
        return await self._http.get("/api/user/domains") or {}

    async def add(self, domain: str) -> dict:
        return await self._http.post("/api/user/domains", json={"domain": domain}) or {}

    async def verify(self, domain: str) -> dict:
        return await self._http.get(f"/api/user/domains/{domain}/verify") or {}

    async def activate(self, domain: str) -> CustomDomain:
        """Deprecated: Firebase-only route, unreachable with an API key. See the sync
        ``CustomDomainsResource.activate`` docstring; removed in the next major version."""
        warnings.warn(
            "custom_domains.activate() is deprecated: this route is Firebase-only and "
            "cannot be called with an API key. Activate the domain from the AWSYS "
            "dashboard instead. This method will be removed in the next major version.",
            DeprecationWarning,
            stacklevel=2,
        )
        raise AwsysForbiddenError(
            f"Cannot activate domain {domain!r} with an API key — "
            "POST /api/user/domains/:domain/activate requires Firebase auth. "
            "Activate the domain from the AWSYS dashboard instead."
        )

    async def update(
        self,
        domain: str,
        *,
        is_default: Optional[bool] = None,
        not_found_html: Optional[str] = None,
        default_redirect: Optional[str] = None,
    ) -> CustomDomain:
        body: Dict[str, Any] = {}
        if is_default is not None:
            body["isDefault"] = is_default
        if not_found_html is not None:
            body["notFoundHtml"] = not_found_html
        if default_redirect is not None:
            body["defaultRedirect"] = default_redirect
        data = await self._http.patch(f"/api/user/domains/{domain}", json=body)
        return CustomDomain.model_validate(data)

    async def remove(self, domain: str) -> dict:
        return await self._http.delete(f"/api/user/domains/{domain}") or {}

    async def check(self, hostname: str) -> dict:
        return await self._http.get(f"/api/domains/check/{hostname}") or {}
