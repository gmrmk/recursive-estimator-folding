# M227 predeclaration -- exact-integrated row HT collision subtraction

Date: 2026-08-09. Frozen before any M227 implementation, M227 test, generated
source-efficiency readout, or M227 native resource run. This is a one-
mechanism, generated-only, response-free mutation. Challenge weights, truth,
scorer, leaderboard data, submissions, cached responses, and champion output
are forbidden.

## Parent boundary and the one changed mechanism

M151 uses an exact deterministic strict-distinct rank-one control plus its
unchanged fixed-`q0`, `K=128` distinct residual. M212 cheaply compiles the
same rank-one control on the complete ordered domain. M215 proves the exact
conversion

```text
Cstrict = Cfull(M212) - Ccollision.
```

M227 changes only how `Ccollision` is obtained. The M212 objects `p`, `B`,
and `rho` remain exact and live. A single uniform-without-replacement subset
of `k=32` hidden rows per layer estimates only the four remaining row totals
`t,A,E,D`. The four estimates use the same subset. M151's strict `K=128`
residual, proposal, exact coefficient, physical collision ownership,
Source211 slots, and single existing M125b forward carrier remain unchanged.

There is no collision-triple sampler, adaptive `k`, clipping, pilot, response
dual, second carrier, M198 adapter, terminal mutation, or proposal mutation
in M227.

## Frozen algebra and ownership proof

For one source layer let

```text
S   = diag(u) W
p   = S^T 1
B   = S^T S
rho = diag(B)

t = sum_i s_i^3
A = sum_i outer(s_i^2, s_i)
E = sum_i outer(s_i^3, s_i)
D = sum_i outer(s_i^2, s_i^2),
```

where `s_i` is row `i` of `S` and powers are componentwise. M215's exact
collision source is

```text
Ccol_aaab = -18 diag(p) A - 6 t p^T - 12 diag(rho) B + 24 E

Ccol_aabb = -12 [A diag(p) + diag(p) A^T]
             - 4 rho rho^T - 8 (B hadamard B) + 24 D

Ccol_aaaa = diag(Ccol_aaab).
```

For each layer draw `H` uniformly from all `k`-subsets of `{0,...,n-1}`,
independently of the unchanged M151 residual stream, and freeze `g=n/k=8`.
M227 uses

```text
that = g sum_(i in H) s_i^3
Ahat = g sum_(i in H) outer(s_i^2, s_i)
Ehat = g sum_(i in H) outer(s_i^3, s_i)
Dhat = g sum_(i in H) outer(s_i^2, s_i^2).
```

Each row inclusion probability is `k/n`, hence each hatted total is unbiased
conditional on the fixed generated state. `Ccol` is affine in these four
totals when exact `p,B,rho` are held fixed, so

```text
E_H[Chat_col | S]    = Ccol
E_H[Chat_strict | S] = Cfull - Ccol = Cstrict.
```

Let `Rhat_D` be M151's unchanged strict residual, with
`E[Rhat_D | S]=T_D-Cstrict`. With independent Philox domains,

```text
E[Chat_strict + Rhat_D | S] = T_D.
```

The existing `B_other` continues to own the physical `[4]`, `[3,1]`, and
`[2,2]` collision paths. M227 subtracts only a semantic rank-one control
collision and never samples or replaces a physical collision owner.

This proof is invalid if `p`, `B`, or `rho` is sketched, squared after
sketching, clipped, shrunk, or reused from a different producer epoch. Those
changes are explicitly prohibited because the displayed nonlinear products
would generally become biased.

## Precise Rao-Blackwell claim

M227 is fundamentally a Horvitz-Thompson estimator of four finite row totals.
It is **not** claimed to be the Rao-Blackwellization of an arbitrary or of the
legacy collision-triple Hansen-Hurwitz sampler.

A narrower conditional statement is valid. Split the collision expression
into the exact live-`B` part `Q_B` and the row-additive `t/A/E/D` part. For a
specifically constructed cluster sampler that keeps `Q_B` analytic, first
samples a row anchor, and then samples a within-row event for only the
row-additive part, the selected row packet is the conditional expectation of
that within-row event. M227 is therefore a partial/conditional
Rao-Blackwellization of that expressly matched sampler. Exact M215, which
sums all rows, remains the full Rao-Blackwell endpoint and has zero row-
sampling variance.

