"""Download the briefs listed in a manifest and verify each one's sha256.

Usage:
    uv run python scripts/fetch_briefs.py                     # Phase 1 manifest
    uv run python scripts/fetch_briefs.py --manifest data/manifest/other.yaml --out data/raw/other

Files are saved as <out>/<id>.pdf (e.g. data/raw/phase1/b01.pdf). data/raw/ is gitignored:
the briefs' authors hold copyright, so the repo records where to get them, not the files.

Safe to re-run. A file already on disk with the right hash is skipped. A file with the
wrong hash is downloaded again; if the fresh copy still doesn't match, it's kept as
<id>.pdf.mismatch for inspection and the script exits non-zero.

Downloads come from storage.courtlistener.com (static files), not the REST API, so they
don't count against API quota and need no token. Still paced politely.
"""

import argparse
import hashlib
import sys
import time
from pathlib import Path

import httpx
import yaml

DEFAULT_MANIFEST = Path("data/manifest/phase1_briefs.yaml")
DEFAULT_OUT_DIR = Path("data/raw/phase1")
USER_AGENT = "PinciteCheck (https://github.com/jkokenge/pincitecheck)"
SECONDS_BETWEEN_DOWNLOADS = 3


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url: str, destination: Path) -> None:
    """Download to a temporary .part file, then rename, so a crash never leaves a half file."""
    partial = destination.with_suffix(destination.suffix + ".part")
    response = httpx.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=120.0, follow_redirects=True
    )
    response.raise_for_status()
    partial.write_bytes(response.content)
    partial.replace(destination)


def fetch_brief(brief: dict, out_dir: Path) -> bool:
    """Make sure one brief is on disk with the expected hash. Returns True if it is."""
    brief_id = brief["id"]
    expected = brief["sha256"]
    destination = out_dir / f"{brief_id}.pdf"

    if destination.exists() and sha256_of(destination) == expected:
        print(f"{brief_id}  ok (already present)")
        return True

    download(brief["pdf_url"], destination)
    time.sleep(SECONDS_BETWEEN_DOWNLOADS)

    if sha256_of(destination) == expected:
        print(f"{brief_id}  ok (downloaded)")
        return True

    mismatch = destination.with_suffix(".pdf.mismatch")
    destination.replace(mismatch)
    print(f"{brief_id}  HASH MISMATCH, saved as {mismatch}", file=sys.stderr)
    print(f"     expected {expected}", file=sys.stderr)
    print(f"     got      {sha256_of(mismatch)}", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    briefs = yaml.safe_load(args.manifest.read_text())["briefs"]
    args.out.mkdir(parents=True, exist_ok=True)

    failures = []
    for brief in briefs:
        try:
            if not fetch_brief(brief, args.out):
                failures.append(brief["id"])
        except httpx.HTTPError as error:
            print(f"{brief['id']}  DOWNLOAD FAILED: {error}", file=sys.stderr)
            failures.append(brief["id"])

    print(f"\n{len(briefs) - len(failures)}/{len(briefs)} briefs verified in {args.out}")
    if failures:
        print(f"Failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
