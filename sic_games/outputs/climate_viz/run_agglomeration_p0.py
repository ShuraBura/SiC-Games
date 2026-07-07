"""P0 (offline): choose the returns-to-labour L(n) so per-capita p(n)=R*L(n)/n is SINGLE-PEAKED at a village-scale
n* (~100-300). No model. Reports p(n)/p(1) (the aggregation incentive) across n for candidate forms. Key checks:
 (a) p rises from n=1 (aggregation bootstraps from TINY groups -- no min_pool needed, unlike the discrete version);
 (b) peak at a realistic n*; (c) not so sharp it is a singularity.
"""
import math

NS = [1, 2, 5, 10, 25, 50, 100, 150, 200, 300, 500, 800]

def smooth(n, alpha, K):   # L=n^alpha * exp(-n/K) -> p ~ n^(alpha-1) exp(-n/K), peak at (alpha-1)K
    return n**(alpha - 1) * math.exp(-n / K)

def kinked(n, alpha, C):   # L=min(n^alpha, C) -> p = min(n^alpha,C)/n, peak at n*=C^(1/alpha)
    return min(n**alpha, C) / n

configs = [
    ("smooth a1.5 K300", lambda n: smooth(n, 1.5, 300), (1.5 - 1) * 300),
    ("smooth a2.0 K150", lambda n: smooth(n, 2.0, 150), (2.0 - 1) * 150),
    ("smooth a1.3 K600", lambda n: smooth(n, 1.3, 600), (1.3 - 1) * 600),
    ("kinked a1.5 C2500", lambda n: kinked(n, 1.5, 2500), 2500 ** (1 / 1.5)),
    ("kinked a1.4 C2000", lambda n: kinked(n, 1.4, 2000), 2000 ** (1 / 1.4)),
]

print("per-capita p(n)/p(1)  (aggregation incentive; >1 means an n-village beats a lone agent)\n")
print(f"  {'config':18s} n*={'':4s} " + " ".join(f"{n:>5d}" for n in NS))
for name, f, nstar in configs:
    p1 = f(1)
    row = " ".join(f"{f(n)/p1:5.1f}" for n in NS)
    print(f"  {name:18s} n*={nstar:4.0f}  {row}")
print("\n  (want: rises from n=2, peak near n*, falls after; peak ratio strong but not singular)")