For any flattened row packet `z_i` belonging to the sampled part, with
`zbar=n^-1 sum_i z_i`, the exact SRSWOR trace variance is

```text
V_row = n^2 (1-k/n) / k
        * [1/(n-1)] sum_i ||z_i-zbar||_F^2.
```

Relative to iid row sampling with replacement, the finite-population factor
is `(n-k)/(n-1)=224/255`. No universal variance dominance over a differently
stratified collision-event proposal is claimed.

## Frozen random receipt

The mathematical law is exact SRSWOR. The target receipt is one Philox
priority vector of length 256 per layer, in a domain separated from M151's
residual draws. The 32 lowest priorities form `H`. Priorities are attached to
hidden-row labels: under a hidden-label permutation, `S` and its priority
receipt are permuted together. Rerunning a position-based `choice` after the
permutation is forbidden because it would fail pathwise covariance.

The proposed FlopScope circuit uses one `(31,256)` float64 priority call and
one row-wise `argsort`. It must explicitly detect equal priorities. A tie may
not be broken by row index; it is a fail-closed receipt error. The proof treats
the Philox priority law as the frozen SRSWOR law conditional on a distinct
receipt. If the native implementation cannot supply this law and pathwise
receipt without changing the frozen ledger, M227 is killed rather than
quietly accepting a biased tie rule.

Frozen domains:

```text
row priorities: M227_ROW_PRIORITY_V1
M151 residual:  inherited M151/M133 domain, unchanged
```

Subset size, domains, and receipts are fixed before state values are read.
No value-dependent resampling or seed replacement is allowed.

## Frozen `k` choice

Only the two pre-audit dyadic candidates `k in {32,64}` were considered. The
comparison uses only the `3.727757440B` M151 B1 compiler envelope that M212
plus M227 proposes to replace, including the hostile five-times wall price.

```text
                              k=32              k=64
M227 arithmetic bill       0.865484288B       1.649180160B
M212 + M227                2.114737664B       2.898433536B
raw envelope remainder     1.613019776B       0.829323904B
combined hostile-wall cap  3.226039552 ms     1.658647808 ms
wall left after M212 max   2.024139684 ms     0.456747940 ms
```

The M212 isolated measured maximum residual wall is
`1.2018998677376658 ms`. `k=64` leaves only `0.456747940 ms` for selection,
gather, two matmul dispatches, pointwise glue, and allocation, so it is killed
before implementation. `k=32` is frozen. This is a headroom choice, not a
claim that 32 is an unconstrained variance optimum. For example, an
arithmetic-only `k=97` nearly fills the envelope but leaves only about
`0.0423 ms` of hostile combined wall and is not credible.

## Frozen target circuit and exact FlopScope 0.10 prediction

Dimensions are `L=31`, `n=256`, `k=32`, float64. Reuse live M212 `S,p,B,rho`
and Source211 slots. Gather the selected rows once; form `S_H^2` and `S_H^3`;
fuse `Ahat,Ehat` in one broadcast-batched matmul; apply all exact `B,p,rho`
terms before those planes die; compute `Dhat=(S_H^2)^T S_H^2` by one direct
batched matmul into the now-dead M212 `B` plane. Fold `g=8` into the existing
integer collision constants. No recursion or reshape is allowed.

```text
operation                         calls      exact billed FLOPs
Philox random (31,256), f64          1              15,872
argsort axis=rows                     1             507,904
take_along_axis, f64                   1           2,031,616
matmul (3 product-equivalents)         2         767,950,848
multiply (14 full + 2 row-power)      16          57,901,056
add                                    9          36,569,088
sum selected cubic rows                1             492,032
copy final aaab diagonal               1              15,872
reshape                                0                   0
TOTAL                                             865,484,288
```

The two matmul calls are one two-product `A/E` broadcast and one `D` product.
The exact rectangular-product ledger is

