# API Documentation

Reference and conceptual notes for the FastAPI backend that complements the auto-generated Swagger UI.

## What goes here

- Endpoint reference with examples and edge cases (beyond Swagger).
- Authentication notes (currently none — to be added when introduced).
- Rate-limit guidance for upstream providers (yfinance, CoinGecko).
- Versioning policy.
- Changelog entries scoped to API contract changes.

## Live Swagger / OpenAPI

Once the backend is running:

| Resource | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

## Naming convention

- Endpoint references: `endpoint-<name>.md` (e.g., `endpoint-analyze.md`).
- Cross-cutting topics: `<topic>.md` (e.g., `error-handling.md`).

## See also

- `../../src/api/main.py` — route definitions.
- `../../src/api/models.py` — Pydantic request/response models.
- `../../CLAUDE.md` — Common Commands section for `curl` examples.
