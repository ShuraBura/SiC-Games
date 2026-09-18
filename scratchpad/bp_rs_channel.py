"""R-106 Addendum 102 — WHICH CHANNEL drives the #11 status->RS skew?

On canon the model shows polygyny 0.042 (Marlowe's monogamous ~4%) yet status->RS 0.283 (temperate), nearly 2x
von Rueden's CROSS-SYSTEM polygynous 0.19. Monogamous-level polygyny should not carry a polygynous-level skew.

`frac_polygynous_all_m` measures only the INTENSIVE margin (simultaneous wives). Candidate channels it cannot see:
  EXTENSIVE   - how many men partner AT ALL (never-partnered men concentrate RS in the rest)
  SEX RATIO   - a male-biased adult/operational sex ratio mechanically excludes men from pairing
  SERIAL      - high-status men re-pair faster after death/divorce (more partners, never simultaneously)
  SURVIVAL    - high-prowess men live longer, so accumulate more offspring (age-partialling is linear only)

The three canonical worlds give a natural contrast: temperate 0.283 / montane 0.262 are HIGH, savanna 0.141 is AT
the anchor. Whatever drives the skew should split the same way. Prints the candidate channels alongside.
"""
import json
import statistics as st

WORLDS = {
    "temperate": "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_temperate.json",
    "savanna":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_savanna.json",
    "montane":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_montane.json",
}

FIELDS = [
    ("status_rs_r_partial", "#11 status->RS (age-ctrl)     "),
    ("frac_polygynous_all_m", "polygyny, all men (INTENSIVE) "),
    ("mean_wives_married_m", "mean wives | married          "),
    ("frac_never_partnered_30", "NEVER partnered by 30 (EXT)   "),
    ("frac_unpaired_adult_m", "unpaired adult men (EXT)      "),
    ("frac_partnered_adult", "partnered adults              "),
    ("frac_widowed_adult", "widowed adults (serial input) "),
    ("adult_sex_ratio", "adult sex ratio m/f           "),
    ("operational_sex_ratio", "operational sex ratio         "),
    ("male_rs_gini", "male RS gini (the skew itself)"),
    ("e0_male", "e0 male (survival channel)    "),
    ("e0_gap_f_minus_m", "e0 gap f-m                    "),
    ("pop", "pop                           "),
]


def sustained(traj, field, frac=0.15):
    n = len(traj)
    w = traj[-max(1, int(n * frac)):]
    v = [r[field] for r in w if r.get(field) is not None and r.get(field) == r.get(field)]
    return st.mean(v) if v else None


def main():
    data = {w: json.load(open(p))["traj"] for w, p in WORLDS.items()}
    print(f"{'channel':32s} {'temperate':>12s} {'savanna':>12s} {'montane':>12s}    split?")
    print("-" * 92)
    ref = {}
    for f, label in FIELDS:
        vals = {w: sustained(data[w], f) for w in WORLDS}
        ref[f] = vals
        cells = "".join(f"{('n/a' if vals[w] is None else f'{vals[w]:.3f}'):>13s}" for w in WORLDS)
        # does it split the same way as status->RS (temperate & montane HIGH, savanna LOW)?
        note = ""
        if all(vals[w] is not None for w in WORLDS):
            t, s, m = vals["temperate"], vals["savanna"], vals["montane"]
            lo, hi = min(t, m), max(t, m)
            if s < lo * 0.85:
                note = "  <-- tracks (sav LOW)"
            elif s > hi * 1.15:
                note = "  <-- tracks INVERSELY (sav HIGH)"
        print(f"{label:32s}{cells}{note}")


if __name__ == "__main__":
    main()
