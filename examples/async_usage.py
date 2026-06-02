"""Async usage examples for the AWSYS.CO Python SDK.

Set AWSYS_API_KEY in your environment before running:

    export AWSYS_API_KEY=awsys_your_key_here
    python examples/async_usage.py
"""

import asyncio
import os

from awsysco import AsyncClient, AwsysNotFoundError

api_key = os.environ.get("AWSYS_API_KEY")
if not api_key:
    raise SystemExit("Set AWSYS_API_KEY environment variable first.")


async def main() -> None:
    async with AsyncClient(api_key=api_key) as client:
        # ── Create a link ────────────────────────────────────────────────────
        print("Creating a short link (async)...")
        link = await client.links.create(
            "https://example.com/async/demo",
            custom_slug=None,
            max_clicks=1000,
        )
        print(f"  Short URL:  {link.short_url}")
        print(f"  Short code: {link.short_code}")

        # ── List links ───────────────────────────────────────────────────────
        print("\nListing recent links (limit=5)...")
        page = await client.links.list(limit=5)
        print(f"  Found {len(page.links)} links (total: {page.total})")

        # ── Analytics ────────────────────────────────────────────────────────
        if link.short_code:
            print(f"\nFetching stats for {link.short_code!r}...")
            stats = await client.analytics.get_stats(link.short_code, period="7d")
            print(f"  Total clicks: {stats.total_clicks}")

        # ── QR code URL ──────────────────────────────────────────────────────
        if link.short_code:
            qr_url = client.qr.get_url(link.short_code, size=400, color="1A1A2E")
            print(f"\nQR code URL: {qr_url}")

        # ── Webhooks ─────────────────────────────────────────────────────────
        print("\nListing available webhook event types...")
        event_types = await client.webhooks.list_event_types()
        print(f"  Event types: {event_types}")

        # ── Namespace ────────────────────────────────────────────────────────
        print("\nChecking namespace info...")
        ns = await client.namespace.get()
        print(f"  Has access: {ns.has_access}")
        print(f"  Namespace:  {ns.namespace}")

        # ── Me ───────────────────────────────────────────────────────────────
        print("\nFetching user info...")
        me = await client.me.get()
        print(f"  Email: {me.email}")
        print(f"  Tier:  {me.subscription_tier}")

        # ── UTM templates ────────────────────────────────────────────────────
        print("\nListing UTM templates...")
        templates = await client.utm_templates.list()
        print(f"  Found {len(templates)} templates")

        # ── Saved views ──────────────────────────────────────────────────────
        print("\nListing saved views...")
        views = await client.saved_views.list()
        print(f"  Found {len(views)} saved views")

        # ── Cleanup ──────────────────────────────────────────────────────────
        print("\nCleaning up...")
        if link.short_code:
            await client.links.delete(link.short_code)
            print(f"  Deleted link {link.short_code!r}")

        print("Done.")


asyncio.run(main())
