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
| `citations` | 60 | — | — | Citations sent to citation-lookup (counted per citation) |
| `fetch` | 30 | — | — | Not yet known |
| `api_usage` | 10 | 120 | — | The usage endpoint itself |

**These are double the documented defaults** (5/min, 50/hour, 125/day). `CLAUDE.md` uses
the observed numbers. Plan against the observed numbers but keep the rate limiter configurable,
and treat the documented defaults as the safe floor: limits can change per account and
over time, so a benchmark run should check the usage endpoint before starting rather
than trusting any hardcoded value.

## Citation lookup

Docs: https://wiki.free.law/c/courtlistener/help/api/rest/v4/citation-lookup
Manual probe: `uv run python scripts/citation_lookup.py "<text>" [--raw]` (uncached; costs quota)

- `POST /api/rest/v4/citation-lookup/`, form field `text` (≤ 64,000 characters), or
  `volume` + `reporter` + `page` for a single citation.
- ≤ 250 citations looked up per request; any beyond that come back with status 429.
- Throttled responses are HTTP 429 with a JSON `wait_until` (ISO-8601) key.

### Response shape

A JSON list, one object per citation the server's parser found:

```json
{
  "citation": "925 F.3d 1339",
  "normalized_citations": ["925 F.3d 1339"],
  "start_index": 139,
  "end_index": 152,
  "status": 404,
  "error_message": "Citation not found: '925 F.3d 1339'",
  "clusters": []
}
```

- `status` — 200 found, 300 ambiguous (multiple clusters), 400 invalid reporter,
  404 not found, 429 throttled.
- `start_index` / `end_index` — character span of the citation in the submitted text.
  The span covers volume–reporter–page only; the pincite (", 681") is not included.
- `clusters` — full case records (~45 fields each: `case_name`, `date_filed`,
  `absolute_url`, `citations`, `sub_opinions`, `precedential_status`, ...).
  `sub_opinions` holds the opinion URLs tier 2 needs to fetch text.

### Observed behavior (2026-09-25)

Test text: Obergefell (576 U.S. 644), Brown (347 U.S. 483), *Varghese v. China Southern
Airlines* (925 F.3d 1339 — a fabricated case from *Mata v. Avianca*), and an invented
reporter ("12 Xyz. 34").

- Obergefell, Brown → 200, one cluster each.
- Varghese → 404 "Citation not found". Tier 1 catches the canonical hallucination.
- **The invented reporter was silently dropped** — no result at all, not a 400. The
  server returns only what its own parser recognizes, so tier 1 must reconcile against
  our eyecite extraction: a citation we extracted with no matching result needs its own
  status, not an implicit pass.
- **Quota accounting:** each request counts **1** against the `user` limits (10/min,
  100/hour, 250/day), and each citation in it counts 1 against `citations` (60/min).
  Two requests with 3 citations each → `user` 2, `citations` 6.

**Implication for the benchmark:** the daily `user` cap is not the bottleneck, because
one request carries up to 250 citations. The binding limit is 60 citations/minute —
~4,500 LePhantomCite citations is about 75 minutes of lookups, as ~18 requests.
Tier 2 opinion fetches are separate requests and will hit the daily cap first.

## Open questions

- What does the `fetch` scope cover? (Possibly opinion/document fetches — check in Phase 3.)
- Do throttled (429) responses include a `Retry-After` header, or only `wait_until`?

## Benchmark call-volume estimate (2026-09-25)

LePhantomCite (Liu, Stammbach & Henderson, arXiv 2606.21155), from the paper:

- 1,300 entries: 1,000 appellate-brief excerpts (245 federal briefs, 2012–2021, via
  CourtListener) + 300 LLM-generated holdings (from Dahl et al. 2024).
- 4,499 citation instances, 1,107 hallucinated. Median 2, max 18 citations per entry.
- 70/30 train/test split → 390 test entries (~1,350 citations, assuming even spread).
- The dataset ships brief context only — **not** the text of cited opinions.

| Run | Tier 1 (citation-lookup) | Tier 2 (opinion fetches) |
|---|---|---|
| Test split (~1,350 cites) | ~6 requests, ~23 min | ≤ ~1,350 fetches → ~6 days at 250/day |
| Full set (4,499 cites) | ~18 requests, ~75 min | ≤ ~4,500 fetches → ~18 days at 250/day |

Tier 2 figures are upper bounds. Real volume is lower because:

- Only citations that tier 1 found (200) *and* that carry a pincite or quote need a fetch.
- Fetches are per **unique** opinion, and briefs cite the same cases repeatedly
  (pleading standards, standards of review). Unique count is unknown until the loader runs.
- The cache makes this a one-time cost: reruns and code changes cost zero quota.

Unknowns: whether an opinion fetch counts against `user`, `fetch` (30/min), or both, and
whether a case with several sub-opinions (majority, dissent) needs several fetches.

### Decision: FLP membership is not needed

- Tier 1 fits in one afternoon on the free tier, even for the full set.
- Tier 2 on the test split is a ~week of staged, cached runs — acceptable.
- If the full set's tier 2 is needed, better options than paying for an unconfirmed
  limit increase: (1) FLP's free bulk data exports, loaded into the cache — sanctioned,
  not scraping; (2) asking FLP directly about research access for a public benchmark.
- Membership may still be worth it as support for a free API this project depends on —
  a goodwill choice, not a quota one.
