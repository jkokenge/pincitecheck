"""Send text to CourtListener's citation-lookup API and print a per-citation summary.

Usage:
    uv run python scripts/citation_lookup.py "See Obergefell v. Hodges, 576 U.S. 644 (2015)."
    uv run python scripts/citation_lookup.py "..." --raw   # full JSON response

For manual exploration only — this bypasses the cache, so each run costs quota.
The pipeline's cached client comes in Phase 2.

Per-citation status codes (from the API docs):
    200 found   300 ambiguous (multiple cases)   400 invalid reporter
    404 not found   429 throttled (over 250 per request or 60 per minute)
"""

import argparse
import json
import sys

import httpx

from pincitecheck.config import get_settings

LOOKUP_URL = "https://www.courtlistener.com/api/rest/v4/citation-lookup/"


def print_summary(results: list[dict]) -> None:
    for result in results:
        print(f"{result['citation']!r}  status={result['status']}")
        print(f"  normalized: {result['normalized_citations']}")
        print(f"  span: {result['start_index']}-{result['end_index']}")
        if result["error_message"]:
            print(f"  error: {result['error_message']}")
        for cluster in result["clusters"]:
            print(f"  match: {cluster.get('case_name')} ({cluster.get('date_filed')})")
            print(f"         https://www.courtlistener.com{cluster.get('absolute_url')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("text", help="Text containing one or more case citations")
    parser.add_argument("--raw", action="store_true", help="Print the full JSON response")
    args = parser.parse_args()

    token = get_settings().courtlistener_api_token.get_secret_value()
    response = httpx.post(
        LOOKUP_URL,
        headers={"Authorization": f"Token {token}"},
        data={"text": args.text},
        timeout=60.0,
    )

    # Print status and body only — never the request headers, which contain the token.
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        return 1

    results = response.json()
    if args.raw:
        print(json.dumps(results, indent=2))
    else:
        print_summary(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
