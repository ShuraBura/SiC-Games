"""Neutral-marker genome: relatedness coefficients, drift, and default-OFF bit-exactness."""
import random
import numpy as np
import pytest

from sic_games.genome import Genome, expected_heterozygosity, mean_pairwise_relatedness, GENOME_LOCI


def test_founder_distinct_high_heterozygosity():
    rng = random.Random(0)
    gs = [Genome.founder(rng, loci=64) for _ in range(50)]
    # unique founders → essentially all alleles distinct → H ≈ 1
    assert expected_heterozygosity(gs) > 0.98
    # two distinct founders share ~0 loci
    assert gs[0].relatedness(gs[1]) < 0.05


def test_relatedness_coefficients_mean():
    """Over many realizations: full sibs ≈ 0.5, parent–offspring ≈ 0.5, unrelated ≈ 0 (L large)."""
    rng = random.Random(1)
    L = 256
    sib, par, unr = [], [], []
    for _ in range(200):
        mom, dad = Genome.founder(rng, L), Genome.founder(rng, L)
        s1, s2 = Genome.inherit(mom, dad, rng), Genome.inherit(mom, dad, rng)
        sib.append(s1.relatedness(s2))
        par.append(mom.relatedness(s1))
        unr.append(mom.relatedness(Genome.founder(rng, L)))
    assert abs(np.mean(sib) - 0.5) < 0.03
    assert abs(np.mean(par) - 0.5) < 0.03
    assert np.mean(unr) < 0.02


def test_inherit_uniparental_when_no_father():
    rng = random.Random(2)
    mom = Genome.founder(rng, 32)
    child = Genome.inherit(mom, None, rng)          # paternity unresolved → clone mother
    assert child.relatedness(mom) == 1.0


def test_relatedness_bounds():
    rng = random.Random(3)
    a, b = Genome.founder(rng, 32), Genome.founder(rng, 32)
    assert 0.0 <= a.relatedness(b) <= 1.0
    assert a.relatedness(a) == 1.0


def test_heterozygosity_falls_under_shared_ancestry():
    """A pool descended from one couple has far lower H than a pool of distinct founders (drift/inbreeding)."""
    rng = random.Random(4)
    mom, dad = Genome.founder(rng, 64), Genome.founder(rng, 64)
    kin = [Genome.inherit(mom, dad, rng) for _ in range(50)]
    founders = [Genome.founder(rng, 64) for _ in range(50)]
    assert expected_heterozygosity(kin) < expected_heterozygosity(founders)


def test_mutation_reintroduces_variation():
    rng = random.Random(5)
    mom = Genome.founder(rng, 64)
    # clone with high mutation → child differs from mother at some loci
    child = Genome.inherit(mom, None, rng, mutation=0.5)
    assert child.relatedness(mom) < 1.0


def test_default_off_no_genome_carried():
    """enable_genome defaults False ⇒ agents carry _genome=None (module never touched → bit-exact path)."""
    from sic_games.demography import DemographyConfig
    cfg = DemographyConfig()
    assert cfg.enable_genome is False
