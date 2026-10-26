# 06 — Known issues (do not report as new) and audit lenses (where defects have been found before)

---

## 1. Known issues at the snapshot

You may report that a known issue is WORSE than documented, or that its consequences are under-appreciated; please do
not report its existence as a discovery.

**Model**
1. Temperate #1 band size (40.2 ± 1.6 vs ≤ 40) and #17 fission ceiling (232 ± 19 vs ≤ 250) are unresolved.
2. Fertility (TFR) is below the forager band on every world; it was in band until the Add.108/Add.113 adoptions.
3. Mortality at ages 5–15 is 2–3× the Aché value; never in band in the five measured canons.
4. Orphanhood is high (motherless ~0.03, fatherless ~0.08); fatherlessness left its range at Add.113.
5. Montane birth intervals are short (32 months).
6. The spatial paradox flag is TRUE on every run: the population does not disperse to its food; Add.105 (previous
   canon) measured it at 5–10% of carrying capacity — not re-measured.
7. The Malthusian contraction under a shock is not tested.
8. #11 status→RS is NOT COMPARABLE (the model lacks the status → partner-fertility channel); #5, #8, #9 are not computed.
9. There is no cause-of-death structure or marker; starvation is 15–29% of deaths.
10. Band cohesion has no headroom (assabiyah pinned; Add.22; `test_cohesion_headroom.py`).
11. No secular cycles (four negatives; Add.105); dynastic concentration is a stable equilibrium.
12. Everything rests on ONE planet (world/climate seed 0); no replication across planets.
13. The Add.113 adoption was decided on #18–#21 only; its side effects (TFR, fatherless, #3-max, #11, #15) were found
    afterwards (Add.114).

**Instruments and documentation**
14. The demography monitor scores band size with `band_med_adults`, the statistic Add.89 retracted.
15. Provenance: 165 of 253 parameters have no tag in their own comment; 12 flags have no own comment; two canon values
    have no recorded reason (`comove_footprint = 0`; `village_fission_threshold` 150 vs the documented 170).
16. `config/*.toml` gives a field without its own comment a neighbour's block (10 flags were affected; 2 fixed in source).
17. 73 broken file references in live documents (47 in the append-only RESULTS).
18. DEFERRED_MECHANICS says no Flannery item (DM-F1…F6) is built; legitimacy, delegitimation and tribute were built later.
19. `capacity_scaled_grouping` has no BENCHMARK_LADDER tier.
20. R-106 Addenda 1–41 have no headings; RESULTS_INDEX cannot list them individually.
21. Five configuration test files fail intermittently with WinError 6 under pytest's default capture.
22. 12 of 15 registered-anchor PDFs are not in the public repository (copyright).
23. The C/Si question (R-1, H1(ii)) is historical and was never re-tested on the Phase-1 substrate.

---

## 2. Audit lenses — the defect classes this project has actually had

Each lens names the class, an example from the record, and the check that would find a new instance.

| lens | example (record) | check |
|---|---|---|
| **Spec ≠ code** | the terrain-risk term scaled the WHOLE a2, not the spec's 10% accident share, for two months (Add.112; filed in commit ae01ced 2026-08-14) | read a MODEL_SPEC formula, then its implementation; the per-factor observers in `_a2_mult` |
| **Config drift** ("validated in one stack, dead in another") | `paternal_provision_frac` was 0.0 in canon vs the documented 0.5 (Add.109) | REGISTRY `≠` column; a doc's "canonical" value vs the run file |
| **Wrong statistic / unit / denominator** | #1 band size (median over band_id vs person-weighted per cell, Add.89); #14 (all-ages vs adults Gini, Add.90); l(45) from birth vs conditional | for each marker: statistic, unit, denominator, freshness against the source (MARKER_MATRIX rules 2b, 5) |
| **A window is not a partition** | #17's 3×3 window straddled ~3 villages (Add.103) | any "largest local group" measure |
| **Instrument defects** | instruments were wrong more often than the model — the reason for the CTB rule (root CLAUDE.md; Add.31) | does each diagnostic a finding rests on have a `*_ctb.py` with a constructed negative? |
| **Hidden denominator / validity domain** | thresholds on shares that fail silently when the denominator drifts (elite layer; R-91 invariants) | thresholds on ratios; `invariants.py` |
| **Seed variance** | e0 noise dominated by the world draw; single-seed verdicts reversed (MARKER_MATRIX rule 3; Add.76) | is the replication unit right for the marker? |
| **Adoption scope** | Add.113 decided on #18–#21; side effects found in Add.114 | does each adoption score the FULL benchmark set (this package's history tool)? |
| **A fix that trades one benchmark for another** | survival up, fertility down across Add.108–113 (`02_BENCHMARKS.md`) | read benchmarks together (MARKER_MATRIX rule 4) |
| **Mis-attributed provenance** | a flag's description inherited from a neighbour in `config/*.toml` (Add.114) | read the comment at the field's definition |
| **Bit-exact claims** | every flag claims "default OFF ⇒ bit-exact" | a control re-run with the flag off vs a stored run |
| **Literature anchors** | four MARKER_MATRIX rows mis-attributed (Add.28); "savanna 31" with no source (Add.73) | `verify_anchor.py --list`; VERIFICATION_LOG; the cited page |
| **Refuted conclusions still quoted** | Add.79 "adaptive equilibrium" refuted by Add.105; Add.80 retracted by Add.89 | before relying on an entry, search for later entries that name it (DEAD_ENDS DE-23) |
| **Test that pins a defect read as a regression** | `test_cohesion_headroom.py`, the whole-a2 test in `test_risk_accident_share.py` | read a failing test's docstring first |
