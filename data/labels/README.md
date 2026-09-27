# Phase 1 ground-truth labels

Hand-labeled case citations for the 10 briefs in `data/manifest/phase1_briefs.yaml`.
These are the answer key the regex and eyecite extractors are scored against (ADR 0001).

One pipe-delimited file per brief: `b01.psv` … `b10.psv`. One row per citation, in reading
order. Pipes, not commas, because citations are full of commas and never contain pipes, so
no quoting is needed.

Edit in VS Code (the Rainbow CSV extension colors columns and detects `|`). Excel and Numbers
need an import step: File → Import, delimiter `|`. Export back as pipe-delimited text.

## Columns

| Column | What to enter | Example |
|---|---|---|
| `cite_no` | 1, 2, 3 … in reading order within the brief | `4` |
| `pdf_page` | PDF page number (the viewer's page, not the printed page number) | `12` |
| `raw_text` | The citation exactly as printed, from case name through closing parenthetical | `Twombly, 550 U.S. at 555 n.3` |
| `form` | `full`, `short`, `id`, or `supra` (see below) | `short` |
| `case_name` | Case name as printed (blank for `id`) | `Twombly` |
| `volume` | Reporter volume (blank for `id` / `supra`) | `550` |
| `reporter` | Reporter as printed | `U.S.` |
| `page` | First page of the case (blank for short forms) | `544` |
| `pincite` | Pinpoint page(s) as printed, including ranges and footnotes | `555 n.3` |
| `paren` | Court/year parenthetical, without the parentheses | `2d Cir. 2016` |
| `refers_to` | For `short` / `id` / `supra`: the `cite_no` of the full citation it points to | `2` |
| `in_footnote` | `y` if the citation is in a footnote, else `n` | `n` |
| `notes` | Anything odd: line break mid-cite, OCR glitch, unsure | `split across pages` |

## Forms

- **full** — case name, volume, reporter, first page: `Bell Atl. Corp. v. Twombly, 550 U.S. 544, 570 (2007)`
- **short** — shortened reference to an earlier full cite: `Iqbal, 556 U.S. at 678`
- **id** — `Id.` or `id.` pointing to the immediately preceding **case** citation: `Id. at 679`
- **supra** — `Twombly, supra, at 556`

## What counts — and what doesn't

Label **case citations in the body and footnotes only**.

**Body** means the introduction or preliminary statement, statement of facts, legal
standard, argument, and conclusion, plus their footnotes. Skip everything else:

- Front matter: cover page and caption, table of contents, **table of authorities**, and
  appellate extras (corporate disclosure, statement on oral argument, statement of related
  cases, certificate of interested persons).
- Back matter: signature block, certificates of compliance and of service, appendices,
  exhibits, proposed orders.
- Every page: the court's header stamp (`Case 1:26-cv-04645 Document 49 Filed … Page 11 of 34`),
  page numbers, and pleading-paper line numbers.

The table of authorities is skipped while labeling but is useful afterwards as a checklist:
every case it lists should appear in your sheet as at least one `full` row. Not every
brief has one.

Because the labels exclude front and back matter, the extractor must skip those sections
too, or it will be scored on citations that aren't in the answer key.

Label:
- Every citation to a court decision, including Westlaw (`2024 WL 123456`) and Lexis cites.
- Each reporter in a parallel cite as its own row, with the same `paren`:
  `556 U.S. 662, 129 S. Ct. 1937 (2009)` → two rows. (This matches how eyecite reports them.)
- Citations inside quotations and parentheticals (`(quoting Iqbal, 556 U.S. at 678)`).
- Every citation in a string cite, one row each.

Do **not** label:
- **The table of authorities.** It duplicates the body and would double-count.
- **`Id.` that points to a non-case** — the complaint, a declaration, a statute, the
  record. On page 11 of b04, `Id. ¶ 29` refers to the complaint: skip it.
- Statutes, regulations, rules, constitutions (`42 U.S.C. § 1981`, `Fed. R. Civ. P. 12`).
- Record and docket cites (`Compl. ¶ 45`, `ECF No. 12 at 5`, `A-001`).
- The brief's own caption and case number.
- Secondary sources (treatises, law reviews, Restatements).

When unsure, label it and say why in `notes`. Deciding later is easier than finding it again.

## Worked example (b04, PDF page 12)

The text:

> …plaintiff to proceed.” Doe v. Columbia Univ., 831 F.3d 46, 59 (2d Cir. 2016). To survive
> a motion to dismiss, a complaint must allege sufficient facts to state a claim for relief
> “that is plausible on its face.” Bell Atl. Corp. v. Twombly, 550 U.S. 544, 570 (2007). …
> Ashcroft v. Iqbal, 556 U.S. 662, 678 (2009). … Twombly, 550 U.S. at 555 n.3. … Iqbal,
> 556 U.S. at 678.

The rows (numbering starts at 1 here only for the example):

```
cite_no|pdf_page|raw_text|form|case_name|volume|reporter|page|pincite|paren|refers_to|in_footnote|notes
1|12|Doe v. Columbia Univ., 831 F.3d 46, 59 (2d Cir. 2016)|full|Doe v. Columbia Univ.|831|F.3d|46|59|2d Cir. 2016||n|
2|12|Bell Atl. Corp. v. Twombly, 550 U.S. 544, 570 (2007)|full|Bell Atl. Corp. v. Twombly|550|U.S.|544|570|2007||n|
3|12|Ashcroft v. Iqbal, 556 U.S. 662, 678 (2009)|full|Ashcroft v. Iqbal|556|U.S.|662|678|2009||n|
4|12|Twombly, 550 U.S. at 555 n.3|short|Twombly|550|U.S.||555 n.3||2|n|
5|12|Iqbal, 556 U.S. at 678|short|Iqbal|556|U.S.||678||3|n|
```

Every row has 13 fields, so 12 pipes, including trailing empty fields. Leave empty
fields empty; don't write `none` or `-`. Don't quote anything: a `"` is kept as part of the
text.

## Tips

- Label a brief in one sitting if you can; `refers_to` is easy to lose track of across breaks.
- Search the PDF for `Id.`, `supra`, and ` at ` after a first pass — they're the easiest to miss.
- Record time spent per brief in the commit message; it becomes a cost number for the ADR.
