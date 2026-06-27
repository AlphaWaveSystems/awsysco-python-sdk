"""Web2App resource — single-use deep-link session consumption."""

from __future__ import annotations

from urllib.parse import quote

from .._http import HttpClient
from ..models import Web2AppSession


class Web2AppResource:
    """Interact with /api/v1/web2app/:token."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def consume_session(self, token: str) -> Web2AppSession:
        """Consume a Web2App deep-link session by its token.

        Sessions are single-use — consuming one deletes it server-side — and
        expire 24 hours after creation. Consuming an unknown, expired, or
        already-consumed token raises ``AwsysNotFoundError`` (404); a
        malformed token raises ``AwsysValidationError`` (400). These are
        mapped by the underlying transport.

        Args:
            token: The 32-character hex session token.

        Returns:
            A Web2AppSession with the resolved link id, UTM params, routing
            rule, country, and click timestamp.
        """
        encoded = quote(token, safe="")
        data = self._http.get(f"/api/v1/web2app/{encoded}")
        return Web2AppSession.model_validate(data)
