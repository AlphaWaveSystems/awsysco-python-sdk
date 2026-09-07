# Changelog

All notable changes to this project are documented in this file. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/).

## [Unreleased] — 1.4.0

Cross-SDK contract-parity pass (Python/TS/Go behavior contract v1.0). No breaking
changes — see below.

### Added
- `client.profile` resource: `get()` / `update(**kwargs)` against `/api/user/profile`.
- `client.imports.get_redirect_map_csv(job_id)` / `get_redirect_map_json(job_id)`.
- `client.imports.start(..., scope_filter=None)` parameter.
- `client.links.list_all()` (sync generator) / `AsyncClient.links.list_all()` (async
  generator) — auto-paginating iterator over every link.
- `AwsysServerError` (5xx), `AwsysNetworkError` (transport failure), `AwsysTimeoutError`
  (subclass of `AwsysNetworkError`), `AwsysConfigurationError` (bad config, raised
  before any network call).
- `AwsysRateLimitError.code` and `.resets_at`.
- `Client`/`AsyncClient` now accept `api_key`/`base_url` as optional, falling back to
  the `AWSYS_API_KEY`/`AWSYS_BASE_URL` environment variables; a `max_retries` param.
- `Client`/`AsyncClient`/`HttpClient`/`AsyncHttpClient.__repr__` — redacted, never
  leak the API key.
- `HttpClient.base_url` / `.redacted_key` public properties.
- `Link.full_path` / `.namespace` fields (previously only reachable as unqueryable
  extras on namespaced-link responses).
- `CustomDomain.default_redirect` field; `custom_domains.update(..., default_redirect=None)`.
- `Webhook.secret` / `.success_count` fields; `Webhook.__repr__` redacts `secret`.
- `Profile` model.
- Firestore-timestamp tolerance: any `{_seconds,_nanoseconds}`/`{seconds,nanoseconds}`
  value in a response is normalized to an ISO-8601 string before model validation
  (fields stay `str`-typed; native `datetime` support is planned for 2.0).
- Per-call `timeout=` override on the underlying transport.
- `tests/test_contract.py`: a fixture-driven test suite (`tests/contracts/sdk-contract.json`,
  vendored from the platform repo) exercising every capability/error/behavior
  scenario in the cross-SDK contract; unmapped scenarios fail rather than skip.
- `.github/workflows/ci.yml`: ruff + mypy + pytest (unit/contract on every push,
  matrix Python 3.9–3.13; integration gated on the `AWSYS_API_KEY` secret).
- `.github/workflows/contract-drift.yml`: weekly + `repository_dispatch`-triggered
  check against the platform's live contract, filing a `sdk-parity`-labeled issue on
  drift; nightly staging integration run.
- `ruff`/`mypy` added to dev dependencies, with config in `pyproject.toml`.
- `LICENSE` (MIT) — referenced by `pyproject.toml` and the README but previously
  missing from the repo.
- `SECURITY-REVIEW.md`.

### Changed
- `pyproject.toml`: pin `httpx>=0.27,<1`, `pydantic>=2,<3`; declare Python 3.13 support.
- `_parse_error()` and the retry/backoff decision logic are now shared between the
  sync and async transports (`awsysco/_transport.py`), removing a byte-for-byte
  duplicate.
- User-Agent header is now `awsysco-python-sdk/{version} (python/{runtime version})`,
  derived from the package's own `__version__` (was a hardcoded, stale `1.0.0`).
- Retry policy: 429 retried for all methods except quota-exhaustion codes
  (`HOURLY_LIMIT_EXCEEDED`/`DAILY_LIMIT_EXCEEDED`/`MONTHLY_LIMIT_EXCEEDED`, never
  retried); `502`/`503`/`504` and transport errors retried only for idempotent
  methods (`GET`/`PUT`/`DELETE`); backoff now uses full jitter.
- `links.create()`/`links.update()` accept `RoutingRule`/`OgMeta`/`GeoRestriction`
  model instances (previously accepted only plain dicts, though the same-named
  model classes existed unused).
