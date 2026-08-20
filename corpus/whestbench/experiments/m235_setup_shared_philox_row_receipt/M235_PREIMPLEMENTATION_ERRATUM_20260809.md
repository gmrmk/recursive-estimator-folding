# M235 preimplementation erratum -- frozen G0 macro replay and M212 setup ledger

Date: 2026-08-09. This erratum is sealed after the M235 predeclaration but
before any M235 test, implementation, native trace, or G0 execution. It fills
an under-specified experimental receipt; it changes no estimator, coefficient,
cost, seed grid already assigned to setup receipts, or promotion threshold.

## Exact G0 residual baseline

For every one of the 24 frozen small-width cells, enumerate the full ordered-
distinct event domain exactly under the frozen M151 `q0`. Compute

```text
V_R(c) = E_q ||H_e F_e/(2 q0(e)) - (T_D-Cstrict)||_F^2
```

without Monte Carlo. The exact M151 `K=128` expected source loss is
`V_R(c)/128`. For each of the 32 primary setup receipt seeds
`{0,23501001..23501031}`, compute the actual deterministic fixed-receipt
sketch error `s(c,j)` and primary conditional expected loss

```text
L_primary(c,j) = V_R(c)/128 + ||s(c,j)||_F^2.
```

The exact independence expectation makes the mean cross term zero here; it is
not used as a substitute for the separate empirical macro-replay stress gate
below.

The 20,000 primary hierarchical bootstrap replicates use Philox seed
`2350001`. In each replicate:

1. resample the 32 setup-receipt indices with replacement;
2. within each of the six fixed family-by-width strata (two families times
   widths 8,16,24), resample its four whole cells with replacement;
3. average the selected **per-cell squared losses**. Never sum source errors
   across MLPs before squaring.

## Frozen empirical K=128 macro replay

The empirical cross-term and tail gate uses exactly 4,096 paired macro
replays per cell. Canonical cell index `c=0..23` is the order printed in the
M235 predeclaration: diagonal-SPD by widths 8,16,24 then iid-He-SPD by widths
8,16,24, with ascending seed inside each width.

For replay index `r=0..4095`:

```text
setup receipt seed          = 23,510,000 + r
residual RNG domain         = M235_G0_RESIDUAL_MACRO_V1
residual Philox seed(c,r)   = 235,200,000,000 + 4,096*c + r
residual events             = exactly 128 independent frozen-q0 draws
event IDs                   = 0..127 in Philox stream order
```

The setup receipt seed is reused across every cell, reproducing one run-level
receipt. Residual seeds are disjoint across cells and replays and are disjoint
from every setup, bootstrap, G1, and holdout seed band. No stream is spawned
from another, retried, clipped, or conditionally skipped.

Let `rbar(c,r)` be the mean of the 128 residual vectors and `s(c,r)` the fixed
receipt error. The paired observations are

```text
L235(c,r) = ||s(c,r) + rbar(c,r)||_F^2
L151(c,r) = ||rbar(c,r)||_F^2
X(c,r)    = 2 <s(c,r), rbar(c,r)>.
```

The M235 and M151 observations use the same residual macro, so their loss
difference is paired. The setup and residual streams remain independent by
construction. The p99 ratio is computed from `L235/L151` separately for every
cell and for each family pool; all reported p99 values must be `<=1.25`.
Nonfinite or zero-denominator observations kill the fixed gate; no epsilon,
clipping, winsorization, or omission is allowed.

For the empirical cross-term interval, retain all 128 event vectors and split
them into exactly eight contiguous blocks of 16 events. Each of 20,000
hierarchical bootstrap replicates, using independent Philox bootstrap seed
`2350002`, does:

1. resample the 4,096 outer replay indices with replacement, preserving the
   setup receipt and its paired residual macro;
2. resample four whole cells with replacement inside each of the six fixed
   family-by-width strata;
3. for every selected `(cell,replay)`, resample its eight contiguous 16-event
   blocks with replacement, concatenate the selected blocks, and recompute
   the K=128 residual mean, combined loss, comparator loss, and cross term;
4. average per-cell squared losses, never an error sum.

The pooled and family 90% intervals for normalized `X` must contain zero. The
loss and tail thresholds remain exactly those in the original M235
predeclaration. The exact exhaustive `V_R` screen and the empirical macro gate
must both pass; neither can waive the other.

## M212 setup-hoist accounting clarification

M235 setup owns the fixed-shape `fnp.empty` staged M212 inputs and M212
depth-3 workspaces. Therefore those zero-bill `empty` calls are absent from
the predict call ledger. This removes allocation wall only. Every positive-
bill M212 operation, call shape, call count, arithmetic order, and exact
`1,249,253,376` per-predict bill remains unchanged and is checked in each
fresh native process. M235 may not treat setup ownership as retirement of any
positive M212 work.

## Freeze rule

This erratum is part of the M235 frozen contract. Any later change to macro
count, seed map, RNG domain, K, event order, block size, pairing, resampling
hierarchy, denominator handling, or M212 positive-call ledger is a new child,
not an M235 repair.
