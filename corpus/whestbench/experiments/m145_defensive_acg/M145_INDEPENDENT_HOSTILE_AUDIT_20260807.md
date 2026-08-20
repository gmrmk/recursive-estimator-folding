# M145 independent hostile pre-execution audit -- 2026-08-07

## Decision

**REPAIR -- DO NOT RUN THE DECLARED OUTCOME SCREEN.**  The orientation-level
importance identity is mathematically sound in real arithmetic, and the
pointwise-Kerdock restriction is correct.  The present artifacts nevertheless
fail three required pre-execution gates:

1. the proposal fitter is not pathwise input-permutation equivariant;
2. the only implementation is a float64 NumPy harness, not the proposed
   float32 FlopScope implementation or a native cost trace; and
3. the manifest permits post-outcome selection among transport cells and does
   not compare the chosen cell by its full adjusted score to the real frozen
   baseline.

These are repairable implementation/protocol defects, not a theorem that all
orientation-level transport is futile.  They are, however, sufficient to
withhold authorization for a generated efficacy run.  No candidate source,
champion, contest artifact, score, or outcome experiment was changed by this
audit.

## Artifact and test record

Read-only SHA-256 values at audit time:

| item | SHA-256 |
|---|---|
| `m145_defensive_acg.py` | `24CD5B40D3FDD255D90AB9F05FA39957E4B8D11FA90EFC66DD09CA2EE08F7B2E` |
| `test_m145_defensive_acg.py` | `7A5DE0099B4E7A68CD395D5B3E1D6C9B5940150209C94BD25522FDB742D13542` |
| `M145_PREEXECUTION_MANIFEST_20260807.json` | `3814602CE1F53A8265890F9A9350DF37F19622265B8C4BCBA85FB83AE74C37BC` |

All **nine** existing structural tests pass under
`work/whest-v014/Scripts/python.exe`.  That result is necessary plumbing
evidence only.  The suite does not test input-permutation equivariance, tied
eigenspaces, main/pilot RNG separation, a complete conditional frame average,
float32 arithmetic, a FlopScope trace, native residual time, or the selection
firewall.

An additional non-outcome toy check used `d=5`, a nonuniform defensive ACG
law, and the full-frame functional `mean_i R[0,i]^4`.  The centered estimator
gave `0.08578039` versus the uniform truth `3/(5*7)=0.08571429`, a difference
of `0.133` estimated standard errors over 10,000 independent frames.  This
is consistent with the conditional identity; it is not a target-shape
efficacy result.

## Mathematical audit

### ACG density, sampler, and defensive weight: PASS in real arithmetic

For `Sigma = I + V diag(lambda-1) V^T`, the implemented Woodbury quadratic
form and determinant give

`a_Sigma(u) = |Sigma|^(-1/2) (u^T Sigma^(-1) u)^(-d/2)`.

The sampler applies the square root with eigenvalues `sqrt(lambda)`, so it
has the declared covariance before normalization.  The code's dense comparison
and independent circle quadrature pass.  Sampling `epsilon Uniform +
(1-epsilon) ACG` while using the *full-mixture* density in
`w=1/q` is also correct.  It yields `0 < w <= 1/epsilon = 1.25` in exact
arithmetic and preserves `E_q[w H]=E_U[H]`.

This passes only as a real/float64 statement.  At the allowed extreme
`r=16, lambda=4`, an aligned direction has approximately

`log a = -0.5*16*log(4) - 128*log(1/4) = 166.36`.

The corresponding full-mixture weight is about `exp(-164.75)`, below the
smallest positive float32.  A float32 implementation that forms that weight
will underflow to zero, violating the module's strict positive-weight check
and losing the claimed exactness.  A repair must either use and bill a stable
float64 log-weight path, prove a float32 safe parameter restriction, or state
and bound an intentional finite-precision bias.  The present float64 harness
does not prove any of those deployed alternatives.

### Conditional Haar frame and centering: PASS in real arithmetic

For Haar `Q` and anchor `A`, the Householder reflector based on `Qe_1-A`
maps `Qe_1` to `A`.  Conditional on `Qe_1`, it maps Haar columns in
`(Qe_1)^perp` isometrically to Haar columns in `A^perp`.  Therefore, if
`F(R)` is the full antipodal frame functional,

