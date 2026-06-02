"""Async Affiliate resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._async_http import AsyncHttpClient
from ..models import AffiliateProgram


class AsyncAffiliateResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create_program(self, name: str, commission_type: str, **kwargs: Any) -> AffiliateProgram:
        body: Dict[str, Any] = {"name": name, "commissionType": commission_type}
        field_map = {"description": "description", "cpc_rate": "cpcRate", "cpa_rate": "cpaRate", "cookie_days": "cookieDays"}
        for k, v in kwargs.items():
            body[field_map.get(k, k)] = v
        data = await self._http.post("/api/affiliate/programs", json=body)
        return AffiliateProgram.model_validate(data)

    async def list_programs(self) -> List[AffiliateProgram]:
        data = await self._http.get("/api/affiliate/programs")
        if isinstance(data, list):
            return [AffiliateProgram.model_validate(item) for item in data]
        items = data.get("programs", []) if isinstance(data, dict) else []
        return [AffiliateProgram.model_validate(item) for item in items]

    async def get_program(self, program_id: str) -> AffiliateProgram:
        data = await self._http.get(f"/api/affiliate/programs/{program_id}")
        return AffiliateProgram.model_validate(data)

    async def update_program(self, program_id: str, **kwargs: Any) -> AffiliateProgram:
        body: Dict[str, Any] = {}
        field_map = {"cpc_rate": "cpcRate", "cpa_rate": "cpaRate", "cookie_days": "cookieDays", "commission_type": "commissionType"}
        for k, v in kwargs.items():
            body[field_map.get(k, k)] = v
        data = await self._http.patch(f"/api/affiliate/programs/{program_id}", json=body)
        return AffiliateProgram.model_validate(data)

    async def get_program_stats(self, program_id: str, *, period: str = "30d") -> dict:
        return await self._http.get(f"/api/affiliate/programs/{program_id}/stats", params={"period": period}) or {}

    async def list_partners(self, program_id: str) -> List[dict]:
        data = await self._http.get(f"/api/affiliate/programs/{program_id}/partners")
        if isinstance(data, list):
            return data
        return data.get("partners", []) if isinstance(data, dict) else []

    async def update_partner_status(self, program_id: str, partner_id: str, status: str) -> dict:
        return await self._http.patch(f"/api/affiliate/programs/{program_id}/partners/{partner_id}", json={"status": status}) or {}

    async def discover(self, *, limit: int = 20) -> List[AffiliateProgram]:
        data = await self._http.get("/api/affiliate/discover", params={"limit": limit})
        if isinstance(data, list):
            return [AffiliateProgram.model_validate(item) for item in data]
        items = data.get("programs", []) if isinstance(data, dict) else []
        return [AffiliateProgram.model_validate(item) for item in items]

    async def join(self, program_id: str, *, partner_code: Optional[str] = None) -> dict:
        body: Dict[str, Any] = {}
        if partner_code is not None:
            body["partnerCode"] = partner_code
        return await self._http.post(f"/api/affiliate/join/{program_id}", json=body) or {}

    async def list_partnerships(self) -> List[dict]:
        data = await self._http.get("/api/affiliate/partnerships")
        if isinstance(data, list):
            return data
        return data.get("partnerships", []) if isinstance(data, dict) else []

    async def get_partnership_stats(self, partnership_id: str, *, period: str = "30d") -> dict:
        return await self._http.get(f"/api/affiliate/partnerships/{partnership_id}/stats", params={"period": period}) or {}

    async def leave_program(self, partnership_id: str) -> dict:
        return await self._http.delete(f"/api/affiliate/partnerships/{partnership_id}") or {}

    async def get_limits(self) -> dict:
        return await self._http.get("/api/affiliate/limits") or {}