```text
3 * L * 2 * (2*n*k*n - n*n) = 767,950,848.
```

`transpose`/`swapaxes` are supported metadata views in the frozen meter path;
any observed extra bill, pack, copy, reshape, or hidden temporary is a failure.

The isolated arithmetic composition is

```text
M212                         1,249,253,376
M227                           865,484,288
component total              2,114,737,664
```

If, and only if, an integrated ABI trace proves that all of M151's
`3.727757440B` B1 compiler is retired, the conditional known branch arithmetic
is

```text
M151 endpoint/residual subtotal  85.980878800B
M212 complete compiler            1.249253376B
M227 row collision subtraction    0.865484288B
conditional total                88.095616464B.
```

That is conditional raw savings of `1.613019776B` versus M151's
`89.708636240B`. It is not granted by this predeclaration. The integrated
trace must prove that the old 49-node forward map, reverse map, dense source
emission, and pointwise compiler do not survive beside M212/M227. If any
unretired portion remains, its full arithmetic and wall are charged; failure
of the same compiler-envelope inequality kills this configuration.

## Frozen memory and call hostility

Incremental nominal payload at `k=32` is

```text
selected S_H                              1.937500 MiB
S_H^2 and S_H^3                           3.875000 MiB
Ahat and Ehat                            31.000000 MiB
full integer rank receipt                 0.060547 MiB
persistent incremental total             36.873047 MiB
transient priority keys                   0.060547 MiB
incremental nominal peak                 36.933594 MiB
M212 + M227 nominal persistent          138.955078 MiB
```

The dead `B` plane owns `Dhat`; M212 scratch owns formula glue. No fourth
rectangular product or sampled `Bhat/rhohat` exists. Nominal payload is not a
peak-RSS credit. The inherited formal reference peak was about `474.859 MiB`,
so naive lifetime addition is unsafe. Every fresh target process must remain
at or below `512 MiB` RSS.

A lawful later repair could stream layer batches such as `8/8/8/7`, inject
Source211, and retire each batch, reducing staged liveness to about 26 MiB.
That repair changes dispatches and wall, is not part of M227, and receives no
credit without a separate predeclaration and integrated trace.

Five fresh target processes use seeds `227700001..227700005`. Each must be
finite, bill-identical, have exactly the declared calls, and satisfy

```text
M212_bill + M227_bill
  + 5 * 1e11 * combined_residual_wall_s
  <= 3,727,757,440.
```

The measured M227-only wall must also be at most `2.024139684 ms` when paired
with M212's frozen maximum. Passing an isolated local trace does not replace
the required integrated process trace.

## Frozen TDD and algebra gates

Implementation may begin only after red tests are written against this file.
No M227 code or test exists at predeclaration time. The future gates are:

1. At widths `3..9`, seeds `227003..227009`, enumerate all subsets for
   `k_small in {1,min(3,n-1)}`. The exact average M227 source must match M215
   strict source in all `aaaa,aaab,aabb` slots within `2e-10`.
2. For each subset, the noncubic circuit must match the direct row-total
   formula within `2e-10`; the M205 cubic oracle is permitted only at these
   generated widths.
3. Hidden-label permutation with the receipt co-permuted, positive ReLU-gauge
   covariance, zero `u`, slot symmetry, producer epoch, layer binding, dtype,
   and independent-random-domain tests must pass. Position-based replay,
   priority ties, duplicate rows, malformed receipts, and epoch mismatch fail
   closed.
4. Target FlopScope traces must match the exact operation and bill ledger,
   with no cubic tensor, triple loop, adaptive branch, fourth `Bhat` product,
   or nonlinear use of an unassembled stochastic source.
5. The existing M125b interface must consume the assembled Source211 once and
   linearly. Any nonlinear transform of `Chat_strict` before the expectation
   identity is completed kills the unbiasedness claim.

## Independent generated source-efficiency ladder

An algebra/resource pass opens only a response-free source premise. It does
not authorize a network-output or score run.

