# SiC Games — Literature Notes

Maintained by the coding agent. Updated each stage when a new mechanism
requires a literature rationale. Supervisor adds entries as appropriate.

---

## Stage 5 — Task 3: Si Cred Mechanism

**Question:** What mechanism governs how the Si "Cred" (performance-based
reputation) accumulates and influences behaviour in bounded-rational agents?

### Sources reviewed

**Epstein & Axtell (1996) — *Growing Artificial Societies* (Sugarscape):**
The original Sugarscape tracks agent wealth as the primary state variable.
Agents with higher accumulated wealth have more slack to survive shocks but
do not acquire a *reputation* signal that modifies decision temperature.
Sugarscape is purely foraging-driven with no peer-influence channel.
**Conclusion:** Sugarscape provides the resource-harvesting substrate but no
direct precedent for a Cred–temperature coupling. The Stage 3.x C Cred design
already departs from Sugarscape by adding a social-coordination signal.

**Axelrod (1984) — *The Evolution of Cooperation*:**
Axelrod demonstrates that repeated-game reputation (via tit-for-tat) stabilises
cooperation without central enforcement. Reputation here is *relational* (between
dyads) and binary (cooperate/defect history). The key insight adopted for
Si Cred: *performance history creates a signal that others (or the agent itself)
can condition behaviour on*. The self-conditioning variant (agent adjusts own
temperature based on own recent harvest surplus) is the Si Cred mechanism.
**Adopted:** the self-referential performance-feedback loop (not the dyadic
reputational model, which requires interaction tracking we defer to Stage 5.x).

**Nowak & May (1992) — spatial prisoner's dilemma:**
Local neighbourhood reputation drives spatial clusters of cooperators.
Relevant to Stage 5.x inter-pool connectivity but not directly to Si Cred
accumulation. The finding that *spatial structure enables local reputation
effects* motivates keeping Si Cred as a local signal rather than a global
broadcast.
**Rejected for Si Cred:** full neighbourhood reputational tracking adds O(N·r²)
state per step; deferred to Stage 5.x.

**Bounded-rationality models with performance-modulated temperature:**
The Softmax / Boltzmann decision rule (σ-temperature) is standard in the ABM
literature (e.g. Hommes 2006 *JEL*; Brock & Hommes 1997 *Econometrica*).
In those models the global temperature is fixed. The Si Cred mechanism
personalises temperature: high-surplus agents get a higher σ_eff, making
them more explorative. This mirrors "confidence" — agents who have recently
harvested well venture further afield.
**Adopted:** σ_Si_eff_i(t) = σ_Si + κ_Si × tanh(si_cred_i(t) / C*_Si).
κ_Si = 0.5 (< C's κ=2.0) because Si has no joint-task amplification channel.

### Mechanism adopted (Stage 5 default)

```
Δsi_cred_i(t) = max(0, harvest_i(t) − metabolism_i(t)) × r_cred_Si
si_cred_i(t)  = si_cred_i(t−1) × (1 − δ) + Δsi_cred_i(t)
σ_Si_eff_i(t) = σ_Si + κ_Si × tanh(si_cred_i(t) / C*_Si)
```

Parameters: r_cred_Si=0.1, δ=0.01 (same as C decay), C*_Si=10.0, κ_Si=0.5.
`enabled=False` recovers Stage 4.5 Si behaviour exactly.

### Rejected alternatives

- **Dyadic reputational Cred:** requires pair interaction log; deferred to Stage 5.x.
- **Wealth-proportional Cred:** direct w_i/mean_w scaling conflates stock and
  flow; surplus-flow (harvest−metabolism) is cleaner because it signals
  *current foraging success*, not accumulated advantage.
- **Binary high/low Cred:** loses gradient information that σ modulation benefits from.

---

*End of Literature Notes — Stage 5 Task 3*
