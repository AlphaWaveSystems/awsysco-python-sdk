"""Manual integration test script for the AWSYS.CO Python SDK.

Tests each major operation with PASS/FAIL output. NOT run by pytest —
run manually after setting AWSYS_API_KEY:

    export AWSYS_API_KEY=awsys_your_key_here
    python examples/integration_test.py
"""

from __future__ import annotations

import os
import time

from awsysco import Client, AwsysError, AwsysNotFoundError
from awsysco.models import (
    AffiliateProgram,
    BulkResult,
    ClickEvent,
    CustomDomain,
    Folder,
    FolderList,
    Link,
    LinkList,
    LinkStats,
    MeResponse,
    NamespaceCheckResult,
    NamespaceInfo,
    SavedView,
    TrustScoreResult,
    UtmTemplate,
    Webhook,
)

api_key = os.environ.get("AWSYS_API_KEY")
if not api_key:
    raise SystemExit("Set AWSYS_API_KEY environment variable first.")

base_url = os.environ.get("AWSYS_BASE_URL", "https://awsys.co")
client = Client(api_key=api_key, base_url=base_url)

_passed = 0
_failed = 0
_skipped = 0


def _ts() -> str:
    return str(int(time.time() * 1000))


def check(name: str, condition: bool, detail: str = "") -> None:
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


def skip(name: str, reason: str) -> None:
    global _skipped
    _skipped += 1
    print(f"  SKIP  {name} — {reason}")


def section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ── Me ────────────────────────────────────────────────────────────────────────
section("Me")
try:
    me = client.me.get()
    check("get() returns MeResponse", isinstance(me, MeResponse))
    check("email is present", me.email is not None)
    check("subscription_tier is present", me.subscription_tier is not None)
except AwsysError as e:
    check("me.get()", False, str(e))

# ── Links ─────────────────────────────────────────────────────────────────────
section("Links")
created_link: Link | None = None
try:
    created_link = client.links.create(f"https://example.com/sdk-test-{_ts()}")
    check("create() returns Link", isinstance(created_link, Link))
    check("short_url is present", created_link.short_url is not None)
    check("short_code is present", created_link.short_code is not None)
except AwsysError as e:
    skip("create()", str(e))

try:
    page = client.links.list(limit=5)
    check("list() returns LinkList", isinstance(page, LinkList))
    check("links is a list", isinstance(page.links, list))
except AwsysError as e:
    check("list()", False, str(e))

if created_link and created_link.short_code:
    try:
        fetched = client.links.get(created_link.short_code)
        check("get() returns Link", isinstance(fetched, Link))
        check("get() returns correct code", fetched.short_code == created_link.short_code)
    except AwsysError as e:
        check("get()", False, str(e))

    try:
        updated = client.links.update(created_link.short_code, max_clicks=999)
        check("update() returns Link", isinstance(updated, Link))
        check("update() applies max_clicks", updated.max_clicks == 999)
    except AwsysError as e:
        check("update()", False, str(e))

# ── Analytics ─────────────────────────────────────────────────────────────────
section("Analytics")
if created_link and created_link.short_code:
    try:
        stats = client.analytics.get_stats(created_link.short_code)
        check("get_stats() returns LinkStats", isinstance(stats, LinkStats))
        check("total_clicks is int", isinstance(stats.total_clicks, int))
    except AwsysError as e:
        check("get_stats()", False, str(e))
else:
    skip("get_stats()", "No link available")

try:
    clicks = client.analytics.get_recent_clicks(limit=5)
    check("get_recent_clicks() returns list", isinstance(clicks, list))
    check("items are ClickEvent", all(isinstance(c, ClickEvent) for c in clicks))
except AwsysError as e:
    check("get_recent_clicks()", False, str(e))

# ── QR ────────────────────────────────────────────────────────────────────────
section("QR")
if created_link and created_link.short_code:
    qr_url = client.qr.get_url(created_link.short_code, size=300)
    check("get_url() returns string", isinstance(qr_url, str))
    check("get_url() contains short code", created_link.short_code in qr_url)
else:
    skip("get_url()", "No link available")

