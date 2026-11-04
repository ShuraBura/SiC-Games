"""R-106 Add.125: the fertility carrier, and the comparison across canons.
A. TFR against the mean brake factor (fert_factor), every window and depth, per run: one curve?
B. Bound on the intake term: its mean factor among past-menarche agents is at least 1 - frac_below_hi, so
   ratio(drought/pre) >= (1 - f_drought) / (1 - f_pre). Compare with the measured ratio of fert_factor.
C. Pre-drought fert_factor from the control runs' rows.
D. Births and deaths deficits vs paired control over the drought, canon A117 / all4 / pair, same arithmetic.
"""
import json
import os
import statistics as st

import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
LOG = os.path.join(ROOT, "scratchpad", "drought_logs")
W = ("temperate", "savanna", "montane")
MS = ("085", "070")
S = (0, 1, 2)


def traj(tag):
    return json.load(open(os.path.join(OUT, f"campaign_trajectory_{tag}.json"), encoding="utf-8"))["traj"]


pts = []
for w in W:
    for m in MS:
        for s in S:
            sc = json.load(open(os.path.join(LOG, f"lt_dr_pair_{w}_m{m}_s{s}.json"), encoding="utf-8"))
            for a, b in (("9000", "9360"), ("9360", "9720")):
                A, B = sc[a], sc[b]
                fb = [y - x for x, y in zip(A["fert_births"], B["fert_births"])]
                fe = [(y - x) / 12 for x, y in zip(A["fert_exposure"], B["fert_exposure"])]
                tfr = sum(p / q for p, q in zip(fb, fe) if q > 0)
                fac = (B["fert_factor_sum"] - A["fert_factor_sum"]) / (B["fert_factor_n"] - A["fert_factor_n"])
                pts.append((w, m, s, a, fac, tfr))
x = np.array([p[4] for p in pts])
y = np.array([p[5] for p in pts])
print(f"A. {len(pts)} points; corr(log factor, log TFR) = {np.corrcoef(np.log(x), np.log(y))[0, 1]:.4f}")
c = np.polyfit(np.log(x), np.log(y), 1)
print(f"   log TFR = {c[1]:.3f} + {c[0]:.3f} log factor; rms residual {np.std(np.log(y) - np.polyval(c, np.log(x))):.4f}")
json.dump(pts, open(os.path.join(ROOT, "scratchpad", "drought_fert_points.json"), "w"))

print("\nC. fert_factor_mean, realised_tfr in control rows near 8900-9000 / drought rows at 9350 (is the column cumulative?)")
for w in W:
    t = traj(f"s2_{w}_pair_s0")
    print(f"   {w[:4]} control rows", [(r["step"], round(r["fert_factor_mean"], 3), round(r["realised_tfr"], 2)) for r in t if r["step"] in (7500, 8500, 9000, 9350, 9700, 11000)])
    d = traj(f"dr_pair_{w}_m070_s0")
    print(f"        drought rows", [(r["step"], round(r["fert_factor_mean"], 3), round(r["realised_tfr"], 2)) for r in d if r["step"] in (9000, 9350, 9700, 11000)])

print("\nB. intake-term bound: frac_below_hi pre -> drought, bound on the ratio")
for w in W:
    for m in MS:
        fp, fd = [], []
        for s in S:
            t = traj(f"dr_pair_{w}_m{m}_s{s}")
            fp.append(st.mean(r["intake_ema_frac_below_hi"] for r in t if 8000 <= r["step"] < 9000))
            fd.append(st.mean(r["intake_ema_frac_below_hi"] for r in t if 9100 <= r["step"] <= 9360))
        print(f"   {w[:4]} x0.{m[1:]} frac {st.mean(fp):.3f} -> {st.mean(fd):.3f}  bound: intake factor ratio >= {(1 - st.mean(fd)) / (1 - st.mean(fp)):.3f}")

print("\nD. Deficit over steps 9000-9350 vs paired control: births, deaths (people, mean of 3 seeds)")
print("   arm: world depth | pop deficit at 9350 | births deficit | excess deaths | births' share")
for arm, ctl in (("", "riskvg"), ("all4", "all4"), ("pair", "pair")):
    for w in W:
        for m in MS:
            B, D, P = [], [], []
            for s in S:
                d = {r["step"]: r for r in traj(f"dr_{arm + '_' if arm else ''}{w}_m{m}_s{s}")}
                c = {r["step"]: r for r in traj(f"s2_{w}_{ctl}_s{s}")}
                dd = (d[9350]["lt_deaths_total"] - d[9000]["lt_deaths_total"]) - (c[9350]["lt_deaths_total"] - c[9000]["lt_deaths_total"])
                dp = (d[9350]["pop"] - d[9000]["pop"]) - (c[9350]["pop"] - c[9000]["pop"])
                B.append(-(dp + dd))
                D.append(dd)
                P.append(-dp)
            print(f"   {arm or 'A117':5s} {w[:4]} x0.{m[1:]} | {st.mean(P):7.0f} | {st.mean(B):7.0f} | {st.mean(D):7.0f} | {st.mean(B) / (st.mean(B) + max(st.mean(D), 0)):.2f}")
