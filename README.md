# PinciteCheck

[![CI](https://github.com/jkokenge/pincitecheck/actions/workflows/ci.yml/badge.svg)](https://github.com/jkokenge/pincitecheck/actions/workflows/ci.yml)

Citation verification for legal AI. PinciteCheck checks the U.S. case citations in a brief
and reports, with evidence, whether each one holds up:

1. **Existence** — does the cited case exist?
2. **Accuracy** — does the quoted text appear at the cited page (pincite)?
3. **Support** — does the cited passage support the proposition it's cited for?

Tiers 1 and 2 are deterministic and reproducible; only tier 3 uses an LLM. Every result
carries its provenance: source URL, retrieved text, timestamp, and confidence.

It's vendor-neutral and will ship as a Python library, a REST API, and an MCP server, so
any legal AI system or agent can call it. It's evaluated on
[LePhantomCite](https://arxiv.org/abs/2606.21155), a public legal-hallucination benchmark,
plus PinciteCheck's own eval sets — full-length clean briefs and real-world error patterns —
that cover what LePhantomCite doesn't.

> **Status:** early development (Phase 0: foundation). Not yet usable.

## Not legal advice

PinciteCheck is a verification aid for attorneys, not legal advice. It can miss errors and
can flag correct citations. Every result must be reviewed by a qualified attorney before
anything is filed with a court.

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```sh
uv sync
cp .env.example .env              # then add your CourtListener API token
uv run pre-commit install
uv run pytest
```

## Attributions

- **Case law data:** [CourtListener](https://www.courtlistener.com/), a project of
  [Free Law Project](https://free.law/). Used via its REST API within its rate limits and
  terms of service.
- **LePhantomCite:** Patty Liu, Dominik Stammbach & Peter Henderson, "Who Checks the
  Citations? Benchmarking Legal Hallucination Detection," 2026,
  [arXiv:2606.21155](https://arxiv.org/abs/2606.21155). Dataset:
  [ai-law-society-lab/Legal_Phantom_Citation](https://huggingface.co/datasets/ai-law-society-lab/Legal_Phantom_Citation),
  licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Its 300 LLM-generated
  holdings derive from [Dahl et al. (2024)](https://doi.org/10.1093/jla/laae003).
- **AI Hallucination Cases Database:** AI Hallucination Cases Database, Damien Charlotin,
  https://www.damiencharlotin.com/hallucinations/. Licensed
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## License

Code is licensed under [Apache-2.0](LICENSE). Benchmark datasets will carry their own
license, noted where they're published.
