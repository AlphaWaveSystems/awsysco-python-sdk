"""Contract-fixture test suite.

Drives every capability/error/behavior scenario in ``tests/contracts/sdk-contract.json``
(vendored from the platform repo) against the SDK. Per Gate 3: a scenario with no
registered handler FAILS the collection-time check below rather than being silently
skipped, so a contract update that adds a new scenario cannot go unnoticed.
"""

from __future__ import annotations

import json
import pathlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from awsysco._transport import parse_error
from awsysco.exceptions import (
    AwsysAuthError,
    AwsysConflictError,
    AwsysError,
    AwsysForbiddenError,
    AwsysNetworkError,
    AwsysNotFoundError,
    AwsysRateLimitError,
    AwsysServerError,
    AwsysTimeoutError,
    AwsysValidationError,
)
from awsysco.resources.affiliate import AffiliateResource
from awsysco.resources.agentlink import AgentlinkResource
from awsysco.resources.analytics import AnalyticsResource
from awsysco.resources.bulk import BulkResource
from awsysco.resources.custom_domains import CustomDomainsResource
from awsysco.resources.data_export import DataExportResource
from awsysco.resources.folders import FoldersResource
from awsysco.resources.imports import ImportsResource
from awsysco.resources.links import LinksResource
from awsysco.resources.me import MeResource
from awsysco.resources.namespace import NamespaceResource
from awsysco.resources.profile import ProfileResource
from awsysco.resources.qr import QRResource
from awsysco.resources.saved_views import SavedViewsResource
from awsysco.resources.tags import TagsResource
from awsysco.resources.trust_score import TrustScoreResource
from awsysco.resources.usage import UsageResource
from awsysco.resources.utm_templates import UtmTemplatesResource
from awsysco.resources.web2app import Web2AppResource
from awsysco.resources.webhooks import WebhooksResource

_CONTRACT_PATH = pathlib.Path(__file__).parent / "contracts" / "sdk-contract.json"
_CONTRACT = json.loads(_CONTRACT_PATH.read_text())

# Diff against the platform's own copy when it's checked out alongside this repo
# (CI won't have it — skip cleanly there).
_PLATFORM_CONTRACT_PATH = (
    pathlib.Path(__file__).parents[3] / "awsys-shortener" / "contracts" / "sdk-contract.json"
)


def test_vendored_contract_matches_platform_copy():
    if not _PLATFORM_CONTRACT_PATH.exists():
        pytest.skip("platform repo not checked out alongside this one")
    platform_contract = json.loads(_PLATFORM_CONTRACT_PATH.read_text())
    assert _CONTRACT == platform_contract, (
        "tests/contracts/sdk-contract.json is stale — re-vendor from "
        f"{_PLATFORM_CONTRACT_PATH}"
    )


# ---------------------------------------------------------------------------
# Resource harness
# ---------------------------------------------------------------------------


def _build_resources() -> SimpleNamespace:
    http = MagicMock()
    http.base_url = "https://awsys.co"
    return SimpleNamespace(
        http=http,
        links=LinksResource(http),
        analytics=AnalyticsResource(http),
        qr=QRResource(http),
        folders=FoldersResource(http),
        bulk=BulkResource(http),
        me=MeResource(http),
        tags=TagsResource(http),
        trust_score=TrustScoreResource(http),
        data_export=DataExportResource(http),
        namespace=NamespaceResource(http),
        utm_templates=UtmTemplatesResource(http),
        webhooks=WebhooksResource(http),
        saved_views=SavedViewsResource(http),
        custom_domains=CustomDomainsResource(http),
        agentlink=AgentlinkResource(http),
        affiliate=AffiliateResource(http),
        usage=UsageResource(http),
        web2app=Web2AppResource(http),
        imports=ImportsResource(http),
        profile=ProfileResource(http),
    )


def _set_json(http: MagicMock, method: str, body) -> None:
    getattr(http, method).return_value = body


def _set_text(http: MagicMock, method: str, text: str) -> None:
    getattr(http, method).return_value = text


# ---------------------------------------------------------------------------
# Capability handlers — one per fixture id. Each: (1) primes the mock transport
# with the fixture's response body, (2) calls the SDK method with matching
# arguments, (3) asserts the transport was called with the fixture's exact
# method/path/query/body, (4) sanity-checks the parsed result.
# ---------------------------------------------------------------------------

