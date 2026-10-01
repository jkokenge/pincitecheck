"""Check a hand-labeled citation file for format errors and missed citations.

Usage:
    uv run python scripts/check_labels.py b02

Runs two kinds of checks on data/labels/<id>.psv (rules in data/labels/README.md):

1. Structure: 13 fields per row, sequential cite_no, no unfilled ## placeholders, valid
   form / in_footnote values, pdf_page within the brief's body pages, full cites have
   volume/reporter/page, and every short / id / supra row's refers_to points to an earlier
   full citation (short cites must also match its volume and reporter).
2. Search pass: scans the PDF's body pages for reporter citations ("517 F.2d 188",
   "517 F.2d at 192"), Id., and supra, and flags any page where the PDF has more than
   the sheet does. Flags are prompts to look, not verdicts: an Id. pointing to the
   complaint or a supra pointing to the brief's own footnotes is correctly unlabeled.

Run it only after finishing a brief by hand. Run earlier, its flags become a list of
citations to copy, and the labels stop being independent of a regex.

This is a quality check on the labels, not a citation extractor; its regex is
deliberately loose and is not the Phase 1 regex baseline.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import pdfplumber
import yaml

MANIFEST = Path("data/manifest/phase1_briefs.yaml")
LABELS_DIR = Path("data/labels")
PDF_DIR = Path("data/raw/phase1")

EXPECTED_FIELDS = 13
FORMS = {"full", "short", "id", "supra"}

# The court's filing stamp at the top of each page ("Case 1:26-cv-... Document 49 Filed ...").
HEADER_STAMP = re.compile(r"^\s*(USCA\d+ Case|Case)\b.*(Document|Filed).*$", re.MULTILINE)

# Reporters seen in the Phase 1 briefs. "U.S." must not match "U.S.C." (statutes).
REPORTER = (
    r"(So\.\s?\dd|F\.\s?Supp\.\s?\dd|F\.\s?Supp\.|F\.\dd|F\.4th|U\.S\.(?!C)|S\.\s?Ct\."
    r"|L\.\s?Ed\.\s?\dd|B\.R\.|F\.R\.D\.|WL|Cal\.\s?App\.\s?\d\w*|Cal\.\s?Rptr\.\s?\dd"
    r"|Cal\.\s?\d\w*|N\.Y\.\dd|N\.Y\.S\.\dd|A\.D\.\dd|S\.W\.\dd|N\.E\.\dd|P\.\dd|A\.\dd)"
)
# Volume, reporter, then a first page or "at <pincite>". Whitespace may be a line break.
REPORTER_CITE = re.compile(rf"\b(\d{{1,4}})\s+{REPORTER}\s+(?:at\s+)?[\d*]")
ID_CITE = re.compile(r"\b[Ii]d\.(?=[\s,]|$)")
SUPRA = re.compile(r"\bsupra\b")


def squash(text: str) -> str:
    """Remove all whitespace, so "So. 2d" and "So.2d" compare equal."""
    return re.sub(r"\s+", "", text)


def load_body_pages(brief_id: str) -> tuple[int, int]:
    briefs = yaml.safe_load(MANIFEST.read_text())["briefs"]
    brief = next(b for b in briefs if b["id"] == brief_id)
    first, last = brief["body_pages"].split("-")
    return int(first), int(last)


def load_rows(brief_id: str) -> tuple[list[dict], list[str]]:
    """Read the label file. Rows with the wrong field count are reported, not loaded."""
    lines = (LABELS_DIR / f"{brief_id}.psv").read_text().splitlines()
    header = lines[0].split("|")
    rows, problems = [], []
    for line_number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        fields = line.split("|")
        if len(fields) != EXPECTED_FIELDS:
            problems.append(
                f"line {line_number}: {len(fields)} fields, expected {EXPECTED_FIELDS}: {line[:70]}"
            )
            continue
        row = dict(zip(header, fields, strict=True))
        row["_line"] = line_number
        rows.append(row)
    return rows, problems


def check_structure(rows: list[dict], first_page: int, last_page: int) -> list[str]:
    problems = []
    rows_by_cite_no = {}
    for expected_cite_no, row in enumerate(rows, start=1):
        where = f"line {row['_line']} (cite {row['cite_no']})"
        rows_by_cite_no[row["cite_no"]] = row

        if any("##" in str(value) for value in row.values()):
            problems.append(f"{where}: unfilled ## placeholder")
        if row["cite_no"] != str(expected_cite_no):
            problems.append(f"{where}: cite_no out of sequence, expected {expected_cite_no}")
        if row["form"] not in FORMS:
            problems.append(f"{where}: form {row['form']!r} is not one of {sorted(FORMS)}")
        if row["in_footnote"] not in {"y", "n"}:
            problems.append(f"{where}: in_footnote must be y or n")
        page = row["pdf_page"]
        if not page.isdigit() or not first_page <= int(page) <= last_page:
            problems.append(f"{where}: pdf_page {page} is outside body {first_page}-{last_page}")
        if row["raw_text"] != row["raw_text"].strip() or "  " in row["raw_text"]:
            problems.append(f"{where}: extra whitespace in raw_text")

        if row["form"] == "full":
            problems.extend(check_full_row(row, where))
        else:
            problems.extend(check_reference_row(row, where, rows_by_cite_no))
    return problems


def check_full_row(row: dict, where: str) -> list[str]:
    problems = []
    is_docket_cite = "docket cite" in row["notes"]
    for field in ("case_name", "volume", "reporter", "page"):
        if not row[field] and not (is_docket_cite and field != "case_name"):
            problems.append(f"{where}: full cite is missing {field}")
    if row["refers_to"]:
        problems.append(f"{where}: full cite should have an empty refers_to")
    return problems


def check_reference_row(row: dict, where: str, rows_by_cite_no: dict) -> list[str]:
    """Short, id, and supra rows must point back to an earlier full citation."""
    target = rows_by_cite_no.get(row["refers_to"])
    if target is None or target is row:
        return [f"{where}: refers_to {row['refers_to']!r} is not an earlier cite_no"]
    if target["form"] != "full":
        return [f"{where}: refers_to {row['refers_to']} is a {target['form']} row, not full"]
    if row["form"] == "short" and (
        row["volume"] != target["volume"] or squash(row["reporter"]) != squash(target["reporter"])
    ):
        return [
            f"{where}: {row['volume']} {row['reporter']} doesn't match refers_to "
            f"{target['cite_no']} ({target['volume']} {target['reporter']})"
        ]
    return []


def read_body_text(brief_id: str, first_page: int, last_page: int) -> dict[int, str]:
    pages = {}
    with pdfplumber.open(PDF_DIR / f"{brief_id}.pdf") as pdf:
        for page_number in range(first_page, last_page + 1):
            text = pdf.pages[page_number - 1].extract_text() or ""
            pages[page_number] = HEADER_STAMP.sub("", text)
    return pages


def search_pass(rows: list[dict], pages: dict[int, str]) -> list[str]:
    flags = []
    for page_number, text in pages.items():
        rows_on_page = [r for r in rows if r["pdf_page"] == str(page_number)]
        flags.extend(compare_reporter_cites(page_number, text, rows, rows_on_page))
        flags.extend(compare_counts(page_number, text, ID_CITE, "Id.", "id", rows_on_page))
        flags.extend(compare_counts(page_number, text, SUPRA, "supra", "supra", rows_on_page))
    return flags


def compare_reporter_cites(
    page_number: int, text: str, rows: list[dict], rows_on_page: list[dict]
) -> list[str]:
    """Flag volume+reporter pairs that appear more often in the PDF than in the sheet.

    Rows on the neighboring pages also count, because a citation split across a page
    break is labeled on the page where it starts.
    """
    in_pdf = Counter(
        (match.group(1), squash(match.group(2))) for match in REPORTER_CITE.finditer(text)
    )
    in_sheet = Counter((r["volume"], squash(r["reporter"])) for r in rows_on_page if r["volume"])
    flags = []
    for (volume, reporter), pdf_count in in_pdf.items():
        if pdf_count <= in_sheet[(volume, reporter)]:
            continue
        nearby_count = sum(
            1
            for r in rows
            if abs(int(r["pdf_page"]) - page_number) <= 1
            and (r["volume"], squash(r["reporter"])) == (volume, reporter)
        )
        if nearby_count < pdf_count:
            flags.append(
                f"p.{page_number} {volume} {reporter}: {pdf_count} in PDF, "
                f"{in_sheet[(volume, reporter)]} in sheet"
            )
    return flags


def compare_counts(
    page_number: int,
    text: str,
    pattern: re.Pattern,
    label: str,
    form: str,
    rows_on_page: list[dict],
) -> list[str]:
    """Flag a page where the PDF has more Id. / supra than the sheet, with context."""
    matches = list(pattern.finditer(text))
    row_count = sum(1 for r in rows_on_page if r["form"] == form)
    if len(matches) <= row_count:
        return []
    contexts = " | ".join(repr(text[max(0, m.start() - 40) : m.end() + 25]) for m in matches)
    return [f"p.{page_number} {label}: {len(matches)} in PDF, {row_count} in sheet -> {contexts}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("brief_id", help="Brief id from the manifest, e.g. b02")
    args = parser.parse_args()

    first_page, last_page = load_body_pages(args.brief_id)
    rows, problems = load_rows(args.brief_id)
    problems += check_structure(rows, first_page, last_page)
    flags = search_pass(rows, read_body_text(args.brief_id, first_page, last_page))

    print(f"{args.brief_id}: {len(rows)} rows, body pages {first_page}-{last_page}")
    print(f"\nStructural problems: {len(problems)}")
    for problem in problems:
        print(f"  {problem}")
    print(f"\nSearch-pass flags (check each in the PDF): {len(flags)}")
    for flag in flags:
        print(f"  {flag}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
