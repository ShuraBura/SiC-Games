"""CTB — DENSITY-DISEASE REFERENCE NORMALISATION (R-106, 2026-08-13).

THE DEFECT THIS ANSWERS. `_a2_mult` multiplies three modulators into Siler's Makeham term `a2`. TWO of them
are reference-normalised so the ANCHOR CONDITION returns exactly 1.0:

    risk_mult(risk_cell, risk_ref, cap) = min(cap, risk_cell / risk_ref)   -> 1 in average-risk terrain
    pathogen_mult(...)                  = (npp/npp_ref) ** gamma           -> 1 at the reference biome

`density_mult` was not. It returned 1.0 only at rho = 0, an EMPTY WORLD. But Gurven & Kaplan 2007 fitted
a2 = 0.0130 on Aché foragers LIVING AT A REAL DENSITY, so that coefficient already contains their
density-dependent disease. Multiplying it again at the same density charges for it twice.

THE MEASUREMENT THAT FOUND IT. Realised e0 is 17.7 yr against a configured 36.6. Decomposed from the run's
own age arrays, the non-starvation hazard runs 1.56x the configured Siler, and the excess is concentrated in
the middle ages (5-10: 2.34x, 15-25: 1.86x, 25-40: 1.80x) where a2 dominates and the infant and senescence
terms do not. `dens_rho_half` = 0.2/km2 sits ABOVE the entire ethnographic range (Binford packing 0.091,
Tallavaara observed HG median 0.119, this model's own capacity ~0.053), so every real forager density sits
on the steep rising limb: at Binford's own anchor the unnormalised term already returns 1.94x.

THE INTERACTION THAT MADE IT LARGE. `aggl_beta` = 1.15 gives increasing returns to crowding, so agents pack
into cells of ~71 occupants = 0.714/km2 — eight times the Binford anchor, 3.6x past half-saturation —
driving the term to 3.34x against its 4.0 ceiling. The maths is the fault; the agglomeration is the
amplifier. `test_agglomeration_pushes_the_term_off_its_calibration_range` pins that pairing, because
fixing the normalisation without noticing the amplifier would leave the second half of the story untested.

WHAT IS DELIBERATELY NOT TESTED HERE. Whether the fix brings e0 to 36.6. It cannot on its own — the
starvation channel is a separate Makeham term worth ~0.018/yr, and a2 modulation cannot remove it. Claiming
otherwise would be the "one fix explains everything" error this arc has already made twice.
"""
import math

import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import ACHE_FOREST, DemographyConfig, density_mult
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

BINFORD = 0.091          # persons/km2 — packing threshold, Binford 2001 [FILED, LITERATURE.md]
D, RH = 3.0, 0.2         # the shipped campaign values for delta / rho_half


# ── default state: nothing changes until the flag is set ──────────────────────────────────────────────────

def test_default_is_off_so_every_prior_run_is_bit_exact():
    d = DemographyConfig()
    assert d.enable_density_reference is False


def test_rho_ref_zero_reproduces_the_historical_form_exactly():
    """The bit-exactness guarantee, at the arithmetic level rather than by assertion."""
    for rho in (0.0, 0.01, 0.091, 0.5, 0.714, 5.0):
        assert density_mult(rho, D, RH, 0.0) == density_mult(rho, D, RH)


def test_the_default_reference_is_the_filed_binford_value():
    """The fix must introduce NO new number. If someone later edits this away from Binford's packing
    threshold, that is a new free parameter and this fails to force the anchor to be restated."""
    assert DemographyConfig().dens_rho_ref == pytest.approx(BINFORD)


# ── the invariant that the other two modulators hold and this one broke ───────────────────────────────────

def test_the_multiplier_is_exactly_one_at_the_reference_density():
    """THE WHOLE POINT. `risk_mult` returns 1 in average-risk terrain and `pathogen_mult` returns 1 at the
    reference biome. This is the same invariant, and its absence is the defect."""
    assert density_mult(BINFORD, D, RH, BINFORD) == pytest.approx(1.0)


@pytest.mark.parametrize("rho_ref", [0.053, 0.091, 0.119, 0.5])
def test_the_invariant_holds_for_any_reference_choice(rho_ref):
    """The three filed candidates are 0.053 (this model's Tallavaara capacity), 0.091 (Binford) and 0.119
    (Tallavaara observed median). The invariant must not depend on which is chosen."""
    assert density_mult(rho_ref, D, RH, rho_ref) == pytest.approx(1.0)


