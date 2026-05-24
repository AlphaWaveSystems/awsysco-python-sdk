# AWSYS.CO Python SDK — Implementation Report

**Date**: 2026-05-24  
**SDK Version**: 0.1.0  
**Test environment**: https://staging.awsys.co  
**Test result**: 26 / 26 passed

---

## Summary

The official Python SDK for the AWSYS.CO URL Shortener API has been implemented and all integration tests pass against the staging environment.

---

## Architecture

```
awsysco/
  __init__.py          # Public surface: Client + all exceptions + all models
  client.py            # Client class — owns .links, .analytics, .qr, .folders, .bulk, .me
  exceptions.py        # AwsysError hierarchy (7 typed exceptions)
  models.py            # Pydantic v2 models (9 types, camelCase alias support)
  _http.py             # httpx wrapper with 429 retry + error mapping
  resources/
    links.py           # /api/v1/links CRUD
    analytics.py       # /api/v1/links/:id/stats
    qr.py              # /api/qr/:short URL builder (no HTTP)
    folders.py         # /api/v1/folders + folder assignment
    bulk.py            # /api/v1/bulk
    me.py              # /api/v1/me
```

---

## Design Decisions

### Error handling
The AWSYS API returns `{ error: true, message: "...", code: "..." }` where `error` is a boolean, not a string. The `message` field carries the human-readable text. The HTTP client reads `message` first, falling back to `error` as a string if `message` is absent.

### Retry logic
429 responses are retried up to 3 times with exponential backoff (1s, 2s, 4s). The `Retry-After` header overrides the backoff delay when present. Retries are not applied to any other error status.

### Model validation
All response models use Pydantic v2 with `alias_generator = to_camel` and `populate_by_name=True`, so models accept both camelCase (from the API) and snake_case (for Python ergonomics). All fields are `Optional` to tolerate API evolution without breaking existing code.

### QR resource
The QR resource builds a URL string — it does not make any HTTP request. This is by design: the caller can embed the URL directly in an `<img>` tag or pass it to any image loader.

---

## Test Coverage

| Module | Tests | Notes |
|---|---|---|
| `test_links.py` | 7 | Create, list, get, update, delete, 404 after delete |
| `test_analytics.py` | 2 | Stats return, clicks list |
| `test_folders.py` | 5 | Create, list, assign, remove, delete |
| `test_bulk.py` | 3 | Count, results shape, short_url present |
| `test_me.py` | 3 | Response type, email, tier |
| `test_qr.py` | 6 | URL shape, params, defaults |
| **Total** | **26** | **26 passed, 0 failed** |

---

## Staging Infrastructure Note

During implementation, four API routes were missing from the staging Cloud Function (`staging.js`) that exist in the production function (`index.js`):

- `GET /api/v1/links/:shortPath` — get single link
- `DELETE /api/v1/links/:shortPath` — delete link
- `PATCH /api/v1/links/:shortPath` — update link
- `POST /api/v1/bulk` — bulk create

These were added to `staging.js` and deployed as part of this work. The staging function memory was also increased from 256 MiB to 512 MiB to accommodate the additional code.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `httpx` | >=0.27 | HTTP client with connection pooling |
| `pydantic` | >=2.0 | Response model validation |
| `python-dotenv` | dev | Load `.env.test` in tests |
| `pytest` | dev | Test runner |
| `pytest-cov` | dev | Coverage reports |
