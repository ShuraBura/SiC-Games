# SiC Games — working notes for Claude

## Literature values: check the SPECS before re-reading PDFs

Every lit-derived value has already been **extracted and pooled into the docs** — that is the whole point of
`DOCS_CHARTER.md`'s "one fact, one home". The `literature/` PDFs are the raw sources; the *usable numbers* live in:

- **`docs/MODEL_SPEC.md`** — methods home: every lit-derived value's exact extraction/scaling arithmetic.
- **`docs/SiC_Games_Resource_Return_Rate_Table.md`** — per-biome forage+game means/stds, each with its derivation
  and source citation (the authoritative derived view; `terrain.py` follows it, never leads).
- **`docs/PARAMETERS.md`** — the constant table (value, status, grounding).
- **`docs/LITERATURE.md`** — the source list + what each source was used for.

**Before opening any PDF in `literature/`, grep these four docs.** The number you want is almost always already
there with its arithmetic and citation — cite it, don't re-derive it, and don't re-render the table image.

**Go to the PDF only when one of these holds** (and say which, in the commit/RESULTS note):
1. **New statistic.** The quantity genuinely isn't pooled — e.g. R-72's *day-to-day (temporal)* return CV, which
   no table held (they pool *spatial* cross-cell variance). Extract it, then **pool it back** into the right doc.
2. **Verifying a suspected error** in a pooled value — e.g. R-79's Bird 2009 desert-game row (the table said
   "bustard" but the underlying figure was hill kangaroo). Check the table's claim against the source, then fix
   the table + the constant + PARAMETERS together.

If you do read a source: many are scans/embedded-image tables with **no text layer**. Render the page with
`pymupdf` (`import pymupdf; pymupdf.open(path)[i].get_pixmap(dpi=200).save(out)`) and read the image — `pypdf`
text extraction silently transposes or drops table columns, which is how the R-79 error entered in the first place.

## Other standing conventions

- Use `py -3` (not `python`; not on PATH in Git Bash here).
- New mechanics land **default-OFF / bit-exact**; adoption = flip the flag in the preset
  (`run_se0_controlled_climate.py`) with a `# CANONICAL <date>:` rationale, never in the `DemographyConfig` default.
- Long/background runs must flush progress to a file (pipe-to-grep buffering hides stdout); poll the log, not the
  wrapper notification. Beware stale `progress_*.txt` from earlier runs — check the timestamp.
- Before believing any demographic claim, run `outputs/phase1_biome_mortality/report_demography.py`
  (per-village markers vs their anchors — R-75).
