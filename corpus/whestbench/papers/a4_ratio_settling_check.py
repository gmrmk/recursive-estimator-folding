"""Settling check for the 128/3 coincidence (manuscript open item, 2026-08-19).

Claim to test: the measured Haar/Kerdock degree-4 defect ratio 42.6667 = 128/3.
Exact rational derivation. For a union of k frames of n orthonormal vectors in R^n
(antipodally doubled), with Q_4 the normalized degree-4 Gegenbauer on S^(n-1):
  A4_haar(k) = [1 + (n-1) Q4(0)] / (k n)                (cross-frame zonal mean = 0)
  A4_mub(k)  = [1 + (n-1) Q4(0) + n (k-1) Q4(1/16)] / (k n)   (|cross| = 1/sqrt(n) exactly)
Everything in Fractions; no floats until display.
"""
from fractions import Fraction as F

n = 256
d = n

def gegenbauer_normalized(deg, t):
    """Q_deg(t) with Q_deg(1) = 1, three-term recurrence, exact rationals."""
    p0, p1 = F(1), t
    for kk in range(2, deg + 1):
        p2 = (F(2 * kk + d - 4, kk + d - 3) * t * p1) - (F(kk - 1) * F(kk - 2 + 2 * (d - 2) // 2 * 1) )  # careful: use exact recurrence
        # exact recurrence: (k+d-3) P_k = (2k+d-4) t P_{k-1} - (k-1) P_{k-2}
        p2 = ((2 * kk + d - 4) * t * p1 - (kk - 1) * p0) / (kk + d - 3)
        p0, p1 = p1, p2
    return p1

Q4_0 = gegenbauer_normalized(4, F(0))
Q4_c = gegenbauer_normalized(4, F(1, 16))
print("Q4(0)    =", Q4_0, "=", float(Q4_0))
print("Q4(1/16) =", Q4_c, "=", float(Q4_c))

def a4_haar(k):
    return (F(1) + (n - 1) * Q4_0) / (k * n)

def a4_mub(k):
    return (F(1) + (n - 1) * Q4_0 + n * (k - 1) * Q4_c) / (k * n)

k = 126
ratio = a4_haar(k) / a4_mub(k)
print("A4_haar(126) =", float(a4_haar(k)))
print("A4_mub(126)  =", float(a4_mub(k)))
print("ratio exact  =", ratio, "=", float(ratio))
print("128/3        =", float(F(128, 3)))
print("IDENTICAL to 128/3:", ratio == F(128, 3))
# measured values for comparison
print("measured haar 3.136387e-05 vs derived", float(a4_haar(k)))
print("measured kerdock 7.350908e-07 vs derived", float(a4_mub(k)))
# the sweep: does A4_mub(k)/A4_mub(126) have closed structure? print a few
for kk in (1, 2, 63, 126, 128, 129):
    print(f"k={kk:3d}  A4_mub = {float(a4_mub(kk)):.9e}   A4_haar = {float(a4_haar(kk)):.9e}")
