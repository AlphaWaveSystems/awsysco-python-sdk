"""Basic usage examples for the AWSYS.CO Python SDK.

Set AWSYS_API_KEY in your environment before running:

    export AWSYS_API_KEY=awsys_your_key_here
    python examples/basic_usage.py
"""

import os

from awsysco import Client, AwsysNotFoundError

api_key = os.environ.get("AWSYS_API_KEY")
if not api_key:
    raise SystemExit("Set AWSYS_API_KEY environment variable first.")

client = Client(api_key=api_key)

# ── Create a link ────────────────────────────────────────────────────────────
print("Creating a short link...")
link = client.links.create("https://example.com/very/long/path?query=value")
print(f"  Short URL: {link.short_url}")
print(f"  Short code: {link.short_code}")

# ── List links ───────────────────────────────────────────────────────────────
print("\nListing recent links (limit=5)...")
page = client.links.list(limit=5)
print(f"  Found {len(page.links)} links (total: {page.total})")
for lnk in page.links:
    print(f"    {lnk.short_code}: {lnk.long}")

# ── Get a link ───────────────────────────────────────────────────────────────
if link.short_code:
    print(f"\nFetching link {link.short_code!r}...")
    fetched = client.links.get(link.short_code)
    print(f"  Long URL: {fetched.long}")
    print(f"  Clicks:   {fetched.clicks}")

# ── Analytics ────────────────────────────────────────────────────────────────
    print(f"\nFetching stats for {link.short_code!r}...")
    stats = client.analytics.get_stats(link.short_code)
    print(f"  Total clicks: {stats.total_clicks}")

# ── QR code URL ──────────────────────────────────────────────────────────────
    qr_url = client.qr.get_url(link.short_code, size=400, color="1A1A2E")
    print(f"\nQR code URL: {qr_url}")

# ── Folders ──────────────────────────────────────────────────────────────────
print("\nCreating a folder...")
folder = client.folders.create("My SDK Demo Folder", color="#3498DB")
print(f"  Folder ID: {folder.id}, Name: {folder.name}")

if link.short_code and folder.id:
    print(f"  Assigning {link.short_code!r} to folder...")
    client.folders.assign_link(link.short_code, folder.id)
    print("  Done.")

folder_list = client.folders.list()
print(f"  Total folders: {len(folder_list.folders)}")

# ── Bulk create ──────────────────────────────────────────────────────────────
print("\nBulk creating 3 links...")
result = client.bulk.create([
    {"url": "https://example.com/bulk-1"},
    {"url": "https://example.com/bulk-2"},
    {"url": "https://example.com/bulk-3"},
])
print(f"  Created: {result.created}, Failed: {result.failed}")
for r in result.results:
    print(f"    {r.short_url}")

# ── Me ───────────────────────────────────────────────────────────────────────
print("\nFetching user info...")
me = client.me.get()
print(f"  Email: {me.email}")
print(f"  Tier:  {me.subscription_tier}")
print(f"  Premium: {me.is_premium}")

# ── Cleanup ──────────────────────────────────────────────────────────────────
print("\nCleaning up demo data...")
if link.short_code:
    client.links.delete(link.short_code)
if folder.id:
    client.folders.delete(folder.id)
print("Done.")
