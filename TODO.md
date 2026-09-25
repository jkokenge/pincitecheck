# TODO

Source of truth for build progress. Each task is sized to fit one short session.
The line marked `← CURRENT` is where to resume; everything above it is done,
everything below is pending.

When you sit down to work, type "Next step" and the current item gets surfaced
without you having to re-read this file.

---

## Phase 0 — Foundation

Repo, tooling, CI, and CourtListener access — everything that must exist before feature work.

**Deliverable:** Public GitHub repo with a green CI badge, a README stating purpose,
disclaimer, and attributions, and a working CourtListener token with known quota.

- [x] Create GitHub repo; `git init`; add `.gitignore` + `.editorconfig`
- [x] `uv init` — `pyproject.toml` (Python 3.12), src layout with `pincitecheck` package
- [x] Configure ruff + pytest in `pyproject.toml`; add one smoke test
- [x] pre-commit hooks: ruff, ruff-format, basic file checks, secret scanning
- [x] GitHub Actions CI: ruff + pytest on push and PR
- [x] Choose code license: Apache-2.0 (`LICENSE` + `pyproject.toml`); dataset license deferred to Phase 7
- [x] CourtListener account + API token; `.env.example`; token loaded from env, never committed
- [x] Script to call the usage endpoint; record actual quota in `docs/notes/courtlistener.md`
- [x] One manual citation-lookup call; record response shape and any per-endpoint limits
- [x] Estimate benchmark-scale call volume (see `docs/notes/courtlistener.md`); FLP membership not needed for limits
- [ ] README stub: purpose, not-legal-advice disclaimer, attributions (FLP/CourtListener, Charlotin CC BY), CI badge

---

## Phase 1 — Extraction

Turn a brief into structured citations, each paired with the proposition it supports.

**Deliverable:** Write-up (ADR 0001) comparing regex vs. eyecite extraction on 10 public
RECAP briefs, with precision/recall numbers.

- [ ] Select 10 public RECAP briefs; record source URLs in a manifest file  ← CURRENT
- [ ] pydantic models: `Citation` (raw text, volume, reporter, page, pincite, span, proposition)
- [ ] PDF text extraction (pdfplumber) + tests
- [ ] DOCX text extraction (python-docx) + tests
- [ ] eyecite extraction of full case citations
- [ ] Short-form resolution (Id., supra, short cites)
- [ ] Capture the proposition sentence for each citation
- [ ] Regex baseline extractor
- [ ] Hand-label ground-truth citations for briefs 1–5
- [ ] Hand-label ground-truth citations for briefs 6–10
- [ ] Comparison script: regex vs. eyecite precision/recall
- [ ] ADR 0001: eyecite vs. regex (Phase 1 showcase)

---

## Phase 2 — Tier 1: Existence

Check whether each cited case exists, within CourtListener's rate limits.

**Deliverable:** `pincitecheck brief.pdf` CLI flags nonexistent cases, with provenance on every result.

- [ ] CourtListener client: httpx, token auth, base URL, typed errors
- [ ] Backoff and retry with tenacity (including 429 handling)
- [ ] Quota awareness: local rate limiter + usage-endpoint check before large runs
- [ ] citation-lookup batching (≤250 citations per request)
- [ ] SQLite cache layer + tests
- [ ] Status mapping: found / not found / ambiguous / error; result model with provenance
- [ ] CLI: `pincitecheck brief.pdf` prints tier 1 results
- [ ] ADR 0002: caching strategy
- [ ] README section + sample output (Phase 2 showcase)

---

## Phase 3 — Tier 2: Accuracy

Check that quoted text appears at the cited pincite.

**Deliverable:** CLI flags wrong pincites and altered quotes, with evidence snippets and similarity scores.

- [ ] Verify CourtListener opinion text fields and page-marker format; record in notes
- [ ] Fetch + cache opinion text
- [ ] Pincite page locator
- [ ] Extract quoted text from the proposition
- [ ] Decide how tier 2 treats paraphrase vs. direct quotes (record the decision)
- [ ] rapidfuzz matching + similarity thresholds
- [ ] Evidence snippet and similarity score in the result model
- [ ] CLI shows tier 2 results
- [ ] Tests against known-good citations from the Phase 1 briefs

---

## Phase 4 — Benchmark v0 (Milestone 1)

