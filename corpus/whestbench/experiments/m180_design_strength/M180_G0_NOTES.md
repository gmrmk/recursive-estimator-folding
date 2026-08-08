# M180 G0 notes — total kill, no arm promoted

Date: 2026-08-08. Predeclaration: `M180_PREDECLARATION.md`. Runner:
`run_m180_g0.py`. Results: `m180_g0_results.json`. Per-net raw estimates:
`m180_g0_partial_net{101,202,303}.npz` (16 replicates x 6 arms x 256
output coordinates each).

## Deviations from the predeclaration (all stated loudly)

1. **Plain numpy, no flopscope metering** — the sanctioned N8a-style G0
   deviation (variance-only gate; no billed-FLOP claim is made here).
2. **16 rotation seeds, not the minimum 12** — the predeclaration says
   >= 12; a timing probe (2.1 s/forward) showed 16 fits the timebox, and
   16 matches the N8a harness for cross-check comparability. Total wall
   ~12 min (226/254/241 s per net).
3. **Arm C partition is frame-level round-robin** (frame i -> group
   i mod k), not literal symmetry-group cosets: 126 frames is not
   divisible by 4 or 8, so equal frame-count cosets do not exist for
   k in {4,8}. Round-robin preserves matched total n exactly (every
   direction appears exactly once) and is the natural stratification of
   the frame index. Group 0 reuses Arm A's rotation to maximize pairing.
4. **Arm D frame 0 reuses Arm A's rotation** (frames 1..125 get
   independent Haar rotations). Marginal distribution is unchanged;
   the shared component only tightens the paired comparison.
5. **Checkpointed execution** — each net wrote a partial .npz and the
   runner was invoked once per net (10-minute shell cap), aggregating
   after the last. Purely operational; one deterministic seed schedule.

## What Arm B actually is (exact construction)

126 frames x 256 rows, every row at exact radius mean_chi(256) =
15.98438..., antipodally doubled downstream, randomized by the shared
per-replicate global Haar rotation (same seeds as Arm A):

- **63 frozen Kerdock frames** — the first 63 of the trimmed 126-frame
  phased-Hadamard set from `kerdock_phases.npz` (rows [2:65] of the
  asset).
- **1 identity frame** — mutually unbiased to every phased-Hadamard
  frame (|<e_i, h_j>| = 1/16 = 1/sqrt(256) exactly).
- **31 Haar-MUB pairs (62 frames)** — per pair, a Haar orthogonal
  Q_j and its Walsh partner H_norm @ Q_j; the pair is mutually unbiased
  because Q (H_norm Q)^T = H_norm^T, all entries of magnitude exactly
  1/sqrt(256) (asserted at build time). Drawn once from seed 424242 —
  Arm B is a frozen design, like Arm A.

mub2_orthogonal_fold3 disposition (read before reuse): no REPORT.md
exists; `premise5.json` shows the mub2 estimator was **performance-
killed** (mean raw MSE 2.42e-7 vs baseline 1.59e-7 on the premise run),
not correctness-killed. Its construction is the candidate's own and is
mathematically sound, so reuse was permitted; it was **reimplemented in
plain numpy** and no mub2 asset was loaded (`premise5.npz` is a premise
file and stayed untouched per the firewall).

Why 63+63 and not "Kerdock + more Kerdock-unbiased frames": the Kerdock
family is already (essentially) the maximal real MUB family in R^256 —
only ~3 frames in the whole space are unbiased to ALL 126 existing
frames (the identity and the two trimmed phase rows). A genuine
augmentation at matched n therefore has to displace Kerdock frames with
frames from a different MUB family, which is exactly what this arm
tests.

## Results (16 paired rotation seeds, 3 nets, matched n = 64,512)

Per-net variance of the final-layer mean estimate (mean over 256 output
coordinates of the across-seed variance), ratio = arm / Arm A:

| net | var Arm A | B ratio | C k=2 | C k=4 | C k=8 | D |
|-----|-----------|---------|-------|-------|-------|----|
| 101 | 2.035e-7 | 1.461 | 1.363 | 1.207 | 1.811 | 1.488 |
| 202 | 5.690e-7 | 1.122 | 1.090 | 0.894 | 0.946 | 1.063 |
| 303 | 2.178e-7 | 1.382 | 1.412 | 1.587 | 1.922 | 1.809 |

Aggregate (geomean over nets) with paired bootstrap 95% CI (4000 draws,
replicate indices resampled jointly across arms):

| arm | ratio | reduction | 95% CI | verdict |
|-----|-------|-----------|--------|---------|
| B mub mix          | 1.3135 | -31.3% | [1.033, 1.661] | **KILL** |
| C coset k=2        | 1.2801 | -28.0% | [0.967, 1.652] | **KILL** |
| C coset k=4        | 1.1962 | -19.6% | [0.933, 1.518] | **KILL** |
| C coset k=8        | 1.4879 | -48.8% | [1.125, 1.919] | **KILL** |
| D per-frame remix  | 1.4194 | -41.9% | [1.089, 1.877] | **KILL** |

Gate check: every arm has reduction < 10% (all are variance
*increases*), so every arm is killed; no promotion. Kills are final for
the arms per the predeclaration.

## Verification (two independent signals beyond the gate numbers)

1. **Unbiasedness agreement** — all arms estimate the same fixed-radius
   spherical mean; their replicate-means agree with Arm A's within
   ~0.5 SEM (0.01–0.04% relative) on every net. A radius, scale, or
   rotation bug in any arm's construction would show up here at the
   percent level; none does.
2. **External cross-check** — Arm A reproduces the N8a G0 kerdock arm's
   per-net variances to 6 significant figures at the same nets and
   rotation seeds (2.0349e-7 / 5.6901e-7 / 2.1781e-7; ratio 1.0000),
   confirming the reused loading/forward/pairing code is faithful and
   the baseline is the same object N8a measured.

Radius asserts (Kerdock and Arm B builds) and the MUB pair-property
assert (|Q (H_norm Q)^T| = 1/16) all passed at build time.

## Interpretation (honest, within-G0 only)

The frozen Kerdock design beats every predeclared alternative, and the
pattern is informative: the arms that *fragment the shared rotation*
(C, D) lose more as fragmentation increases (k=4 < k=2 < k=8 ~ D on the
two nets that drive the aggregate), and *replacing half the coherent
family with locally-unbiased random pairs* (B) loses ~31%. Both point
the same way — the design's strength lives in the mutual unbiasedness
of ALL 126 frames under ONE shared rotation, i.e., the inter-frame
coherence is doing negative-covariance work that every mutation here
destroys. Net 202 is the exception (C k=4 at 0.894) but is a single
net inside a CI that spans 1.0.

The M180 design-strength family is closed at G0: the angular design
axis, as mutated here (MUB mix, rotation stratification, per-frame
remix), does not contain a >= 10% variance win at matched n. No G1-G4
work occurs. No claim about other families.
