# Labeling quality log

Hand-label miss rate, measured by the quality checks in `README.md`. Feeds ADR 0001.

A **miss** is a citation the labeler skipped that a check later found. A **fix** is a wrong
field on a row that was labeled. Rows are counted after fixes.

| Brief | Rows | TOA check | Search pass | Misses | Fixes | Source |
|---|---|---|---|---|---|---|
| b01 | 58 | clean | clean | 0 | 0 | commit a189b15 |
| b02 | 85 | clean (hand-checked) | clean (4 flags, all record cites) | 0 | 0 | re-run 2026-11-13 |
| b03 | 166 | clean (hand-checked) | clean (5 flags: complaint, 29 C.F.R. `id.`) | 0 | 0 | re-run 2026-11-13 |
| b04 | 79 | 41/41 | 1 miss (#4, Twombly short cite) | 1 | 1 (#72, page 29 not 28) | commit 1e77c97 |
| b05 | 95 | clean (hand-checked) | clean (18 flags: FAC cites, pleading line numbers) | 0 | 0 | re-run 2026-11-13 |
| b06 | 94 | clean (hand-checked) | clean (18 flags: patent, exhibit, treatise `id.`) | 0 | 0 | re-run 2026-11-13 |
| b07 | 101 | 66/66 | 1 miss (#6, `Id.` after page break) | 1 | 0 | commit 96dcda4 |

**Running total (b01–b07):** 2 misses / 678 rows ≈ 0.3%. Both misses are short forms.

b03's one structural flag (#12, `258 F.3d` vs. `779 F.3d`) is the brief's own error, already
noted in the row; it is not a labeling error.

The re-runs for b02, b03, b05, and b06 happened after those briefs were committed, so any miss
caught and fixed before the commit went unrecorded. Their 0s are a floor, not an exact count.

**Limits:** the checks only catch misses that the table of authorities lists or that contain
`Id.`, `supra`, or a reporter followed by ` at `. The blind re-label of b04 estimates the rest.
