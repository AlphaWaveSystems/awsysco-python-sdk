"""Usage resource — live account consumption and tier limits."""

from __future__ import annotations

from .._http import HttpClient
from ..models import UsageStats


class UsageResource:
    """Interact with /api/user/stats."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self) -> UsageStats:
        """Get live consumption stats for the authenticated account.

        Unlike :meth:`MeResource.get`, which returns the user's static
        profile, this returns live usage counters (links, clicks, QR codes,
        API calls, tracked clicks) alongside the current tier limits and any
        active overage state.

        Returns:
            A UsageStats with current consumption, limits, and overage state.
        """
        data = self._http.get("/api/user/stats")
        return UsageStats.model_validate(data)
