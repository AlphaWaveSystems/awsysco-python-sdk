"""Trust Score resource — URL safety scan."""

from __future__ import annotations

from urllib.parse import quote

from .._http import HttpClient
from ..models import TrustScoreResult


class TrustScoreResource:
    """Interact with /api/link-scan/:short."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def scan(self, short_path: str) -> TrustScoreResult:
        """Run a trust/safety scan on a shortened link.

        Args:
            short_path: The short code or slug identifying the link.

        Returns:
            A TrustScoreResult with score, status, and any detected threats.
        """
        encoded = quote(short_path, safe="")
        data = self._http.get(f"/api/link-scan/{encoded}")
        return TrustScoreResult.model_validate(data)
