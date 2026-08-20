# Independent adversarial judge: compression campaign

Date: 2026-08-06

## Verdict

Compression is a real route to a better score, but none of the audited
implementations is yet a validated whole-entry improvement.

The exact Winograd branch has the strongest near-term evidence.  Mutation B
reduces the effective proxy of one full sampled product to `0.885099x` direct
with excellent synthetic numerical parity.  That number is **not** the cost
ratio of the complete estimator.  An intentionally optimistic whole-entry
upper envelope, obtained by granting the same reduction to every matrix
multiplication in the current entry, is only a `10.50%` effective-compute and
score reduction.  The actual child changes a subset of those products,
dispatches some ragged shapes direct, has not been run as an integrated
estimator, and failed its frozen wall-time gate.  Its present honest projected
improvement range is therefore `0%` validated and `0--10.5%` optimistic before
any raw-MSE change.  A negative result remains possible after integrated
residual, timeout, memory, and reassociation effects.

The amplitude/quotient work proves that a useful oracle-fed cumulant
**representation** is small.  It does not provide the missing responses.
Price--Hermite Q2 is a promising synthetic transport diagnostic, not a score
projection and not a faithful conditional cumulant source.  No cumulant result
in this bundle can currently be added to the champion's expected score.

No WHest row, target, scorer, API, submission, or holdout was opened.  Source
artifacts were not edited.

## Checks performed

Local tests under `work/whest-v014/Scripts/python.exe`:

| artifact | result |
|---|---:|
| `exact_sampler_compression` | 4/4 unittest tests pass |
| `preallocated_strassen_compression` | 9/9 unittest tests pass |
| `amplitude_coded_cumulant_probes` | 8/8 unittest tests pass |
| `cumulant_polynomial_quotient` | 5/5 unittest tests pass |
| `price_hermite_higher_moment_response` | 6/6 plain test functions pass |

The Price--Hermite file uses pytest-style free functions, but pytest is not
installed in the frozen environment; the six functions were imported and
executed directly.  The independent B/C depth-32 script was also rerun:

```text
Mutation B relative final error      2.741893676e-6
Mutation B gate changes              2 / 4,194,304
Mutation C relative final error      2.479849285e-6
Mutation C gate changes              1 / 4,194,304
```

The billing formulas agree with the installed FlopScope convention on the
tested shapes.  The local tests establish algebra, billing on those paths,
and synthetic parity.  They do not exercise the complete estimator, its true
live set, its full shape distribution, or its score.

## Correction 1: score-ratio calculus must be matched per network

For network `i`, above the multiplier floor,

```text
s_child_i / s_parent_i
  = (MSE_child_i / MSE_parent_i) * (C_child_i / C_parent_i).
```

This is the correct `r_V*r_C` rule.  For the aggregate benchmark,

```text
S = mean_i [ MSE_i * max(0.1, C_i/B) ].
```

The aggregate ratio is a score-weighted average of the per-network products;
it is not generally the product of aggregate raw-MSE and aggregate-cost
ratios.  The table of single-network thresholds in
`COMPRESSION_SCORE_CALCULUS_20260806.md` is correct, but the opening formula
needs this qualification.  Aggregate projections require paired per-network
cost and prediction changes or a genuinely uniform ratio.

There is also a numerical correction to the ideal floor claim.  With unchanged
predictions and every network reduced to the `0.1` multiplier floor,

```text
ideal score                  = 0.1 * 3.089512726e-7
                             = 3.089512726e-8
current adjusted / ideal     = 7.305617x
```

`7.4368x` is the mean multiplier divided by `0.1`.  It is not the aggregate
score ratio because network MSE and multiplier are correlated.  The observed
aggregate multiplier-equivalent is
`2.257079776e-7 / 3.089512726e-7 = 0.7305617`.

The `3.327%` break-even statement for adding `8.622B` to random32,256 is also
only a maximum-cost planning calculation:

```text
8.622 / (250.488783 + 8.622) = 3.3275%.
```

At the reported mean effective cost the analogous scalar threshold is

```text
8.622 / (202.281790 + 8.622) = 4.0881%.
```

Neither scalar replaces the paired aggregate calculation.  The `12.698%`
threshold against a `59.276B` base is arithmetically correct for that billed
base, but the scorer uses residual-adjusted `C`, not billed FLOPs alone.

## Correction 2: a full-product saving is not a whole-entry saving

Mutation B's full-product measurements are internally consistent:

```text
(64512x256) @ (256x256)
direct billed                         8.439201792B
B billed                              7.427768320B
billed ratio                          0.880150576
effective-proxy ratio                 0.885098733
total-wall ratio                      1.545590007
```

The current entry's aggregate breakdown is:

```text
mean effective C                      202.281790B
mean billed matrix multiplication     184.821668B
```

