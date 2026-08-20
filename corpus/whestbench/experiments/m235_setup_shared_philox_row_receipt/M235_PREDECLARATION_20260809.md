# M235 predeclaration -- setup-shared Philox SRSWOR row receipt

Date: 2026-08-09. Frozen before any M235 implementation, M235 test, M235
native trace, or M235 source-efficiency readout. Generated-only and response-
free: challenge weights, responses, truth, scorer, leaderboard data,
submissions, cached outcomes, and champion artifacts are forbidden.

## Objective and failed-parent fold

M231 proved the `k=32` row collision estimator, exact integer-permutation
receipt, and `864,993,280` predict-time bill, but failed its hostile wall gate.
M234 then froze an explicit Philox constructor inside predict; a cheaper
fresh-process diagnostic statically killed it because the constructor alone
exceeded the available residual allowance. No M234 code or tests were written.

M235 changes exactly one statistical/execution mechanism: issue one immutable
SRSWOR receipt in the official setup lifecycle and reuse that same receipt for
every MLP in the run. Fixed-shape empty workspaces are also setup-owned. M235
does not change `k`, the M215 collision formula, `t/A/E/D` coefficients,
precision, matmul shapes, the exact live `p/B/rho`, or M151's independent
`K=128` strict residual.

This is not merely a free scheduling claim. Sharing one setup receipt changes
dependence across MLPs and changes the conditioning statement: the estimator
is unbiased over the official setup-seed randomization, but one realized
receipt is deterministic conditional on setup. M235 therefore receives new
outer-setup-seed gates before any source-efficiency promotion.

## Local legality boundary

The pinned starter-kit contract provides the needed boundary:

- `work/whest-starterkit/docs/troubleshooting/faq.md` lines 37-51 says setup
  runs before predict, is outside the per-predict FLOP budget, may perform
  one-time preparation independent of the particular MLP, and has a typical
  five-second timeout.
- `work/whest-starterkit/docs/reference/code-patterns.md` lines 90-130 permits
  setup-time fixed random projections seeded from grader `ctx.seed` and
  forbids participant-chosen or time-based seeds.
- `work/whest-v014/Lib/site-packages/whestbench/sdk.py` defines
  `SetupContext.seed` as one run-level seed shared by all MLPs.
- The pinned worker calls `estimator.setup` before constructing the predict
  BudgetContext.

The isolated M235 component owns exactly one
`fnp.random.Generator(fnp.random.Philox(ctx.seed))` in setup. It passes the
official seed directly: no participant salt, fixed private seed, wall-clock
entropy, retry, or state-dependent reseed. In a final estimator with multiple
setup RNG consumers, all streams must instead be deterministically spawned
from one official `ctx.seed` root; isolated M235 grants no integrated RNG-
ownership credit.

Setup work is independent of every MLP's weights, activations, name, and
`mlp.seed`. It is measured against the five-second setup timeout and RSS cap
even though its FlopScope operations do not enter per-predict score `F_m`.

## Preserved algebra and exact expectation

For one layer let `S=diag(u)W`, with exact live

```text
p = S^T 1,  B = S^T S,  rho = diag(B).
```

Setup generates a uniform random permutation `P_l` of labels `0..255`
independently for every one of 31 layers and stores
`H_l=P_l[0:32]`. With `g=256/32=8`, predict forms

```text
that = g sum_(i in H_l) s_i^3
Ahat = g sum_(i in H_l) outer(s_i^2,s_i)
Ehat = g sum_(i in H_l) outer(s_i^3,s_i)
Dhat = g sum_(i in H_l) outer(s_i^2,s_i^2).
```

The first 32 labels of a uniform permutation are exact SRSWOR. Each row has
inclusion probability `32/256`, so over `ctx.seed`

```text
E_setup[that,Ahat,Ehat,Dhat] = [t,A,E,D].
```

M215's collision expression is affine in those four totals while `p/B/rho`
remain exact. Thus

