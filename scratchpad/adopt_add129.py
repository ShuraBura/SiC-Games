"""Correct the draft of Add.129 against the logs, insert it into RESULTS (append-only), update the audit pointer."""
import json
for w in ("montane",):
    for s in (0, 1):
        d = json.load(open(f"sic_games/outputs/substrate_run/campaign_trajectory_vc_{w}_on_c_s{s}.json", encoding="utf-8"))
        print(w, s, "modal", d["meta"].get("period_life_table", {}).get("modal_adult_death"))

p = "scratchpad/add129_text.md"
s = open(p, encoding="utf-8").read()
for old, new in [
    ("and the median falls 2.4 / 1.6 / 2.6 ×.", "and the median falls 2.5 / 1.6 / 2.6 ×."),
    ("Hold: `fill` still reads 2.2–3 × need,", "Hold: `fill` still reads about 2–3 × need,"),
    ("- **Births still over-respond,** by 2–5 × the price route on savanna and montane and 6 × on temperate. The same-step read of the brake is still there. That is Stage B's job, and the first figure of births shows the step in the shock year.",
     "- **Births still over-respond:** −9 to −24 per 10%, against −0.8 by output and −1.8 to −4 by price. The same-step read of the brake is still there, as the step in the births panel of the shock figure shows. That is Stage B's job."),
    ("The one-year shock costs little, and the store absorbs it, as Add.128 expected.", "The one-year shock costs 3–5% of the population, and the store falls by about one step, as Add.128 expected."),
]:
    assert s.count(old) == 1, old[:50]
    s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)

r = open("docs/RESULTS.md", encoding="utf-8").read()
end = "*End of RESULTS — seeded"
assert r.count(end) == 1
open("docs/RESULTS.md", "w", encoding="utf-8").write(r.replace(end, s + end))

q = "audit/2026-10-26/00_START_HERE.md"
a = "and the village food account, with a design for review (Add.128). **For the current verdicts read"
u = open(q, encoding="utf-8").read()
assert u.count(a) == 1
open(q, "w", encoding="utf-8").write(u.replace(a, "the village food account, with a design for review (Add.128); and Stage A of that design, stopped for review (Add.129). **For the current verdicts read"))
