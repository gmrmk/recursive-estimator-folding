# M120C analytic reference second independent audit - 2026-08-07

## Verdict: `REPAIR`

`PASS_TO_INTEGRATE` is not granted. The repaired global refinement policy is
correct for finite indicators, but one fail-open non-finite-indicator path
still violates the required invariant and is inherited by both forward
consumers. This is a narrow controller repair, not a mathematical kill.

This audit was source-only. I did not edit the analytic reference or its tests,
did not run the 27-network grid, and did not create or write `out/`. R1, R2,
R4, and R5 remain open and outside this verdict.

## Frozen subject hashes

| subject | SHA-256 |
|---|---|
| `m120c_analytic_dense_reference.py` | `cdb3df03fb60d6a810a63506c97c8e3db3df3c3c535fd913630bf7feba9d4f54` |
| `test_m120c_analytic_dense_reference.py` | `e0438ff67395ab074e465d281bbc9aee2fb55f5fcf5e33fcec09c322d5fea05a` |
| `test_m120c_protocol.py` | `b559bdb72c750f5d1451a4168f63d768af02f791382983a7c0b7f4e35908701d` |
| `test_corrected_cp_jacobian.py` | `8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d` |
| `corrected_cp_jacobian.py` | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| `m120c_protocol_harness.py` | `58b91067c13a66ada75f5e32e4d8883ce8495b8b7a167fbfce97a4b62569a788` |
| `m120c_protocol_manifest.json` | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` |
| author repair report | `821ebcf1aba0ea4b3abeccd10970193faf098bf7550a01f791f8556f88ec220d` |
| first independent analytic audit | `678dee4ca4e1b126c972052f617a8cd3f8aaa8380ce5f29845dd17df3130e60c` |

The analytic source and analytic-test hashes exactly match the author repair
report. The binding harness still does not import the standalone analytic
module, so this audit concerns readiness to integrate the R3 reference, not an
already-integrated or executable binding path.

## What the finite controller repair gets right

For finite 32/64 estimates, `quadrant_probability` now keeps every active
interval in one ledger. It recomputes

```text
disagreement = fsum(abs(I64(interval) - I32(interval))
                    for every active interval)
```

after each split and returns only after the finite test cases put that global
sum at or below `1e-13`. The selected interval is explicitly
`max(..., key=indicator)`, so refinement follows the largest contributor, not
insertion order.

Independent mocked checks observed:

- the repaired `1.48*T` root is split once and returns with the two child
  indicators summing to exactly `0.74*T = 7.4e-14`;
- a deliberately larger right child is selected before the earlier, smaller
  left child, producing the interval trace
  `[0,.5] -> {[0,.25],[.25,.5]} -> {[.25,.375],[.375,.5]}`;
- an irreducible indicator reaches all 4,096 allowed splits and then raises
  `AnalyticReferenceFailClosed("Plackett paired-order global convergence failed")`
  before evaluating split 4,097. The exact `_gauss_interval` call count was
  `2 + 4*4096 = 16,386` single-order evaluations (8,193 interval pairs).

Thus the original dynamic-local-budget defect is repaired, the largest-error
policy is implemented, and finite 4,096-split exhaustion fails closed.

## Blocking counterexample: NaN indicator returns

The controller never establishes that either paired estimate or their
disagreement is finite. Python comparisons with `NaN` are false. I replaced
only the in-memory interval evaluator so the 32-node estimate returned `NaN`
and the 64-node estimate returned `0.0`. The unedited function then computed

```text
indicator = abs(0.0 - NaN) = NaN
NaN > 1e-13                    -> False (loop skipped)
NaN > 1e-13                    -> False (post-check skipped)
value = Phi(0)*Phi(0) + 0.0    -> 0.25 (finite and range-valid)
```

and returned normally:

```text
QuadrantProbability(
    value=0.25,
    paired_order_disagreement=nan,
    subdivisions=0,
)
```

Therefore the global active-interval indicator is not guaranteed to be
`<=1e-13` before return.

Both forward callers inherit the failure rather than the intended rejection:

- `analytic_local_kernels` returned finite kernels and reported
  `max_quadrature_disagreement == 0.0`; Python's `max(0.0, NaN)` masked the
  non-finite indicator.
- `analytic_relu_gaussian_moments` consumed `.value` and returned finite means
  and covariance.

This is an exact fail-closed contract violation even though ordinary tested
Gaussian inputs did not trigger it.

## Required repair and acceptance test

Before integration:

1. In `interval`, reject unless `coarse`, `fine`, and
   `abs(fine-coarse)` are all finite. Raise `AnalyticReferenceFailClosed`.
2. Before every convergence comparison and before return, require
   `math.isfinite(disagreement)` as well as
   `disagreement <= QUADRATURE_TOLERANCE`.
3. Add a regression with a non-finite 32-node result and finite 64-node result.
   `quadrant_probability`, `analytic_local_kernels`, and
   `analytic_relu_gaussian_moments` must all raise; none may return a value or
   hide the indicator.
4. Preserve the existing `1.48*T`, largest-contributor, 4,096-cap, Philox, and
   endpoint checks.

The repair should not clip or replace a non-finite estimate. It must reject it.

## Unchanged mathematics and prohibited mechanisms

The mathematical formulas re-audited cleanly. The signed Plackett interval is
correct for negative correlation. The off-diagonal Price kernel, central-mean
cross block, conditional variance cross block, direct diagonal limits,
bivariate raw second moment, symmetric off-diagonal contraction, and diagonal
pullback overwrite agree with the identities documented in the first audit.

A fresh 24-state Philox directional audit over dimensions 2 through 5 and all
generated outputs gave maximum fine-step error
`1.1595179039147752e-08`, versus coarse-step
`4.6379132534468681e-08`; the maximum refinement gap was
`3.4783953495320930e-08`. A separate fresh 256-case signed zero-mean Philox
sweep had maximum closed-form identity error `1.6653345369377348e-16`, maximum
reported finite indicator `5.4845017416482733e-14`, and at most five splits.
Both signed just-outside endpoint cases were accepted within tolerance; exact
and inside-margin endpoints rejected.

Static inspection found no correlation clip, variance replacement, terminal
denominator replacement, old `fullcov` call, or finite-difference machinery in
the binding module. `FLOOR=1e-10` is used only as a rejection threshold. The
finite differences above are independent audit probes, not binding logic.

## Executed scoped checks and artifact state

- `python -m unittest test_m120c_analytic_dense_reference.py
  test_m120c_protocol.py test_corrected_cp_jacobian.py`: **20/20 passed**.
- Independent global-sum, largest-contributor, exact split-cap, forward-caller,
  fresh Philox directional, closed-form, and signed endpoint probes were run
  only in memory.
- `m120_price_normal_ordered_adjoint/out/` was absent before and after every
  check.

The passing ordinary tests do not override the deterministic NaN
counterexample. The exact next state is `REPAIR`; R3 may be re-audited after
the narrow fail-closed change. R1, R2, R4, and R5 remain open.