`E_q[w(A) F(R)] = E_Haar[F(R)]`.

With pilot-only `C`, the code's `C + mean_m w_m(F_m-C)` has the same
conditional mean.  Importantly, directly weighting each column would not
have this proof; neither does the artifact attempt that.  The report's
prohibition on pointwise ACG weighting of MUB/Kerdock nodes is correct.  A
whole rotated Kerdock rule could only receive one orientation-level weight,
and is explicitly out of scope here.

The code does not assemble a deployed `F`, pilot `C`, or formal L1 tangent
path.  Thus this is an identity audit, not source-level proof that the
eventual contest program uses exactly that functional or preserves radial
scaling.

## Invariance failure: required repair

`fit_pilot_acg` begins its block power iteration at
`B_0=[e_1,...,e_r]` (line 174), and its completion/sign convention is also
coordinate anchored (lines 105--125).  If an input permutation `P` transforms
pilot directions to `U P^T`, a pathwise equivariant rule would have
`Sigma(UP^T)=P Sigma(U) P^T`.  The current code restarts at the same canonical
coordinates, not at `P B_0`, so that relation fails.

Two read-only counterexamples were computed using the shipped fitter:

| pilot | rank | max covariance defect `||Sigma(UP^T)-P Sigma(U) P^T||_max` |
|---|---:|---:|
| generic 24-by-7 random pilot | 3 | `0.0457753371` |
| tied spectrum `diag(1.5,1.5,0.5,0.5)`, swap axes 1 and 2 | 1 | `0.3333333333` |

In the tied example, both executions choose `e_1`; the transformed first
proposal should instead select `e_2`.  Therefore the rank truncation is not
well defined as an equivariant operation at a cutoff tie.  This violates the
requested pathwise input-permutation invariant and creates arbitrary
coordinate-label dependence in a white-box adaptation rule.

The all-output energy itself is invariant under output permutations and under
exact hidden permutation/positive-ReLU-gauge transformations in real
arithmetic.  The supplied test establishes that limited claim.  It does not
cover 32 layers or float32 rounding, and no input-permutation or tied-spectrum
test exists.

**Required repair:** replace coordinate-started rank truncation with a
covariant construction.  It must specify a pilot-data-derived, permutation
equivariant tie rule (or retain every tied eigenspace rather than choosing a
rank-limited subspace), and add generic, exact-tie, hidden-gauge, output-
permutation, and float32 pathwise tests.  A merely different fixed coordinate
start does not repair the issue.

## Independence, frame counts, and cost: not yet certified

The manifest says pilot and main streams are independent, but no executable
seed tree, frame-bank construction, or overlap assertion exists.  In fact,
`conditional_haar_frame` directly calls `np.linalg.qr(rng.normal(...))`
(line 277).  If invoked after fitting the pilot, this QR is extra per-network
work; it does not automatically replace the formal estimator's setup-time
Haar frames.  The zero-QR-delta worksheet is valid only after an implementation
does all of the following:

1. constructs a fixed disjoint bank of pilot and main Haar `Q` frames in the
   same setup regime as the formal baseline;
2. derives `q` from pilot outputs only; and
3. applies an anchored Householder transform to those independent **stored**
   main frames, without a new per-network QR.

No current artifact implements or traces that route.  If QR is performed in
`predict`, the worksheet omits an entire adaptive per-network QR workload and
its residual time.

The worksheet's arithmetic for its most expensive declared cell reproduces
from source as follows:

| P / r | main frames | protected extra |
|---:|---:|---:|
| 256 / 4 | 125 | 10.053248160 B |
| 512 / 8 | 124 | 10.082303872 B |
| 1024 / 16 | 122 | 10.194132288 B |

For `P=1024,r=16`, `0.194132288 B` is calculated array arithmetic and the
remaining `10 B` is an unmeasured residual-time reserve.  It is not evidence
that native residual time is at most 100 ms.  Every runtime array in the
current harness is cast to float64 (`m145_defensive_acg.py` lines 68, 88--89,
105, 174, 200, 275, and 311--313), while the worksheet labels its memory
float32.  Under the stated contest billing model, float64 doubles billed
arithmetic.  `numpy.linalg`, NumPy RNG, and NumPy transcendental operations
also do not establish FlopScope per-call billing.