CapabilityHandler = "Callable[[SimpleNamespace, dict], None]"


def _h_create_link(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    result = r.links.create(e["request"]["body"]["url"])
    r.http.post.assert_called_once_with("/api/v1/links", json=e["request"]["body"])
    assert result.short_code == e["response"]["body"]["shortCode"]


def _h_create_link_custom_slug(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    body = e["request"]["body"]
    result = r.links.create(
        body["url"], custom_slug=body["customSlug"], expires_at=body["expiresAt"], max_clicks=body["maxClicks"]
    )
    r.http.post.assert_called_once_with("/api/v1/links", json=body)
    assert result.short_code == e["response"]["body"]["shortCode"]


def _h_list_links(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    q = e["request"]["query"]
    result = r.links.list(limit=int(q["limit"]), offset=int(q["offset"]))
    r.http.get.assert_called_once_with(
        "/api/v1/links", params={"limit": int(q["limit"]), "offset": int(q["offset"])}
    )
    assert len(result.links) == len(e["response"]["body"]["links"])


def _h_list_links_limit_clamped(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.links.list(limit=500, offset=0)
    r.http.get.assert_called_once_with("/api/v1/links", params={"limit": 100, "offset": 0})


def _h_get_link(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    short = e["request"]["path"].rsplit("/", 1)[-1]
    result = r.links.get(short)
    r.http.get.assert_called_once_with(e["request"]["path"])
    assert result.id == e["response"]["body"]["id"]


def _h_get_link_namespaced(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    short = e["request"]["path"].split("/api/v1/links/", 1)[1]
    result = r.links.get(short)
    # note: slash must NOT be encoded for GET wildcard routes
    r.http.get.assert_called_once_with(e["request"]["path"])
    assert result.full_path == "ns/slug"


def _h_update_link(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    short = e["request"]["path"].rsplit("/", 1)[-1]
    body = e["request"]["body"]
    r.links.update(short, max_clicks=body["maxClicks"], expires_at=body["expiresAt"])
    r.http.patch.assert_called_once_with(e["request"]["path"], json=body)


def _h_delete_link(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    short = e["request"]["path"].rsplit("/", 1)[-1]
    r.links.delete(short)
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_link_stats(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    short = e["request"]["path"].split("/")[4]
    result = r.analytics.get_stats(short, period=e["request"]["query"]["period"])
    r.http.get.assert_called_once_with(e["request"]["path"], params=e["request"]["query"])
    assert result.total_clicks == e["response"]["body"]["totalClicks"]


def _h_aggregate_stats(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    short = e["request"]["path"].split("/")[4]
    result = r.analytics.get_aggregate_stats(short, period=e["request"]["query"]["period"])
    r.http.get.assert_called_once_with(e["request"]["path"], params=e["request"]["query"])
    assert result.total_clicks == e["response"]["body"]["totalClicks"]


def _h_bulk_create(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    urls = e["request"]["body"]["urls"]
    result = r.bulk.create(urls)
    r.http.post.assert_called_once_with("/api/v1/bulk", json={"urls": urls})
    assert result.created == e["response"]["body"]["summary"]["created"]


def _h_me(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    result = r.me.get()
    r.http.get.assert_called_once_with("/api/v1/me")
    assert result.email == e["response"]["body"]["email"]


def _h_usage(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.usage.get()
    r.http.get.assert_called_once_with("/api/user/stats")


def _h_recent_clicks(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    q = e["request"]["query"]
    result = r.analytics.get_recent_clicks(limit=int(q["limit"]))
    r.http.get.assert_called_once_with("/api/user/clicks/recent", params={"limit": int(q["limit"])})
    assert len(result) == len(e["response"]["body"]["clicks"])


def _h_profile_get(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    result = r.profile.get()
    r.http.get.assert_called_once_with("/api/user/profile")
    assert result.email == e["response"]["body"]["email"]


def _h_profile_update(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    r.profile.update(display_name=e["request"]["body"]["displayName"])
    r.http.patch.assert_called_once_with("/api/user/profile", json=e["request"]["body"])


def _h_qr_url(r, e):
    q = e["request"]["query"]
    url = r.qr.get_url("abc123", size=int(q["size"]), color=q["color"], bg_color=q["bgColor"])
    assert url == "https://awsys.co/api/qr/abc123?size=300&color=000000&bgColor=ffffff"


def _h_qr_settings_get(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.qr.get_settings("abc123")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_qr_settings_update(r, e):
    _set_json(r.http, "put", e["response"]["body"])
    r.qr.update_settings("abc123", e["request"]["body"])
    r.http.put.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_folders_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    result = r.folders.list()
    r.http.get.assert_called_once_with("/api/v1/folders")
    assert len(result.folders) == len(e["response"]["body"]["folders"])


def _h_folder_create(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.folders.create(e["request"]["body"]["name"])
    r.http.post.assert_called_once_with("/api/v1/folders", json=e["request"]["body"])


def _h_folder_update(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    r.folders.update("f1", name=e["request"]["body"]["name"])
    r.http.patch.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_folder_delete(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.folders.delete("f1")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_folder_assign(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.folders.assign_link("abc123", e["request"]["body"]["folderId"])
    r.http.post.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_folder_remove(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.folders.remove_link("abc123")
    r.http.post.assert_called_once_with(e["request"]["path"], json={"folderId": None})


def _h_tags_add(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    tag = e["request"]["body"]["tags"][0]
    r.tags.add("abc123", tag)
    r.http.post.assert_called_once_with(e["request"]["path"], json={"tags": [tag]})


def _h_tag_remove(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.tags.remove("abc123", "a")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_views_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    result = r.saved_views.list()
    r.http.get.assert_called_once_with("/api/views")
    assert len(result) == len(e["response"]["body"]["views"])


def _h_view_create(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    body = e["request"]["body"]
    r.saved_views.create(body["name"], body["filters"])
    r.http.post.assert_called_once_with("/api/views", json=body)


def _h_view_update(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    r.saved_views.update("v1", name=e["request"]["body"]["name"])
    r.http.patch.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_view_delete(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.saved_views.delete("v1")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_utm_list_via_me(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    result = r.utm_templates.list()
    r.http.get.assert_called_once_with("/api/v1/me")
    assert len(result) == len(e["response"]["body"]["utmTemplates"])


def _h_utm_create(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    body = e["request"]["body"]
    r.utm_templates.create(body["name"], body["utmSource"], body["utmMedium"], body["utmCampaign"])
    called_body = r.http.post.call_args[1]["json"]
    assert called_body["name"] == body["name"]


def _h_utm_delete(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.utm_templates.delete("t1")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_webhook_event_types(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.webhooks.list_event_types()
    r.http.get.assert_called_once_with("/api/webhooks/event-types")


def _h_webhooks_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.webhooks.list()
    r.http.get.assert_called_once_with("/api/v1/webhooks")


def _h_webhook_create(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    body = e["request"]["body"]
    r.webhooks.create(body["url"], body["events"])
    r.http.post.assert_called_once_with("/api/v1/webhooks", json=body)


def _h_webhook_update(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    r.webhooks.update("w1", enabled=e["request"]["body"]["enabled"])
    r.http.patch.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_webhook_delete(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.webhooks.delete("w1")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_webhook_test(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.webhooks.test("w1", e["request"]["body"]["eventType"])
    r.http.post.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_domains_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.custom_domains.list()
    r.http.get.assert_called_once_with("/api/user/domains")


def _h_domain_add(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.custom_domains.add(e["request"]["body"]["domain"])
    r.http.post.assert_called_once_with("/api/user/domains", json=e["request"]["body"])


def _h_domain_verify(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.custom_domains.verify("go.example.com")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_domain_activate_deprecated(r, e):
    with pytest.deprecated_call():
        with pytest.raises(AwsysForbiddenError):
            r.custom_domains.activate("go.example.com")
    r.http.post.assert_not_called()


def _h_domain_update(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    body = e["request"]["body"]
    result = r.custom_domains.update("go.example.com", default_redirect=body["defaultRedirect"])
    r.http.patch.assert_called_once_with(e["request"]["path"], json=body)
    assert result.default_redirect == body["defaultRedirect"]


def _h_domain_remove(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.custom_domains.remove("go.example.com")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_domain_check(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.custom_domains.check("go.example.com")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_namespace_get(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.namespace.get()
    r.http.get.assert_called_once_with("/api/user/namespace")


def _h_namespace_check(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.namespace.check("acme")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_namespace_claim(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.namespace.claim("acme")
    r.http.post.assert_called_once_with("/api/user/namespace", json=e["request"]["body"])


def _h_namespace_release(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.namespace.release()
    r.http.delete.assert_called_once_with("/api/user/namespace")


def _h_affiliate_program_create(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.affiliate.create_program("P", "cpa_return", cpa_rate=10)
    assert r.http.post.call_args[0][0] == "/api/affiliate/programs"


def _h_affiliate_programs_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.list_programs()
    r.http.get.assert_called_once_with("/api/affiliate/programs")


def _h_affiliate_program_get(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.get_program("p1")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_affiliate_program_update(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    r.affiliate.update_program("p1", name="P2")
    r.http.patch.assert_called_once_with(e["request"]["path"], json={"name": "P2"})


def _h_affiliate_program_stats(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.get_program_stats("p1", period=e["request"]["query"]["period"])
    r.http.get.assert_called_once_with(e["request"]["path"], params=e["request"]["query"])


def _h_affiliate_partners_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.list_partners("p1")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_affiliate_partner_status(r, e):
    _set_json(r.http, "patch", e["response"]["body"])
    r.affiliate.update_partner_status("p1", "pt1", e["request"]["body"]["status"])
    r.http.patch.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_affiliate_discover(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.discover(limit=int(e["request"]["query"]["limit"]))
    r.http.get.assert_called_once_with(
        "/api/affiliate/discover", params={"limit": int(e["request"]["query"]["limit"])}
    )


def _h_affiliate_join(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.affiliate.join("p9", partner_code=e["request"]["body"]["partnerCode"])
    r.http.post.assert_called_once_with(e["request"]["path"], json=e["request"]["body"])


def _h_affiliate_partnerships_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.list_partnerships()
    r.http.get.assert_called_once_with("/api/affiliate/partnerships")


def _h_affiliate_partnership_stats(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.get_partnership_stats("ps1", period=e["request"]["query"]["period"])
    r.http.get.assert_called_once_with(e["request"]["path"], params=e["request"]["query"])


def _h_affiliate_leave(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.affiliate.leave_program("ps1")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_affiliate_limits(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.affiliate.get_limits()
    r.http.get.assert_called_once_with("/api/affiliate/limits")


def _h_agentlink_link_stats(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.agentlink.get_link_stats("abc123", period_days=int(e["request"]["query"]["period"]))
    r.http.get.assert_called_once_with(
        e["request"]["path"], params={"period": int(e["request"]["query"]["period"])}
    )


def _h_agentlink_account_stats(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.agentlink.get_account_stats(period_days=int(e["request"]["query"]["period"]))
    r.http.get.assert_called_once_with(
        "/api/agentlink/account/stats", params={"period": int(e["request"]["query"]["period"])}
    )


def _h_agentlink_subscribe(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    r.agentlink.subscribe(e["request"]["body"]["email"])
    r.http.post.assert_called_once_with("/api/agentlink/subscribe", json=e["request"]["body"])


def _h_web2app_consume(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.web2app.consume_session("tok123")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_import_start(r, e):
    _set_json(r.http, "post", e["response"]["body"])
    body = e["request"]["body"]
    r.imports.start(provider=body["provider"], access_token=body["accessToken"], scan_only=body.get("scanOnly"))
    r.http.post.assert_called_once_with("/api/v1/imports", json=body)


def _h_imports_list(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.imports.list(limit=int(e["request"]["query"]["limit"]))
    r.http.get.assert_called_once_with(
        "/api/v1/imports", params={"limit": int(e["request"]["query"]["limit"])}
    )


def _h_import_get(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    r.imports.get_status("j1")
    r.http.get.assert_called_once_with(e["request"]["path"])


def _h_import_cancel(r, e):
    _set_json(r.http, "delete", e["response"]["body"])
    r.imports.cancel("j1")
    r.http.delete.assert_called_once_with(e["request"]["path"])


def _h_import_redirect_map_csv(r, e):
    _set_text(r.http, "get_text", e["response"]["body"])
    result = r.imports.get_redirect_map_csv("j1")
    r.http.get_text.assert_called_once_with(e["request"]["path"])
    assert result == e["response"]["body"]


def _h_import_redirect_map_json(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    result = r.imports.get_redirect_map_json("j1")
    r.http.get.assert_called_once_with(e["request"]["path"])
    assert result == e["response"]["body"]


def _h_export_links_csv(r, e):
    _set_text(r.http, "get_text", e["response"]["body"])
    result = r.data_export.export_links()
    r.http.get_text.assert_called_once_with("/api/export/links")
    assert result == e["response"]["body"]


def _h_export_link_stats_csv(r, e):
    _set_text(r.http, "get_text", e["response"]["body"])
    result = r.data_export.export_link_stats("abc123")
    r.http.get_text.assert_called_once_with(e["request"]["path"])
    assert result == e["response"]["body"]


def _h_trust_scan(r, e):
    _set_json(r.http, "get", e["response"]["body"])
    result = r.trust_score.scan("abc123")
    r.http.get.assert_called_once_with(e["request"]["path"])
    assert result.score == e["response"]["body"]["trustScore"]


CAPABILITY_HANDLERS = {
    "create_link": _h_create_link,
    "create_link_custom_slug": _h_create_link_custom_slug,
    "list_links": _h_list_links,
    "list_links_last_page": _h_list_links,
    "list_links_missing_hasmore": _h_list_links,
    "list_links_limit_clamped": _h_list_links_limit_clamped,
    "get_link": _h_get_link,
    "get_link_namespaced": _h_get_link_namespaced,
    "update_link": _h_update_link,
    "delete_link": _h_delete_link,
    "link_stats": _h_link_stats,
    "aggregate_stats": _h_aggregate_stats,
    "bulk_create": _h_bulk_create,
    "me": _h_me,
    "usage": _h_usage,
    "recent_clicks": _h_recent_clicks,
    "profile_get": _h_profile_get,
    "profile_update": _h_profile_update,
    "qr_url": _h_qr_url,
    "qr_settings_get": _h_qr_settings_get,
    "qr_settings_update": _h_qr_settings_update,
    "folders_list": _h_folders_list,
    "folder_create": _h_folder_create,
    "folder_update": _h_folder_update,
    "folder_delete": _h_folder_delete,
    "folder_assign": _h_folder_assign,
    "folder_remove": _h_folder_remove,
    "tags_add": _h_tags_add,
    "tag_remove": _h_tag_remove,
    "views_list": _h_views_list,
    "view_create": _h_view_create,
    "view_update": _h_view_update,
    "view_delete": _h_view_delete,
    "utm_list_via_me": _h_utm_list_via_me,
    "utm_create": _h_utm_create,
    "utm_delete": _h_utm_delete,
    "webhook_event_types": _h_webhook_event_types,
    "webhooks_list": _h_webhooks_list,
    "webhook_create": _h_webhook_create,
    "webhook_update": _h_webhook_update,
    "webhook_delete": _h_webhook_delete,
    "webhook_test": _h_webhook_test,
    "domains_list": _h_domains_list,
    "domain_add": _h_domain_add,
    "domain_verify": _h_domain_verify,
    "domain_activate_deprecated": _h_domain_activate_deprecated,
    "domain_update": _h_domain_update,
    "domain_remove": _h_domain_remove,
    "domain_check": _h_domain_check,
    "namespace_get": _h_namespace_get,
    "namespace_check": _h_namespace_check,
    "namespace_claim": _h_namespace_claim,
    "namespace_release": _h_namespace_release,
    "affiliate_program_create": _h_affiliate_program_create,
    "affiliate_programs_list": _h_affiliate_programs_list,
    "affiliate_program_get": _h_affiliate_program_get,
    "affiliate_program_update": _h_affiliate_program_update,
    "affiliate_program_stats": _h_affiliate_program_stats,
    "affiliate_partners_list": _h_affiliate_partners_list,
    "affiliate_partner_status": _h_affiliate_partner_status,
    "affiliate_discover": _h_affiliate_discover,
    "affiliate_join": _h_affiliate_join,
    "affiliate_partnerships_list": _h_affiliate_partnerships_list,
    "affiliate_partnership_stats": _h_affiliate_partnership_stats,
    "affiliate_leave": _h_affiliate_leave,
    "affiliate_limits": _h_affiliate_limits,
    "agentlink_link_stats": _h_agentlink_link_stats,
    "agentlink_account_stats": _h_agentlink_account_stats,
    "agentlink_subscribe": _h_agentlink_subscribe,
    "web2app_consume": _h_web2app_consume,
    "import_start": _h_import_start,
    "imports_list": _h_imports_list,
    "import_get": _h_import_get,
    "import_cancel": _h_import_cancel,
    "import_redirect_map_csv": _h_import_redirect_map_csv,
    "import_redirect_map_json": _h_import_redirect_map_json,
    "export_links_csv": _h_export_links_csv,
    "export_link_stats_csv": _h_export_link_stats_csv,
    "trust_scan": _h_trust_scan,
}


@pytest.mark.parametrize("entry", _CONTRACT["capabilities"], ids=lambda e: e["id"])
def test_capability_scenario(entry):
    if entry["id"] not in CAPABILITY_HANDLERS:
        pytest.fail(
            f"No contract handler registered for capability {entry['id']!r} — "
            "add one to CAPABILITY_HANDLERS in tests/test_contract.py (Gate 3: "
            "unmapped scenarios must fail, not skip)."
        )
    resources = _build_resources()
    CAPABILITY_HANDLERS[entry["id"]](resources, entry)


# ---------------------------------------------------------------------------
# Error scenarios — generic: parse_error() handles every body shape uniformly,
# so most scenarios need no per-id handler. The few that assert retry behavior
# reuse the retry-loop coverage in test_transport.py; here we only check the
# status → exception class mapping (and, for feature-disabled, the .code).
# ---------------------------------------------------------------------------

_ERROR_CLASS_MAP = {
    "AuthenticationError": AwsysAuthError,
    "AuthorizationError": AwsysForbiddenError,
    "ValidationError": AwsysValidationError,
    "NotFoundError": AwsysNotFoundError,
    "ConflictError": AwsysConflictError,
    "RateLimitError": AwsysRateLimitError,
    "ServerError": AwsysServerError,
    "TimeoutError": AwsysTimeoutError,
    "NetworkError": AwsysNetworkError,
}

# Scenarios with status=None describe transport-level failures (no HTTP response at
# all) — those are exercised directly against HttpClient in test_transport.py
# (TestSyncRetryLoop.test_timeout_*, test_transport_error_on_post_not_retried), not
# via parse_error (which requires a response object). Retry-behavior scenarios are
# likewise covered end-to-end there. We still assert every id maps to a known
# expect_error class so a new, unrecognized error type in the contract fails loudly.
_TRANSPORT_LEVEL_IDS = {"err_timeout", "err_network"}
_RETRY_BEHAVIOR_IDS = {
    "err_429_retry_after",
    "err_429_exhausted",
    "err_503_get_retried",
    "err_503_post_not_retried",
}
# expect_error is not an AwsysError subclass name for these — each is a distinct,
# already-covered-elsewhere case handled specially rather than through parse_error.
_SPECIAL_CASE_ERROR_COVERAGE = {
    # non-JSON 2xx body → typed SDKError (AwsysServerError here), not a raw
    # JSONDecodeError — exercised against the real HttpClient/AsyncHttpClient
    # request path (parse_error is never reached; the transport's own try/except
    # around response.json() is what's under test).
    "err_2xx_malformed_json": (
        "tests/test_transport.py::TestAdditionalContractRequirements::"
        "test_non_json_2xx_body_raises_typed_error_not_raw_decode_error (+ _async)"
    ),
    # caller-initiated cancellation must pass through unmodified, never become
    # AwsysTimeoutError — asyncio.CancelledError is a BaseException, so it's never
    # caught by the `except httpx.TimeoutException`/`except httpx.TransportError`
    # clauses in the first place; the test proves that stays true.
    "err_user_cancel": (
        "tests/test_transport.py::TestAdditionalContractRequirements::"
        "test_cancelled_error_passes_through_unmodified"
    ),
}


class _FakeResponse:
    def __init__(self, status_code, body, headers=None):
        self.status_code = status_code
        self._body = body
        self.headers = headers or {}
        self.is_error = status_code >= 400

    def json(self):
        if not isinstance(self._body, dict):
            raise ValueError("not json")
        return self._body

    @property
    def text(self):
        return self._body if isinstance(self._body, str) else ""

    @property
    def reason_phrase(self):
        import http.client

        return http.client.responses.get(self.status_code, "")


@pytest.mark.parametrize("entry", _CONTRACT["errors"], ids=lambda e: e["id"])
def test_error_scenario(entry):
    if entry["id"] in _SPECIAL_CASE_ERROR_COVERAGE:
        return  # covered elsewhere — see _SPECIAL_CASE_ERROR_COVERAGE for the pointer

    if entry["expect_error"] not in _ERROR_CLASS_MAP:
        pytest.fail(f"Unrecognized expect_error {entry['expect_error']!r} for {entry['id']!r}")
    expected_cls = _ERROR_CLASS_MAP[entry["expect_error"]]

    if entry["id"] in _TRANSPORT_LEVEL_IDS or entry["id"] in _RETRY_BEHAVIOR_IDS:
        # Covered end-to-end (with a mocked clock) in test_transport.py.
        assert issubclass(expected_cls, AwsysError)
        return

    resp = _FakeResponse(entry["status"], entry["body"], headers=entry.get("headers"))
    exc = parse_error(resp)
    assert isinstance(exc, expected_cls), f"{entry['id']}: expected {expected_cls}, got {type(exc)}"
    if entry["id"] == "err_403_feature_disabled":
        assert exc.code == "FEATURE_DISABLED"


# ---------------------------------------------------------------------------
# Behaviors — cross-cutting assertions already covered elsewhere; this table
# just proves every declared behavior id has a home, per Gate 3.
# ---------------------------------------------------------------------------

_BEHAVIOR_COVERAGE = {
    "redaction": "tests/test_config.py::TestRedaction",
    "user_agent": "tests/test_config.py::TestUserAgent",
    "auth_header": "tests/test_config.py (Authorization header set at HttpClient construction)",
    "retry_policy": "tests/test_transport.py::TestSyncRetryLoop / TestAsyncRetryLoop",
    "pagination": "tests/test_links.py::TestLinksListAll",
    "error_body_tolerance": "tests/test_transport.py::TestParseErrorBodyShapes",
    "base_url_validation": "tests/test_config.py::TestBaseUrlResolution",
    "timeout_override": "tests/test_config.py::TestPerCallTimeout",
    "base_url_override": "tests/test_config.py::TestBaseUrlResolution",
    "missing_api_key": "tests/test_config.py::TestApiKeyResolution::test_missing_key_raises_configuration_error",
    "unknown_fields_preserved": "tests/test_models.py::TestUnknownFieldsPreserved",
    "timestamp_variants": "tests/test_models.py::TestTimestampCoercion",
    "iterator_links": "test_iterator_links_behavior (below)",
    "body_read_within_timeout": "tests/test_transport.py::TestTimeoutCoversBodyRead",
    "config_warnings": (
        "tests/test_config.py::TestApiKeyResolution::test_non_awsys_prefixed_key_warns(_only_once...) "
        "/ TestBaseUrlResolution::test_warns_on_plain_http(_only_once...)"
    ),
    "release_tag_matches_version": ".github/workflows/publish.yml (Verify tag matches package version step)",
}


def test_iterator_links_behavior():
    """behaviors.iterator_links: list_all() over list_links → list_links_last_page
    yields 3 links across exactly 2 requests."""
    page1 = next(c for c in _CONTRACT["capabilities"] if c["id"] == "list_links")
    page2 = next(c for c in _CONTRACT["capabilities"] if c["id"] == "list_links_last_page")
    r = _build_resources()
    r.http.get.side_effect = [page1["response"]["body"], page2["response"]["body"]]
    results = list(r.links.list_all(limit=2))
    assert len(results) == 3
    assert r.http.get.call_count == 2


@pytest.mark.parametrize("entry", _CONTRACT["behaviors"], ids=lambda e: e["id"])
def test_behavior_scenario_is_covered(entry):
    if entry["id"] not in _BEHAVIOR_COVERAGE:
        pytest.fail(
            f"No coverage note registered for behavior {entry['id']!r} — add one to "
            "_BEHAVIOR_COVERAGE in tests/test_contract.py, pointing at the test(s) "
            "that actually exercise it (Gate 3: unmapped scenarios must fail)."
        )
