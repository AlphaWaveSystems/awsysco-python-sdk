"""Profile resource (async) — the authenticated user's account profile."""

from __future__ import annotations

from typing import Any, Dict

from pydantic.alias_generators import to_camel

from .._async_http import AsyncHttpClient
from ..models import Profile


class AsyncProfileResource:
    """Interact with /api/user/profile."""

    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get(self) -> Profile:
        """Get the authenticated user's account profile.

        Distinct from :meth:`AsyncMeResource.get` (subscription/feature summary) and
        :meth:`AsyncUsageResource.get` (live consumption counters) — this returns account
        profile fields (display name, email, etc).

        Returns:
            A Profile object.
        """
        data = await self._http.get("/api/user/profile")
        return Profile.model_validate(data)

    async def update(self, **kwargs: Any) -> Profile:
        """Update the authenticated user's account profile.

        Args:
            **kwargs: Profile fields to update (e.g. ``display_name``). snake_case
                keys are converted to camelCase for the wire; already-camelCase keys
                pass through unchanged.

        Returns:
            The updated Profile object.
        """
        body: Dict[str, Any] = {to_camel(k): v for k, v in kwargs.items()}
        data = await self._http.patch("/api/user/profile", json=body)
        return Profile.model_validate(data)
