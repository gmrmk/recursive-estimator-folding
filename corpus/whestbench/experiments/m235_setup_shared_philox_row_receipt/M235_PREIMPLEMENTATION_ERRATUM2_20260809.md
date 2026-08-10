# M235 preimplementation erratum 2 -- dimensions, aggregation, and native reuse

Date: 2026-08-09. Sealed after independent contract review and before any
M235 test, implementation, native trace, or G0 execution. This file completes
protocol details missing from the original declaration and first erratum. It
does not change the target estimator, target `k=32`, positive-bill circuit,
or thresholds.

## Small-width receipt size and layer-slice ownership

G0 uses M227's exact small-width rule

```text
k_small = n/8:
width 8  -> k=1
width 16 -> k=2
width 24 -> k=3.
```

For every `(setup_seed,width)`, generate one full 31-slice setup receipt of
shape `(31,width)` using the same explicit setup Philox owner and one
independent-slice `permuted(axis=1)` call. Every G0 source cell at that width
uses canonical layer slice 1, array index 0. Thus one setup seed gives exactly
the same selected label set `H` to every cell of a width, matching the shared-
receipt dependence rather than silently drawing per-cell subsets.

G1 and holdout use the same source-proxy convention: generate the full
`(31,256)` receipt, use target `k=32`, and give canonical layer slice 1 to
every response-free source cell. Native 31-layer stack tests differ only
because they represent actual layers: actual layer `l=1..31` consumes receipt
slice `l`. No result may select a favorable slice or average over slices.

The small-width algebra unit tests at widths 3..9 may use their already-frozen
enumerated subset sizes solely to prove the unchanged formula; they are not
G0 receipt simulations and grant no source-efficiency evidence.

## Exact aggregate loss ratios and family weights

Let `b_c=V_R(c)/128`, `s_cj` be cell `c`'s fixed-receipt source error for
setup seed `j`, and `a=C235/C151=0.982013509293762`. For family `F` with 12
cells, define

```text
B_F = (1/12) sum_(c in F) b_c
L_F = (1/(12*J)) sum_(c in F,j) [b_c + ||s_cj||_F^2]
G_F = a * L_F / B_F.
```

The pooled ratio gives each family weight one half:

```text
B_pool = (B_diag + B_iid)/2
L_pool = (L_diag + L_iid)/2
G_pool = a * L_pool / B_pool.
```

All primary and bootstrap ratios are ratios of aggregate mean losses. Taking
the mean of cellwise ratios is forbidden. Individual-cell gates may still use
`a*(b_c+mean_j||s_cj||^2)/b_c`. Bootstrap resampling preserves two equal
family weights and four cells per family-by-width stratum.

## Exact empirical cross-term normalization

Use the first erratum's paired macros and notation
`X(c,r)=2<s(c,r),rbar(c,r)>`. For a selected bootstrap sample, define family
normalized cross term

```text
Z_F = [mean_(selected c in F, selected r) X(c,r)]
      / [mean_(selected c in F) b_c]
```

and pooled

```text
Z_pool = [(mean X_diag + mean X_iid)/2]
         / [(mean b_diag + mean b_iid)/2].
```

The denominator uses positive exact exhaustive `b_c`, never a realized
`L151` macro. For each of the 20,000 block-bootstrap replicates frozen in the
first erratum, compute `Z_diag`, `Z_iid`, and `Z_pool`. Sort each list in
ascending order. The central 90% interval is the one-based 1,000th and
19,000th order statistics (no interpolation). Each interval must satisfy
`lower <= 0 <= upper`. Nonfinite values kill the gate.

The pointwise p99 `L235/L151` remains the stricter tail check in the first
erratum. It uses the one-based `ceil(0.99*4096)=4056` order statistic per cell
and the corresponding one-based ceiling rank for each family pool, with no
interpolation, clipping, epsilon, or omitted denominator.

## Two-predict native reuse and immutability receipt

Each of the five fresh sequential native processes calls setup exactly once,
then performs two sequential target predictions using the same setup receipt
and fixed empty workspaces. Pair setup seeds

```text
0, 235700001, 235700002, 235700003, 235700004
```

with first generated source seeds

```text
227700001, 227700002, 227700003, 227700004, 227700005
```

and second generated source seeds

```text
227710001, 227710002, 227710003, 227710004, 227710005.
```

Before prediction 1, after prediction 1, and after prediction 2, hostile code
outside the timed kernels records the receipt object identity, selected-view
object identity, underlying data pointer, shape/dtype, and SHA-256 digest.
Every field must be identical at all three observations. Both predictions
must independently satisfy exact M212/M235 calls and bills, finite/symmetry,
M235 component wall, both combined wall gates, and RSS. A warm second call
cannot excuse a failing first call, and a cold first call cannot excuse a
failing second call.

## Exact setup and predict allocation receipts

At target shape setup performs exactly 18 zero-bill `fnp.empty` calls:

```text
M212 staged weight/factor                         2
M212 depth-3 base workspace                      14
M235 powers/cross workspace                       2
TOTAL                                             18.
```

No `empty` call may appear in either predict ledger. The hoist changes only
allocation lifetime. All positive M212 calls, shapes, arithmetic order, and
the exact `1,249,253,376` bill remain unchanged in both predictions. M235's
predict correction remains exactly `864,960,512`.

## Constant-time predict binding scope

The permitted predict-time binding check consists only of fixed Python
identity and integer/string metadata comparisons:

- setup receipt object is the plan-owned receipt object;
- staged and full-domain receipts own the prebound live objects by `is`;
- canonical layer-ID tuple equals the prebound tuple;
- producer epoch, setup seed, width, layers, subset size, and domain tag equal
  prebound scalar metadata.

No predict-time shape walk, dtype string conversion, array equality, value
scan, digest, pointer lookup, uniqueness check, sort, set/list conversion,
allocation ledger, runtime hash, or receipt reconstruction is allowed.
Complete shape/dtype/law/digest checks occur in setup and hostile code outside
the timed predict kernel.

## Setup safety margin and pinned lifecycle hashes

In each fresh official-style process measure raw elapsed time from immediately
before `estimator.setup(ctx)` until it returns. It must be `<4.0 s`, preserving
one second below the official five-second hard limit. Also measure isolated
integer-receipt issuance excluding workspace allocation; it must be `<0.05 s`.
Both are hard M235 gates, not diagnostics. Setup RSS remains `<512 MiB`.

Pinned lifecycle sources are:

```text
whestbench/sdk.py
  B0FCC52C6B531981E46DA6955365AA786260FAB53FD66DCF3675791ED8C3C105
whestbench/subprocess_worker.py
  F1EA178C94E4F7BA790EC1350D83A078982964D6A0C88F90EF58522A234EC089
whestbench/runner.py
  6176EB3A91233AC6AAB8057141C2E82FEEA02BDF955E9F830EE8F756DE9ABC86
```

Any mismatch fails before implementation/native credit.

## Freeze rule

This second erratum is part of the immutable M235 contract. Changing small-
width `k`, layer slice, family weighting, ratio aggregation, cross-term
denominator, quantile convention, second source seeds, setup/predict empty
ownership, binding scope, setup margin, or lifecycle hashes creates a new
child and cannot repair M235.
