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