Even if every one of those matrix-multiplication FLOPs received B's measured
full-product effective ratio, which the current implementation cannot do,

```text
C_optimistic = 202.281790
             - (1 - 0.885098733) * 184.821668
             = 181.045546B

C_optimistic / C_parent = 0.8950165.
```

Thus `10.50%` is an optimistic whole-entry cost/score ceiling for Mutation B,
not an expected gain.  Under the extra uniform-ratio and unchanged-prediction
assumptions it would map the current adjusted score to about `2.0201e-7`.
Using billed ratio alone produces a looser `10.95%` ceiling, but effective
compute is the relevant objective.

The actual subclass only intercepts the first sampled product and the ordinary
sampled products through layer 29.  Terminal fold products and numerous small
analytic products remain direct.  Mutation B also dispatches an odd contracted
width direct.  No audited artifact inventories the eligible billed fraction
on the complete entry.  Therefore `0.885099x` must not be described as the
entry cost ratio.

The earlier L2 rectangular result has a better nominal bill ratio
(`0.795427`) but an effective proxy worse than direct (`1.445x`).  It supplies
algebraic ideas, not an operational projected gain.

## Exact-compression promotion blockers

1. **Formal frozen gate.** Mutations A/B/C have total-wall ratios
   `1.5587/1.5456/1.7015`, all above the declared `1.5` limit.  They are
   correctly unpromoted under their own protocol.
2. **The wall gate is self-imposed, not itself the score.** The competition
   charges FlopScope residual and enforces a whole-entry wall limit.  A
   `1.5456x` product wall ratio can still be score-positive if integrated
   residual remains low and the complete prediction stays within the wall
   limit.  Reopening this branch does not require claiming the failed gate
   passed; it requires a new predeclared *whole-entry* gate aligned to actual
   `C`, timeout, and memory.
3. **No complete-estimator trace.** There is no fresh synthetic integrated
   run proving eligible-shape fraction, total billed work, total residual,
   elapsed time, call distribution, or finite output for the subclass.
4. **Memory is not certified end to end.** B's `283.94 MiB` workspace and
   standalone process peaks pass the local product screen.  The reported
   `480.94 MiB` "conservative estimator peak" is an accounting formula, not a
   measured estimator peak.  Fold3 can retain `x`, `x30_kink`, and
   `x31_kink`, plus `pre31/pre32` temporaries, while the workspace stays live.
   The standalone memory process contains only one left matrix, one right
   matrix, the workspace, and its output.  A full synthetic estimator memory
   trace or a proven liveness bound is required before calling the 512 MiB
   gate passed.
5. **Numerical parity is not MSE parity.** The depth-32 gate-mismatch rate is
   excellent, but no bound connects it to final integration MSE.  A paired
   prediction-parity gate on a legally available frozen synthetic network
   suite is needed before any score estimate.
6. **Timing sample is narrow.** Seven pairs at one full shape are enough for
   the frozen screen but not for a whole-entry performance claim.  Active and
   odd/ragged shapes can change BLAS efficiency and dispatch savings.

The minimum next exact-compression rung is therefore an integrated fresh
synthetic estimator trace with shape-by-shape direct/candidate bills, peak
live memory, residual, total wall, and prediction deltas.  It should use a
newly frozen whole-entry criterion and still touch no WHest target.

## Amplitude probes and quotient: what is actually proved

The following claims are supported on the frozen synthetic cases:

- constant-modulus blindness is repaired by nonconstant amplitudes;
- the evaluated cubic/quartic polynomial maps have ranks `64/58` rather than
  literal `84/78`;
- their 20-dimensional losses equal the kernels of the explicitly constructed
  symmetrization/monomial maps in those cases;
- with dense oracle directional cumulants supplied free, the reduced inverse
  reconstructs responses and physical cores to about `1e-14` and preserves
  the reported downstream oracle fidelity.

The following stronger readings are not supported:

1. **No responses are produced.** Every `0.98--0.99` downstream fidelity
   number is oracle-fed.  It answers whether the geometry discards a supplied
   signal, not whether weights and current state can compute that signal.
2. **`64/58` is not yet a universal n=256 rank theorem.** Equality was checked
   in 141 nontrivial small synthetic cells.  The kernel theorem is general,
   but the observed rank of a cell-specific map can fall on degenerate bases.
   Production must prove generic/nondegenerate rank or adapt safely to the
   runtime rank.
3. **Equivariance transports the probes too.** The covariance test rotates or
   permutes directions together with bases.  This proves equivariance of the
   algebra conditional on a transported design.  A fixed seeded finite probe
   set is invariant only in distribution, not pointwise under a coordinate
   transform.  The report should use that precise wording.
