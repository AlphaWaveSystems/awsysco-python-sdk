"""Me resource — authenticated user profile."""

from __future__ import annotations

from .._http import HttpClient
from ..models import MeResponse


class MeResource:
    """Interact with /api/v1/me."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self) -> MeResponse:
        """Get the current authenticated user's profile.

        Returns:
            A MeResponse with user info, tier, and feature limits.
        """
        data = self._http.get("/api/v1/me")
        return MeResponse.model_validate(data)