First benchmark numbers on tiers 1–2: PinciteCheck on LePhantomCite, compared against the
paper's published LLM-agent baselines, plus a false-flag rate on clean briefs.

**Deliverable:** Reproducible result — "On LePhantomCite, deterministic checking catches X%
of nonexistent cites, wrong pincites, and misquotes vs. Y% for the best LLM agent, at $Z per
brief, with a W% false-flag rate on clean briefs" — plus a minimal HTML report.

- [ ] Read the LePhantomCite paper; record taxonomy, metrics, and reported baselines in `docs/notes/lephantomcite.md`
- [ ] Check LePhantomCite license + attribution terms; download the dataset
- [ ] Ground-truth file format for benchmark items
- [ ] LePhantomCite loader → PinciteCheck ground-truth format
- [ ] Quota estimate for the LePhantomCite run; stage it within daily limits
- [ ] Set A: select clean public briefs (false-flag baseline)
- [ ] Gap analysis: which error patterns LePhantomCite lacks; add a small Set B only for those
- [ ] Benchmark runner: precision, recall, false-flag rate, latency, cost per tier and per error type
- [ ] Comparison table vs. the paper's baselines (same subsets, same metrics)
- [ ] Minimal HTML report (citation, tier verdicts, evidence, links, disclaimer)
- [ ] Results write-up + README Milestone 1 section (content-misrepresentation items marked as tier 3, deferred to Phase 7)

---

## Phase 5 — Tool Surfaces (Milestone 2)

Make PinciteCheck callable by any service or agent.

**Deliverable:** FastAPI endpoint and MCP server running in Docker; demo clip of an agent calling `verify_citations`.

- [ ] FastAPI: `POST /verify` → verification report
- [ ] MCP server: `verify_citations` tool with clear schema and descriptions
- [ ] Dockerfile + local run instructions
- [ ] Test the MCP server from Claude Desktop; record a demo clip
- [ ] ADR 0003: MCP tool design

---

## Phase 6 — Tier 3: Support

Judge whether the cited passage supports the brief's proposition, and measure the judge.

**Deliverable:** Judge-vs-human agreement numbers and an accuracy/cost/latency comparison across 2+ models.

- [ ] Decide spend ceiling and cost guardrails (Open Decision) — record in CLAUDE.md
- [ ] Model-agnostic judge interface
- [ ] Judge prompt → structured JSON {supports | partially | does_not_support | unclear} + rationale
- [ ] Claude via Bedrock adapter
- [ ] Decide second provider (Open Decision); implement its adapter
- [ ] Decide on labeling credibility: attorney review of a subset, or a documented limitation
- [ ] Hand-label pairs 1–25
- [ ] Hand-label pairs 26–50
- [ ] Hand-label pairs 51–75
- [ ] Hand-label pairs 76–100
- [ ] Agreement metrics (judge vs. human)
- [ ] Model comparison: accuracy, cost, latency
- [ ] ADR 0004: LLM only for tier 3; ADR 0005: model selection

---

## Phase 7 — Benchmark v1 (Milestone 3)

Full benchmark across tiers and systems, published.

**Deliverable:** Published CiteBench sets, methodology, and results — including tier 3 on
LePhantomCite and the real-world set (GitHub, optionally Hugging Face).

