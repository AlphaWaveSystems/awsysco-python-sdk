"""Affiliate resource — manage affiliate programs and partnerships."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import HttpClient
from ..models import AffiliateProgram


class AffiliateResource:
    """Interact with /api/affiliate endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create_program(
        self,
        name: str,
        commission_type: str,
        **kwargs: Any,
    ) -> AffiliateProgram:
        """Create a new affiliate program.

        Args:
            name: Display name for the program.
            commission_type: Commission model — ``'cpc'``, ``'cpa_return'``,
                or ``'both'``.
            **kwargs: Optional fields: ``description``, ``cpc_rate`` (0.01–10),
                ``cpa_rate`` (1–100), ``cookie_days``.

        Returns:
            The created AffiliateProgram object.
        """
        body: Dict[str, Any] = {"name": name, "commissionType": commission_type}
        field_map = {
            "description": "description",
            "cpc_rate": "cpcRate",
            "cpa_rate": "cpaRate",
            "cookie_days": "cookieDays",
        }
        for k, v in kwargs.items():
            mapped = field_map.get(k, k)
            body[mapped] = v
        data = self._http.post("/api/affiliate/programs", json=body)
        return AffiliateProgram.model_validate(data)

    def list_programs(self) -> List[AffiliateProgram]:
        """List all affiliate programs owned by the authenticated user.

        Returns:
            A list of AffiliateProgram objects.
        """
        data = self._http.get("/api/affiliate/programs")
        if isinstance(data, list):
            return [AffiliateProgram.model_validate(item) for item in data]
        items = data.get("programs", []) if isinstance(data, dict) else []
        return [AffiliateProgram.model_validate(item) for item in items]

    def get_program(self, program_id: str) -> AffiliateProgram:
        """Get a single affiliate program by ID.

        Args:
            program_id: The ID of the program.

        Returns:
            The AffiliateProgram object.
        """
        data = self._http.get(f"/api/affiliate/programs/{program_id}")
        return AffiliateProgram.model_validate(data)

    def update_program(self, program_id: str, **kwargs: Any) -> AffiliateProgram:
        """Update an affiliate program.

        Args:
            program_id: The ID of the program to update.
            **kwargs: Fields to update. Supported: ``name``, ``description``,
                ``cpc_rate``, ``cpa_rate``, ``cookie_days``, ``status``.

        Returns:
            The updated AffiliateProgram object.
        """
        body: Dict[str, Any] = {}
        field_map = {
            "cpc_rate": "cpcRate",
            "cpa_rate": "cpaRate",
            "cookie_days": "cookieDays",
            "commission_type": "commissionType",
        }
        for k, v in kwargs.items():
            mapped = field_map.get(k, k)
            body[mapped] = v
        data = self._http.patch(f"/api/affiliate/programs/{program_id}", json=body)
        return AffiliateProgram.model_validate(data)

    def get_program_stats(self, program_id: str, *, period: str = "30d") -> dict:
        """Get statistics for an affiliate program.

        Args:
            program_id: The ID of the program.
            period: Time period (default ``'30d'``).

        Returns:
            API response dict with program statistics.
        """
        return (
            self._http.get(
                f"/api/affiliate/programs/{program_id}/stats",
                params={"period": period},
            )
            or {}
        )

    def list_partners(self, program_id: str) -> List[dict]:
        """List all partners for an affiliate program.

        Args:
            program_id: The ID of the program.

        Returns:
            A list of partner dicts.
        """
        data = self._http.get(f"/api/affiliate/programs/{program_id}/partners")
        if isinstance(data, list):
            return data
        return data.get("partners", []) if isinstance(data, dict) else []

    def update_partner_status(
        self,
        program_id: str,
        partner_id: str,
        status: str,
    ) -> dict:
        """Update a partner's status within an affiliate program.

        Args:
            program_id: The ID of the program.
            partner_id: The ID of the partner.
            status: New status string (e.g. ``'approved'``, ``'rejected'``).

        Returns:
            API response dict.
        """
        return (
            self._http.patch(
                f"/api/affiliate/programs/{program_id}/partners/{partner_id}",
                json={"status": status},
            )
            or {}
        )

    def discover(self, *, limit: int = 20) -> List[AffiliateProgram]:
        """Discover public affiliate programs available to join.

        Args:
            limit: Maximum number of programs to return (default 20).

        Returns:
            A list of AffiliateProgram objects.
        """
        data = self._http.get("/api/affiliate/discover", params={"limit": limit})
        if isinstance(data, list):
            return [AffiliateProgram.model_validate(item) for item in data]
        items = data.get("programs", []) if isinstance(data, dict) else []
        return [AffiliateProgram.model_validate(item) for item in items]

    def join(self, program_id: str, *, partner_code: Optional[str] = None) -> dict:
        """Join a public affiliate program.

        Args:
            program_id: The ID of the program to join.
            partner_code: Optional referral/partner code.

        Returns:
            API response dict with partnership details.
        """
        body: Dict[str, Any] = {}
        if partner_code is not None:
            body["partnerCode"] = partner_code
        return self._http.post(f"/api/affiliate/join/{program_id}", json=body) or {}

    def list_partnerships(self) -> List[dict]:
        """List all affiliate partnerships the authenticated user has joined.

        Returns:
            A list of partnership dicts.
        """
        data = self._http.get("/api/affiliate/partnerships")
        if isinstance(data, list):
            return data
        return data.get("partnerships", []) if isinstance(data, dict) else []

    def get_partnership_stats(
        self,
        partnership_id: str,
        *,
        period: str = "30d",
    ) -> dict:
        """Get statistics for a specific partnership.

        Args:
            partnership_id: The ID of the partnership.
            period: Time period (default ``'30d'``).

        Returns:
            API response dict with partnership statistics.
        """
        return (
            self._http.get(
                f"/api/affiliate/partnerships/{partnership_id}/stats",
                params={"period": period},
            )
            or {}
        )

    def leave_program(self, partnership_id: str) -> dict:
        """Leave an affiliate partnership.

        Args:
            partnership_id: The ID of the partnership to leave.

        Returns:
            API response dict.
        """
        return self._http.delete(f"/api/affiliate/partnerships/{partnership_id}") or {}

    def get_limits(self) -> dict:
        """Get the affiliate program limits for the authenticated user's tier.

        Returns:
            API response dict with limit information.
        """
        return self._http.get("/api/affiliate/limits") or {}
