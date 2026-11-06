"""Insert Add.127 into RESULTS (append-only), update the audit pointer, and fix two labels in the Add.127 figure script."""
s = open("scratchpad/add127_text.md", encoding="utf-8").read()
r = open("docs/RESULTS.md", encoding="utf-8").read()
end = "*End of RESULTS — seeded"
assert r.count(end) == 1
open("docs/RESULTS.md", "w", encoding="utf-8").write(r.replace(end, s + end))

q = "audit/2026-10-26/00_START_HERE.md"
a = "and the anchor for that test (Add.126). **For the current verdicts read"
u = open(q, encoding="utf-8").read()
assert u.count(a) == 1
open(q, "w", encoding="utf-8").write(u.replace(a, "the anchor for that test (Add.126); and the one-year test against that anchor (Add.127). **For the current verdicts read"))

p = "scratchpad/bp_add127_fig.py"
f = open(p, encoding="utf-8").read()
for old, new in [
    ('ax.axvspan(-0.08, 1 - 0.08, color="#f0efe8", lw=0)', 'ax.axvspan(-0.5, 0.5, color="#f0efe8", lw=0)'),
    ('ax.set_title("One shocked step, identical state: grey control", loc="left", fontsize=10.5, fontweight="bold", color=INK)',
     'ax.set_title("Births in one shocked step, identical state", loc="left", fontsize=10.5, fontweight="bold", color=INK)\n'
     'from matplotlib.patches import Patch\n'
     'ax.legend(handles=[Patch(color=MUTED, label="control"), Patch(color=CD["085"], label="×0.85"), Patch(color=CD["070"], label="×0.70")], '
     'frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.1))'),
]:
    assert f.count(old) == 1
    f = f.replace(old, new)
open(p, "w", encoding="utf-8").write(f)