def test_the_unnormalised_form_is_wrong_at_the_anchor_by_the_measured_amount():
    """The NEGATIVE control: state the defect as a number, so a silent revert is caught. Without the
    reference, a forager population at Binford's own density gets its baseline mortality nearly doubled."""
    assert density_mult(BINFORD, D, RH) == pytest.approx(1.94, abs=0.01)


# ── shape: the fix must rescale, not reshape ──────────────────────────────────────────────────────────────

def test_normalisation_preserves_the_shape_and_only_rescales():
    """A normalisation divides by a constant. If it altered the ordering or the curvature it would be a new
    dose-response, not a re-referencing, and the Dunn/Houldcroft citation would no longer cover it."""
    rhos = [0.0, 0.02, 0.091, 0.3, 0.714, 2.0, 50.0]
    raw = [density_mult(r, D, RH) for r in rhos]
    norm = [density_mult(r, D, RH, BINFORD) for r in rhos]
    k = raw[0] / norm[0]
    for a, b in zip(raw, norm):
        assert a / b == pytest.approx(k)
    assert all(x < y for x, y in zip(norm, norm[1:])), "monotonicity in density must survive"


def test_below_the_reference_the_term_now_protects_rather_than_punishes():
    """A population SPARSER than the anchor should carry LESS than the fitted baseline, not more. The
    unnormalised form could never express that — it was >= 1 everywhere, so sparse living was costless but
    never beneficial, and a2 could only ever be inflated."""
    assert density_mult(0.01, D, RH, BINFORD) < 1.0
    assert density_mult(BINFORD * 2, D, RH, BINFORD) > 1.0


# ── the amplifier, pinned alongside the fault ─────────────────────────────────────────────────────────────

def test_agglomeration_pushes_the_term_off_its_calibration_range():
    """MEASURED 2026-08-13: the average living agent sits in a cell of 71.4 occupants = 0.714/km2, against a
    Binford anchor of 0.091 and a half-saturation of 0.2. Even after normalisation the term is large there,
    because the AGGLOMERATION is a separate fault. Pinning both stops the fix being mistaken for a cure."""
    occ_living = 71.4 / 100.0            # cell = 100 km2
    assert occ_living / BINFORD == pytest.approx(7.8, abs=0.2), "8x the packing anchor"
    assert density_mult(occ_living, D, RH) == pytest.approx(3.34, abs=0.02)
    still_high = density_mult(occ_living, D, RH, BINFORD)
    assert still_high == pytest.approx(1.72, abs=0.02)
    assert still_high > 1.5, "normalisation alone does NOT bring the crowded case back to the anchor"


def test_the_fix_cannot_close_the_whole_e0_gap_on_its_own():
    """HONESTY GUARD. The starvation channel is a SECOND Makeham term measured at ~0.018/yr, and no amount of
    a2 modulation removes it. If a later change makes this test fail, someone has quietly attributed the
    whole life-expectancy gap to one mechanism again."""
    DA = 1 / 12.0
    ages = [i * DA for i in range(1200)]
    def e0(extra_makeham):
        return sum(math.exp(-(ACHE_FOREST.cumulative_hazard(a) + extra_makeham * a)) for a in ages) * DA
    assert e0(0.0) == pytest.approx(36.6, abs=0.3)
    assert e0(0.018) < 24.0, "the starvation Makeham term alone still costs >12 yr of e0"


# ── the flag reaches a real run ───────────────────────────────────────────────────────────────────────────

def _world(**upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, enable_density_disease=True,
                         dens_delta=D, dens_rho_half=RH, **upd)
    return TerrainWorld(n_agents=80, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


def test_the_flag_changes_the_realised_a2_multiplier_in_a_real_run():
    """LOAD-BEARING CHECK (the CTB corollary added 2026-08-06): a flag that reads ON must MOVE something.
    Crowd a cell well past the reference and compare the multiplier the model itself computes."""
    off = _world(enable_density_reference=False)
    on = _world(enable_density_reference=True)
    for w in (off, on):
        w.step()
    cell = off.agent_list[0].pos
    occ = {cell: 60}
    m_off = TerrainWorld._a2_mult(off, off.agent_list[0], occ)
    m_on = TerrainWorld._a2_mult(on, on.agent_list[0], occ)
    assert m_on < m_off, "the reference normalisation must reduce the multiplier at high density"
    assert m_off / m_on == pytest.approx(density_mult(BINFORD, D, RH), rel=0.05)
