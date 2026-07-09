"""Neutral-marker genome — emergent population genetics (relatedness, inbreeding, effective population size, drift).

Haploid **infinite-allele** model: each of `L` loci holds an allele-id (int). Each founder is seeded with `L` distinct
random allele-ids (a unique founder signature). A child inherits each locus from mother or father with probability ½
(Mendelian recombination); optional low mutation reintroduces novel alleles. Because founders start all-distinct and
(without mutation) alleles only propagate by descent, **identity-by-state ≈ identity-by-descent**, so:

    relatedness(a, b) = fraction of loci sharing an allele-id

reproduces the standard coefficients as an expectation — full sibs ≈ 0.5, half sibs / grandparent ≈ 0.25, first
cousins ≈ 0.125 — *above the drifting population baseline* (as alleles fix, the baseline rises = the inbreeding /
N_e signal). Fixed size (`L` ints) per agent ⇒ O(L) relatedness, scales to 1e5 agents.

NB this is a **diagnostic / enrichment** substrate, NOT the marriage rule: forager exogamy is *cultural* (lineage /
clan; handled by the connubium). Default OFF ⇒ agents carry no genome and this module is never touched (bit-exact).
"""
from __future__ import annotations
import numpy as np

GENOME_LOCI = 32          # default number of neutral loci (relatedness resolution ~1/L)
_ALLELE_BITS = 31         # allele-ids drawn as 31-bit ints (fit signed int64, effectively infinite-allele)


class Genome:
    """A haploid multi-locus neutral genome. `loci` is an int64 ndarray of allele-ids, shape (L,)."""
    __slots__ = ("loci",)

    def __init__(self, loci: np.ndarray):
        self.loci = loci

    @classmethod
    def founder(cls, rng, loci: int = GENOME_LOCI) -> "Genome":
        """Seed a founder with `loci` distinct random allele-ids (unique signature; drift/inbreeding start from here)."""
        return cls(np.fromiter((rng.getrandbits(_ALLELE_BITS) for _ in range(loci)), dtype=np.int64, count=loci))

    @classmethod
    def inherit(cls, mother: "Genome", father: "Genome | None", rng, mutation: float = 0.0) -> "Genome":
        """Child genome: each locus from mother or father with prob ½ (one `getrandbits(L)` draw = the L-bit
        recombination mask ⇒ a single RNG call, deterministic). If `father` is None (paternity unresolved), the child
        clones the mother (uniparental). `mutation` (per-locus prob) reseeds a novel allele."""
        L = mother.loci.shape[0]
        if father is None:
            child = mother.loci.copy()
        else:
            bits = rng.getrandbits(L)
            take_mother = np.fromiter(((bits >> i) & 1 for i in range(L)), dtype=bool, count=L)
            child = np.where(take_mother, mother.loci, father.loci)
        if mutation > 0.0:
            for i in range(L):
                if rng.random() < mutation:
                    child[i] = rng.getrandbits(_ALLELE_BITS)
        return cls(child)

    def relatedness(self, other: "Genome") -> float:
        """Fraction of loci sharing an allele-id (identity-by-state ≈ IBD). In [0, 1]."""
        return float(np.mean(self.loci == other.loci))


def expected_heterozygosity(genomes) -> float:
    """Mean over loci of H = 1 − Σ pᵢ² (prob two random gene copies differ). Falls toward 0 as drift fixes alleles;
    its decay rate per generation ≈ 1/Nₑ (haploid) → the effective-population-size read-out."""
    mats = [g.loci for g in genomes if g is not None]
    if len(mats) < 2:
        return 0.0
    M = np.vstack(mats)                                   # (n_agents, L)
    n, L = M.shape
    het = np.empty(L)
    for j in range(L):
        _, counts = np.unique(M[:, j], return_counts=True)
        p = counts / n
        het[j] = 1.0 - float(np.sum(p * p))
    return float(het.mean())


def mean_pairwise_relatedness(genomes, rng, sample_pairs: int = 2000) -> float:
    """Mean relatedness over a random sample of agent pairs — the realized inbreeding/relatedness level of the pool."""
    gs = [g for g in genomes if g is not None]
    if len(gs) < 2:
        return 0.0
    n = len(gs)
    acc = 0.0
    k = min(sample_pairs, n * (n - 1) // 2)
    for _ in range(k):
        i = rng.randrange(n)
        j = rng.randrange(n)
        while j == i:
            j = rng.randrange(n)
        acc += gs[i].relatedness(gs[j])
    return acc / k
