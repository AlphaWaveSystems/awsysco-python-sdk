# Security Review — awsysco Python SDK

Review date: 2026-09-06. Scope: `awsys-orch`'s Phase 5 (contract-v1-parity) work on
this SDK, plus a pass over the pre-existing codebase surfaced along the way. Findings
are ordered by severity. See `SECURITY.md` for the repo's secret-hygiene policy
(pre-commit hook, gitleaks CI) — that is not repeated here.

## Dependency audit

`pip-audit` run against the exact installed versions:

```
Auditing httpx (0.28.1)
Auditing pydantic (2.13.5)
Auditing pydantic_core (2.46.5)
No known vulnerabilities found
```

`pyproject.toml` now pins `httpx>=0.27,<1` and `pydantic>=2,<3` (previously
unbounded above the major version).

## Findings

### Medium — API key was not redacted from `repr()`/logs (fixed)
Before this pass, `Client`/`AsyncClient`/`HttpClient`/`AsyncHttpClient` had no
custom `__repr__`; the default object repr didn't leak the key directly, but
nothing prevented a future change from doing so, and there was no way to safely
print client state for debugging. **Fixed**: all four now expose a redacted
`awsys_...last4` form via `__repr__`/`.redacted_key`, verified by
`tests/test_config.py::TestRedaction`.

### Medium — `base_url` accepted any string, no scheme validation (fixed)
Previously `base_url` was only `.rstrip("/")`'d — a caller (or anything deriving
config from an untrusted source) could point the client at any host or scheme
with no validation. **Fixed**: `resolve_base_url()` now rejects anything without
an `http://`/`https://` scheme (raises `AwsysConfigurationError`) and warns on
plain `http://`. Verified by `tests/test_config.py::TestBaseUrlResolution`.

### Low — Webhook signing secret was not redacted from model reprs (fixed)
`Webhook.secret` (the webhook's HMAC signing secret) was a plain model field with
no redaction — `print(webhook)`/`repr(webhook)`/an uncaught exception embedding the
model would leak it into logs. **Fixed**: `Webhook.__repr__` masks `secret` as
`<redacted>`. Verified by `tests/test_webhooks.py::test_repr_never_contains_raw_secret`.

### Low — stale, incorrect User-Agent version string (fixed)
Both transports hardcoded `User-Agent: awsysco-python-sdk/1.0.0` regardless of the
actual installed version (1.3.0 at the time, now 1.4.0) — not a vulnerability, but
a support/telemetry accuracy issue (the platform can't reliably tell which SDK
version is making a request from its own logs). **Fixed**: derived from
`awsysco.__version__`; a test (`test_pyproject_version_matches_dunder_version`)
prevents the two from drifting again.

### Informational — exception `.raw` retains the full response body
`AwsysError.raw` intentionally stores the parsed (or raw-text) response body for
debugging, and `__repr__` deliberately excludes it (unchanged, predates this pass).
A caller who explicitly does `print(exc.raw)` or logs it can still surface whatever
the platform put in the body. This is accepted as intentional (the contract
requires exposing the raw body for callers who need it) — confirmed the body never
contains the request's `Authorization` header (`tests/test_transport.py::TestParseErrorBodyShapes::test_raw_never_includes_request_headers`).

### Informational — TLS verification
No code path disables TLS certificate verification (`verify=False`) anywhere in
either transport; `httpx`'s default (verify on) is preserved. Confirmed by
inspection — no such option is exposed to callers either.

### Informational — retry policy and duplicate requests
Per the platform contract, the API has no idempotency keys. The retry policy
(this pass) restricts 5xx/transport-error retries to idempotent methods
(`GET`/`PUT`/`DELETE`) specifically to avoid a retried `POST`/`PATCH` silently
creating a duplicate resource (e.g. two links from one `links.create()` call
during a flaky connection). `429` is retried for all methods since it indicates
the original request was already rejected before any side effect occurred.

## Out of scope / carried forward, not addressed this pass
- Native `datetime` exposure for timestamp fields (currently normalized to
  ISO-8601 `str`) — deferred to 2.0 per `awsys-orch` ADR-017, to avoid a breaking
  type change in a minor release.
- Request-ID / distributed tracing support — the platform doesn't emit a request ID
  today (per the capability catalog), so there's nothing for the SDK to surface.
