"""Print your CourtListener API usage and limits as JSON.

Usage:
    uv run python scripts/courtlistener_usage.py

Calls GET /api/rest/v4/api-usage/. Per CourtListener's docs, this endpoint has its own
throttle: checking usage never counts against the limits it reports, and it works even
while other requests are being throttled. Safe to run before and during benchmark runs.
"""

import json
import sys

import httpx

from pincitecheck.config import get_settings

USAGE_URL = "https://www.courtlistener.com/api/rest/v4/api-usage/"


def main() -> int:
    token = get_settings().courtlistener_api_token.get_secret_value()

    response = httpx.get(
        USAGE_URL,
        headers={"Authorization": f"Token {token}"},
        timeout=30.0,
    )

    if response.status_code != 200:
        # Print status and body only — never the request headers, which contain the token.
        print(f"Error: HTTP {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        return 1

    print(json.dumps(response.json(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
