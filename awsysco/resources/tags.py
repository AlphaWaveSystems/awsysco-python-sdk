"""Tags resource — add and remove tags on links."""

from __future__ import annotations

from urllib.parse import quote

from .._http import HttpClient


class TagsResource:
    """Interact with /api/link/:short/tags."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def add(self, short_path: str, tag: str) -> dict:
        """Add a tag to a link.

        Args:
            short_path: The short code or slug identifying the link.
            tag: The tag string to add.

        Returns:
            The API response dict.
        """
        encoded = quote(short_path, safe="")
        return self._http.post(f"/api/link/{encoded}/tags", json={"tag": tag}) or {}

    def remove(self, short_path: str, tag: str) -> dict:
        """Remove a tag from a link.

        Args:
            short_path: The short code or slug identifying the link.
            tag: The tag string to remove.

        Returns:
            The API response dict.
        """
        encoded = quote(short_path, safe="")
        encoded_tag = quote(tag, safe="")
        return self._http.delete(f"/api/link/{encoded}/tags/{encoded_tag}") or {}