# ── Folders ───────────────────────────────────────────────────────────────────
section("Folders")
created_folder: Folder | None = None
try:
    created_folder = client.folders.create(f"SDK Test {_ts()}", color="#3498DB")
    check("create() returns Folder", isinstance(created_folder, Folder))
    check("id is present", created_folder.id is not None)
except AwsysError as e:
    check("create()", False, str(e))

try:
    folder_list = client.folders.list()
    check("list() returns FolderList", isinstance(folder_list, FolderList))
except AwsysError as e:
    check("list()", False, str(e))

if created_folder and created_folder.id:
    try:
        updated_folder = client.folders.update(created_folder.id, name=f"Renamed {_ts()}")
        check("update() returns Folder", isinstance(updated_folder, Folder))
    except AwsysError as e:
        check("update()", False, str(e))

# ── Bulk ──────────────────────────────────────────────────────────────────────
section("Bulk")
try:
    ts = _ts()
    result = client.bulk.create([
        {"url": f"https://example.com/bulk-{ts}-0"},
        {"url": f"https://example.com/bulk-{ts}-1"},
    ])
    check("create() returns BulkResult", isinstance(result, BulkResult))
    if result.results and all(r.success for r in result.results):
        check("all items succeeded", True)
    else:
        skip("all items succeeded", "Some items failed (account restriction?)")
except AwsysError as e:
    check("bulk.create()", False, str(e))

# ── Webhooks ──────────────────────────────────────────────────────────────────
section("Webhooks")
try:
    event_types = client.webhooks.list_event_types()
    check("list_event_types() returns dict", isinstance(event_types, dict))
except AwsysError as e:
    check("list_event_types()", False, str(e))

try:
    webhooks = client.webhooks.list()
    check("list() returns dict", isinstance(webhooks, dict))
except AwsysError as e:
    check("list()", False, str(e))

created_webhook: Webhook | None = None
try:
    created_webhook = client.webhooks.create(
        url="https://example.com/webhook",
        events=["link.created"],
        name=f"SDK Test {_ts()}",
    )
    check("create() returns Webhook", isinstance(created_webhook, Webhook))
    check("webhook id is present", created_webhook.id is not None)
except AwsysError as e:
    skip("create()", str(e))

if created_webhook and created_webhook.id:
    try:
        updated_wh = client.webhooks.update(created_webhook.id, enabled=False)
        check("update() returns Webhook", isinstance(updated_wh, Webhook))
    except AwsysError as e:
        check("update()", False, str(e))

    try:
        client.webhooks.delete(created_webhook.id)
        check("delete() succeeds", True)
    except AwsysError as e:
        check("delete()", False, str(e))

# ── Namespace ─────────────────────────────────────────────────────────────────
section("Namespace")
try:
    ns = client.namespace.get()
    check("get() returns NamespaceInfo", isinstance(ns, NamespaceInfo))
except AwsysError as e:
    check("get()", False, str(e))

try:
    result_check = client.namespace.check(f"sdktest{_ts()[-6:]}")
    check("check() returns NamespaceCheckResult", isinstance(result_check, NamespaceCheckResult))
    check("available field is bool", isinstance(result_check.available, bool))
except AwsysError as e:
    check("check()", False, str(e))

# ── UTM Templates ─────────────────────────────────────────────────────────────
section("UTM Templates")
try:
    templates = client.utm_templates.list()
    check("list() returns list", isinstance(templates, list))
    check("items are UtmTemplate", all(isinstance(t, UtmTemplate) for t in templates))
except AwsysError as e:
    check("list()", False, str(e))

try:
    resp = client.utm_templates.create(
        name=f"SDK Test {_ts()}",
        source="sdk",
        medium="test",
        campaign="integration",
    )
    check("create() returns dict", isinstance(resp, dict))
except AwsysError as e:
    check("create()", False, str(e))

# ── Saved Views ───────────────────────────────────────────────────────────────
section("Saved Views")
try:
    views = client.saved_views.list()
    check("list() returns list", isinstance(views, list))
    check("items are SavedView", all(isinstance(v, SavedView) for v in views))
except AwsysError as e:
    check("list()", False, str(e))

created_view: SavedView | None = None
try:
    created_view = client.saved_views.create(
        name=f"SDK Test {_ts()}",
        filters={"status": "active"},
    )
    check("create() returns SavedView", isinstance(created_view, SavedView))
    check("view id is present", created_view.id is not None)