```text
Chat_strict = Cfull_M212 - Chat_collision,
E_setup[Chat_strict] = Cstrict,
E_setup,residual[Chat_strict + Rhat_D] = T_D.
```

Conditional on one setup receipt and one arbitrary fixed MLP, `Chat_strict`
need not equal `Cstrict`; M235 must not be described as conditionally unbiased
per predict. Its marginal one-MLP receipt law matches M231. The shared receipt
does not add cross-MLP inner products to the contest score: the score averages
per-MLP squared losses `M^-1 sum_m ||e_m||^2`. Sharing changes uncertainty and
conditional loss dispersion, which is why setup seeds are top-level
experimental clusters.

Pathwise hidden-row covariance is tested by co-permuting the immutable receipt
labels with the hidden rows. Distributional covariance alone is insufficient
for that audit, but actual predict never mutates or reissues the receipt.

## Frozen setup owner

For `width=256`, `layers=31`, `k=32`, setup may do only:

1. construct explicit isolated `Generator(Philox(ctx.seed))`;
2. create `arange(256,int64)`, broadcast to `(31,256)`, and call exactly one
   `permuted(axis=1)`;
3. retain the full immutable rank receipt and its first-32 selected-label
   view, bound to canonical layer IDs, width, depth, subset size, and setup
   seed;
4. allocate only fixed-shape empty M212 staged inputs, M212 depth-3 workspace,
   and M235 powers/cross workspaces;
5. prebind value-independent workspace views and scalar coefficients.

No weight, factor, moment, source, response, MLP seed, input record, filled
array, sampled collision event, or predict output may be computed in setup.
The receipt object and bytes must remain identical before and after multiple
generated predictions. Setup failure rejects the candidate; no fallback
receipt is allowed.

An isolated setup audit predicts the receipt operations:

```text
arange(256,int64)                   1,024
broadcast_to(31,256)                    0
random.Generator.permuted          31,744
fixed-shape empty workspaces            0
SETUP RECEIPT BILL                 32,768  (recorded, not per-predict F_m)
```

All setup calls, raw elapsed time, full-rank uniqueness, layer independence,
receipt digest, allocated shapes, and RSS are recorded. Setup elapsed must be
strictly below `5.0 s` and RSS below `512 MiB` in every frozen fresh process.

## Frozen predict ABI and exact bill

Predict accepts the setup-owned immutable receipt and workspaces. It performs
only a constant-time binding check, the selected-row gather, and the unchanged
M231 collision kernel. There is no predict-time RNG or label-bank construction.
The timed correction source must contain no `default_rng`, `Philox`,
`Generator`, `arange`, `broadcast_to`, `permuted`, priority, argsort, retry,
allocation ledger, runtime hash, receipt mutation, or data-dependent branch.

The exact per-predict M235 bill is:

```text
operation                            calls      exact billed FLOPs
take_along_axis selected S, f64         1           2,031,616
matmul (3 product-equivalents)          2         767,950,848
multiply                               16          57,901,056
add                                     9          36,569,088
sum                                     1             492,032
copyto                                  1              15,872
reshape                                 0                   0
TOTAL                                              864,960,512
```

Zero-bill empty allocations and static transpose/swapaxes/diagonal views are
setup-owned and must not occur in the timed correction. The composed bill is

```text
M212                                1,249,253,376
M235                                  864,960,512
M212+M235                           2,114,213,888
M151 comparison envelope           3,727,757,440
raw arithmetic remainder           1,613,543,552
```

For a full conditional branch comparison, M235's frozen cost is
`88.095092688B` versus M151's `89.708636240B`, a ratio
`0.982013509293762`. Break-even requires
`V_S/V_R < 0.000143093203212184`; a one-percent normalized win requires
`V_S/V_R < 0.0000635372711800617`.

