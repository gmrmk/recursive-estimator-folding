# M145 repaired defensive ACG transport — second pre-execution packet

## Decision

**REPAIRED PRE-EXECUTION SURVIVOR / AWAITING SECOND HOSTILE AUDIT / NO
EFFICACY AUTHORIZATION.**  The first hostile audit correctly rejected the
coordinate-started block-power fitter, the float64-only implementation, the
unmeasured QR/cost story, and the nine-cell selection surface.  This packet
changes those failed links and nothing else:

* exactly one cell is frozen: `P=1024` pilot lines, `r=16`, four pilot and 122
  main complete frames, `epsilon=.8`;
* a full symmetric eigensolve defines a permutation-covariant spectral
  covariance, with uniform fallback at a rank-boundary tie;
* ACG and full-mixture weights are evaluated in the float32 log domain under
  a proved no-underflow eigenvalue box `[.25,1.75]`;
* setup QR, pilot, main, component, uniform, and ACG streams have explicit
  child-seed ownership;
* a target-shaped FlopScope 0.10.0 sidecar trace measures bill, residual wall,
  setup wall, peak memory, frame restoration, and weight range; and
* a source-hash-bound crosswalk identifies every Formal-L1 insertion point and
  makes adjusted score—not raw MSE—the primary gate.

No generated-network MSE, target truth, contest model, scorer, public/private
row, leaderboard result, submission, or champion artifact was opened or
changed.  The immutable Formal-L1 and sealed M71 artifacts remain untouched.

## Fixed estimator and probability law

Radialization and antipodes retain the Formal-L1 target

\[
 I_j=\rho_{256}E_U\,g_j(U),\qquad
 g_j(u)=\{f_j(u)+f_j(-u)\}/2.
\]

The random unit is one complete 256-line orthogonal frame, not an individual
line.  Given a pilot-only proposal, sample one anchor per main frame from

\[
 q(u)=\epsilon +(1-\epsilon)a_\Sigma(u),\qquad\epsilon=.8,
\]

where, relative to uniform probability on the sphere,

\[
 a_\Sigma(u)=|\Sigma|^{-1/2}(u^T\Sigma^{-1}u)^{-d/2},\qquad
 \Sigma=I+V\operatorname{diag}(\lambda-1)V^T.
\]

A stored setup-time QR frame is right-multiplied by the Householder reflector
taking its first **row** to that anchor.  Formal L1 flattens QR matrices by
rows, so this is the actual backend orientation.  The remaining rows are the
conditional orthogonal completion.  The complete frame receives one weight
`w=1/q(anchor)`; dependent lines never receive iid ACG weights.  MUB/Kerdock
point weighting remains explicitly forbidden.

Let C be the four-pilot-frame mean of the same frozen Formal-L1 surrogate and
F_m a main complete-frame contribution.  The correction is

\[
 \widehat I=C+{1\over122}\sum_{m=1}^{122}w_m(F_m-C).
\]

Conditional on the independent frozen pilot,

\[
 E_q[wF]=E_{\rm Haar}F,\qquad E_q[wC]=C,
\]

so the ACG change of measure is exact in real arithmetic.  It introduces no
additional modeling approximation beyond Formal L1's already frozen
pruning/fold/tangent class.

## Repaired pathwise proposal covariance

For pilot direction rows u_t and all-output even energy

\[
 h_t={1\over256}\left\|{f_{\rm surrogate}(u_t)+
 f_{\rm surrogate}(-u_t)\over2}\right\|_2^2,
 \qquad
 \widehat S=256\sum_t {h_t\over\sum_s h_s}u_tu_t^T,
\]

the repaired code forms the full float32 symmetric scatter and runs one full
`eigh`.  If the rank-16 boundary is separated, the covariance is the spectral
matrix function

\[
 \Sigma=I+\sum_{a=1}^{16}
 [\operatorname{clip}(1+.8(\mu_a-1),.25,1.75)-1]v_av_a^T.
\]

Here `.8=P/(P+d)=1024/1280`; it was declared before outcomes.  Under an input
permutation P, the scatter becomes `P S P.T`, and this spectral matrix
function becomes `P Sigma P.T`.  Eigenvector signs and rotations inside a
fully retained tied eigenspace cancel in the projector.

If the selected/unselected boundary satisfies

```text
mu[16] - mu[17]
    <= 128 * eps_float32 * max(1, |mu[16]|, |mu[17]|),
```

choosing only part of the tied eigenspace would be label-dependent.  The
protocol therefore returns `Sigma=I`, before seeing any outcome.  Tests cover
a generic pilot and an exact boundary tie under the same generated seed and a
nontrivial coordinate permutation.  Their proposal covariances transform to
`2.5e-5` float32 tolerance; both tied executions return uniform exactly.

