"""CC-1 Tallavaara capacity mode. Locks the segmented regression values, the hump shape, the persons/cell units,
and that the mode is selectable (default 'linear' unchanged)."""
import math
import numpy as np
from sic_games.capacity import density_tallavaara, NPPCapacityField, TALL_BP


class _F:
    def __init__(self, npp):
        self.npp_gm2 = np.full((10, 10), float(npp)); self.isWater = np.zeros((10, 10), int)


def test_density_matches_regression():
    # ln(d) = -0.1352714 + 0.0028623*npp - 0.0030745*(npp-1371.664)+
    for npp in (300, 633, 1372, 2000):
        exp = math.exp(-0.1352714 + 0.0028623*npp - (0.0030745*(npp-1371.664) if npp > 1371.664 else 0.0))
        assert abs(float(density_tallavaara(npp)) - exp) < 1e-9


def test_hump_shape():
    # rises to the breakpoint, then slightly declines (pathogen-limited high-NPP)
    d = [float(density_tallavaara(n)) for n in (300, 700, 1200, 1372, 1800, 2600)]
    assert d[0] < d[1] < d[2] < d[3]                          # rising up to the breakpoint
    assert d[3] > d[4] > d[5]                                 # declining above it
    assert abs(density_tallavaara(TALL_BP + 0.0) - density_tallavaara(TALL_BP - 0.0)) < 1e-6   # continuous at BP


def test_units_persons_per_cell():
    # tallavaara: E = density(#/100km2 = persons/cell) * burn ; linear: min(0.5,.3*npp/1360)*100*burn
    burn = 1000.0
    ft = NPPCapacityField(_F(633), burn, mode="tallavaara")
    assert abs(ft.level(1, 1) - float(density_tallavaara(633)) * burn) < 1e-6
    fl = NPPCapacityField(_F(633), burn, mode="linear")
    assert abs(fl.level(1, 1) - min(0.5, 0.3*633/1360.0)*100*burn) < 1e-6
    assert ft.level(1, 1) < fl.level(1, 1)                    # Tallavaara more conservative at low NPP


def test_default_mode_is_linear():
    assert NPPCapacityField(_F(633), 1000.0).mode == "linear"
