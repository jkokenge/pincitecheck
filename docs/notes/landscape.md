# Landscape — Related Tools, Models, and Benchmarks

What already exists near PinciteCheck, so pitches, talks, and design decisions start from
the same facts. Checked 2026-10-29 — re-check before any talk or publication; this space
moves fast.

## Positioning

Existence checking is solved and free (Free Law Project's Citation Lookup API) and several
open-source tools wrap it. The open problem is **accuracy**. LePhantomCite's best agent
(GPT-5) catches 95.2% of misquotes but only 52.8% of wrong pincites. The paper blames the
pincite gap mainly on access to sources, not on reasoning: many CourtListener opinions lack
page markers, and ~10% of real citations are Westlaw/Lexis cites CourtListener can't
resolve. A CourtListener-based tier 2 shares that ceiling. PinciteCheck's distinct
contribution is deterministic tier 2 (pincite + quote accuracy), which is cheaper,
reproducible, and auditable given the same source text; an LLM only for tier 3; and public
benchmark numbers. Anthropic's cite check (see Commercial) publishes no accuracy numbers.

Framing: "built on CourtListener, a Free Law Project service" — never imply FLP
endorsement or partnership.

## Open-source tools

| Project | What it does | Overlap |
|---|---|---|
| [FLP Citation Lookup API](https://free.law/2024/04/16/citation-lookup-api/) (Apr 2024) | Free Law Project's hallucination guardrail: extracts citations from text (eyecite) and matches them to CourtListener opinions | Tier 1 is built on it |
| [CiteSight](https://github.com/JaySmith502/CiteSight) | Self-hosted web app: PDF extraction, existence validation via CourtListener, traffic-light status, PDF report | Tier 1 + report |
| [courtlistener_citations_mcp](https://github.com/john-walkoe/courtlistener_citations_mcp) | MCP server: validates citations against CourtListener; flags hallucinated citations, name mismatches, ambiguous reporters | Tier 1 **and the Phase 5 MCP server** — ADR 0003 must differentiate |
| [legal-hallucination-agent](https://github.com/nwyin/legal-hallucination-agent) | LLM agent verifying citations, quotes, and holdings via web search + CourtListener (fork of the paper's code) | All tiers, fully LLM-driven — the approach PinciteCheck contrasts with |
| [princeton-polaris-lab/legal-hallucination-agent](https://github.com/princeton-polaris-lab/legal-hallucination-agent) | The LePhantomCite paper's official agent code | Source of the paper's baselines |

## Models

| Model | What it does | Notes |
|---|---|---|
| [vrushket/legalcite-support-base](https://huggingface.co/vrushket/legalcite-support-base) | DeBERTa-v3-base classifier: does cited text support / contradict / not verify a proposition. Apache-2.0 | Tier 3 task. Candidate Phase 6 baseline. Self-reported 49.1% on LegalCiteBench's resolved subset (n=57). Its model card wrongly says LePhantomCite has no public download. |

## Benchmarks

| Benchmark | Scope | Relation |
|---|---|---|
| LePhantomCite — Liu, Stammbach & Henderson, "Who Checks the Citations?", [arXiv 2606.21155](https://arxiv.org/abs/2606.21155); [dataset](https://huggingface.co/datasets/ai-law-society-lab/Legal_Phantom_Citation) | Hallucination detection in brief excerpts; 5 error types | PinciteCheck's external eval set |
| LegalCiteBench — [arXiv 2605.10186](https://arxiv.org/abs/2605.10186) (ICML 2026 workshop) | ~24K closed-book citation tasks (retrieval, completion, error detection, case matching) | Related work: shows LLMs can't recall citations from memory. Name collision is why the eval sets are unbranded. |
| LegalPincite — [paper](https://pith.science/paper/2608.03756) | Paragraph-level legal retrieval (pincite finding) | Adjacent retrieval task, not verification |
| [Dahl et al. (2024)](https://doi.org/10.1093/jla/laae003) | LLM legal hallucination rates | Source of LePhantomCite's 300 LLM-generated entries |

## Commercial

| Product | Notes |
|---|---|
| [LawDroid CiteCheck AI](https://www.lawnext.com/2025/06/lawdroid-launches-citecheck-ai-a-fail-safe-against-ai-citation-hallucinations.html) (Jun 2025) | Citation-hallucination checker; its name is why this project isn't called CiteCheck |
| [Claude for Legal — Cite check](https://claude.com/resources/articles/introducing-artifacts-for-legal-work) (Oct 2026) | Anthropic-built artifact. It compares a document with sources the user uploads or connects, and flags mismatched quotes, wrong page numbers, and claims the sources don't support. Claude does the first pass. No accuracy numbers published, and no existence check described. Users bring paginated sources, which avoids the pincite gap. Tiers 2–3: the most direct competitor |
| Westlaw, Lexis | Hold pagination (star paging) that free sources often lack — the root of the pincite gap |

## Real-world tracking

- [AI Hallucination Cases Database](https://www.damiencharlotin.com/hallucinations/) — Damien Charlotin, CC BY 4.0, CSV export.
- [Ropes & Gray AI court order tracker](https://www.ropesgray.com/en/sites/artificial-intelligence-court-order-tracker) — cited by the LePhantomCite paper.