The all-output energy continues to pass output-permutation and positive hidden
ReLU-gauge tests in float32.  No output coordinate, seed, or eigenspace basis
is selected after an outcome.

## Stable float32 full-mixture weights

Woodbury evaluates

\[
 \log a_\Sigma(u)=-{1\over2}\sum_a\log\lambda_a
 -128\log\left(1-\sum_a(1-\lambda_a^{-1})(v_a^Tu)^2\right).
\]

The code never materializes `a_Sigma`.  It uses

```text
log_q = logaddexp(log(.8), log(.2) + log_a)
log_w = -max(log_q, log(.8))
w     = min(exp(log_w), float32(1.25))
```

entirely in float32.  The lower maximum eigenvalue cap repairs the first
audit's underflow counterexample.  Over
`lambda in [.25,1.75]^16`, the worst determinant and Rayleigh terms give

\[
 \log a\le {1\over2}\{255\log1.75-15\log.25\}=81.74822067,
\]

and therefore

\[
 \log q\le80.13878270,
 \quad w\ge1.57096799\times10^{-35}
 >\mathrm{tiny}_{f32}=1.17549435\times10^{-38}.
\]

Thus every permitted weight is positive normal float32, finite, and no larger
than `1/.8=1.25`.  The tests hit the mixed extreme box directly and inspect
100,000 directions: zero underflows/nonfinites and maximum at most 1.25.  The
native target-shaped structural trace measured weights
`[.94192684,1.03316307]`; that observed range is plumbing evidence, not an
efficacy result.

## Explicit seed tree and frame ownership

The namespace is frozen as integer `1295070261`.  Setup uses

```text
SeedSequence([namespace, setup_seed, 0])
  -> pilot_qr   # exactly four stored frames
  -> main_qr    # exactly 122 stored frames
```

and prediction for each network uses

```text
SeedSequence([namespace, setup_seed, mlp.seed, 1])
  -> mixture_labels
  -> uniform_anchors
  -> acg_latents
```

The setup and prediction roots are distinct even where their local spawn-key
indices coincide.  All five generated uint64 child seeds are distinct,
replay bit-identically, and the test suite checks child ownership.  Pilot and
main QR frames are fully constructed in setup.  `predict` performs no QR.

The 122 main QR frames are Householder-transformed in the existing 126-frame
bank.  A fixed `256x256` scratch and `256`-vector suffice.  A `finally` path
applies the same self-inverse reflectors to restore the setup bank; the native
trace's maximum restoration defect is `8.9406967e-8`.  This is why the
33,030,144-byte bank replaces Formal L1's existing direction bank rather than
being added to it.

## Actual Formal-L1 integration crosswalk

`m145_formal_l1_crosswalk.py` verifies five immutable source hashes before
accepting these hooks:

| Formal-L1 owner | M145 insertion |
|---|---|
| `orthogonal_fold3.setup` | same 126 setup QR frames and chi-mean radius; split only the child streams |
| `predict` before `first_pre` | execute four pilot frames first, freeze active/fold regimes and proposal, then tilt stored main frames |
| `first_moment_residual` and `first_variance_residual` | replace two ordinary means with complete-frame coefficient means |
| existing `_weighted_mean` terminal sites | pass the duplicated antipodal line coefficient vector |
| `predict` cleanup | restore stored main frames with the frozen reflectors in `finally` |

For use in Formal L1's ordinary mean over T=126 frames, the four pilot frame
coefficients and 122 main coefficients are

\[
 c_p={126\over4}(1-\bar w),\qquad
 c_m={126\over122}w_m.
\]

Their sum is 126, and expanding each coefficient to all 256 rows and
duplicating the line vector in Formal L1's `[positive block, negative block]`
order exactly reproduces `C+mean(w(F-C))`.  Consequently constant/dead
analytic pieces remain owned, the first-moment/variance residual uses the same
change of measure, and the downstream moment tangent remains unchanged because
it is linear in those residuals.  Radial scaling, active/cold logic, terminal
folding, and the row-blocked backend are otherwise unchanged.

Splitting the actual Winograd shapes into pilot and main calls adds exactly
`114,688` billed operations per hook.  One first hook plus 28 ordinary hooks
adds `3,325,952` billed operations and at most 29 calls.  The crosswalk is
hash-bound to:

