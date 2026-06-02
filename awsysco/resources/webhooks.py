"""Webhooks resource — manage webhook endpoints and subscriptions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import HttpClient
from ..models import Webhook


class WebhooksResource:
    """Interact with /api/webhooks endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list_event_types(self) -> dict:
        """List all available webhook event types.

        Returns:
            API response dict containing supported event types.
        """
        return self._http.get("/api/webhooks/event-types") or {}

    def list(self) -> dict:
        """List all registered webhooks for the authenticated user.

        Returns:
            API response dict containing webhooks.
        """
        return self._http.get("/api/webhooks") or {}

    def create(
        self,
        url: str,
        events: List[str],
        *,
        name: Optional[str] = None,
        secret: Optional[str] = None,
    ) -> Webhook:
        """Register a new webhook.

        Args:
            url: The HTTPS URL to deliver events to.
            events: List of event type strings to subscribe to (e.g.
                ``['link.created', 'link.click']``).
            name: Optional human-readable name for this webhook.
            secret: Optional signing secret for request verification.

        Returns:
            The created Webhook object.
        """
        body: Dict[str, Any] = {"url": url, "events": events}
        if name is not None:
            body["name"] = name
        if secret is not None:
            body["secret"] = secret
        data = self._http.post("/api/webhooks", json=body)
        return Webhook.model_validate(data)

    def update(self, webhook_id: str, **kwargs: Any) -> Webhook:
        """Update a webhook's configuration.

        Args:
            webhook_id: The ID of the webhook to update.
            **kwargs: Fields to update. Supported keys: ``url``, ``events``,
                ``name``, ``secret``, ``enabled``.

        Returns:
            The updated Webhook object.
        """
        # Map snake_case kwargs to camelCase
        body: Dict[str, Any] = {}
        key_map = {
            "url": "url",
            "events": "events",
            "name": "name",
            "secret": "secret",
            "enabled": "enabled",
        }
        for k, v in kwargs.items():
            mapped = key_map.get(k, k)
            body[mapped] = v
        data = self._http.patch(f"/api/webhooks/{webhook_id}", json=body)
        return Webhook.model_validate(data)

    def delete(self, webhook_id: str) -> dict:
        """Delete a webhook.

        Args:
            webhook_id: The ID of the webhook to delete.

        Returns:
            The API response dict.
        """
        return self._http.delete(f"/api/webhooks/{webhook_id}") or {}

    def test(self, webhook_id: str, event_type: str) -> dict:
        """Send a test event to a webhook.

        Args:
            webhook_id: The ID of the webhook to test.
            event_type: The event type string to simulate.

        Returns:
            The API response dict.
        """
        return (
            self._http.post(
                f"/api/webhooks/{webhook_id}/test",
                json={"eventType": event_type},
            )
            or {}
        )