4. **The quotient is not runtime compression yet.** The current path still
   constructs the response-free SVD and reports a billed-like arithmetic
   model, not a FlopScope port.  The report correctly says this in its
   compression section; summary language should retain the qualifier.
5. **Canonical signs do not certify a stable basis at spectral clusters.**
   Sign fixing handles one-dimensional SVD ambiguity but not rotations inside
   repeated or nearly repeated singular subspaces.  Conditions are moderate,
   but singular-value gap stability is not reported.  A production mechanism
   should operate on the quotient projector or freeze a gap-aware basis rule.

The honest status is `screened oracle-response geometry`, not an estimator and
not an expected score gain.

## Price--Hermite Q2: what is actually proved

The exact algebraic pieces survive review:

- for a rectified-normal prior,
  `a1=sigma*Phi(alpha)` and `a2=sigma*phi(alpha)/2` are the first two
  probabilists'-Hermite coefficients;
- the linear-plus-quadratic Gaussian-chaos formulas
  `k3=6 b' R A R b + 8 tr((A R)^3)` and
  `k4=48 b' R A R A R b + 48 tr((A R)^4)` are correct;
- the diagonal-plus-rank-four contraction matches its dense implementation;
- permutation and positive coordinate gauge tests pass.

The synthetic accuracy claims need strict qualifiers:

1. **The state is supplied, not produced.** In the audit the cell means and
   covariance factors are built from synthetic activation paths.  The
   weights-only recurrence that would create this state at width 256/depth 32
   remains deployment work.
2. **The reported Edgeworth correction is oracle-normalized.** The evaluation
   calls `standardized(exact_mean, exact_variance, candidate_k3,
   candidate_k4)`.  Thus candidate and baseline receive exact downstream mean
   and variance when their correction fidelity is computed.  This is a fair
   isolation of higher-cumulant transport, but it is not end-to-end estimator
   fidelity.
3. **Direct conditional formation fails.** Aggregate isolated fidelity is
   `0.67069` for k3, `0.16234` for k4, and `0.28234` combined; one case has
   k4 fidelity `-4.8064`.  These values block any claim that Q2 supplies the
   quotient responses.
4. **The transported aggregate is small-suite evidence.** Results come from
   six networks with widths `8--16` and depths `2/4`, not width 256/depth 32.
   One case slightly worsens combined fidelity versus the zero-conditional
   baseline.  Aggregate success does not establish extrapolation.
5. **Factor clipping is material.** `481/1152 = 41.75%` of rows are clipped.
   The resulting prior preserves neither the intended untruncated latent
   factor nor necessarily the supplied covariance once Q2 covariance terms
   are included.
6. **The moment-two witness is general, not WHest-specific.** Exponential and
   two-point nonnegative laws prove no second-order state identifies higher
   cumulants over all nonnegative laws.  Without a realizability/density
   argument they do not prove impossibility restricted to conditional laws of
   this fixed deep-ReLU Gaussian-input ensemble.
7. **The `61.286B` envelope is not a bill.** It is scalar arithmetic with a
   float64 factor and contingency, plus an inherited state envelope.  Special
   functions, small-call residual, a legal state recurrence, and an actual
   FlopScope implementation remain unmeasured.

The honest status is `promising Q2 transported-total diagnostic under oracle
evaluation; killed direct conditional response source`.

## Strongest honest projected improvement

There are three different answers and they must not be mixed:

```text
validated deployable improvement now                  0%

optimistic Mutation-B whole-entry cost ceiling
  if every current matmul were eligible,
  per-call effective ratio transferred,
  predictions were unchanged, and ratios uniform      <= 10.50%

cumulant representation/Q2 score improvement          unquantified
```

The `<=10.50%` ceiling would correspond to an adjusted score near
`2.0201e-7`, but the assumptions deliberately favor the child.  Because the
actual intercepted/eligible fraction is smaller, full-entry memory is
uncertified, the formal wall gate failed, and no matched MSE measurement
exists, the defensible operational range is `no proven gain yet` through
`about 10% upside`, with regression still possible.

## Promotion order

1. Run a fresh-synthetic **integrated** Mutation-B estimator audit and report
   the whole-entry eligible bill, residual, elapsed time, live memory, and
   output parity.  Do not infer these from one full GEMM.
2. If it survives a newly predeclared competition-aligned gate, perform the
   separately authorized paired validation required by the campaign firewall.
3. Keep the cumulant branch separate.  First derive legal directional RHS or
   an equivalent direct quotient recurrence.  Then implement and bill it.
4. Evaluate Q3/Q4 only against isolated conditional responses and end-to-end
   corrections using candidate-available mean/variance.  Do not promote on
   oracle-normalized transported totals alone.

Until those steps pass, the deployed random32,256 artifact remains unchanged.
