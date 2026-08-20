# S15 verdict -- first-layer stratification premise test

Ledger id: `s15_firstlayer_stratification_premise`
Date: 2026-08-09.  Direction set: full antipodally-doubled Kerdock design
(64,512 directions at radius mean_chi(256)=15.98438), no subsample.
Nets: synthetic He, seeds 101/202/303, width 256, depth 32, bias-free,
one Haar rotation each (seed 900000 + net*1000 + 0).

## VERDICT: KILL

The residual is covariate-blind. The best pooled out-of-sample incremental
R^2 across every cheap first-layer covariate set is **0.0156 (1.56%)**,
below the predeclared **5% KILL bar**. No covariate set reaches the 20% PASS
bar on any net (0 of 3). There is no material stratification headroom for a
cheap first-layer conditional/stratified estimator beyond what the design's
exactly-integrated degree-<=2 harmonics already capture.

Gate arithmetic (gate quantity = swap-halves OOS incremental R^2, Base-B):

| covariate set        | net101 | net202 | net303 | pooled mean | nets >=20% |
|----------------------|--------|--------|--------|-------------|------------|
| C1 firing rate       | 0.0051 | 0.0059 | 0.0057 | 0.0056      | 0 |
| C2 \|\|h1\|\|_2       | 0.0111 | 0.0139 | 0.0129 | 0.0126      | 0 |
| C3 top-1             | 0.0012 | 0.0014 | -0.0000| 0.0008      | 0 |
| C3 top-2             | 0.0013 | 0.0045 | -0.0000| 0.0019      | 0 |
| C3 top-4             | 0.0013 | 0.0047 | -0.0000| 0.0020      | 0 |
| C3 top-8             | 0.0026 | 0.0056 | 0.0009 | 0.0030      | 0 |
| **union C1,C2,C3top8** | 0.0136 | 0.0195 | 0.0138 | **0.0156** | 0 |
| C4 control (degree-1)| -0.0000| -0.0000| -0.0000| -0.0000     | 0 |

- PASS bar (>=20% on >=2/3 nets): NOT met by any set.
- KILL bar (pooled < 5%): MET (best = 1.56%).

## Target, covariates, bases (exact definitions)

TARGET  f(u) = neuron-averaged final post-ReLU output = the estimator's
per-direction contribution (the design averages f over directions to estimate
the sphere mean). This is exactly S5's `ybar`; reused (see reuse verification).

COVARIATES (first-layer only, ~1/32 forward cost; a = W1_eff @ u with
W1_eff = R.T @ W[0] in Kerdock coordinates, pre1 = kerdock @ W1_eff):
- C1 firing rate rho(u) = mean_j 1(a_j > 0).  Antipode: rho(-u) = mean_j 1(a_j < 0).
- C2 first-layer output norm ||h1(u)||_2, h1 = ReLU(a).
- C3 top-k projections of h1(u) onto the leading RIGHT singular vectors of
  W1_eff (hidden-space directions, rows of Vt from svd(W1_eff)), k in {1,2,4,8}.
  (W1_eff is laid out (input,hidden) so its right singular vectors live in the
  hidden space where h1 lives -- dimensionally consistent projection.)
- C4 control: raw first-moment linear statistic <u, w_moment>, w_moment the
  unit direction of sum_u (f(u)-fbar) u.  Pure degree-1 -> must re-measure ~0
  because the base already spans all of degree-1.

DEGREE-<=2 BASIS on u (design integrates degrees 0,1,2 exactly -> zero
headroom there; confirmed a 2-design by M191 G0-a).  Let s_m(u) = <u, U_f[:,m]>
be the projection onto left singular vector m of W1_eff (a degree-1 statistic;
{s_m}_{m=0..255} is an orthonormal rotation of {u_j}, so it spans ALL of
degree-1).  Two bases:
- **Base-B (PRIMARY, conservative):** 256 linear {s_m} + 256 diagonal squares
  {s_m^2} + top-16 off-diagonal cross {s_m s_n : m<n<16} = 633 columns.  The
  diagonal squares capture ||pre1||^2 = sum_m S_m^2 s_m^2 EXACTLY, i.e. the
  even part of C2.  Column-centering supplies the constant.
- **Base-A (sensitivity, task-literal lean):** top-8 linear + degree-2 within
  top-8 (incl diagonal) = 45 columns.

Both bases contain only degree-<=2 functions (products of degree-1), so
neither can absorb genuine degree>2 covariate signal; the incremental R^2
measures precisely the degree>2 explanatory power the design does not already
integrate.

## Why Base-B is the correct base (the C4 control decides it)

Base-A grossly overstates headroom: under Base-A the C4 degree-1 control shows
**+0.29 to +0.37 incremental R^2** -- a pure degree-1 statistic "explaining"
30%+ of variance. That is impossible headroom: it is degree-1 content the
design integrates exactly, leaking because Base-A's top-8 linear terms do not
span the first-moment direction. Under Base-B the same control measures
**-0.000** on all three nets: Base-B absorbs degree-1 exactly, so the control
correctly shows zero. Base-A's inflated covariate numbers (C2 ~11%, union
~11%) are the same leakage and are dismissed. Every gate number above uses
Base-B, whose control passes.

## Split-sample method (gate quantity)