Accordingly, the manifest's own mandatory pre-outcome checks -- native
residual wall, peak memory, float32 parity, and FlopScope per-call bill -- are
still unperformed.  The arithmetic margin to the historical `258.4B` safety
line is not a substitute for those checks.

The number of useful frames is fixed only once a cell is frozen.  It is 125,
124, or 122 across the declared pilot sizes.  A zero-energy fallback keeps
the chosen frame count but discards pilot frames, which is safe for
unbiasedness but can be variance-negative.  The eventual production source
must assert the selected `P`, rank, and exact main count on every MLP.

## Selection firewall and actual-score gap

The manifest lists **10 executable cells**: one `P=0,r=0` baseline plus nine
nontrivial cells.  The Cartesian lists `3 ranks x 4 pilot sizes` could be
misread as 12, but the three `P=0,r>0` combinations are invalid in the code.
Neither ten nor twelve supports a single uncorrected promotion claim.

The manifest provides no preselected deployment cell, generated-network seed
list, development/selection/holdout partition, multiple-comparison rule, or
definition of the `every_holdout` unit.  Calling the full grid a "no post-hoc
selection" screen does not prevent choosing the best observed transport cell.
The reported `.75` raw-MSE criterion is also insufficient on its own: the
candidate costs more and the official objective weights per-network MSE by
effective compute.

For scale only, using the formal L1 mean effective compute
`189.852555559B` and the unverified `10.194132288B` added envelope gives a
mean-cost multiplier `1.053694996`.  If a single frozen M145 variant achieved
a uniform `.75` raw-MSE ratio against the **same formal L1 estimator**, its
rough adjusted-score proxy would be

`2.121762464e-7 * .75 * 1.053694996 = 1.676767869e-7`.

That would be better than both the formal score and the sealed M71 projection
of about `2.05e-7`.  Thus the `.75` effect is numerically large enough *in
principle*.  It is not established here because (a) this is only a
mean-cost proxy and ignores MSE/cost correlation and residual tails, and
(b) M145 currently defines a raw radial frame functional rather than an
integrated formal-L1 production estimator with the frozen analytic/tangent
path.  A win over a weaker bare Haar mean cannot be promoted as a win over the
actual champion.

## Minimum repair gate before any efficacy work

1. Implement a single FlopScope/float32 production path based on the formal
   L1 estimator, including radial factor, antipodal fold, analytic/tangent
   operations, disjoint seed tree, stored independent QR frames, anchored
   Householder update, complete-frame weight, and pilot-only centre.
2. Either preserve exactness with a billed stable precision path or state a
   tested finite-precision bias bound; test every permitted lambda/rank edge
   and no nonfinite/zero/out-of-bound weight.
3. Repair input-permutation/tie equivariance and add the missing tests above.
4. Run the manifest's *native trace only* on the frozen source: FlopScope
   calls/bill, residual wall, peak memory, float32 parity, and worst-case
   frame count.  A trace failure kills this implementation before efficacy.
5. Freeze one cell before any efficacy screen.  The strongest declared,
   costliest choice is `P=1024,r=16,M=122`; alternatively use a completely
   prespecified development selection set and an untouched generated holdout,
   with familywise correction.  In either case, predeclare an **adjusted,
   per-network, same-backend** score gate against formal L1, not merely raw
   MSE against a vague Haar comparator.

Only after all five repairs is one frozen generated-only screen scientifically
worthwhile.  Presently it is not: a favorable number could not distinguish a
legal covariant M145 improvement from coordinate choice, unbilled precision,
or grid selection.

## Salvage map

- **Preserve:** low-rank ACG algebra, full-mixture defensive weighting,
  orientation-level conditional-Haar law, centered whole-frame correction,
  and the explicit no-pointwise-Kerdock boundary.
- **Repair:** covariant/tie-safe proposal fitter, deployment integration,
  seed provenance, float32/numerical plan, and native accounting.
- **Do not infer:** a score improvement, a champion replacement, or a
  competition rank from the current pre-execution harness.
