# Physics sweep — "nonlinear" cluster mechanism map (read-only, no execution)

Agent: Opus-5 mechanism cartographer. Date 2026-08-10. Firewall respected:
nothing was executed, no estimator run, no measurement, no git, no network.
Every number below is quoted from a committed artifact and cited to its file.

Concepts assigned: Chua attractors / chaotic dynamics; strange attractors and
their invariant measures; "a saddle of primes" / saddle-point / steepest
descent; momentum optimisation for escaping saddles; the GW quadrupole formula
h_ij = (2G/c^4 r) Qbar_ij(t - r/c) and multipole expansions.

Sharp question posed: does a saddle-point / Laplace evaluation of the sphere
integral give anything at depth 32, and does multipole structure suggest a
truncation the flat degree-4 spectrum does not already forbid?

ANSWER TO BOTH: no. The saddle lane has exactly one real exponent (the radial
Gaussian) and the champion already evaluates it EXACTLY rather than
asymptotically; the angular integral after radial conditioning carries no
exponent at all, so steepest descent has no object. The multipole lane is
forbidden twice over — once by a counting theorem (dim H_4 = 1.83e8 vs N =
32,256) and once by direct measurement of the one algebraic escape from that
count (the 129-frame exact 5-design, built, verified, worth <= 0.42% against a
2.33% break-even).

---

## 1. Saddle-point / steepest descent (Laplace on the Gaussian exponent)

The problem after positive 1-homogeneity is E[f] = E[r] * mean_{S^255} g(u).
There are three candidate saddle objects and they dispose differently.

### 1a. Radial saddle — ALREADY-IN-CHAMPION, and exactly, not asymptotically

The only genuine exponent in the whole problem is -|x|^2/2. Laplace on it
gives r* = sqrt(d-1), i.e. chi-concentration. The champion does not use the
asymptotic expansion; it uses the exact chi mean by positive homogeneity.
Ledger record `gen8_resnet_layernorm_reduction`: "LayerNorm shadow = radial
conditioning (2.14x, exact by positive homogeneity)". An asymptotic Laplace
series can only degrade an already-exact evaluation. Nothing to gain.

### 1b. Angular saddle — DOES NOT EXIST

After radial conditioning the remaining integral is against the UNIFORM measure
on S^255. There is no exponent, so there is no stationary phase and no
steepest-descent contour. Worse, g is piecewise linear and non-analytic across
the conical kink set: S9 §1.1 states f is PL on finitely many closed convex
polyhedral cones with grad f jumping across every facet of the kink set K, so
there is no analytic continuation to deform a contour through. Any exponent
introduced by hand is an
importance-sampling tilt = reweighting = failure family F4, which the god node
forbids (GOD_NODE_SYNTHESIS_20260810.md: max-entropy speckle has no
reweighting handle; S15 <= 1.56%, S18 2.371e-5 < 2.63e-5 bar).

### 1c. Large-width saddle — ALREADY-KILLED at 9.6e-5

