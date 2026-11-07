"""Add to bp_vlog.py the exposure by age class and status decile, the null for the status order of the deaths (C5)."""
p = "scratchpad/bp_vlog.py"
s = open(p, encoding="utf-8").read()
for a, b in [
    ("""        vw[key] = sorted(weights)
        got = sum(gives)
""", """        vw[key] = sw = sorted(weights)
        for (a, d), w, g in zip(needy, weights, gives):      # the exposure by age class and status decile, the null for the deaths
            cl = 0 if a.age < 180 else (1 if a.age < 312 else (2 if a.age < 552 else 3))
            dc = min(9, int(10 * bisect.bisect_left(sw, w) / max(1, n - 1)))
            pgrid[int(vil)][cl][dc] += 1
            short[int(vil)][cl][dc] += (1 if g < d else 0)
        got = sum(gives)
"""),
    ("""first = {}           # site -> first step seen
""", """first = {}           # site -> first step seen
pgrid = [[[0] * 10 for _ in range(4)] for _ in range(2)]   # [cell, village][age class][status decile] person-steps in a draw
short = [[[0] * 10 for _ in range(4)] for _ in range(2)]   # the same, for a draw below the deficit
"""),
    ("""    Y.clear()


def _step(""", """    Y.clear()
    with open(os.path.join(LOG, f"grd{TAG}.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(st=t, pgrid=pgrid, short=short), fh)


def _step("""),
]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("patched")