Coefficients are fit on one random half of the directions and the incremental
R^2 is evaluated on the held-out half, swap-halves averaged (fit A -> eval B,
fit B -> eval A, mean). Antipodal pairs {u, -u} are kept in the SAME half
(they are deterministically related; splitting them would leak). Split seed
777000 + net. Base and full share the split per direction so the incremental
is paired. In-sample incrementals (reported in the JSON) inflate modestly;
the OOS numbers above are the gate quantity.

## R2_base interpretation (verification #3)

R2_base is LARGE, not ~0: Base-B explains 36-44% of f's cross-direction
variance (OOS 0.361 / 0.404 / 0.439). This is EXPECTED and benign, not the
failure mode the predeclaration flagged. R2_base measures cross-direction
variance of f within a fixed rotation, NOT estimator error. f genuinely has
large degree-<=2 content (dominated by ||pre1||^2, captured by the diagonal
squares); that content makes f vary across directions but the design
integrates its MEAN exactly (M191 G0-a confirmed degree-2 quadrature error
~0), so it contributes ZERO to estimator variance. The ~40% is "free"
integrated variance. The stratifiable residual is the remaining ~60% (degree
>2), of which the covariates explain only ~1.6% of total (~2.6% of the
residual). The C4 control (=0 under Base-B) and the positive control confirm
the base is correctly calibrated to degree-<=2.

## Positive control (verification #2) -- instrument confirmed

A KNOWN degree-4 zonal harmonic regressed on f (t = <u,axis>/mean_chi):
- Single top-singular-axis raw-t4 R^2 (== (a.u)^4 form, M191's monomial):
  **0.00149 / 0.00122 / 0.00219** across nets -- squarely in M191's reported
  per-harmonic 0.0018-0.0023 band (`m191_g0b_results.json` r2_summary.deg4).
  Instrument NOT wildly different: confirmed.
- Pure degree-4 R^2 (deg-2 confound removed via increment of t^4 over [1,t^2]):
  **~6e-6 to 1.2e-5** -- three-to-four orders smaller than the raw monomial.
  The apparent degree-4 "signal" is almost entirely degree-2 contamination
  (which the design integrates exactly); genuine degree-4 content is
  negligible. This is the mechanism behind both this KILL and M191's own KILL
  (harmonic CV gave only 0.8% reduction).
- Supplementary: M191's 12-axis raw-t4 basis reproduced here gives 0.0072-0.0089
  (same order as M191's 0.0018-0.0023; the exact value differs because M191
  regressed a truth-based CV residual with a measured noise floor subtracted,
  a different target than this cross-direction-variance R^2). The single-axis
  match above is the direct, valid comparison.

## Limitations

- Covariates enter the regression LINEARLY, so nonlinear covariate structure
  (e.g. a binning stratifier) is not directly measured here. Two facts bound
  that gap: (a) the dominant nonlinear transform of C2, its square ||pre1||^2,
  is already an explicit Base-B feature (the diagonal singular squares), so its
  incremental is measured and folded into the C2/union numbers; (b) even
  Base-A, which leaves far more residual for a covariate to claim, tops out at
  ~11%, and the C4 degree-1 control shows +0.29 to +0.37 under Base-A --
  proving that 11% is spurious degree-<=2 leakage, not covariate headroom. A
  nonlinear stratifier would have to beat both the ~1.6% Base-B ceiling and the
  degree-<=2 exactness the design already exploits.
- Base-B removes all of degree-1 but only a subset of the ~33k-dim degree-2
  space (the 256 diagonal + 120 dominant cross singular terms). Residual
  degree-2 leakage would bias the incremental UPWARD (toward false PASS), so a
  1.56% result is a conservative KILL.
- One rotation per net (r=0), 3 nets -- matches the S5/P2/M191 lineage; not a
  rotation ensemble.

## Reuse verification (two independent signals, both exact)

Target f reused from S5 arrays. Reuse validated two ways:
1. d1 recomputed from my independent pre1 vs saved S5 d1: max abs diff =
   **0.0** on all three nets (confirms weights + rotation + W1_eff + kerdock
   all identical to S5).
2. Net-101 full 32-layer forward recompute of ybar vs saved: max abs diff =
   **0.0** (bit-identical; confirms the reused target end-to-end).

Exact reused files (read-only):
- `../s5_kink_concentration/s5_net101_arrays.npz` (ybar, d1)
- `../s5_kink_concentration/s5_net202_arrays.npz`
- `../s5_kink_concentration/s5_net303_arrays.npz`
- `../n8a_rqmc_kerdock/run_n8a_gates.py` (imported: load_kerdock_directions,
  he_mlp_weights, haar_rotation, WIDTH/DEPTH/MEAN_CHI_256/N_BASE)
Reference reproduced: `../pb1_premise_battery/m191_g0b_results.json`
(deg4 R^2 0.0018-0.0023).

## Firewall

Synthetic He nets only; n8a machinery + S5 arrays + m191 results loaded
read-only (n8a loads the frozen v3 sampling asset kerdock_phases.npz
read-only); no dataset/truth/scorer/submission; no git; no ledger edits; no
touch of any m243_*/m244_*/m245_*/*_fable_oracle lane; writes confined to
this directory.

## Files
- `run_s15.py` -- harness
- `s15_results.json` -- full per-net / per-covariate-set numbers
- `S15_VERDICT.md` -- this document