The n -> infinity saddle of the layer-wise measure IS the mean-field / Gaussian
closure. Scored as a standalone estimator in `t2_fullcov_closure_standalone_
estimator` [killed]: 9.6e-5 vs sampling 2.818e-7, ~340x. Its 1/n correction
(Yaida-Roberts style finite-width effective theory) is S12 route (a): the
transmission gate passes (0.890 vs S8's fitted 0.869-0.879) but the curve gate
FAILS 4/7 on every net — "the deterministic flow leaves the normalized
correlation curve essentially at mean field". A correction that leaves the
curve at mean field cannot close a 340x gap.

### 1d. "A saddle of primes" — NO PRECISE MECHANISM

Circle-method / prime-counting saddle points have no object here: there is no
arithmetic generating function, no exponential sum, no lattice count in the
estimand. Recording it as no-mechanism rather than inventing one.

---

## 2. Multipole / quadrupole truncation

### 2a. Truncation at low ell — ALREADY-IN-CHAMPION and next rung ALREADY-KILLED

The exact 2-design nulls ell <= 2; antipodal doubling to 64,512 nulls all odd
ell. That IS the multipole truncation, already spent.

The next rung (null ell = 4, the "quadrupole" of the residual) is forbidden by
counting before it is forbidden by flatness. S6_VERDICT.md, exact:

    dim H_4(S^255) = 183,148,480      (two independent formulas agree)
    dim H_6(S^255) = 414,173,091,136
    N (design)     = 32,256           = 0.0176% of dim H_4

A design annihilating ell = 4 in general position needs >= dim H_4 nodes, i.e.
5,678x the champion's point budget. S6 also measures the consequence: the
design is a near-perfectly tight rank-N frame on H_4, tr(A^2) = 1.0000310/N,
and D's spectrum is three shells at ~1/N plus a -1/m sea of multiplicity
183,116,224. Top-100 eigenvalues carry 0.32% of tr(D^2).

The ONE algebraic escape from the counting bound — the Kerdock/real-MUB
completion, which reaches an exact 5-design at only 66,048 points — was built
and measured in S11_VERDICT.md:

    126-frame Kerdock:  Phi4/Welch = 1.015811,  deg-4 error present (1.58%)
    129-frame complete: Phi4/Welch = 1.0000000000, deg-4 error identically 0
    measured MSE benefit attributable to deg-4 exactness: <= +0.18%
      (point-count-matched, an upper bound)
    corroborated: m191 cv_deg4 +0.42%, R^2_deg4 ~0.2%
    cost break-even: 2.32558%   -> RE-KILLED

So the multipole truncation is not merely forbidden by the flat spectrum; the
exact-5-design version was constructed, certified to machine precision, and
measured worth roughly one fifth of what it costs.

Also: `m180_design_strength_g0` [killed] (four design-mutation arms, all < 10%
variance reduction) and `gen8_rival_5design_adjudication` [killed].

### 2b. Retardation, h ~ Qbar(t - r/c) — ALREADY-IN-CHAMPION plus killed higher orders

The retarded-time structure maps to depth-lag: a source inserted at layer l
reaches the terminal with a delay, and one expands the terminal mean in the
source's derivatives. The first term of that expansion is exactly the frozen
moment-tangent control already in the champion (frozen lambda =
0.9807112198896164, m80/n8c; +19.8% when subtracted, T2 report). Its higher
orders are the killed source/Born family: m120, m121, m129, m132 (one-delay
Edgeworth response), m137 second-order Edgeworth resummation.

### 2c. The conservation content — monopole/dipole do not radiate — ALREADY-KILLED

The real physics of the quadrupole formula is that conservation of mass and
momentum annihilates ell = 0 and 1, pushing radiation onto the first
non-conserved multipole. The exact analogue exists for a bias-free ReLU net and
was found: Euler's identity x . grad f = f, which with Gaussian
integration-by-parts moves E[f] onto a surface integral of gradient jumps over
the kink set. `s9_crofton_kink_transect_identity`:

    Stage A: IDENTITY VERIFIED, 3/3 nets, structural checks <= 6.7e-16,
             independent cross-check of Euler per-sample to 1.1e-15
    Stage B: KILL. variance-per-FLOP (transect/MC) geomean 176,860x
             (kill line 100x). Errors uncorrelated with MC (r = 0.055),
             so inverse-variance combination gains 0.3% — worthless.

This is the single most informative kill for the multipole cluster: the exact
conservation-law reformulation is true, unbiased, and five orders of magnitude
too expensive.

### 2d. Near-zone / wave-zone split (the 256 outputs share a common mode)

S7's coherence cone c_32(0) = 0.974720 means the 256 per-neuron means are
~97.5% a common function. Pooling that common mode is the natural multipole
move. Closed: `m79_common_axis_output_shrinkage` [killed],
`m193_analytic_anchor_frame_gls` [killed], `m194_independent_pilot_block_gls`
[killed]; `m192_cross_output_frame_gls_oracle` survives only as a
truth-fitted ORACLE (effect 0.8738, ci_upper 0.1517, explicitly "not a
deployable estimator").

---

## 3. Chua attractors / chaotic dynamics

Sharpest mechanism: read depth as time, treat u_l = h_l/|h_l| as a discrete
dynamical system on the sphere, compute the angular Lyapunov exponent, and use
the resulting bandwidth of g to set node spacing or a local smoother.

That object is measured, and it says the network is NOT chaotic. S7_VERDICT.md
gives the exact correlation map c_{l+1} = f(c_l), f(c) = (sqrt(1-c^2) + c(pi -
arccos c))/pi, verified two ways (arcsin re-implementation to 3.3e-16, MC to
1.4e-3). He-init ReLU sits at criticality: the fixed point c = 1 is ATTRACTING,
approach is polynomial not exponential, and c_32(0) = 0.974720. There is no
positive angular Lyapunov exponent, hence no strange attractor and no
exponential bandwidth blow-up to exploit. Correlation length xi_meanfield =
20.91 deg; measured 1.70 / 1.77 / 2.20x longer (S7 PASS), with the inflation
derived at 1.577 by S12 route (b).

Estimator consequence: the design spacing already sits far inside the
decorrelation scale — S17 anchors the floor on Var(ybar)/N precisely because
the residual is decorrelated at design spacing. A smoother inside the coherence
cone is `m181_terminal_smoothing_g0` [killed], all arms < 10%.

Chua-specific residue (Chua's diode is exactly a piecewise-linear
nonlinearity, the same class as ReLU): the cell/arrangement combinatorics that
implies is `s18_cell_membership_probe` [killed], OOS incremental R^2 =
2.371e-5 below the 2.63e-5 per-coefficient fitting-noise bar.

---

## 4. Strange attractors and their invariant measures

Sharpest mechanism: Perron-Frobenius / transfer operator. Propagate the
layer-wise pushforward density of the activation direction, Galerkin-truncated
at moment order K, then integrate the terminal linear functional analytically —
a fully deterministic, zero-sampling estimator.

- K = 2 truncation IS the full-covariance Gaussian closure:
  `t2_fullcov_closure_standalone_estimator` [killed], 9.6e-5 vs 2.818e-7.
  Also dead as CV (N5), smoother (M181), corrector (`n8c_offline_corrector_
  premise` [killed]).
- K = 3, 4 truncation: `m137_terminal_law_resummation`
  [killed_closures_theorem_preserved]. Even GRANTING exact terminal k1..k4 for
  free, no four-moment map (second-order Edgeworth, quartic max-entropy,
  two-Gaussian mixture, certified moment interval) closed the gap; the record's
  own kill list names "nonnormalizable saddlepoint law" as an anticipated
  failure mode, which is the saddle-point concept meeting this concept.
- Ulam / cell discretization of the invariant measure on S^255 is forbidden by
  the same counting bound as §2a: representing a density to degree 4 alone
  needs 1.83e8 coefficients.

---

## 5. Momentum optimisation for escaping saddles

Mechanism (a): momentum/Nesterov descent on the design point set to minimise
the degree-4 quadrature error tr(D^2), escaping the saddle-riddled frame-
potential landscape.

FORBIDDEN, with numbers. The objective is the 4th-moment frame potential Phi4,
whose global minimum over ALL N-point configurations is the Welch/Sidelnikov
bound 3/(d(d+2)) = 3/66048. S11 measures the champion at Phi4/Welch =
1.015811 — 1.58% above the ABSOLUTE floor. S6 states the same fact in the
operator norm: tr(A^2) = 1.0000310/N, within 3.1e-5 relative of the rank-N
tight-frame floor. There is no saddle to escape; the configuration is already
essentially at the global optimum, and the total prize for reaching it exactly
was measured at <= 0.42% (§2a) against a 2.33% cost.

Mechanism (b): momentum for fitting the control coefficients. The frozen
moment-tangent coefficient is a single scalar fitted by convex least squares
(frozen lambda = 0.9807112198896164). Closed form, no saddles, offline, free.
NO PRECISE MECHANISM.

---

## 6. The seed-side corollary this cluster contributes (derived, not measured)

Tonight's only live lane is seed-side. This cluster's concepts, run through the
committed S6 spectrum, produce a derivation that ALREADY forbids the natural
seed-side move, and I record it as a derivation, not a measurement:

Write the degree-4 error of the design against estimand component g as
g^T D g. S6 gives spec(D) = {three shells within +/-2% of 1/N on the 32,256-dim
design span} union {-1/m with multiplicity 183,116,224 on the orthocomplement}.
S6 states explicitly that "rotations conjugate A and leave the spectrum
invariant". Since the design span is 0.0176% of H_4, essentially all of any
estimand's degree-4 energy lands in the SEA, whose eigenvalue -1/m is a single
constant independent of any rotation or weight-derived construction. Therefore
an input-rotation-based seed-side construction has, to leading order, exactly
zero effect on the degree-4 error — regardless of how cleverly the rotation is
coupled to the possessed weights.

That is the mechanism behind the measured null of
`gen7_svdv_rotation_construction` [killed] (paired t = +0.19). It upgrades an
empirical null to a structural one, and it says: do not spend the night
building a better weight-coupled input rotation.

The one caveat I will not overstate: this argument is about the DEGREE-4
quadrature error only. It says nothing about a seed-side construction that
changes the estimand rather than the design — e.g. anything that uses the
weights to reduce the finite-width residual magnitude at its source (the M245
exact-control frontier). That lane is outside this cluster's concepts and I
make no claim about it.

---

## Provenance of every quoted number

- S6_VERDICT.md — dim H_4/H_6, tr(A^2) = 1.0000310/N, 3-shell spectrum,
  top-100 = 0.32%, participation rank 32,266, rotation-invariance of spec(A).
- S7_VERDICT.md — c_32(0) = 0.974720, xi_meanfield = 20.91 deg, measured ratios
  1.77 / 1.70 / 2.20, kernel verification 3.3e-16.
- S9_VERDICT.md — identity verified, variance-per-FLOP 176,860x, r = 0.055,
  combination gain 0.3%, Euler check 1.1e-15.
- S11_VERDICT.md — Phi4/Welch 1.015811 vs 1.0000000000, deg-4 benefit <= 0.18%,
  cv_deg4 +0.42%, R^2_deg4 ~0.2%, break-even 2.32558%.
- S12_VERDICT.md — route (a) transmission 0.890, curve gate FAILS 4/7;
  route (b) inflation 1.577.
- S17_VERDICT.md — pooled ratio 1.79, distinct-direction 0.90.
- fold_ledger.json candidates — t2_fullcov_closure_standalone_estimator,
  m137_terminal_law_resummation, m180_design_strength_g0,
  m181_terminal_smoothing_g0, n8c_offline_corrector_premise,
  s18_cell_membership_probe, s15_firstlayer_stratification_premise,
  gen7_svdv_rotation_construction, m79_common_axis_output_shrinkage,
  m192/m193/m194, gen8_rival_5design_adjudication.
- GOD_NODE_SYNTHESIS_20260810.md — the three god nodes and the F1-F7 filter.