```text
estimator.py              d32de9fb7fa8f953fc873eec91a39e66778215f8607fb03bebbbe1292ca5d432
orthogonal_fold3.py       24f2eebb1adf37f6be1392de57611c52cbaac7b04e319ff771533da54257796a
fold3_estimator.py        6952abc0a617e1fb32c64a4483f1539b79933c049f9190984460266bf357e116
row_blocked_winograd.py   876ac0f042239c88bb48205585d7175da1f956ed0c4b96d8d6f95f5be5ea74b5
cost_model.py             21b077a7bcdf244b9480e891a8b63ecee05427d2725ea30ef5d2fc016bc03023
```

This is an executable integration/cost crosswalk, not a packaged Formal-L1
descendant and not permission to run one.  A second hostile audit must accept
the semantics before an estimator source is materialized.

## Native structural trace and protected resource crosswalk

The fixed target-shaped trace used FlopScope `0.10.0+np2.4.6`, float32,
`d=256`, `P=1024`, `r=16`, `M=122`, the explicit seed tree, a stored 126-frame
bank, full scatter/eigh, three main RNG children, full-mixture log weights,
246 apply/restore Householder matmuls, and the 64,512-path coefficient vector.
It formed no target estimate or error.

| native sidecar measurement | value |
|---|---:|
| billed FLOPs | `357,099,678` |
| residual wall | `.022555598 s` |
| effective sidecar at `1e11/s` | `2.612659437B` |
| total sidecar wall | `.131760200 s` |
| setup QR bank | `1.314100500 s` |
| process peak working set | `300,863,488 B` |
| frame bank | `33,030,144 B` |
| realized rank / fallback | `16 / none` |
| frame restoration max defect | `8.9406967e-8` |
| zero/nonfinite weights | `0 / 0` |

The protected Formal-L1 crosswalk additionally charges:

* `3,325,952` exact split-Winograd operations;
* `99,090,432` operations for six worst-shape float32 coefficient products;
* the measured `.022555598s` sidecar residual; and
* an extra `.050s` (`5B`) integration reserve for 29 split calls and adapter
  control flow not present in the isolated sidecar.

Recomputing from `run_m145_crosswalk.py` gives a protected effective delta of
approximately `7.715B`; the exact value is emitted by the script.  Against
Formal L1's measured `189.852556B` mean and `222.405357B` maximum, projected
mean/max remain about `197.57B/230.12B`, below both `258.4B` safety and the
272B cliff.  In-place ownership replaces the baseline frame bank; a 5MiB live
scratch reserve projects `479.859MiB`, below 512MiB.  Native setup is also
below 4s.  These are pre-outcome resource gates, not a prediction that hosted
residuals will be identical.

## Frozen promotion gate: adjusted score first

There is no parameter grid.  If and only if a second hostile audit authorizes
one generated-only screen, the network is the independent unit and Formal L1
and M145 must share generated networks, setup seed root, row-blocked backend,
radialization, runner, and scoring implementation.

Primary promotion requires all of:

1. paired per-network **official adjusted-score** mean ratio `<=.80` against
   Formal L1;
2. paired network-bootstrap upper 90% ratio strictly `<.90`;
3. candidate adjusted-score bootstrap upper 90% below the sealed M71 proxy
   `2.05e-7`;
4. zero failures, every C `<258.4B`, no nonfinite output/weight, setup `<4s`,
   prediction `<20s`, and peak `<512MiB`; and
5. no champion mutation or target/public/private run.

Raw MSE ratio is secondary diagnostic evidence only and cannot promote the
candidate.  Under the current protected crosswalk the mean cost ratio is about
`1.04`, so a raw `.75` ratio would imply adjusted ratio about `.78`; the exact
threshold is recomputed by the hash-bound crosswalk rather than assumed.

## Relation to the floor and isotropy no-go

The average-case linear-cubature floor does not literally bind a nonlinear,
network-adaptive proposal, so M145 does not “evade” it by theorem.  It must
demonstrate extra pilot information about **whole-frame residuals**.  The
prior subspace-tumbling result remains hostile: an antipodal degree-2 frame's
first surviving even band is degree four, and a rank-16 linear channel has the
scale `(16/256)^4=1.53e-5` before pilot noise.  The repaired method is now
legal and measurable; it is still unlikely to clear a 20% adjusted-score gate.

That distinction is the point of the repair.  A favorable future number could
now be attributed to a single covariant, billed, seed-owned operator.  No such
number has been generated yet.

## Salvage and stop condition

Preserve the spectral tie-safe proposal, float32 log-weight envelope,
orientation-level frame law, centered coefficients, explicit seed tree,
in-place reflector/restore operator, native trace, and Formal-L1 hook/cost
crosswalk.  If the second hostile audit rejects a hook, the repaired artifact
stops there.  If it passes, only the one frozen generated-only adjusted-score
screen may be considered; no automatic submission, designation, or champion
replacement follows.
