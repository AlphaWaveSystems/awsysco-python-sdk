# awsysco — Official Python SDK

[![PyPI version](https://img.shields.io/pypi/v/awsysco.svg)](https://pypi.org/project/awsysco/)
[![Python versions](https://img.shields.io/pypi/pyversions/awsysco.svg)](https://pypi.org/project/awsysco/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The official Python SDK for the [AWSYS.CO](https://awsys.co) URL Shortener API.

## Installation

```bash
pip install awsysco
```

Requires Python 3.9+.

## Quick Start

```python
from awsysco import Client

client = Client(api_key="awsys_your_key_here")

# Shorten a URL
link = client.links.create("https://example.com/very/long/path")
print(link.short_url)  # https://awsys.co/abc123

# Get analytics
stats = client.analytics.get_stats(link.short_code)
print(f"Total clicks: {stats.total_clicks}")

# Build a QR code URL
qr_url = client.qr.get_url(link.short_code, size=400)
print(qr_url)
```

## Authentication

Generate an API key from your [AWSYS dashboard](https://awsys.co/dashboard/settings/api). All API keys begin with `awsys_`.

```python
client = Client(api_key="awsys_...")
```

Store keys in environment variables — never hardcode them:

```python
import os
from awsysco import Client

client = Client(api_key=os.environ["AWSYS_API_KEY"])
```

## API Reference

### Links

| Method | Description |
|---|---|
| `client.links.create(url, *, custom_slug, expires_at, max_clicks)` | Create a shortened link |
| `client.links.list(*, limit=20, offset=0)` | List links (paginated) |
| `client.links.get(short_path)` | Get a single link |
| `client.links.update(short_path, *, expires_at, max_clicks)` | Update link settings |
| `client.links.delete(short_path)` | Delete a link |

```python
# Create with options
link = client.links.create(
    "https://example.com",
    custom_slug="my-link",
    expires_at="2025-12-31T23:59:59Z",
    max_clicks=1000,
)

# Paginate
page1 = client.links.list(limit=20, offset=0)
page2 = client.links.list(limit=20, offset=20)

# Update
updated = client.links.update("my-link", max_clicks=500)

# Delete
client.links.delete("my-link")
```

### Analytics

| Method | Description |
|---|---|
| `client.analytics.get_stats(short_path)` | Get click stats for a link |

```python
stats = client.analytics.get_stats("abc123")
print(stats.total_clicks)
for click in stats.clicks:
    print(click.country, click.device, click.timestamp)
```

### QR Codes

| Method | Description |
|---|---|
| `client.qr.get_url(short_code, *, size=300, color='000000', bg_color='FFFFFF')` | Build QR image URL |

No HTTP request is made — this method constructs and returns the URL string.

```python
url = client.qr.get_url("abc123", size=400, color="FF5733", bg_color="FFFFFF")
# https://awsys.co/api/qr/abc123?size=400&color=FF5733&bgColor=FFFFFF
```

### Folders

| Method | Description |
|---|---|
| `client.folders.list()` | List all folders |
| `client.folders.create(name, *, color)` | Create a folder |
| `client.folders.delete(folder_id)` | Delete a folder |
| `client.folders.assign_link(short_path, folder_id)` | Assign a link to a folder |
| `client.folders.remove_link(short_path)` | Remove a link from its folder |

```python
folder = client.folders.create("Q1 Campaign", color="#FF5733")
client.folders.assign_link("abc123", folder.id)

folders = client.folders.list()
for f in folders.folders:
    print(f.name, f.link_count)

client.folders.remove_link("abc123")
client.folders.delete(folder.id)
```

### Bulk Create

| Method | Description |
|---|---|
| `client.bulk.create(urls)` | Create multiple links in one request |

```python
result = client.bulk.create([
    {"url": "https://example.com/page-1"},
    {"url": "https://example.com/page-2", "custom_slug": "page-two"},
    {"url": "https://example.com/page-3", "max_clicks": 100},
])
print(f"Created: {result.created}, Failed: {result.failed}")
for r in result.results:
    print(r.short_url, r.success)
```

### Me

| Method | Description |
|---|---|
| `client.me.get()` | Get the authenticated user's profile |

```python
me = client.me.get()
print(me.email, me.subscription_tier, me.is_premium)
```

### Usage

| Method | Description |
|---|---|
| `client.usage.get()` | Get live account consumption + tier limits |

Distinct from `me.get()` (static profile), `usage.get()` returns live counters
(links, clicks, QR codes, API calls, tracked clicks), the current tier limits,
and any active overage state. Limit fields may be an integer or the literal
string `"unlimited"`.

```python
usage = client.usage.get()
print(usage.total_links, usage.tracked_clicks_this_month)
print(usage.limits.monthly_links)  # int or "unlimited"
if usage.overage.active:
    print(f"Overage charge: {usage.overage.estimated_charge_cents}c")
```

### Web2App

| Method | Description |
|---|---|
| `client.web2app.consume_session(token)` | Consume a Web2App deep-link session |

Web2App sessions are **single-use** (consumed on read) with a **24-hour TTL**.
Unknown, expired, or already-consumed tokens raise `AwsysNotFoundError`;
malformed tokens raise `AwsysValidationError`.

```python
session = client.web2app.consume_session("0123456789abcdef0123456789abcdef")
print(session.link_id, session.utm_params, session.country)
```

## Error Handling

All errors inherit from `AwsysError`.

```python
from awsysco import (
    Client,
    AwsysError,
    AwsysAuthError,
    AwsysForbiddenError,
    AwsysNotFoundError,
    AwsysConflictError,
    AwsysValidationError,
    AwsysRateLimitError,
)

try:
    link = client.links.get("nonexistent")
except AwsysNotFoundError:
    print("Link not found")
except AwsysAuthError:
    print("Invalid API key")
except AwsysConflictError as e:
    print(f"Slug already taken: {e.message}")
except AwsysValidationError as e:
    print(f"Bad request: {e.message} ({e.code})")
except AwsysRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except AwsysError as e:
    print(f"API error {e.status}: {e.message}")
```

| Exception | HTTP Status | When raised |
|---|---|---|
| `AwsysValidationError` | 400 | Invalid request parameters |
| `AwsysAuthError` | 401 | Missing or invalid API key |
| `AwsysForbiddenError` | 403 | Insufficient permissions |
| `AwsysNotFoundError` | 404 | Resource does not exist |
| `AwsysConflictError` | 409 | Custom slug already taken |
| `AwsysRateLimitError` | 429 | Too many requests |
| `AwsysError` | 5xx | Server errors |

All exceptions expose `.message`, `.code`, `.status`, and `.raw` attributes.

## Rate Limiting

The SDK automatically retries on `429 Too Many Requests` with exponential backoff (up to 3 retries). The `Retry-After` response header is respected.

```python
from awsysco import AwsysRateLimitError

try:
    link = client.links.create("https://example.com")
except AwsysRateLimitError as e:
    print(f"Still rate limited after retries. Retry after: {e.retry_after}s")
```

## Custom Base URL

```python
# Point at staging
client = Client(
    api_key="awsys_...",
    base_url="https://staging.awsys.co",
)
```

## Context Manager

```python
with Client(api_key="awsys_...") as client:
    link = client.links.create("https://example.com")
    print(link.short_url)
# HTTP connections are closed automatically
```

## Models

All responses are parsed into Pydantic v2 models:

| Model | Fields |
|---|---|
| `Link` | `id`, `short_url`, `short_code`, `long`, `clicks`, `created`, `expires_at`, `max_clicks`, `password_protected` |
| `LinkList` | `links`, `total`, `has_more` |
| `LinkStats` | `short_code`, `total_clicks`, `clicks` |
| `ClickEvent` | `timestamp`, `country`, `device`, `browser`, `os`, `referrer` |
| `Folder` | `id`, `name`, `color`, `link_count`, `created_at` |
| `FolderList` | `folders`, `limit`, `used` |
| `BulkResult` | `created`, `failed`, `results` |
| `BulkLinkResult` | `success`, `short_url`, `long`, `error` |
| `MeResponse` | `uid`, `email`, `subscription_tier`, `user_prefix`, `is_premium`, `features`, `limits` |
| `UsageStats` | `total_links`, `total_clicks`, `links_created_this_month`, `qr_codes_this_month`, `folder_count`, `api_calls_this_month`, `tracked_clicks_this_month`, `tier`, `limits`, `has_api_key`, `api_key_created_at`, `user_prefix`, `is_premium`, `overage` |
| `UsageLimits` | `links_per_month`, `monthly_links`, `daily_links`, `monthly_tracked_clicks`, `qr_codes`, `folders` (each `int` or `"unlimited"`), `api_calls_per_month`, `custom_slugs` |
| `UsageOverage` | `active`, `started_at`, `expires_at`, `hours_until_drop`, `clicks_this_cycle`, `spending_limit_cents`, `estimated_charge_cents` |
| `Web2AppSession` | `success`, `link_id`, `utm_params`, `routing_rule`, `country`, `clicked_at` |

## Development Setup

```bash
git clone https://github.com/AlphaWaveSystems/awsysco-python-sdk.git
cd awsysco-python-sdk

pip install -e ".[dev]"

# Configure test credentials
cp .env.example .env.test
# Edit .env.test — add your AWSYS_API_KEY (staging recommended)

# Run tests
pytest

# Run with coverage
pytest --cov=awsysco --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes and add tests
4. Run `pytest` — all tests must pass
5. Open a pull request

Please read [SECURITY.md](SECURITY.md) before contributing — never commit API keys.

## License

MIT License — see [LICENSE](LICENSE) for details.