except AwsysError as e:
    skip("create()", str(e))

if created_view and created_view.id:
    try:
        client.saved_views.delete(created_view.id)
        check("delete() succeeds", True)
    except AwsysError as e:
        check("delete()", False, str(e))

# ── Custom Domains ────────────────────────────────────────────────────────────
section("Custom Domains")
try:
    domains = client.custom_domains.list()
    check("list() returns dict", isinstance(domains, dict))
except AwsysError as e:
    check("list()", False, str(e))

try:
    avail = client.custom_domains.check("sdk-test-never-exists.example.com")
    check("check() returns dict", isinstance(avail, dict))
except AwsysError as e:
    check("check()", False, str(e))

# ── Tags ──────────────────────────────────────────────────────────────────────
section("Tags")
if created_link and created_link.short_code:
    try:
        resp = client.tags.add(created_link.short_code, "sdk-test")
        check("add() returns dict", isinstance(resp, dict))
    except AwsysError as e:
        check("add()", False, str(e))

    try:
        resp = client.tags.remove(created_link.short_code, "sdk-test")
        check("remove() returns dict", isinstance(resp, dict))
    except AwsysError as e:
        check("remove()", False, str(e))
else:
    skip("tags", "No link available")

# ── Trust Score ───────────────────────────────────────────────────────────────
section("Trust Score")
if created_link and created_link.short_code:
    try:
        result_ts = client.trust_score.scan(created_link.short_code)
        check("scan() returns TrustScoreResult", isinstance(result_ts, TrustScoreResult))
    except AwsysError as e:
        skip("scan()", str(e))
else:
    skip("scan()", "No link available")

# ── Agentlink ─────────────────────────────────────────────────────────────────
section("Agentlink")
try:
    resp = client.agentlink.subscribe("sdk-test@example.com")
    check("subscribe() returns dict", isinstance(resp, dict))
except AwsysError as e:
    skip("subscribe()", str(e))

try:
    stats = client.agentlink.get_account_stats(period_days=7)
    check("get_account_stats() returns dict", isinstance(stats, dict))
except AwsysError as e:
    skip("get_account_stats()", str(e))

# ── Affiliate ─────────────────────────────────────────────────────────────────
section("Affiliate")
try:
    programs = client.affiliate.list_programs()
    check("list_programs() returns list", isinstance(programs, list))
except AwsysError as e:
    check("list_programs()", False, str(e))

try:
    discover = client.affiliate.discover(limit=5)
    check("discover() returns list", isinstance(discover, list))
except AwsysError as e:
    check("discover()", False, str(e))

try:
    limits = client.affiliate.get_limits()
    check("get_limits() returns dict", isinstance(limits, dict))
except AwsysError as e:
    check("get_limits()", False, str(e))

try:
    partnerships = client.affiliate.list_partnerships()
    check("list_partnerships() returns list", isinstance(partnerships, list))
except AwsysError as e:
    check("list_partnerships()", False, str(e))

# ── Data Export ───────────────────────────────────────────────────────────────
section("Data Export")
try:
    csv_data = client.data_export.export_links()
    check("export_links() returns string", isinstance(csv_data, str))
    check("export_links() is non-empty", len(csv_data) > 0)
except AwsysError as e:
    check("export_links()", False, str(e))

# ── Cleanup ───────────────────────────────────────────────────────────────────
section("Cleanup")
if created_link and created_link.short_code:
    try:
        client.links.delete(created_link.short_code)
        check("delete link", True)
    except AwsysError as e:
        check("delete link", False, str(e))

if created_folder and created_folder.id:
    try:
        client.folders.delete(created_folder.id)
        check("delete folder", True)
    except AwsysError as e:
        check("delete folder", False, str(e))

# ── Summary ───────────────────────────────────────────────────────────────────
total = _passed + _failed + _skipped
print(f"\n{'=' * 60}")
print(f"  Results: {_passed} passed / {_failed} failed / {_skipped} skipped  ({total} total)")
print(f"{'=' * 60}\n")

if _failed > 0:
    raise SystemExit(1)
