"""AgentLink resource — AWSYS AgentLinks feature."""

from __future__ import annotations

from .._http import HttpClient


class AgentlinkResource:
    """Interact with /api/agentlink endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def subscribe(self, email: str) -> dict:
        """Subscribe an email address to AgentLink updates.

        This is a public endpoint — no authentication required, though the
        SDK will attach the Authorization header if an API key is configured.

        Args:
            email: The email address to subscribe.

        Returns:
            API response dict.
        """
        return self._http.post("/api/agentlink/subscribe", json={"email": email}) or {}

    def get_link_stats(self, short_path: str, *, period_days: int = 7) -> dict:
        """Get AgentLink click statistics for a specific link.

        Args:
            short_path: The short code or slug identifying the link.
            period_days: Number of days to include in the stats window (default 7).

        Returns:
            API response dict with click statistics.
        """
        return (
            self._http.get(
                f"/api/agentlink/links/{short_path}/stats",
                params={"period": period_days},
            )
            or {}
        )

    def get_account_stats(self, *, period_days: int = 7) -> dict:
        """Get aggregated AgentLink statistics for the authenticated account.

        Args:
            period_days: Number of days to include in the stats window (default 7).

        Returns:
            API response dict with account-level statistics.
        """
        return (
            self._http.get(
                "/api/agentlink/account/stats",
                params={"period": period_days},
            )
            or {}
        )
