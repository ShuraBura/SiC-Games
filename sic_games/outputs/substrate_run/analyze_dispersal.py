"""R-102 — SEX-BIASED DISPERSAL from the genealogy stream: the signature of post-marital residence.

WHY THIS EXISTS. `aggregation_residence` moves one spouse's band affiliation at marriage (phase1_model.py:3405-3412)
— virilocal moves the bride, uxorilocal the groom. Nothing in the trajectory rows records that: the campaign logs
`mean_relatedness` but nothing sex-specific, so a virilocal and an uxorilocal arm are distinguishable only through
downstream aggregates, which is the weakest possible read of the axis. The genealogy CSV does carry sex, band_id
and both parent uids per event, so the signature is recoverable OFFLINE. This is what the R-101 full-genealogy
decision was for.

THE MEASURE. For every individual with BOTH a birth row and a death row, compare natal band against band at death:
did they leave the band they were born into? Then split by sex.

WHY THE SEX *DIFFERENCE* AND NOT THE RATE. Band ids also change for reasons that have nothing to do with marriage
— fission, budding, dissolution, merging. Those confounds are not sex-specific, so they inflate BOTH rates about
equally and cancel in the difference. The absolute rate is therefore uninterpretable on its own and the difference
is the estimand. Reporting P(moved) alone would be exactly the hidden-denominator error the charter's D15 names.

FOUNDERS ARE EXCLUDED BY CONSTRUCTION: seeded agents have no birth row, so their natal band is unknown. Anyone
still alive at the end is likewise never counted (reported as `unresolved`).

ADULTS ONLY: someone who died before marriageable age could not have dispersed by marriage, and including them
dilutes both arms toward zero. Threshold comes from the run's own `menarche_months`, not a literal.

Run:  py -3 sic_games/outputs/substrate_run/analyze_dispersal.py TAG [TAG2 ...]
"""
import csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _z_two_prop(k1, n1, k2, n2):
    """Two-proportion z test. Returns (z, two-sided p). Pooled SE; normal approx is fine at these n."""
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se <= 0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def analyze(tag, adult_months=None):
    traj = os.path.join(HERE, f"campaign_trajectory_{tag}.json")
    csvp = os.path.join(HERE, f"campaign_genealogy_{tag}.csv")
    meta = {}
    if os.path.exists(traj):
        try:
            meta = json.load(open(traj, encoding="utf-8"))["meta"]
        except Exception:
            meta = {}
    if adult_months is None:
        adult_months = (meta.get("demography_config") or {}).get("menarche_months", 168)

    natal = {}                       # uid -> (band_id, sex)   ONLY the living; popped at death (bounded memory)
    moved = {"male": 0, "female": 0}
    total = {"male": 0, "female": 0}
    juvenile = 0
    with open(csvp, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                ev, uid, sex = row["event"], row["uid"], row["sex"]
                if ev == "birth":
                    natal[uid] = (row["band_id"], sex)
                elif ev == "death":
                    got = natal.pop(uid, None)
                    if got is None:
                        continue                       # founder, or born before this CSV began
                    if float(row["age"] or 0) < adult_months:
                        juvenile += 1
                        continue
                    if sex not in total:
                        continue
                    total[sex] += 1
                    if row["band_id"] != got[0]:
                        moved[sex] += 1
            except (KeyError, ValueError):
                continue                               # tolerate a torn final line on a LIVE file

    pm = moved["male"] / total["male"] if total["male"] else float("nan")
    pf = moved["female"] / total["female"] if total["female"] else float("nan")
    z, p = _z_two_prop(moved["female"], total["female"], moved["male"], total["male"])
    return dict(tag=tag, world=meta.get("world"), residence=meta.get("residence"),
                steps=meta.get("steps_completed"), adult_months=adult_months,
                n_male=total["male"], n_female=total["female"],
                p_male=pm, p_female=pf, diff=pf - pm, z=z, p_value=p,
                juvenile_skipped=juvenile, unresolved=len(natal))


MIN_N = 100          # per sex; below this the difference cannot resolve anything useful
CEILING = 0.90       # if BOTH sexes are above this, the difference is compressed by saturation
FLOOR = 0.05         # if BOTH are below this, nobody is dispersing at all


def validity(r):
    """Refuse to pronounce on data that cannot support a verdict — mechanically, not by remembering to check.

    TWO WAYS THIS MEASURE GOES INVALID, and the boreal arms hit both at once:

    POWER. n=15 males and n=6 females cannot resolve a 0.4 difference, let alone a small one. A sign read off
    that many individuals is noise, and the first cut of this script duly reported a confident-looking
    "CONTRADICTS" from p=0.11.

    SATURATION — the subtler one, and a validity DOMAIN in the charter's D15 sense. The difference-in-differences
    only cancels the band-turnover confound while rates are away from the ceiling. In a COLLAPSING population
    bands dissolve under everyone, both sexes approach P(moved)=1.0, and the difference is squeezed toward zero
    no matter what the residence rule says. The estimand stops being about marriage and starts being about band
    death. A rate near 1.0 in both sexes is therefore not evidence of "no residence effect" — it is evidence that
    this instrument does not apply."""
    if r["n_male"] < MIN_N or r["n_female"] < MIN_N:
        return f"UNDERPOWERED (n={r['n_male']}/{r['n_female']}, need >={MIN_N} per sex)"
    lo = min(r["p_male"], r["p_female"])
    hi = max(r["p_male"], r["p_female"])
    if lo > CEILING:
        return f"SATURATED (both rates >{CEILING:.0%}: band turnover dominates, difference compressed)"
    if hi < FLOOR:
        return f"NO DISPERSAL (both rates <{FLOOR:.0%})"
    return None


def _fmt(r):
    exp = {"virilocal": "female > male", "uxorilocal": "male > female"}.get(r["residence"], "?")
    bad = validity(r)
    if bad:
        obs, agree = "(not interpretable)", bad
    elif r["n_male"] and r["n_female"]:
        obs = "female > male" if r["diff"] > 0 else ("male > female" if r["diff"] < 0 else "equal")
        agree = "AGREES" if obs == exp else ("n/a" if exp == "?" else "CONTRADICTS")
    else:
        obs, agree = "(no data)", "n/a"
    return (f"{r['tag']}\n"
            f"   world={r['world']}  residence={r['residence']}  steps={r['steps']}  adult>={r['adult_months']}mo\n"
            f"   left natal band:  male {r['p_male']:.3f} (n={r['n_male']})   "
            f"female {r['p_female']:.3f} (n={r['n_female']})\n"
            f"   difference (F-M) = {r['diff']:+.3f}   z={r['z']:+.2f}  p={r['p_value']:.2g}\n"
            f"   expected {exp} -> observed {obs}   [{agree}]\n"
            f"   juveniles skipped={r['juvenile_skipped']}  still-alive unresolved={r['unresolved']}")


if __name__ == "__main__":
    tags = sys.argv[1:] or ["sw_hilly_temperate_viri"]
    out = []
    for t in tags:
        try:
            r = analyze(t)
            out.append(r)
            print(_fmt(r) + "\n")
        except FileNotFoundError as e:
            print(f"{t}: no genealogy ({e})\n")
    if len(out) == 2:
        a, b = out
        print("SIGN-FLIP TEST (the instrument's own control — the strongest check available:")
        print("the SAME code on two arms differing only in residence must reverse the sign):")
        print(f"   {str(a['residence']):11s} diff={a['diff']:+.3f}   {validity(a) or 'valid'}")
        print(f"   {str(b['residence']):11s} diff={b['diff']:+.3f}   {validity(b) or 'valid'}")
        if validity(a) or validity(b):
            # A sign-flip verdict inherits the weaker arm's validity. Announcing PASS/FAIL here on invalid
            # inputs is how an underpowered pair gets written up as a finding.
            print("   -> INCONCLUSIVE: at least one arm is not interpretable; no verdict drawn")
        else:
            flipped = (a["diff"] > 0) != (b["diff"] > 0)
            print(f"   -> {'PASS: sign flips with residence' if flipped else 'FAIL: same sign in both arms'}")
