# CourtListener API — Notes

Working notes on CourtListener REST API v4 behavior, recorded from real calls.
Docs: https://wiki.free.law/c/courtlistener/help/api/rest/v4/overview

## Authentication

- Header: `Authorization: Token <token>`
- Token loaded from `COURTLISTENER_API_TOKEN` via `pincitecheck.config.get_settings()`.

## Usage endpoint

- `GET /api/rest/v4/api-usage/` — check with `uv run python scripts/courtlistener_usage.py`
- Has its own throttle (`api_usage` scope); per the docs, checking usage never counts
  against the limits it reports and works while other requests are throttled.
- All limits are rolling windows, and all throttles apply concurrently.

### Response shape

```json
{
  "current_usage": [
    {
      "scope": "user",
      "rate": "250/day",
      "used": 0,
      "limit": 250,
      "remaining": 250,
      "window_seconds": 86400,
      "reset_at": null,
      "blocked": false
    }
  ],
  "historical_usage": { "total": 0 },
  "membership": null
}
```

- `current_usage` — one entry per throttle; per the docs, the limit closest to being hit
  is listed first.
- `reset_at` — when the window's oldest request expires; `null` when nothing is used yet.
- `historical_usage` — daily request counts for the past 15 days (only `total` when unused).
- `membership` — `null` on a free account.

## Observed limits (free account, 2026-09-25)

| Scope | Per minute | Per hour | Per day | Applies to |
|---|---|---|---|---|
| `user` | 10 | 100 | 250 | General API requests |
| `citations` | 60 | — | — | Citation-lookup (to confirm in the citation-lookup task) |
| `fetch` | 30 | — | — | Not yet known |
| `api_usage` | 10 | 120 | — | The usage endpoint itself |

**These are double the documented defaults** (5/min, 50/hour, 125/day). `CLAUDE.md` uses
the observed numbers. Plan against the observed numbers but keep the rate limiter configurable,
and treat the documented defaults as the safe floor: limits can change per account and
over time, so a benchmark run should check the usage endpoint before starting rather
than trusting any hardcoded value.

## Open questions

- Does a citation-lookup request count against `user` as well as `citations`?
- What does the `fetch` scope cover?
- Do throttled (429) responses include a `Retry-After` header?
