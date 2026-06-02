"""Saved Views resource — manage dashboard view presets."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import HttpClient
from ..models import SavedView


class SavedViewsResource:
    """Interact with /api/views endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self) -> List[SavedView]:
        """List all saved views for the authenticated user.

        Returns:
            A list of SavedView objects.
        """
        data = self._http.get("/api/views")
        if isinstance(data, list):
            return [SavedView.model_validate(item) for item in data]
        items = data.get("views", []) if isinstance(data, dict) else []
        return [SavedView.model_validate(item) for item in items]

    def create(self, name: str, filters: Dict[str, Any]) -> SavedView:
        """Create a new saved view.

        Args:
            name: Display name for the view.
            filters: Filter criteria dict. Supported keys: ``folderId``,
                ``tag``, ``status``, ``search``, ``dateRange``.

        Returns:
            The created SavedView object.
        """
        data = self._http.post("/api/views", json={"name": name, "filters": filters})
        return SavedView.model_validate(data)

    def update(
        self,
        view_id: str,
        *,
        name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> SavedView:
        """Update a saved view.

        Args:
            view_id: The ID of the view to update.
            name: New display name.
            filters: New filter criteria dict.

        Returns:
            The updated SavedView object.
        """
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if filters is not None:
            body["filters"] = filters
        data = self._http.patch(f"/api/views/{view_id}", json=body)
        return SavedView.model_validate(data)

    def delete(self, view_id: str) -> None:
        """Delete a saved view.

        Args:
            view_id: The ID of the view to delete.
        """
        self._http.delete(f"/api/views/{view_id}")
