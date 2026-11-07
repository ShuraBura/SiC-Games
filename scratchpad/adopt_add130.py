"""Correct the draft of Add.130 against the checked numbers, insert it into RESULTS (append-only), update the audit pointer."""
p = "scratchpad/add130_text.md"
s = open(p, encoding="utf-8").read()
for old, new in [
    ("In the canon the exponent is 1.5 in nearly all draws, and the weight", "The exponent is 1.5 in nearly all draws at a death, and the weight"),
    ("The lowest status decile carries 100–230 starvation deaths per 1,000 per year. From the fourth decile up, the hazard is about 1 per 1,000 or less on temperate and savanna (first figure).",
     "With the flag on, adults in the lowest status decile carry 70–230 starvation deaths per 1,000 per year. From the fourth decile up, their hazard is about 1 per 1,000 or less on temperate and savanna (first figure)."),
    ("Possible, but then the model says that a village lets people die beside food, which the source of the mechanism does not claim and the spec denies", "Possible, but then the model says that a village lets people die beside food, which the specification denies"),
    ("1. Add.129's \"people do not leave a hungry village\" is wrong as written. Exit stays at the usual rate. Entry replaces it.", "1. Add.129's \"people do not leave a hungry village\" is wrong as written for montane and savanna. Exit stays near the usual rate, and entry replaces it."),
]:
    assert s.count(old) == 1, old[:50]
    s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)

r = open("docs/RESULTS.md", encoding="utf-8").read()
end = "*End of RESULTS — seeded"
assert r.count(end) == 1
open("docs/RESULTS.md", "w", encoding="utf-8").write(r.replace(end, s + end))

q = "audit/2026-10-26/00_START_HERE.md"
a = "and Stage A of that design, stopped for review (Add.129). **For the current verdicts read"
u = open(q, encoding="utf-8").read()
assert u.count(a) == 1
open(q, "w", encoding="utf-8").write(u.replace(a, "Stage A of that design, stopped for review (Add.129); and the per-village log, which finds people starving beside a stocked store in the canon (Add.130). **For the current verdicts read"))
print("ok")
