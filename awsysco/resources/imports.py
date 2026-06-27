"""Imports resource — provider link-import jobs."""

from __future__ import annotations

import time
from typing import List, Optional
from urllib.parse import quote

from .._http import HttpClient
from ..models import ImportJob

# Statuses that indicate the import job has stopped progressing.
_TERMINAL_STATES = {"completed", "partial", "failed", "cancelled"}


class ImportsResource:
    """Interact with /api/v1/imports."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def start(
        self,
        *,
        provider: str,
        access_token: str,
        target_namespace: Optional[str] = None,
        scan_only: Optional[bool] = None,
    ) -> ImportJob:
        """Start a new provider link-import job.

        Args:
            provider: The source provider (e.g. ``'bitly'``, ``'rebrandly'``).
            access_token: An OAuth/API token for the source provider account.
            target_namespace: Optional namespace to import links into.
            scan_only: If ``True``, fetch and report without writing links.

        Returns:
            The created ImportJob (initially in a ``pending`` state).
        """
        body = {"provider": provider, "access_token": access_token}
        if target_namespace is not None:
            body["target_namespace"] = target_namespace
        if scan_only is not None:
            body["scan_only"] = scan_only
        data = self._http.post("/api/v1/imports", json=body)
        return ImportJob.model_validate(data)

    def get_status(self, job_id: str) -> ImportJob:
        """Get the current state of an import job.

        Args:
            job_id: The import job id.

        Returns:
            The ImportJob with up-to-date status and counts.
        """
        encoded = quote(job_id, safe="")
        data = self._http.get(f"/api/v1/imports/{encoded}")
        return ImportJob.model_validate(data)

    def cancel(self, job_id: str) -> ImportJob:
        """Cancel an in-progress import job.

        Args:
            job_id: The import job id.

        Returns:
            The ImportJob reflecting the cancelled state.
        """
        encoded = quote(job_id, safe="")
        data = self._http.delete(f"/api/v1/imports/{encoded}")
        return ImportJob.model_validate(data)

    def list(self, *, limit: Optional[int] = None) -> List[ImportJob]:
        """List import jobs for the authenticated user.

        Args:
            limit: Maximum number of jobs to return.

        Returns:
            A list of ImportJob objects.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        data = self._http.get(
            "/api/v1/imports",
            params=params if params else None,
        )
        items = data.get("jobs", []) if isinstance(data, dict) else (data or [])
        return [ImportJob.model_validate(item) for item in items]

    def wait_for_completion(
        self,
        job_id: str,
        *,
        poll_interval: float = 2.0,
        timeout: float = 120.0,
    ) -> ImportJob:
        """Poll an import job until it reaches a terminal state.

        Polls :meth:`get_status` every ``poll_interval`` seconds until the
        job status is one of ``completed``, ``partial``, ``failed``, or
        ``cancelled``.

        Args:
            job_id: The import job id.
            poll_interval: Seconds to wait between status checks.
            timeout: Maximum seconds to wait before giving up.

        Returns:
            The terminal-state ImportJob.

        Raises:
            TimeoutError: If the job does not finish within ``timeout``.
        """
        deadline = time.monotonic() + timeout
        while True:
            job = self.get_status(job_id)
            if job.status in _TERMINAL_STATES:
                return job
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Import job {job_id} did not complete within {timeout}s "
                    f"(last status: {job.status})"
                )
            time.sleep(poll_interval)
