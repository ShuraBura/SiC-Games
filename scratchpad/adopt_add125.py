"""Insert Add.125 into RESULTS (before the end line) after the corrections to the draft, and update the audit pointer."""
p = "scratchpad/add125_text.md"
s = open(p, encoding="utf-8").read()
fix = [
 ("mortality moves −1% to +5%", "mortality moves −1% to +6%"),
 ("- Null floor: about 3,000–4,500 deaths per run give a Poisson SE near ±0.8 per 1000 per year for one run, ±0.45 for the\n  mean of 3 seeds.",
  "- Null floor: 2,600–4,700 deaths per run give a Poisson SE near ±0.5 per 1000 per year for one run, ±0.3 for the mean of\n  3 seeds."),
 ("| +3.1% |", "| +2.9% |"), ("| +5.5% |", "| +5.9% |"), ("| −0.7% |", "| −0.8% |"), ("| +0.9% |", "| +1.0% |"),
 ("| +2.0% |", "| +2.2% |"),
 ("Land use falls about 10%; the number of villages falls\nonly 1–3%, so", "Land use falls 2–10% against control; the number of\nvillages falls at most 2%, so"),
 ("Only temperate shows an ASDR rise above the null floor.", "Only temperate shows a clear ASDR rise above the null floor (+0.8 and +1.5 per 1000 per\nyear); montane ×0.70 is marginal (+0.65); the other cells are inside it."),
 ("The non-starvation part of the ASDR is flat (−0.9 to +0.2 per 1000 per year). All of the rise is starvation, at most\n+1.3 per 1000 per year (temperate and savanna ×0.70). After the drought the ASDR falls 3–11% below pre, because the\nstarvation part falls by up to half: the smaller population has more food per head.",
  "The non-starvation part of the ASDR is flat (−0.8 to +0.3 per 1000 per year). The starvation part moves −0.2 to +1.4.\nAfter the drought the ASDR falls 2.5–11% below pre, and most of that fall is starvation, which falls by up to a third:\nthe smaller population has more food per head."),
 ("median intake (EMA) falls 15–20% against", "median intake (EMA) falls 14–19% against"),
 ("f_syn ≈ 1.012 for children.", "f_syn ≈ 1.012–1.018 for children."),
 ("small: +0.1 to +1.6 per 1000 per year above the crude change.", "small: +0.4 to +1.4 per 1000 per year above the crude change."),
]
for a, b in fix:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
r = open("docs/RESULTS.md", encoding="utf-8").read()
end = "*End of RESULTS — seeded"
assert r.count(end) == 1
r = r.replace(end, s + end)
open("docs/RESULTS.md", "w", encoding="utf-8").write(r)
q = "audit/2026-10-26/00_START_HERE.md"
t = open(q, encoding="utf-8").read()
a = "with TFR re-scored by the identity (Add.124, 2026-10-29). **For the current verdicts read"
assert t.count(a) == 1
t = t.replace(a, "with TFR re-scored by the identity (Add.124, 2026-10-29); and the drought test on that canon, which\n> corrects Add.119 (Add.125, 2026-11-04). **For the current verdicts read")
open(q, "w", encoding="utf-8").write(t)
