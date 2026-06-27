"""Async Imports resource."""

from __future__ import annotations

import asyncio
import time
from typing import List, Optional
from urllib.parse import quote

from .._async_http import AsyncHttpClient
from ..models import ImportJob

# Statuses that indicate the import job has stopped progressing.
_TERMINAL_STATES = {"completed", "partial", "failed", "cancelled"}


class AsyncImportsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def start(
        self,
        *,
        provider: str,
        access_token: str,
        target_namespace: Optional[str] = None,
        scan_only: Optional[bool] = None,
    ) -> ImportJob:
        """Start a new provider link-import job.

        The request body uses snake_case keys (``provider``, ``access_token``,
        optional ``target_namespace`` / ``scan_only``).
        """
        body = {"provider": provider, "access_token": access_token}
        if target_namespace is not None:
            body["target_namespace"] = target_namespace
        if scan_only is not None:
            body["scan_only"] = scan_only
        data = await self._http.post("/api/v1/imports", json=body)
        return ImportJob.model_validate(data)

    async def get_status(self, job_id: str) -> ImportJob:
        """Get the current state of an import job."""
        encoded = quote(job_id, safe="")
        data = await self._http.get(f"/api/v1/imports/{encoded}")
        return ImportJob.model_validate(data)

    async def cancel(self, job_id: str) -> ImportJob:
        """Cancel an in-progress import job."""
        encoded = quote(job_id, safe="")
        data = await self._http.delete(f"/api/v1/imports/{encoded}")
        return ImportJob.model_validate(data)

    async def list(self, *, limit: Optional[int] = None) -> List[ImportJob]:
        """List import jobs for the authenticated user."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        data = await self._http.get(
            "/api/v1/imports",
            params=params if params else None,
        )
        items = data.get("jobs", []) if isinstance(data, dict) else (data or [])
        return [ImportJob.model_validate(item) for item in items]

    async def wait_for_completion(
        self,
        job_id: str,
        *,
        poll_interval: float = 2.0,
        timeout: float = 120.0,
    ) -> ImportJob:
        """Poll an import job until it reaches a terminal state.

        Polls ``get_status`` every ``poll_interval`` seconds until the job
        status is one of ``completed``, ``partial``, ``failed``, or
        ``cancelled``.

        Raises:
            TimeoutError: If the job does not finish within ``timeout``.
        """
        deadline = time.monotonic() + timeout
        while True:
            job = await self.get_status(job_id)
            if job.status in _TERMINAL_STATES:
                return job
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Import job {job_id} did not complete within {timeout}s "
                    f"(last status: {job.status})"
                )
            await asyncio.sleep(poll_interval)
