# PinciteCheck

PinciteCheck is a vendor-neutral citation verification tool for legal AI — a Python library,
REST API, and MCP server that checks whether cited U.S. cases exist, whether quotes and
pincites are accurate, and whether the cited passage supports the brief's proposition.
It is evaluated on LePhantomCite (Princeton's public legal-hallucination benchmark) plus
CiteBench, its own reproducible sets of clean briefs and real-world-patterned cases, with
results compared across legal AI systems. It is a portfolio project aimed at legal AI companies (Harvey, StrongSuit,
Free Law Project), framed as verification assistance for attorneys — not legal advice.

## Constraints — Non-Negotiable

- No private or client data anywhere — code, tests, fixtures, benchmark sets, commits,
  or docs. Public documents only (e.g., CourtListener RECAP briefs). The demurrer that
  inspired the project may be described as a process only, never named or included.
- Not-legal-advice disclaimer in the README and in every generated report.
- CC BY 4.0 attribution for any Charlotin AI Hallucination Cases Database content.
- Respect CourtListener rate limits (default 5/min, 50/hour, 125/day, rolling) and terms
  of service. No scraping. All lookups go through the cache.
- No automation of vendor web apps. Vendor outputs come from manual exports only.
- Vendor benchmark results: check each vendor's terms before publishing, share results
  with the vendor privately first, and default to anonymized names ("Tool A/B") in public.
- No document retention by default (configurable) — mirrors law-firm data expectations.
- Every verification result carries provenance: source URL, retrieved text, timestamp,
  model/version, confidence.
- v1 scope is U.S. case law only. Out of scope: statutes, regulations, law journals,
  non-U.S. law, legal advice, outcome prediction. Good-law/overruled detection is
  stretch only.

## Architecture Decisions Already Made — Do Not Re-Litigate

- **Three verification tiers (existence → accuracy → support)** — separates hallucination
  (tiers 1–2 fail) from interpretive disagreement (tier 3 unclear), which is not a failure.
- **LLM only for tier 3** — tiers 1–2 are deterministic (plus fuzzy match), so they are
  cheap, reproducible, and auditable.
- **eyecite for extraction; regex kept as a baseline** — eyecite handles Id./supra and
  pincites; the regex comparison becomes an ADR and a benchmark data point.
- **Model-agnostic judge interface, tested on 2+ providers** — model selection is itself
  an eval result, and target companies may not share one provider.
- **Cache every CourtListener call (SQLite locally → DynamoDB on AWS)** — rate limits make
  benchmark-scale runs impossible otherwise.
- **Showable milestone at the end of every phase** — keeps focus and gives an employer-ready
  artifact at each stage instead of one big reveal.
- **LePhantomCite as the external evaluation set** — a public benchmark with the same error
  taxonomy already exists (Liu, Stammbach & Henderson, Princeton, 2026, arXiv 2606.21155).
  Independent numbers are more credible than self-built mutations, and it reports that
  LLM agents struggle on pincites and misquotes — exactly where deterministic tier 2 aims.
  CiteBench covers only what it lacks: clean briefs (false-flag rate) and real-world
  (Charlotin-style) patterns. Never claim CiteBench is the first legal citation benchmark.
- **Benchmark split into v0 (tiers 1–2) and v1 (full)** — real numbers exist before any
  hand-labeling; tier 3 results on LePhantomCite come in v1.
- **MCP server before tier 3 and AWS** — cheap once the core exists, and agent tool design
  is a core pitch angle.
- **AWS deployment after the benchmark** — Terraform wraps a stable pipeline rather than
  chasing a moving one.
- **GitHub (not GitLab) with GitHub Actions** — FLP/eyecite live there, the upstream PR
  lands there, and it's where reviewers look first.
- **Public repo from the first commit** — no private data is allowed anywhere, so nothing
  needs hiding, and a steady commit history is itself portfolio evidence.
- **uv for Python packaging, Python 3.12 floor** — one tool for interpreter, venv, deps,
  and lockfile; the lockfile makes benchmark runs reproducible. 3.10 is EOL Oct 2026.
- **Docker packaging** — target companies may not be AWS shops.
- **Names: GitHub repo `pincitecheck`, domain pincitecheck.com (Route 53); local directory
  stays `citecheck`** — the original "CiteCheck" name collides with LawDroid's CiteCheck AI.
  The mismatch with the local directory is intentional.

## Open Decisions

Deliberately unresolved. Decide when the listed phase forces it, then move the decision
(with its reason) into the section above.

| Decision | Forced by | Notes |
|---|---|---|
| Spend ceiling / cost guardrails (LLM + AWS) | Phase 6 | First paid LLM calls are the tier-3 judge. |
| Second LLM provider for the judge | Phase 6 | Claude via Bedrock is one; the model comparison informs the pick. |
| API/MCP hosting: API Gateway + Lambda vs. ECS/Fargate | Phase 8 | Depends on the finished pipeline's runtime shape. |

## Tech Stack

| Layer | Choice |
|---|---|
| Language / packaging | Python 3.12+, uv (`pyproject.toml` + `uv.lock`) |
| Lint / format / test | ruff, pytest, pre-commit |
| Citation extraction | eyecite (regex baseline for comparison) |
| Document text | python-docx, pdfplumber |
| Quote matching | rapidfuzz |
| HTTP client | httpx + tenacity (backoff) |
| Models / schemas | pydantic |
| Case law source | CourtListener REST API v4 (citation-lookup, search, opinions/clusters, usage) |
| Benchmark data | LePhantomCite (Hugging Face) + CiteBench sets |
| Local cache | SQLite |
| LLM judge | Model-agnostic interface; Claude via Bedrock + one other (TBD) |
| REST API | FastAPI |
| Agent interface | MCP Python SDK (`verify_citations` tool) |
| Packaging | Docker |
| CI | GitHub Actions: ruff, pytest (later: terraform validate/plan, Checkov gate, deploy) |
| Cloud (Phase 8) | Terraform; S3 (SSE-KMS) → EventBridge → Step Functions → Lambda; DynamoDB (cache, results, audit log); Secrets Manager; KMS; Bedrock; CloudWatch; least-privilege IAM per function |

## Build Phases

- **Phase 0** — Foundation ← Current phase.
- **Phase 1** — Extraction (docx/pdf, eyecite, proposition capture, regex baseline)
- **Phase 2** — Tier 1: Existence
- **Phase 3** — Tier 2: Accuracy
- **Phase 4** — Benchmark v0: LePhantomCite + clean briefs, tiers 1–2, minimal HTML report (Milestone 1)
- **Phase 5** — Tool surfaces: FastAPI + MCP server (Milestone 2)
- **Phase 6** — Tier 3: Support + judge evaluation
- **Phase 7** — Benchmark v1: tier 3 on LePhantomCite, CiteBench real-world set, system comparison, publication (Milestone 3)
- **Phase 8** — AWS reference architecture (Terraform)
- **Phase 9** — Attorney-facing report UX
- **Phase 10** — Outreach & role packaging: per-role materials (AI/ML, backend/platform, cloud/security, solutions/FDE), company pitches, demo video, blog post (eyecite PR opportunistically, any phase)
- **Phase 11** — Stretch: webhook re-verification, negative-treatment detection

## Working Preferences

- Push back when I'm wrong or about to make a costly mistake. Don't let me proceed on
  a bad decision without flagging it.
- Explain the *why* behind decisions, not just the what.
- Short, complete answers. One "Next step:" line at the end of every planned-work
  response.
- Don't answer if you don't have enough information — say so and ask.
- Ask clarifying questions one at a time, not in batches.
- Never use popups. Chat window only.
- When generating code, prefer explicit and readable over clever and terse.
