"""Namespace resource — branded namespace management."""

from __future__ import annotations

from .._http import HttpClient
from ..models import NamespaceCheckResult, NamespaceInfo


class NamespaceResource:
    """Interact with /api/user/namespace and /api/namespace/check endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self) -> NamespaceInfo:
        """Get the authenticated user's namespace info.

        Returns:
            A NamespaceInfo object.
        """
        data = self._http.get("/api/user/namespace")
        return NamespaceInfo.model_validate(data)

    def check(self, namespace: str) -> NamespaceCheckResult:
        """Check whether a namespace is available.

        Args:
            namespace: The namespace string to check.

        Returns:
            A NamespaceCheckResult indicating availability.
        """
        data = self._http.get(f"/api/namespace/check/{namespace}")
        return NamespaceCheckResult.model_validate(data)

    def claim(self, namespace: str) -> NamespaceInfo:
        """Claim a namespace for the authenticated user.

        Args:
            namespace: The namespace string to claim.

        Returns:
            Updated NamespaceInfo after claiming.
        """
        data = self._http.post("/api/user/namespace", json={"namespace": namespace})
        return NamespaceInfo.model_validate(data)

    def release(self) -> dict:
        """Release the authenticated user's current namespace.

        Returns:
            The API response dict.
        """
        return self._http.delete("/api/user/namespace") or {}
