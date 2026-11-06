"""Correct the draft of Add.128 against bp_add128_verify.py, insert it into RESULTS (append-only), update the audit pointer."""
p = "scratchpad/add128_text.md"
s = open(p, encoding="utf-8").read()
for old, new in [
    ("the brake factor (−41 to −78%)", "the brake factor (−41 to −79%)"),
    ("At ×0.70 the factor falls by about 1% or less.", "At ×0.70 the factor falls by 0.7–1.7%."),
    ("Only 3% / 4% / 34% of all children live there.", "Only 3% / 4% / 33% of all children live there."),
    ("**6. The two errors have the same sign for the brake and the opposite meaning for food.** On the supply side, the village has 1.7–3.6 × the ceiling. On the demand side, `fill` reads 2.0–3.4 × the true need ratio, because its numerator counts heads at adult burn over the 25-cell window and its denominator covers 9 cells. Add.106 found the radius part of this, and `enable_density_fill_matched_radius` is held dark.",
     "**6. Both sides of the ratio are wrong.** On the supply side, the village has 1.7–3.6 × the ceiling. On the demand side, `fill` reads 2.0–3.4 × the true need ratio. Its numerator counts heads at adult burn over the 25-cell window, and its denominator covers 9 cells. I did not measure the split between these causes. Add.106 found the radius part, and `enable_density_fill_matched_radius` is held dark."),
    ("τ 1.4 yr −5 to −12%, τ 5 yr −1.1 to −4.7%, τ 10 yr −0.6 to −2.6%, τ 20 yr −0.3 to −1.4%", "τ 1.4 yr −2.6 to −12%, τ 5 yr −1.1 to −4.8%, τ 10 yr −0.6 to −2.6%, τ 20 yr −0.3 to −1.4%"),
    ("A linear estimate gives a damping ratio of 0.56–0.79 for these τ", "A linear estimate gives a damping ratio of 0.57–0.81 for these τ"),
    ("A village occupies 7–11 cells, so it collects several ceilings.", "A village occupies about 7–10 cells, so it collects several ceilings."),
    ("- **Settled adults starve beside a full store.** In the ×0.70 year on temperate, starvation inside villages about doubles (2 seeds, 72 against 33 deaths), in the lean months, and the store of those villages is not empty. The cause is not known. One candidate is an agent that enters a village after the harvest.",
     "- **Settled people starve beside a stocked store.** In the ×0.70 year, starvation inside villages rises from 35 to 73 deaths on temperate, 7 to 22 on savanna and 9 to 36 on montane (2 seeds), mostly adults, and on temperate in the lean months. Only 6 of those 131 deaths were in a village with less than one step of store per head. The cause is not known. One candidate is an agent that enters a village after the harvest."),
    ("- **Starved children outside villages:** about 60% have no living mother.", "- **Starved children outside villages:** 55–70% have no living mother."),
]:
    assert s.count(old) == 1, old[:50]
    s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)

r = open("docs/RESULTS.md", encoding="utf-8").read()
end = "*End of RESULTS — seeded"
assert r.count(end) == 1
open("docs/RESULTS.md", "w", encoding="utf-8").write(r.replace(end, s + end))

q = "audit/2026-10-26/00_START_HERE.md"
a = "and the one-year test against that anchor (Add.127). **For the current verdicts read"
u = open(q, encoding="utf-8").read()
assert u.count(a) == 1
open(q, "w", encoding="utf-8").write(u.replace(a, "the one-year test against that anchor (Add.127); and the village food account, with a design for review (Add.128). **For the current verdicts read"))
