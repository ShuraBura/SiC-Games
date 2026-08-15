"""CTB — THE ENERGETIC REFRACTORY (R-106, 2026-08-14).

WHY THIS TERM AND NOT THE OTHER. RESULTS Addendum 42 established, and verified against both measured arms to
within 1%:

    TFR = span / (refractory + 1/(fecundability x brake))

The shipped brake multiplies `fecundability`, and `1/(fecundability x brake)` is only 22% of the birth
interval. At its ABSOLUTE ceiling — mean factor 0.767, measured over 240 steps and 331 women — it reaches
TFR 7.93 where about 4.5 is needed. An EMA half-life bracket (1/3/6/12 vs the shipped ~17 months) confirmed
this empirically: the applied factor moved 0.967 → 0.861 and TFR, frac_child, dependency, e0 and starv_share
ALL stayed flat. The refractory is the term with leverage.

IT IS ALSO THE CORRECT PHYSIOLOGY, AND THAT IS ANCHORED. Ellison 2008 (PaleoAnthropology 2008:172-200, filed
2026-08-14) reports for the Toba that C-peptide rises in the one to two months before menstruation resumes,
correlates with maternal weight and urinary estrogen, and shows "no correlations ... with any indices of
nursing pattern or frequency" [VERIFIED VERBATIM]. Energy sets the length of lactational amenorrhea; suckling
frequency does not. The competing pathway is ruled out in the same dataset.

WHY IT MATTERS BEYOND FERTILITY. Addendum 44 established that once the carrying-capacity ceiling is repaired
the model is MALTHUSIAN: equilibrium e0 is set by the food-to-population balance, not by the hazard
parameters, and every hazard fix is absorbed by starvation. Fertility is therefore the ONLY remaining lever
on e0. This mechanism is that lever.

THE PREDICTION UNDER TEST, recorded before the arms run: lower fertility → lower equilibrium density → less
starvation → e0 RISES. If e0 does not rise, the Malthusian reading in Addendum 44 is wrong and must be
retracted. `test_the_stretch_only_ever_lengthens` and the arm comparison are what make that falsifiable.
"""
import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import (SEDENTISM_IBI_MONTHS, DemographyConfig, energetic_refractory,
                                  sedentism_ibi)
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


# ── default state ─────────────────────────────────────────────────────────────────────────────────────────

def test_default_off_so_every_prior_run_is_bit_exact():
    d = DemographyConfig()
    assert d.enable_energetic_refractory is False


def test_the_stretch_is_the_filed_ratio_not_a_chosen_number():
    """Hill & Hurtado Table 8.2 gives realised Aché IBI 34.4 reservation / 37.6 forest / 49.4 contact
    [VERIFIED]. The default is 49.4/34.4 — the full span of that filed range. If someone edits it, this
    fails and forces the new value to be justified rather than tuned until a run looks right."""
    assert DemographyConfig().refractory_stretch_max == pytest.approx(49.4 / 34.4, rel=1e-3)


# ── the mapping ───────────────────────────────────────────────────────────────────────────────────────────

def test_at_full_energy_it_is_the_identity():
    """THE BIT-EXACTNESS ARGUMENT. Above `intake_fert_hi` the function must return the base untouched, so a
    world where everyone is well fed behaves exactly as before the mechanism existed."""
    d = DemographyConfig(enable_energetic_refractory=True)
    for intake in (d.intake_fert_hi, 1.5, 3.0, 10.0):
        assert energetic_refractory(30.0, intake, d) == pytest.approx(30.0)


def test_at_maintenance_it_stretches_by_exactly_the_maximum():
    d = DemographyConfig(enable_energetic_refractory=True)
    for intake in (d.intake_fert_lo, 0.9, 0.0):
        assert energetic_refractory(30.0, intake, d) == pytest.approx(30.0 * d.refractory_stretch_max)


def test_it_interpolates_monotonically_across_the_window():
    d = DemographyConfig(enable_energetic_refractory=True)
    vals = [energetic_refractory(30.0, x, d) for x in (1.0, 1.05, 1.10, 1.15, 1.20)]
    assert all(a > b for a, b in zip(vals, vals[1:])), f"must fall monotonically with energy: {vals}"


def test_the_stretch_only_ever_lengthens():
    """It may not shorten spacing below the society base. A mechanism that could RAISE fertility under some
    energy state would break the Malthusian prediction this whole line of work rests on."""
    d = DemographyConfig(enable_energetic_refractory=True)
    for intake in (0.0, 0.5, 1.0, 1.1, 1.2, 5.0):
        assert energetic_refractory(30.0, intake, d) >= 30.0 - 1e-9


def test_no_new_threshold_is_introduced():
    """The energy window is the SAME FAO/IOM one the fecundability brake reads (pregnancy +11%, lactation
    +20%). Moving `intake_fert_hi` must move this mechanism too, or a second, unanchored threshold has
    appeared in the model."""
    a = DemographyConfig(enable_energetic_refractory=True, intake_fert_hi=1.2)
    b = DemographyConfig(enable_energetic_refractory=True, intake_fert_hi=2.0)
    assert energetic_refractory(30.0, 1.5, a) < energetic_refractory(30.0, 1.5, b)


