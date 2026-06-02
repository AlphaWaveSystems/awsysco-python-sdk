"""UTM Templates resource — manage saved UTM parameter templates."""

from __future__ import annotations

from typing import Any, Dict, List

from .._http import HttpClient
from ..models import UtmTemplate


class UtmTemplatesResource:
    """Interact with UTM template endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self) -> List[UtmTemplate]:
        """List all saved UTM templates for the authenticated user.

        Returns:
            A list of UtmTemplate objects.
        """
        resp = self._http.get("/api/v1/me")
        items = resp.get("utmTemplates", []) if isinstance(resp, dict) else []
        return [UtmTemplate.model_validate(item) for item in items]

    def create(
        self,
        name: str,
        source: str,
        medium: str,
        campaign: str,
        *,
        term: str = "",
        content: str = "",
    ) -> dict:
        """Create a new UTM template.

        Args:
            name: Display name for the template.
            source: UTM source value.
            medium: UTM medium value.
            campaign: UTM campaign value.
            term: Optional UTM term value.
            content: Optional UTM content value.

        Returns:
            The API response dict.
        """
        body: Dict[str, Any] = {
            "name": name,
            "source": source,
            "medium": medium,
            "campaign": campaign,
            "term": term,
            "content": content,
        }
        return self._http.post("/api/user/utm-templates", json=body) or {}

    def delete(self, template_id: str) -> dict:
        """Delete a UTM template.

        Args:
            template_id: The ID of the template to delete.

        Returns:
            The API response dict.
        """
        return self._http.delete(f"/api/user/utm-templates/{template_id}") or {}