For one generated cell let `H_e=Delta_e-c_e` on the ordered-distinct domain,
`F_e` be the full flattened `aaaa,aaab,aabb` source feature, and `q0` be the
unchanged full-support M151/M133 proposal. Define the exact one-draw M151
residual trace variance

```text
V_R = E_q ||H_e F_e/(2q0(e)) - (T_D-Cstrict)||_F^2.
```

Let `V_S` be the exact finite-population row variance displayed above for the
M227 sampled packet. Independent streams give

```text
V151 = V_R / 128
V227 = V_R / 128 + V_S.
```

Using arithmetic-only costs, M227 can merely break even if

```text
V_S / V_R < 0.0001430459029156082
```

or, equivalently, if added sketch variance is below `1.8309875573%` of
M151's `K=128` residual variance. A one-percent cost-normalized win requires
the stricter `V_S/V_R < 0.00006349044388645213`.

### G0 - cheapest fresh exact falsifier

Construct exactly 24 new M161-style Gaussian-background cells, never the
already-read M161 cells:

```text
family diagonal-SPD: widths 8,16,24; seeds 2270801..2270804,
                     2271601..2271604, 2272401..2272404
family iid-He-SPD:   widths 8,16,24; seeds 2270811..2270814,
                     2271611..2271614, 2272411..2272414
```

Use the M205 rank-one `u`, exact M147-compatible distinct coefficients, the
unchanged M151 `q0`, exhaustive ordered-distinct enumeration, and
`k_small=n/8`. Compute `V_R` and `V_S` as finite-population quantities, not
from sampled subsets. Use target arithmetic costs only for the diagnostic
cost ratio

```text
G = (88.095616464 / 89.708636240) * (V227 / V151).
```

With Philox bootstrap seed `2270001`, perform 20,000 cell-cluster resamples
within family. Kill before target confirmation unless every family and the
pooled one-sided paired-bootstrap 90% upper bound is below `0.99`, every
individual cell has `G<1`, the p99 squared-source-error ratio from 4,096
paired estimator replays per cell is at most `1.25`, and no family has a
positive least-squares slope of `G` against width. This stage may kill but
cannot promote target width.

### G1 - sealed target-width confirmation

Only if G0 and all native gates pass, open eight width-256 generated cells:

```text
diagonal-SPD state seeds 22732001..22732004
iid-He-SPD state seeds   22732101..22732104
event-stream seeds       22733001..22733008, paired in listed order
```

Compute `V_S` exactly over all 256 row packets. Estimate `V_R` with exactly
16,384 independent M151-q0 events per cell through the certified provider;
no fallback or omitted refusal is allowed. Resample whole cells and event
blocks, not individual source coordinates, with bootstrap seed `22730001`
and 20,000 resamples. Replace arithmetic costs by the measured integrated
inclusive costs. Promotion to an integrated generated-source survivor needs
the one-sided 90% upper bound on the pooled and each-family cost-normalized
ratio below `0.99`, every cell's point ratio below `1`, and p99 error ratio at
most `1.25`.

The untouched holdout, opened only after G1 passes, is
`22732201..22732208` and `22732301..22732308` with event seeds
`22734001..22734016`, under the identical fixed analysis. Any tuning after G0,
seed substitution, optional cell exclusion, or covariance coupling between
the row subset and residual is a new mechanism and invalidates this ladder.

The source proxy is pre-transport and response-free. Even a holdout pass
would authorize only an unbiased, cost-traced, generated source-efficiency
survivor. It would not establish final-output MSE, score, submission safety,
or a winning entry.

## Stop and preservation rule

Any algebra, ownership, SRSWOR, receipt covariance, exact-bill, call-count,
memory, hostile-wall, ABI-retirement, or source-efficiency failure kills the
fixed `k=32` M227 configuration. Do not retune to `k=64`, correlate streams,
sketch `B/p/rho`, or add a fourth product after a failure.

A kill preserves the useful facts: the M215 collision identity, the unbiased
row-total construction, the finite-population variance formula, the exact
cost law, and the localization of failure to variance, resource headroom, or
integration ownership. A pass is not called done; it advances to the next
already-frozen gate only.