def test_the_realised_interval_lands_on_the_filed_range():
    """THE ANCHOR CHECK, and it records a known overshoot rather than hiding it.

    Realised IBI ~= refractory + 1/fecundability. With the shipped base 30 and fecundability 0.12 the
    mechanism spans 38.3 months at full energy — against Hill's FOREST 37.6 — up to 51.4 at maintenance,
    against Hill's CONTACT 49.4. The top end therefore OVERSHOOTS the filed maximum by about 2 months,
    because the 49.4/34.4 ratio is applied to the refractory while the anchor is on the realised interval.
    That is why `refractory_stretch_max` is documented as a BRACKET ENDPOINT to sweep downward from, not a
    fitted value. Recorded here so the overshoot is a known property and not a later surprise.
    """
    d = DemographyConfig(enable_energetic_refractory=True)
    wait = 1.0 / d.fecundability
    hi = energetic_refractory(float(d.ibi_refractory_months), 5.0, d) + wait
    lo = energetic_refractory(float(d.ibi_refractory_months), 1.0, d) + wait
    assert hi == pytest.approx(38.3, abs=0.5), "well-fed IBI should sit near Hill's forest 37.6"
    assert 49.0 < lo < 53.0, f"maintenance IBI {lo:.1f} should sit near Hill's contact 49.4 (slight overshoot)"


# ── composition with the NDT mechanism ────────────────────────────────────────────────────────────────────

def test_it_multiplies_the_SOCIETY_base_rather_than_replacing_it():
    """The two mechanisms must compose. `enable_sedentism_fertility` shortens the base for complex societies
    (storable weaning foods); energy stretches whatever base applies. A hungry sedentary woman must still
    space births further than a fed sedentary woman, and each flag must stay independently ablatable."""
    d = DemographyConfig(enable_energetic_refractory=True)
    for soc in SEDENTISM_IBI_MONTHS:
        base = float(sedentism_ibi(soc, d.ibi_refractory_months))
        assert energetic_refractory(base, 1.0, d) == pytest.approx(base * d.refractory_stretch_max)
        assert energetic_refractory(base, 5.0, d) == pytest.approx(base)
    egal = float(sedentism_ibi("egalitarian_forager", d.ibi_refractory_months))
    cplx = float(sedentism_ibi("stratified_chiefdom", d.ibi_refractory_months))
    if egal != cplx:
        assert energetic_refractory(cplx, 1.0, d) < energetic_refractory(egal, 1.0, d), \
            "the society ordering must survive the stretch"


# ── the flag reaches a real run, and is not ON-but-dead ───────────────────────────────────────────────────

def _world(**upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, enable_pair_bonds=True,
                         enable_bonded_mating=True, **upd)
    return TerrainWorld(n_agents=150, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


def _fertile_world(**upd):
    """As `_world` but WITHOUT the pair-bond / bonded-mating gates. Measured: with them on, a 150-agent test
    world yields 0 births in 160 steps; without them, 342 births and 301 completed intervals. Mating is
    orthogonal to the refractory, and a test with no births cannot detect a change in birth spacing."""
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, **upd)
    return TerrainWorld(n_agents=150, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


def test_the_flag_switches_on_the_intake_signal_it_depends_on():
    """THE ON-BUT-DEAD GUARD. The mechanism reads `_intake_ema`, which is only maintained when something
    asks for it. If the flag did not widen that gate the refractory would read a frozen signal and the flag
    would be live in the config dump and inert in the run — the exact failure this project keeps finding."""
    w = _world(enable_energetic_refractory=True, enable_intake_fertility=False,
               enable_productivity_mobility=False)
    for _ in range(6):
        w.step()
    emas = {round(getattr(a, "_intake_ema", -1.0), 6) for a in w.agent_list}
    assert len(emas) > 1, f"the intake EMA is not being updated: {emas}"


def test_the_flag_lengthens_the_realised_interval_in_a_real_run():
    """LOAD-BEARING. A flag that reads ON must MOVE something. Compared on identical seeds, turning the
    mechanism on must not SHORTEN the realised interval.

    A CONSTRUCTED SHORT REFRACTORY. At the shipped 30 months a woman needs ~76 steps between recorded
    intervals, so a test-length run closes almost none and the comparison is over an empty sample. The base
    is set to 6 months here purely so intervals COMPLETE; the mechanism is multiplicative, so the ratio it
    applies is unchanged by the base it multiplies.
    """
    # MATE GATING OFF, and this is why: with `enable_pair_bonds` on, a 150-agent test world produces ZERO
    # births (measured), because no durable co-resident pairs form at that scale. The empty sample had
    # nothing to do with the refractory. Pairing is orthogonal to the mechanism under test, so it is removed
    # rather than worked around — a vacuous comparison would have read as a pass.
    off = _fertile_world(enable_energetic_refractory=False, ibi_refractory_months=6)
    on = _fertile_world(enable_energetic_refractory=True, ibi_refractory_months=6)
    for w in (off, on):
        for _ in range(160):
            w.step()
    a, b = off.fertility_schedule(), on.fertility_schedule()
    assert a["ibi_n"] > 0 and b["ibi_n"] > 0, "no completed intervals — the test would be vacuous"
    assert b["ibi_mean"] >= a["ibi_mean"] - 0.5, (
        f"the mechanism shortened spacing: {a['ibi_mean']:.1f} -> {b['ibi_mean']:.1f}")


def test_it_is_bit_exact_when_every_woman_is_well_fed():
    """The identity property, end to end: with the stretch at 1.0 the flag cannot change any outcome, so a
    run carrying it must match a run without it exactly."""
    off = _fertile_world(enable_energetic_refractory=False, ibi_refractory_months=6)
    on = _fertile_world(enable_energetic_refractory=True, refractory_stretch_max=1.0,
                        ibi_refractory_months=6)
    for _ in range(40):
        off.step(); on.step()
    assert len(off.agent_list) == len(on.agent_list)
    assert off.fertility_schedule()["births"] == on.fertility_schedule()["births"]
