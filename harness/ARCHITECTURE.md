<!-- HARNESS:START
     version=0.33.0
     schema=1
     updated=2026-07-19T05:36:09Z
     DO NOT EDIT — regenerate with: harness-ctl update /Users/patrickbertsch/dev/awsysco-python-sdk
-->

# Architecture — awsysco-python-sdk

> Auto-generated from constitution scan on 2026-07-19T05:36:09Z.
> Reflects the state of the repo at install time — update manually as the project evolves,
> or re-run `harness-ctl update /Users/patrickbertsch/dev/awsysco-python-sdk` to refresh from the latest scan.

---

## Project identity

| Field | Value |
|---|---|
| Name | awsysco-python-sdk |
| Path | `/Users/patrickbertsch/dev/awsysco-python-sdk` |
| Repository | (not a git repo) |
| Stack | python |
| Language(s) | Python |
| Runtime | (not detected) |
| Package manager | pip / poetry |
| Zeus owner | `hephaestus` |

---

## Project overview


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


---

## Stack overview

Python project.

### Key entry points


### Build and test commands

| Action | Command |
|---|---|
| Install deps | `pip install -e '.[dev]'` |
| Build | `python -m build` |
| Test | `pytest` |
| Lint | `(not detected — configure manually)` |
| Dev server | `python main.py` |
| Deploy (staging) | `bash scripts/deploy-staging.sh` |
| Deploy (production) | `bash scripts/deploy.sh` |



---

## Directory structure

```
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── SECURITY.md
├── awsysco/
│   └── __init__.py
│   └── __pycache__/
│   └── _async_http.py
│   └── _http.py
│   └── async_resources/
│   └── client.py
│   └── exceptions.py
│   └── models.py
│   └── resources/
├── examples/
│   └── async_usage.py
│   └── basic_usage.py
│   └── integration_test.py
├── harness/
│   └── ARCHITECTURE.md
│   └── FEATURES.md
│   └── INFRASTRUCTURE.md
│   └── SECURITY.md
│   └── TESTING.md
│   └── TOOLS.md
│   └── VERSION
│   └── WORKFLOWS.md
├── pyproject.toml
├── reports/
├── tests/
```

---

## Dependencies

**Runtime dependencies (0):**



**Dev dependencies:**


---

## Environment variables

Variables the project reads at runtime. Do not commit values — use the harness vault.

| Variable | Required | Purpose |
|---|---|---|

| `AWSYS_API_KEY` | yes | (see .env.example) |

| `AWSYS_BASE_URL` | yes | (see .env.example) |



---

## External services



*(none detected)*


---

## Constitution context

Rules extracted from `CLAUDE.md` at install time:

<!-- HARNESS:START
     version=0.32.0
     schema=1
     agent=awsysco-python-sdk
     updated=2026-07-18T02:25:54Z
     DO NOT EDIT THIS BLOCK — regenerate with: harness-ctl update /Users/patrickbertsch/dev/awsysco-python-sdk
-->

# Harness — Active Constraints

**This file is the entry point for every task in this project — always start here.**

**Agent:** `awsysco-python-sdk` · trust: `worker` · model: `mid`
**Budget:** 40 steps · 80000 tokens · $3.00 per session
**Privacy:** local_preferred — local models preferred; cloud only on low confidence
**Memory namespace:** `awsysco-python-sdk-worker`


## Must escalate (blocks until human approves)

*(truncated — see CLAUDE.md for full rules)*

*(Full rules in `CLAUDE.md` — this is a harness-generated summary only)*



---

## Notes from previous version

---

<!-- Add architecture decisions, diagrams, and notes below.
     The harness block above is managed automatically — everything below is yours. -->



<!-- HARNESS:END -->

---

<!-- Add architecture decisions, diagrams, and notes below.
     The harness block above is managed automatically — everything below is yours. -->