Setup is legally outside `F_m`, but M235 also carries a conservative
single-call amortization gate that charges its `32,768` receipt bill once per
predict. Consequently every native process must satisfy both:

```text
exact-lawful:
  2,114,213,888 + 5e11*(r_M212+r_M235) <= 3,727,757,440
  r_M212+r_M235 <= 0.003227087104 s

conservative setup-amortized:
  2,114,246,656 + 5e11*(r_M212+r_M235) <= 3,727,757,440
  r_M212+r_M235 <= 0.003227021568 s.
```

Using M212's frozen maximum residual, M235 alone must also be at most
`0.002025121700262334 s`. No setup or compiler-retirement credit is inferred
from a diagnostic.

## Frozen memory, seeds, and native gate

Numeric storage is the M231 layout; setup changes lifetime, not payload:

```text
M235 incremental persistent          36.873046875 MiB
M235 incremental nominal peak        36.875000000 MiB
M212+M235 nominal persistent         138.955078125 MiB
fresh-process RSS cap                512.000000000 MiB
```

Run exactly five fresh sequential native processes. Pair generated MLP/source
seeds

```text
227700001, 227700002, 227700003, 227700004, 227700005
```

with setup receipt seeds

```text
0, 235700001, 235700002, 235700003, 235700004.
```

All five must have: setup below five seconds; matching pinned hashes; exact
setup receipt law and unchanged digest; exact constant M212/M235 bills and
calls; no forbidden predict calls; finite symmetric source; correction and
both combined wall gates; RSS below 512 MiB; and zero failure. Seed `0` is
included because it is the documented SetupContext default when no run seed
is supplied. Native aggregation must be independently confirmed before G0 is
opened, and G0 may not run in the same unreviewed execution step.

Pinned runtime hashes:

```text
flopscope/_registry.py
  D735DA7D36ECF05BA7B927452DB126FE297E33398F3903C59B886E1BC1228795
flopscope/numpy/random/_cost_formulas.py
  D14D86A2CA0700C0899318A9C7CD3F08E91AC80948682225D383D71E2D628F8F
flopscope/numpy/random/_counted_classes.py
  6D7AA1E9C4F7A135EF7487FAF6B645AEA61C74983FA780DAFFB68240C6DA3F0D
numpy/random/_philox.cp314-win_amd64.pyd
  8CEB13F5A97EB161FD7D93D2E597DC99D3387A76F32EF187A57103AC759BDA15
numpy/random/_generator.cp314-win_amd64.pyd
  69C5AA9B41C0A60EE8600A4C1434C86FA96DFC00F4CD3171AED9729AACAA549B
whestbench/sdk.py
  [must be hashed and frozen by the RED provenance test before GREEN]
whestbench/subprocess_worker.py
  [must be hashed and frozen by the RED provenance test before GREEN]
```

## Frozen strict-TDD order

No M235 implementation or M235 test exists at freeze time.

1. **RED setup/provenance tests.** They fail only because the M235 module is
   absent. Require direct `ctx.seed`, explicit Philox, one permutation call,
   exact SRSWOR, immutable shared receipt, fixed-empty-only setup ownership,
   setup timeout/RSS receipt, and forbidden predict-source scan.
2. **GREEN algebra tests.** At widths `3..9`, reuse M227/M231's exhaustive
   cubic oracle, row-loop, gauge, zero, and `2e-10` gates. At target shape,
   compare the actual setup receipt's collision delta to the M227 row oracle
   at `2e-9`. Co-permute receipt labels and rows and require pathwise parity.
3. **RED/GREEN native sidecar.** Prove exact setup/predict calls and bills,
   receipt immutability across predictions, five fresh-process wall/RSS gates,
   and both lawful and conservative effective-compute caps.
4. **Independent native aggregate review.** Any native failure kills fixed
   M235 without retuning. Only a confirmed full pass authorizes G0.
5. **G0, then G1, then holdout.** No later stage is opened early.

## Frozen outer-setup-seed G0

