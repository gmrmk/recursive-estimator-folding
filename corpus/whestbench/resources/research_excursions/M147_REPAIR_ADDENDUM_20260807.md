# M147 repair addendum -- finite closure and conditional-rank contract

## Status

This addendum implements the two repair gates found by the independent hostile
audit.  It changes neither the Plackett/Price mathematics nor the literal
`48/64 x 16/32` target-cost disposition.  No response cell, truth, scorer,
candidate efficacy, champion, or contest action was used.

## 1. Exact supported local-boundary domain

For a selected `[2,1,1]` triple with repeated index `i` and singleton indices
`j,k`, M147 conditions on the standardized repeated preactivation.  Its
conditional singleton covariance is the Schur minor

```text
S = C[{j,k},{j,k}] - C[{j,k},i] C[i,{j,k}] / C[i,i].
```

The repaired local API accepts a PSD-boundary triple only when both entries of
`diag(S)` are strictly positive above the frozen floating-point floor

```text
256 * eps64 * max(1, max(abs(diag(C)))).
```

`S` itself may be rank one, including exact conditional `rho=+/-1`; that is
the endpoint case solved by M147's rank-one bivariate primitive.  A zero
entry of `diag(S)` is **not** sent through that primitive.  It represents a
deterministic conditional singleton.  If its conditional mean crosses the
ReLU kink, generic PSD-opening directions do not possess the ordinary tangent
that the current fixed-node central derivative expects.  The exact all-strata
branch would require a separate piecewise moving-kink derivation.  Until that
derivation is separately frozen and audited, the API refuses this stratum with
`EndpointCertificationFailure` before quadrature.

This is a narrowing and enforcement of the contract, not a correlation clip,
ridge, deletion, or numerical approximation.

## 2. Finite arithmetic closure

The original public inputs were checked finite, but exact mathematical values
can exceed float64 range.  The repair does the following:

- avoids `inf * 0` in remote truncated-normal boundary terms;
- converts powered endpoint-moment overflow to `EndpointCertificationFailure`;
- checks finite raw moment, tangent, standardized derivatives, and Price
  enclosure before returning a bivariate certificate;
- checks finite univariate conditional moments, completed bridge-state arrays,
  and completed central/tree collision outputs.

Thus a representational overflow is a deterministic rejection, not a nonfinite
estimate that could leak downstream.  It does not assert an artificial finite
answer for an unrepresentable exact moment.

## 3. Added hostile evidence

The static audit and unit suite now include:

1. rank-one all-equal and rank-two repeated/singleton-identical PSD triples,
   each with a feasible zero tangent, both refused explicitly as degenerate
   conditional singleton strata;
2. `rho=+1, alpha=beta=1e308` and
   `rho=-1, alpha=beta=1e200`, both rejected rather than returning `inf/nan`;
3. preservation of the exact conditional rank-one pair test where the Schur
   diagonal remains positive.

The repaired suite has 12 response-free tests.  The re-run static audit retains
the previous mathematical defects and counts, including the cost-kill:

```text
ordinary high-correlation core lower bound: 108,480 > 102,400
conditional-rho=.999 adversary lower bound: 606,720 > 102,400.
```

## 4. Downstream rule

M146 or a later generated-state caller may treat every triple deterministically:

- supported positive-Schur triple: evaluate M147;
- zero-Schur singleton or arithmetic overflow: fail closed and select a
  separately predeclared non-M147 fallback; do not clip, ridge, retry, or infer
  a coefficient.

Any future exact zero-Schur branch is a new mutation and must prove its
piecewise tangent treatment and cost independently.
