"""Analyze a finished campaign arm: trajectory shape (secular cycling vs monotone consolidation) + offline
genealogy reconstruction (completed reproductive success, dynastic fixation curve). Streams the (million-row)
genealogy CSV so memory stays flat.

Run:  py -3 sic_games/outputs/substrate_run/analyze_campaign.py off on   (tags; default: off on)
"""
import sys, os, json, csv, statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(__file__)


def gini(xs):
    xs = sorted(v for v in xs if v is not None)
    n = len(xs)
    if n < 2 or sum(xs) <= 0:
        return 0.0
    cum = sum((i + 1) * v for i, v in enumerate(xs))
    return (2.0 * cum) / (n * sum(xs)) - (n + 1.0) / n


def n_swings(series, rel=0.10):
    """Count peak↔trough reversals exceeding `rel` fractional amplitude — a crude 'is it cyclic?' measure."""
    if len(series) < 3:
        return 0
    swings, last_ext, direction = 0, series[0], 0
    for v in series[1:]:
        if direction >= 0 and v > last_ext:
            last_ext = v
        elif direction <= 0 and v < last_ext:
            last_ext = v
        if last_ext > 0 and abs(v - last_ext) / (abs(last_ext) + 1e-9) > rel:
            if (v > last_ext and direction <= 0) or (v < last_ext and direction >= 0):
                swings += 1
                direction = 1 if v > last_ext else -1
                last_ext = v
    return swings


def analyze_traj(tag):
    path = os.path.join(HERE, f"campaign_trajectory_{tag}.json")
    if not os.path.exists(path):
        print(f"[{tag}] no trajectory ({path})"); return None
    d = json.load(open(path))
    tr, meta = d["traj"], d["meta"]
    pop = [r["pop"] for r in tr]
    strat = [r["pct_stratified"] for r in tr]
    eff = [r["eff_lineages"] for r in tr]
    top = [r["lin_top_share"] for r in tr]
    steps = [r["step"] for r in tr]
    peak_pop_i = pop.index(max(pop))
    # capacity phase = after population first reaches 90% of its peak
    cap_start = next((i for i, p in enumerate(pop) if p >= 0.9 * max(pop)), len(pop) - 1)
    strat_cap = strat[cap_start:]
    print(f"\n===== {tag.upper()}  ({meta['world']}, {meta['steps']} steps, seed {meta['seed']}) =====")
    print(f"  POP     final {pop[-1]}  peak {max(pop)}@step{steps[peak_pop_i]}  min-after-peak "
          f"{min(pop[peak_pop_i:])}  → {'BUST' if min(pop[peak_pop_i:]) < 0.8*max(pop) else 'glide (no bust)'}")
    print(f"  STRAT%  final {strat[-1]}  peak {max(strat)}@step{steps[strat.index(max(strat))]}  "
          f"cap-phase mean {statistics.mean(strat_cap):.1f} cv {statistics.pstdev(strat_cap)/(statistics.mean(strat_cap)+1e-9):.2f}  "
          f"swings(>10%) {n_swings(strat_cap)}")
    print(f"  DYNASTY eff_lineages {eff[0]:.0f}→{eff[-1]:.1f}  top_share {top[0]:.3f}→{top[-1]:.3f}  "
          f"(fixation: {'YES — winner-take-all' if top[-1] > 0.6 else 'pluralistic' if top[-1] < 0.35 else 'partial'})")
    print(f"  SETTLE  n {tr[-1]['n_settle']} max {tr[-1]['settle_max']} primate {tr[-1].get('primate_ratio')} "
          f"zipf {tr[-1].get('zipf_slope')} | villages {tr[-1]['n_villages']} med {tr[-1]['village_med']}")
    print(f"  MATING  connubium median max {max(r.get('connubium_med') or 0 for r in tr):.0f} (→Wobst ~475)  "
          f"| INSTAB mean {statistics.mean(r['claim_events'] for r in tr):.1f} events/step  cells-owned final {tr[-1]['cells_owned']}")
    print(f"  INEQ    gini_cred {tr[-1]['gini_cred']} gini_wealth {tr[-1]['gini_wealth']}  male_RS_gini {tr[-1]['male_rs_gini']}  "
          f"| assab {tr[-1]['assab_med']} leaderturnover {tr[-1]['leader_turnover']}")
    g = [(r['step'], r.get('heterozygosity'), r.get('mean_relatedness')) for r in tr if r.get('heterozygosity') is not None]
    if len(g) >= 2:
        print(f"  GENOME  H {g[0][1]:.3f}→{g[-1][1]:.3f}  relatedness {g[0][2]:.3f}→{g[-1][2]:.3f}  (H-decay ⇒ N_e signal)")
    return tr


def analyze_genealogy(tag, sample_every=1):
    """Stream the genealogy CSV: completed RS from DEATH rows (parity / n_fathered), reproductive skew, and the
    dynastic-fixation curve (distinct lineages among births, binned by step)."""
    path = os.path.join(HERE, f"campaign_genealogy_{tag}.csv")
    if not os.path.exists(path):
        print(f"  [{tag}] no genealogy CSV"); return
    rs, zero, nrows = [], 0, 0
    births_by_bin = defaultdict(Counter)   # step-bin → lineage → n births
    BIN = 1000
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(f); next(rd, None)
        for row in rd:
            nrows += 1
            step, event = int(row[0]), row[1]
            if event == "death":
                # adults only: completed RS = parity (female) / n_fathered (male); skip juveniles (age<180 mo)
                age = int(row[11]); sex = row[10]
                if age >= 180:
                    r = int(row[12]) if sex == "female" else int(row[13])
                    rs.append(r)
                    if r == 0:
                        zero += 1
            elif event == "birth":
                births_by_bin[step // BIN][row[5]] += 1     # row[5] = lineage
    print(f"  GENEALOGY {nrows:,} rows → {len(rs):,} adult deaths (completed RS)")
    if rs:
        print(f"    completed RS: mean {statistics.mean(rs):.2f}  median {statistics.median(rs)}  max {max(rs)}  "
              f"childless {100*zero/len(rs):.0f}%  RS-gini {gini(rs):.3f}  (elite overproduction ⇑ with skew)")
    # dynastic fixation curve: distinct + effective lineages among births per 1000-step bin
    print("    dynastic fixation (births per 1000-step bin):")
    for b in sorted(births_by_bin):
        c = births_by_bin[b]; tot = sum(c.values())
        p = [n / tot for n in c.values()]
        eff = 1.0 / sum(x * x for x in p)
        if b % 3 == 0 or b == max(births_by_bin):    # thin the print
            print(f"      step {b*BIN:>6}-{(b+1)*BIN:<6}: distinct {len(c):>4}  eff {eff:6.1f}  top {max(p):.3f}")


def main():
    tags = sys.argv[1:] or ["off", "on"]
    for tag in tags:
        tr = analyze_traj(tag)
        if tr is not None:
            analyze_genealogy(tag)


if __name__ == "__main__":
    main()