- `links.update()` URL-encodes a namespaced `short_path` (the platform's `PATCH`
  route can't otherwise address `prefix/slug`).
- `bulk.create()`'s snake_case/camelCase key handling consolidated into one
  normalizer (previously duplicated per field).
- `qr.py` reads the transport's `base_url` via its public property instead of a
  private attribute.
- README rewritten with full coverage of all 20 resources, pagination, error
  hierarchy, configuration, and async/retry/timeout behavior.

### Fixed
- **`analytics.get_recent_clicks()`** called `/api/user/recent-clicks`, a path that
  never existed on the platform (always 404'd). Now calls `/api/user/clicks/recent`
  and supports a `since` parameter.
- **`folders.update()`** called `PATCH /api/v1/folders/:id`, which 404s — the
  platform only exposes this route unversioned. Now calls `PATCH /api/folders/:id`.
- **`tags.add()`** sent `{"tag": "..."}` (singular) — the platform requires
  `{"tags": [...]}` (a plural array); every call previously failed validation
  server-side.
- **`webhooks.list()`/`.create()`/`.delete()`/`.test()`** called unversioned
  `/api/webhooks/*` paths; the platform's canonical routes for these four are
  `/api/v1/webhooks/*` (`.update()` correctly stays unversioned — no v1 alias
  exists for it).
- **`TrustScoreResult.score`/`.status`** were always `None` — the platform sends
  `trustScore`/`trustStatus`, not `score`/`status`. Fixed via a field alias (no
  public rename).
- **`ProfileResource.update(**kwargs)`** sent raw Python kwarg names on the wire
  (e.g. `display_name`) instead of camelCase (`displayName`), so non-camelCase
  update fields silently no-opped server-side.
- **`imports.start()`** sent snake_case body keys (`access_token`, etc.); the
  platform's documented shape is camelCase (`accessToken`, etc.) — both are
  accepted server-side, but the fixture/catalog standardize on camelCase.
- `custom_domains.activate()` previously made a network call to a route that's
  Firebase-auth-only and always 401s for an API key. Now raises
  `AwsysForbiddenError` immediately (with a `DeprecationWarning`) without a
  network round-trip.
- `tests/conftest.py`'s `pytest_runtest_call` hook was a plain function, not a
  pytest hookwrapper — since it called `item.runtest()` itself, pytest's own
  internal call to the same hookspec ran again alongside it, so **every test in
  the suite silently executed twice per run**, including live calls against
  staging. Fixed by converting it to a proper `@pytest.hookimpl(wrapper=True)`.
- **`LinkList.has_more`** was always `None` — the platform nests pagination
  under `pagination: {limit, offset, hasMore}`, not at the top level, so the
  field's auto-generated alias never matched anything real. This silently broke
  `links.list_all()`'s primary stop condition; the iterator only ever worked by
  accident, via its secondary "short page" length check. A before-validator now
  hoists `pagination.hasMore`/`.limit`/`.offset` up before field validation.
- **`links.list_all(limit=0)`** (or a negative limit) could loop forever — the
  limit was clamped with `min(limit, 100)` but no lower bound, so a `0`/negative
  limit reached the platform as-is and the "page shorter than limit" stop
  condition (`len(page.links) < limit`) could never fire. Now clamped to `>=1`.
- **`Webhook.secret` leaked via `str()`/f-strings.** An earlier fix in this same
  PR added a custom `__repr__` that masked it, but pydantic generates `__str__`
  independently of a subclass's `__repr__` — so `str(webhook)`/`f"{webhook}"`/
  `logging.info("%s", webhook)` still leaked the raw secret. An independent
  review caught it before merge. Fixed properly via `Field(repr=False)` (which
  backs both representations) plus `__str__ = __repr__`.
- The Firestore-timestamp coercion validator could itself raise: a non-numeric
  `nanoseconds` value (e.g. `{"seconds": 1, "nanoseconds": "q"}`) hit an
  uncaught `TypeError`, and an out-of-range `seconds` value (huge, deeply
  negative, or non-numeric) that failed conversion left the *raw dict* in place,
  which then failed downstream field validation (a dict into a `str` field) —
  the "never raise" guarantee didn't actually hold for either case. Both are now
  caught and the field is stringified on any conversion failure.
- Retry-After capping (raise immediately rather than sleep, for a value beyond
  the 30s cap or non-finite) previously only applied to 429s — a retryable 5xx
  with an oversized `Retry-After` (e.g. `503` + `Retry-After: 3600`) slept for
  the full, uncapped duration instead. Also fixed: a `Retry-After: nan` was
  silently clamped to `0.0` by an unconditional `max(0.0, ...)`, which caused it
  to sleep almost instantly and retry rather than being recognized as
  non-finite and raising immediately.
- `qr.get_url()`'s default `bg_color` was `"FFFFFF"` (uppercase); the platform's
  own convention (and the contract fixture) uses lowercase — aligned to
  `"ffffff"` for consistency (purely cosmetic; hex color parsing is
  case-insensitive either way).
- `pyproject.toml` and `awsysco/_version.py` each held their own copy of the
  version string, requiring a manual sync on every release. `pyproject.toml`
  now declares `dynamic = ["version"]` and reads it from `_version.py` via
  hatchling's `[tool.hatch.version]`, so there's a single source of truth.
- `[tool.ruff.lint]` had no explicit `select`, so `ruff check .` picked up
  whatever ruff's bare default was for whatever version got installed — ruff
  0.16 started flagging import-sort (I001) issues that 0.15 (already installed
  locally) didn't, breaking the PR's first CI run. Pinned explicitly to the
  classic default (`E4`, `E7`, `E9`, `F`) so a future ruff upgrade can't change
  what's enforced out from under CI.

### Deprecated
- `custom_domains.activate()` — Firebase-only route, unreachable with an API key.
  Emits `DeprecationWarning`; will be removed in the next major version.

### Security
- `AwsysError.raw`/exception messages never include request headers (unchanged,
  reconfirmed by the contract-fixture suite).
- `Webhook.__repr__` redacts `.secret`.
- `base_url` is validated (must be `http(s)://`; non-`https` warns) before any
  request is made.
- API key is redacted in `repr(Client)`/`repr(AsyncClient)`/`repr(HttpClient)`/
  `repr(AsyncHttpClient)`.
- See `SECURITY-REVIEW.md` for the full dependency audit and finding list.

## [1.3.0] — 2026-07-19
Parity resources: `usage`, `web2app`, `imports` (Phase "parity").

## [1.1.0]
Phase 3 resources: `webhooks`, `saved_views`, `custom_domains`, `agentlink`, `affiliate`.

## [1.0.0]
Phase 2 resources: `tags`, `trust_score`, `data_export`, `namespace`, `utm_templates`.

## [0.1.0]
Initial release: `links`, `analytics`, `qr`, `folders`, `bulk`, `me`.
