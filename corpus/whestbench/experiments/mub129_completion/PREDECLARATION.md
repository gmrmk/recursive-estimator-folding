# M-MUB129 — predeclaration: does completing the real-MUB set pay?

**Author:** opus-5. **Written:** 2026-08-12, before any measurement code was run.
**Lane:** L7 generation (output-side / design-side search, reopened by P1's
withdrawal — `HANDOFF_OPUS5_20260812.md:228-231`). No kill is revived by this.

## 0. Mechanism

The deployed GUARDS design uses **126** phased-Hadamard frames
(`kerdock_v3_estimator.py:47,51,52`: `n_base = 126*256`, `phase_start = 2`,
`phase_stop = 128`), each frame `H_256 diag(phi_s) / 16` (`:103-132`),
antipodally doubled to **64,512** points. It is an exact spherical 2-design, and
by antipodality an exact 3-design.

The Delsarte-Goethals-Seidel lower bound for an antipodal spherical 4-design in
`S^255` (which is automatically a 5-design) is `2*C(257,2) = 65,792`. Moller's
theorem extends the same bound to arbitrary **positive-weight** cubature on the
sphere with no antipodality hypothesis, so no reweighting escapes it.

- 126 frames -> 64,512 points. **1,280 below the floor. Cannot be a 4-design.**
- 128 frames -> 65,536 points. **256 below the floor. Also cannot be.**
- **129 frames -> 66,048 points. Clears by exactly 256.**

129 = d/2 + 1 is the maximum number of real MUBs in `R^d` for `d` a power of
four, and 256 = 4^4. The 129th frame is the **standard basis**, which is
mutually unbiased with every `H diag(phi)` frame because
`<e_i, (H diag(phi))_j>/16 = H_ji phi_i / 16`, of modulus 1/16.

Under the Walsh doubling `d = 4^k`, the complete antipodal real-MUB design has
`N = (d/2+1)*d*2 = d^2 + 2d` points against a floor of `2*C(d+1,2) = d^2 + d`,
i.e. **it clears by exactly `d` at every level of the recursion**: (4, 24, 20),
(16, 288, 272), (64, 4224, 4160), (256, 66048, 65792).

**Hypothesis.** Completing 126 -> 129 frames annihilates the degree-4 quadrature
error exactly, and the variance so removed exceeds the 2.381% compute increase.

## 1. Why this needs no truth, scorer, or holdout read

For a fixed equal-weight point set randomly rotated by Haar `R`,
`E_R[(1/N) sum_i f(R u_i)] = (1/N) sum_i E_R[f(R u_i)] = integral f`
exactly, for every point set. The estimator is therefore **exactly unbiased**,
so `MSE = Var_R` identically. The comparison is a variance comparison over
rotation draws on locally generated development networks. **No truth read, no
scorer read, no holdout, no challenge network, no submission, no leaderboard
contact.**

## 2. Estimand and design of the experiment

Both estimators are evaluated from **one shared forward pass**: evaluate all 129
frames per (network, rotation), then form

- `Q_126` = mean over frames `s = 2..127` (the deployed slice),
- `Q_129` = mean over all 129 frames (standard basis + `s = 0..127`),

antipodally doubled in both cases. Paired on identical networks and identical
rotations, which is the maximum-power comparison available.

Primary statistic, per network, over `R` independent Haar rotations, on the
final-layer (depth-32) mean vector:

```
V126 = mean_over_neurons Var_R[ Q_126 ]
V129 = mean_over_neurons Var_R[ Q_129 ]
```

**Cost ratio, fixed now and deliberately conservative: `C_129/C_126 = 129/126 =
1.0238095…`.** The true ratio is strictly smaller, because the standard-basis
frame needs no Walsh butterfly, so adopting 1.0238 can only understate the
completion's value, never overstate it.

## 3. Kill conditions, fixed before the value exists

**K1 (primary).** KILL the completion if the paired score ratio
`(V129 / V126) * (129/126) >= 1.0`,
i.e. if the variance removed does not pay for the compute added. Equivalently,
KILL unless `V129/V126 < 0.976744…`, i.e. unless the completion removes more
than **2.3256%** of the rotation-draw variance.

**K2 (structural precondition).** KILL, before K1 is read, if any of:
(a) the frozen archive `kerdock_phases.npz` holds fewer than 128 phase rows;
(b) the 129 candidate frames are not pairwise mutually unbiased at exactly
`|<x,y>| = 1/16` for cross-frame pairs and `0` within a frame;
(c) the resulting 66,048-point antipodal set fails the degree-4 moment identity
`sum_y <x,y>^4 = 3N/(d(d+2)) = 3` in exact rational arithmetic.
Any of these means the completion is not a 5-design and the premise is void.

**K3 (protocol).** KILL with zero credit on: any change to the 2.3256% bar,
`R`, the network count, or the rotation seeds after seeing any variance number;
any truth, scorer, or holdout read; any use of a challenge network.

**Reported alongside, with no gate authority:** the exact degree-4 design defect
`A_4 = (1/N^2) sum_x sum_y G_4(<x,y>)` for both designs (a pure-geometry
quantity, expected `> 0` for 126 and `= 0` for 129); the per-network paired
ratios; and the implied variance share removed.

## 4. What each outcome licenses

- **K1 fires:** the 129-frame completion is dead **as a score lever**. The
  design-axis closure result (DGS/Moller at degrees 4 and 6) stands on its own
  as a negative result for the manuscript and is unaffected — it is a theorem
  about what cannot be done, not a claim that doing it would help.
- **K1 does not fire:** licenses *writing* a source-level candidate and its own
  cost predeclaration. It does **not** authorize a submission, a selection
  change, a package, or any hosted run. Those need Jonah's explicit word.

## 5. Standing disclosures

- The corpus's only prior degree-4 energy figure (0.45%, from
  `r0_harmonic_energy_spectrum`) is **inadmissible**: that ledger record is
  killed and its evidence is quarantined as post-charter. No threshold here was
  sized from it, and the 2.3256% bar comes solely from the cost arithmetic.
- The §3b harmonic control-variate failure (+0.83%, CI [-0.6%, +2.4%]) does not
  close this. That was a *finite projection* onto a tractable basis, defeated by
  dispersion across ~1.8e8 harmonic dimensions. The completion annihilates
  degree 4 **exactly and entirely**, by exactness rather than by projection, and
  is a different mechanism.
- GUARDS remains the incumbent throughout. Nothing here touches deployed bytes.
