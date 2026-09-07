"""Custom Domains resource — manage custom short link domains."""

from __future__ import annotations

import warnings
from typing import Any, Dict, Optional

from .._http import HttpClient
from ..exceptions import AwsysForbiddenError
from ..models import CustomDomain


class CustomDomainsResource:
    """Interact with /api/user/domains and /api/domains/check endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self) -> dict:
        """List all custom domains for the authenticated user.

        Returns:
            API response dict containing domains.
        """
        return self._http.get("/api/user/domains") or {}

    def add(self, domain: str) -> dict:
        """Add a new custom domain.

        Args:
            domain: The domain hostname to register (e.g. ``'links.example.com'``).

        Returns:
            API response dict with verification token.
        """
        return self._http.post("/api/user/domains", json={"domain": domain}) or {}

    def verify(self, domain: str) -> dict:
        """Check DNS verification status for a domain.

        Args:
            domain: The domain hostname to verify.

        Returns:
            API response dict with verification status.
        """
        return self._http.get(f"/api/user/domains/{domain}/verify") or {}

    def activate(self, domain: str) -> CustomDomain:
        """Activate a verified domain.

        .. deprecated::
            This route (``POST /api/user/domains/:domain/activate``) is Firebase-only
            (``requireAuthStrict``) and cannot be called with an API key — it always
            401s. Deprecated in 1.4.0, will be removed in the next major version. Use
            the AWSYS dashboard to activate a domain instead.

        Args:
            domain: The domain hostname to activate.

        Raises:
            AwsysForbiddenError: Always — this route is not reachable with an API key.
        """
        warnings.warn(
            "custom_domains.activate() is deprecated: this route is Firebase-only and "
            "cannot be called with an API key. Activate the domain from the AWSYS "
            "dashboard instead. This method will be removed in the next major version.",
            DeprecationWarning,
            stacklevel=2,
        )
        raise AwsysForbiddenError(
            f"Cannot activate domain {domain!r} with an API key — "
            "POST /api/user/domains/:domain/activate requires Firebase auth. "
            "Activate the domain from the AWSYS dashboard instead."
        )

    def update(
        self,
        domain: str,
        *,
        is_default: Optional[bool] = None,
        not_found_html: Optional[str] = None,
        default_redirect: Optional[str] = None,
    ) -> CustomDomain:
        """Update custom domain settings.

        Args:
            domain: The domain hostname to update.
            is_default: Whether this domain should be the default.
            not_found_html: Custom HTML for 404 pages on this domain.
            default_redirect: URL to redirect to when a short path on this domain
                isn't found.

        Returns:
            The updated CustomDomain object.
        """
        body: Dict[str, Any] = {}
        if is_default is not None:
            body["isDefault"] = is_default
        if not_found_html is not None:
            body["notFoundHtml"] = not_found_html
        if default_redirect is not None:
            body["defaultRedirect"] = default_redirect
        data = self._http.patch(f"/api/user/domains/{domain}", json=body)
        return CustomDomain.model_validate(data)

    def remove(self, domain: str) -> dict:
        """Remove a custom domain.

        Args:
            domain: The domain hostname to remove.

        Returns:
            API response dict.
        """
        return self._http.delete(f"/api/user/domains/{domain}") or {}

    def check(self, hostname: str) -> dict:
        """Check if a hostname is available for use as a custom domain.

        Args:
            hostname: The hostname to check.

        Returns:
            API response dict indicating availability.
        """
        return self._http.get(f"/api/domains/check/{hostname}") or {}