- [ ] Tier 3 run on LePhantomCite content-misrepresentation items; compare with paper baselines
- [ ] Check Charlotin database for bulk export; confirm attribution requirements (CSV export exists; cite wording is in README — confirm both still hold)
- [ ] Set C: patterns modeled on Charlotin categories (real-world distribution — LePhantomCite's stated gap)
- [ ] Check each vendor's terms on publishing benchmarks; check StrongSuit API access
- [ ] Run raw general-purpose LLMs
- [ ] Collect legal AI tool outputs (manual exports only)
- [ ] Agent benchmark: agent with vs. without PinciteCheck + CourtListener MCP
- [ ] Share vendor results privately with vendors
- [ ] Choose CiteBench dataset license (likely CC BY 4.0 — must be compatible with Charlotin CC BY and LePhantomCite terms)
- [ ] Methodology doc
- [ ] Publish dataset + results (anonymized vendors by default)

---

## Phase 8 — AWS Reference Architecture

Deploy the pipeline with regulated-industry engineering: IaC, encryption, least privilege, audit.

**Deliverable:** Deployed, diagrammed AWS stack via Terraform, behind a Checkov-gated pipeline, with a teardown path.

- [ ] Decide API/MCP hosting (Open Decision) — record in CLAUDE.md
- [ ] Terraform skeleton + remote state; AWS budget alarm
- [ ] KMS keys + S3 buckets (SSE-KMS, no retention by default)
- [ ] Secrets Manager for the CourtListener token
- [ ] DynamoDB tables (cache, results, audit log); swap cache backend
- [ ] Lambda per stage + least-privilege IAM
- [ ] Step Functions + EventBridge wiring
- [ ] API/MCP hosting
- [ ] CloudWatch metrics: latency, cost per document, cache hit rate, quota usage
- [ ] CI: terraform validate/plan + Checkov gate + deploy
- [ ] Architecture diagram + teardown instructions

---

## Phase 9 — Attorney-Facing Report UX

**Deliverable:** Polished HTML report an attorney could use to review a brief.

- [ ] Report layout: per-citation tier verdicts, evidence snippets, source links
- [ ] "Needs human review" flags and legend
- [ ] Provenance and disclaimer sections
- [ ] Screenshot/demo for the README

---

## Phase 10 — Outreach & Role Packaging

Package the same project for different roles. Each role emphasizes a different facet:
AI/ML → evals; backend/platform → API and rate-limit design; cloud/security → the AWS
stack (the "cloud engineer who now builds AI systems" upgrade story); solutions/FDE →
demo and integration. A role's tasks can be done as soon as its source milestone lands —
no need to wait for Phase 10 to start applying.

**Deliverable:** For each role type: resume bullets, a tailored write-up or artifact, and a
talk track — plus company pitches, demo video, and blog post ready to send.

### Shared

- [ ] Upstream contribution to eyecite or a related FLP repo (do earlier if an opportunity arises)
- [ ] Core story: one paragraph (problem → approach → result) every pitch builds from
- [ ] README final pass: problem, architecture diagram, benchmark results, limitations
- [ ] Narrative link to the IaC Security Agent project
- [ ] Pin the repo on GitHub; add the project to LinkedIn
- [ ] 3–5 minute demo video + 60-second cut
- [ ] Blog post on methodology

### AI / ML engineer (source: Phases 4, 6, 7)

- [ ] Resume bullets: eval design, benchmark results, judge calibration
- [ ] Error analysis write-up: 10 failure cases, root cause for each
- [ ] Judge calibration write-up: judge-vs-human agreement (Cohen's kappa), cost/latency tradeoffs
- [ ] Talk track: "how I'd evaluate a legal AI product's citation accuracy"

### Backend / platform engineer (source: Phases 2, 5)

- [ ] Resume bullets: API design, caching, rate-limit-aware client
- [ ] API polish: OpenAPI docs, request/response examples, versioned endpoint
- [ ] Write-up: designing around a 250-requests/day upstream quota (caching, batching, backoff)
- [ ] Talk track: MCP tool design — schema choices and why

### Cloud / security engineer (source: Phase 8)

- [ ] Resume bullets: AI workloads on AWS, IaC, least privilege, policy-as-code gate
- [ ] Threat model for the AWS stack (data flows, trust boundaries, mitigations)
- [ ] Write-up: encryption, no-retention design, and audit trail for law-firm data
- [ ] Cost write-up: $ per document, budget alarms, teardown
- [ ] Talk track: running AI workloads in a regulated environment (Federal Reserve background)

### Solutions / forward-deployed engineer (source: Phases 5, 9)

- [ ] Resume bullets: customer-facing tooling, integrations, demos
- [ ] Integration guide: "add PinciteCheck to your agent in 10 minutes" (MCP config + API)
- [ ] Customer one-pager: walkthrough of the attorney report
- [ ] Talk track: mock discovery — map a target company's product to a PinciteCheck integration

### Company pitches

- [ ] One-page pitch: Harvey
- [ ] One-page pitch: StrongSuit
- [ ] One-page pitch: Free Law Project
- [ ] Research + pitch other target companies

---

## Phase 11 — Stretch

- [ ] Webhook-driven re-verification
- [ ] Negative-treatment detection via citation graph + LLM classification
