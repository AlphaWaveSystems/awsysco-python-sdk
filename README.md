# awsysco — Official Python SDK

[![PyPI version](https://img.shields.io/pypi/v/awsysco.svg)](https://pypi.org/project/awsysco/)
[![Python versions](https://img.shields.io/pypi/pyversions/awsysco.svg)](https://pypi.org/project/awsysco/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What

The official Python SDK for the [AWSYS.CO](https://awsys.co) URL Shortener API — a
typed, sync-and-async client covering every capability the platform exposes to an
API key: links, analytics, QR codes, folders, bulk create, account/profile/usage,
tags, trust scoring, data export, branded namespaces, UTM templates, webhooks, saved
views, custom domains, affiliate programs, AgentLink, Web2App, and provider imports.
Every method is documented and Pydantic-typed; every error maps to a specific,
catchable exception.

## Install

```bash
pip install awsysco
```

Requires Python 3.9+. See [Supported Versions](#supported-versions) below.

## Authentication

Generate an API key from your [AWSYS dashboard](https://awsys.co/dashboard/settings/api).
All API keys begin with `awsys_`.

```python
from awsysco import Client

client = Client(api_key="awsys_...")
```

Or set `AWSYS_API_KEY` in your environment and omit `api_key` entirely:

```bash
export AWSYS_API_KEY=awsys_...
```

```python
client = Client()  # picks up AWSYS_API_KEY automatically
```

Passing neither raises `AwsysConfigurationError` before any network call is made.

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

## Core Resources

Every resource below is available on `client.<resource>` (sync `Client`) and
identically on `await client.<resource>.<method>(...)` (`AsyncClient`).

### Links — `client.links`

```python
link = client.links.create("https://example.com", custom_slug="my-link", max_clicks=1000)
page = client.links.list(limit=20, offset=0)
one = client.links.get("my-link")
updated = client.links.update("my-link", max_clicks=500)
client.links.delete("my-link")

# Auto-paginate every link (see Pagination below)
for link in client.links.list_all():
    print(link.short_code)
```

### Analytics — `client.analytics`

```python
stats = client.analytics.get_stats("abc123")
print(stats.total_clicks)

agg = client.analytics.get_aggregate_stats("abc123", period="30d")
print(agg.total_clicks, agg.unique_visitors, agg.country_breakdown)
if agg.upgrade_for_more:   # present on free tier; richer breakdowns need Pro+
    print(agg.upgrade_for_more.message)

# Requires the account's "Live Globe" feature flag; 403 FEATURE_DISABLED otherwise.
recent = client.analytics.get_recent_clicks(limit=10)
```

### QR Codes — `client.qr`

```python
# Client-side URL builder — no HTTP request is made.
url = client.qr.get_url("abc123", size=400, color="FF5733", bg_color="FFFFFF")

settings = client.qr.get_settings("abc123")
client.qr.update_settings("abc123", {"color": "#ff0000"})
```

### Folders — `client.folders`

```python
folder = client.folders.create("Q1 Campaign", color="#FF5733")
client.folders.assign_link("abc123", folder.id)
client.folders.update(folder.id, name="Q1 Campaign (final)")
client.folders.remove_link("abc123")
client.folders.delete(folder.id)
```

### Bulk Create — `client.bulk`

```python
result = client.bulk.create([
    {"url": "https://example.com/page-1"},
    {"url": "https://example.com/page-2", "custom_slug": "page-two"},
])
print(result.created, result.failed)
```

### Me / Profile / Usage

Three distinct, non-overlapping views of the account:

```python
me = client.me.get()              # subscription tier, features, limits
profile = client.profile.get()    # account profile: email, display name
usage = client.usage.get()        # live consumption counters + overage state

client.profile.update(display_name="New Name")
```

### Tags — `client.tags`

```python
client.tags.add("abc123", "promo")
client.tags.remove("abc123", "promo")
```

### Trust Score — `client.trust_score`

```python
result = client.trust_score.scan("abc123")
print(result.score, result.status, result.threats)
```

### Data Export — `client.data_export`

```python
csv_text = client.data_export.export_links()             # all links, as CSV
stats_csv = client.data_export.export_link_stats("abc123")
```

### Namespace — `client.namespace`

```python
info = client.namespace.get()
available = client.namespace.check("acme")
client.namespace.claim("acme")
client.namespace.release()
```

### UTM Templates — `client.utm_templates`

```python
client.utm_templates.create("Launch", "newsletter", "email", "sept")
for t in client.utm_templates.list():   # derived from /api/v1/me — no dedicated list route
    print(t.name)
client.utm_templates.delete(t.id)
```

### Webhooks — `client.webhooks`

```python
webhook = client.webhooks.create("https://you.example/hook", ["link.created", "link.click"])
client.webhooks.update(webhook.id, enabled=False)
client.webhooks.test(webhook.id, "link.created")
client.webhooks.delete(webhook.id)
```

### Saved Views — `client.saved_views`

```python
view = client.saved_views.create("My View", {"tag": "promo"})
client.saved_views.update(view.id, name="Renamed View")
client.saved_views.delete(view.id)
```

### Custom Domains — `client.custom_domains`

```python
client.custom_domains.add("go.example.com")
client.custom_domains.verify("go.example.com")
client.custom_domains.update("go.example.com", default_redirect="https://example.com/")
# .activate() is deprecated — Firebase-only, unreachable with an API key. Use the dashboard.
```

### Affiliate — `client.affiliate`

```python
program = client.affiliate.create_program("Partner Program", "cpa_return", cpa_rate=15)
client.affiliate.discover(limit=20)
client.affiliate.join(program.id, partner_code="LAUNCH")
stats = client.affiliate.get_program_stats(program.id, period="30d")
```

### AgentLink — `client.agentlink`

```python
client.agentlink.subscribe("dev@example.com")          # public, no auth required
stats = client.agentlink.get_account_stats(period_days=7)
```

### Web2App — `client.web2app`

Sessions are **single-use** (consumed on read) with a **24-hour TTL**.

```python
session = client.web2app.consume_session("0123456789abcdef0123456789abcdef")
print(session.link_id, session.utm_params, session.country)
```

### Imports — `client.imports`

```python
job = client.imports.start(provider="bitly", access_token="<bitly-token>")
done = client.imports.wait_for_completion(job.id, poll_interval=5.0, timeout=300.0)
print(done.status, done.counts.written, done.counts.errored)

csv_map = client.imports.get_redirect_map_csv(job.id)
json_map = client.imports.get_redirect_map_json(job.id)
```

## Pagination

Only `links.list()` is paginated (offset/limit; the platform ignores offsets on
every other list endpoint, so the SDK doesn't fake them). `limit` is clamped to the
platform max of 100 client-side.

```python
page1 = client.links.list(limit=20, offset=0)
page2 = client.links.list(limit=20, offset=20)
print(page1.has_more)   # None if the platform didn't send pagination info

# Or auto-paginate everything:
for link in client.links.list_all(limit=100):
    ...

# Async equivalent:
async for link in async_client.links.list_all():
    ...
```

The iterator stops when the platform reports `has_more=False`, **or** a page comes
back shorter than the requested `limit` (including empty) — this guards against a
response that omits `has_more` entirely.

## Errors

All errors inherit from `AwsysError`.

```python
from awsysco import (
    Client,
    AwsysError,
    AwsysConfigurationError,
    AwsysAuthError,
    AwsysForbiddenError,
    AwsysNotFoundError,
    AwsysConflictError,
    AwsysValidationError,
    AwsysRateLimitError,
    AwsysServerError,
    AwsysNetworkError,
    AwsysTimeoutError,
)

try:
    link = client.links.get("nonexistent")
except AwsysNotFoundError:
    print("Link not found")
except AwsysRateLimitError as e:
    print(f"Rate limited (code={e.code}). Retry after {e.retry_after}s, resets {e.resets_at}")
except AwsysServerError as e:
    print(f"Platform error {e.status}: {e.message}")
except AwsysTimeoutError:
    print("Request timed out")
except AwsysError as e:
    print(f"API error {e.status}: {e.message}")
```

| Exception | HTTP status | When raised |
|---|---|---|
| `AwsysConfigurationError` | – | Missing API key or invalid `base_url`, before any network call |
| `AwsysValidationError` | 400 | Invalid request parameters |
| `AwsysAuthError` | 401 | Missing or invalid API key |
| `AwsysForbiddenError` | 403 | Insufficient permissions / tier / feature flag |
| `AwsysNotFoundError` | 404 | Resource does not exist |
| `AwsysConflictError` | 409 | Custom slug already taken |
| `AwsysRateLimitError` | 429 | Too many requests (`.code`, `.retry_after`, `.resets_at`) |
| `AwsysServerError` | 5xx | Platform-side error |
| `AwsysNetworkError` | – | Connection failure (no HTTP response at all) |
| `AwsysTimeoutError` | – | Request exceeded its timeout (subclass of `AwsysNetworkError`) |
| `AwsysError` | any | Base class; catches everything above |

Every exception exposes `.message`, `.code`, `.status`, and `.raw` (the parsed —
or raw text — response body). The platform emits several error-body shapes
(`{error:true,code,message}`, `{error:"<string>",code}`, `{success:false,...}`,
and occasionally non-JSON bodies); the SDK tolerates all of them.

## Configuration

```python
client = Client(
    api_key="awsys_...",                    # or omit to read AWSYS_API_KEY
    base_url="https://staging.awsys.co",    # or omit to read AWSYS_BASE_URL, default https://awsys.co
    timeout=30.0,                           # per-request default, in seconds
    max_retries=3,                          # retry attempts for 429s / retryable 5xx / transport errors
)
```

`base_url` must start with `http://` or `https://` (anything else raises
`AwsysConfigurationError`); a plain `http://` URL is accepted but emits a warning.
The API key and base URL are never included in `repr(client)`, log output, or any
exception — `repr()` shows a redacted `awsys_...last4` form.

## Advanced

**Async**: every resource and method is mirrored on `AsyncClient`.

```python
import asyncio
from awsysco import AsyncClient

async def main():
    async with AsyncClient(api_key="awsys_...") as client:
        link = await client.links.create("https://example.com")
        print(link.short_url)

asyncio.run(main())
```

**Retries**: `429` is retried for every HTTP method (except quota-exhaustion 429s —
`HOURLY_LIMIT_EXCEEDED`/`DAILY_LIMIT_EXCEEDED`/`MONTHLY_LIMIT_EXCEEDED` — which raise
immediately, since waiting a few seconds can't help). `502`/`503`/`504` and
transport-level failures (connection reset/refused, DNS) are retried only for
idempotent methods (`GET`/`PUT`/`DELETE`) — the platform has no idempotency keys, so
a retried `POST`/`PATCH` could create duplicates. Backoff uses the `Retry-After`
header when present (seconds or an HTTP-date), otherwise `1s × 2^attempt` capped at
30s, with full jitter. Set `max_retries=0` to disable retries entirely.

**Timeouts**: 30s default per attempt, configurable at the client level
(`Client(timeout=...)`) or per call via each resource method's underlying request.

**Context managers**: `with Client(...) as client:` / `async with AsyncClient(...) as client:`
close the underlying HTTP connection pool automatically.

## Models

Every response is parsed into a Pydantic v2 model. All fields are `Optional`
(the platform's response shapes vary by tier/feature flags), unknown fields from
the platform are preserved rather than rejected, and timestamp fields accept both
plain ISO-8601 strings and Firestore's `{_seconds,_nanoseconds}` shape (normalized
to an ISO-8601 string — models expose timestamps as `str`, not a native `datetime`,
in the 1.x series; native `datetime` support is planned for 2.0).

## Supported Versions

Python 3.9, 3.10, 3.11, 3.12, and 3.13 are tested in CI on every push. Runtime
dependencies: `httpx>=0.27,<1`, `pydantic>=2,<3`.

## Development Setup

```bash
git clone https://github.com/AlphaWaveSystems/awsysco-python-sdk.git
cd awsysco-python-sdk

pip install -e ".[dev]"

# Configure test credentials (staging recommended)
cp .env.example .env.test
# Edit .env.test — add your AWSYS_API_KEY

# Unit + contract tests — no network required
pytest -m "not integration"

# Full suite, including live staging integration tests
pytest

# Lint and type-check
ruff check .
mypy awsysco

# Coverage
pytest --cov=awsysco --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes and add tests (see `tests/test_contract.py` if you're touching
   request/response shapes — it's driven by `tests/contracts/sdk-contract.json`)
4. Run `pytest -m "not integration"`, `ruff check .`, and `mypy awsysco` — all must pass
5. Open a pull request

## Security

See [SECURITY.md](SECURITY.md) for the secret-hygiene policy (never commit API
keys) and [SECURITY-REVIEW.md](SECURITY-REVIEW.md) for the SDK's own security
review (dependency audit, redaction guarantees, TLS/base-URL validation). Report
vulnerabilities to security@awsys.co — do not open a public issue.

## License

MIT License — see [LICENSE](LICENSE) for details.