Use exactly M227's 24 fresh M161-style response-free cells:

```text
diagonal-SPD widths 8,16,24:
  2270801..2270804, 2271601..2271604, 2272401..2272404
iid-He-SPD widths 8,16,24:
  2270811..2270814, 2271611..2271614, 2272411..2272414.
```

The frozen setup-seed grid is

```text
0 and 23501001..23501031                         (32 setup receipts).
```

Each setup receipt is generated once at each width and reused across all cells
of that width, exactly mirroring run-level sharing. For each cell and setup
seed compute the actual fixed-receipt squared source error, not the squared
norm of an error sum across MLPs. Combine it with independently sampled M151
residual events, retaining the empirical cross term; do not replace the
fixed-receipt loss by an independence identity in the primary tail analysis.

Define each cell's cost-normalized loss ratio using M235 cost
`88.095092688B`, M151 cost `89.708636240B`, and the actual fixed receipt.
Use 20,000 hierarchical bootstrap resamples with seed `2350001`: resample
setup-receipt clusters first, cells within family second, and residual event
blocks within cell. The primary statistic is the arithmetic mean of per-cell
squared losses, matching the contest's mean-per-MLP MSE.

G0 passes only if:

- pooled and each-family one-sided 90% upper bounds are `<0.99`;
- every cell's mean across the 32 setup seeds is `<1`;
- setup seed `0` has pooled and each-family point ratios `<1`;
- at least 30 of 32 setup seeds have pooled point ratio `<1`, and the worst
  setup-seed pooled ratio is `<=1.05`;
- the p99 paired squared-source-loss ratio over the separate outer seed band
  `23510000..23514095` (4,096 setup receipts, each shared across all cells) is
  `<=1.25`;
- the empirical mean residual/sketch cross term is consistent with zero under
  the hierarchical 90% interval, and no family has a positive ratio-vs-width
  slope.

This stage may kill but cannot promote target width.

## Frozen G1 and untouched holdout

Only after native and G0 independently pass, open M227's eight width-256
generated cells:

```text
diagonal-SPD state seeds 22732001..22732004
iid-He-SPD state seeds   22732101..22732104
event streams            22733001..22733008
setup receipts           0 and 23532001..23532015  (16 total).
```

Use exactly 16,384 independent M151-q0 events per cell. Each setup receipt is
shared across all eight cells. Bootstrap setup seed, whole cell, and event
block hierarchically with seed `22730001`, 20,000 resamples. Promotion to a
generated-source survivor requires pooled and family upper90 `<0.99`; every
cell's setup-averaged point ratio `<1`; seed `0` pooled/family ratios `<1`; at
least 14/16 outer seeds pooled `<1`; worst outer-seed pooled ratio `<=1.05`;
p99 paired loss ratio `<=1.25`; and a cross-term interval containing zero.

The untouched holdout remains state seeds `22732201..22732208` and
`22732301..22732308`, event seeds `22734001..22734016`, and new setup receipt
seeds `23532251..23532266`. Analysis and thresholds are identical. No G0/G1
or seed-0 result may select or alter the holdout procedure.

## Stop, ownership, and credit

Any setup legality, official-seed ownership, explicit-Philox, receipt law,
immutability, covariance, shared-dependence, algebra, exact bill, call, setup
timeout, wall, RSS, cross-term, tail, or source-efficiency failure kills this
fully specified implementation. No setup-seed substitution, cyclic shift,
per-MLP RNG, coefficient, `k`, threshold, batching, precision, or timing-
boundary drift is allowed under M235. A per-MLP cyclic transform would be a
new statistical child with a new bill and ladder.

M235 claims no retirement of the `3.727757440B` M151 compiler without a later
integrated ABI trace. Even a holdout pass would grant only an unbiased-over-
setup, cost-traced, generated-source survivor. It would not establish final-
output MSE, score, submission safety, rank, prize, or a winning entry.
