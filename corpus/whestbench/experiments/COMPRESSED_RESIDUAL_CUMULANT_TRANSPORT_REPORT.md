# Compressed residual-cumulant transport

## Verdict

**Kill this constant-modulus probe-formation implementation. Preserve the
`<=12D` residual covariance algebra.**

With exact scalar cumulant responses supplied free by the evaluation oracle,
the compressed inverse remains strong: iid probes retain `0.92627` combined
standardized fidelity and `0.98353` correction fidelity; orthogonal Hadamard
frames retain `0.92479` and `0.98346`. Both get every material sign (`94/94`).

That is not a deployable win. The probe equations are rank-deficient, and the
preserved weights/current conditional state supplies no scalar k3/k4 response
vector. Orthogonalization rearranges the same measurements; it creates no new
higher-moment information. This is a local coefficient-formation kill, not a
rejection of the compressed representation.

No official row, scorer, API, or competition holdout was touched.

## Frozen comparison

| 128 symmetry-paired lines/cell | k3 fidelity | k4 fidelity | combined | correction | signs |
|---|---:|---:|---:|---:|---:|
| iid Rademacher | 0.978195 | 0.917108 | **0.926273** | 0.983525 | 94/94 |
| orthogonal Hadamard/Rademacher | 0.978195 | 0.915363 | **0.924790** | 0.983457 | 94/94 |

These are oracle-geometry scores: exact dense cores generated the right-hand
sides solely to measure what the inverse map would preserve. They are not
candidate formation scores.

Orthogonal frames offer no material gain. Their combined fidelity is 0.15%
lower, and the recovered core errors are essentially identical:

| design | median k3 core error | median k4 core error |
|---|---:|---:|
| iid | 0.15310 | 0.20331 |
| orthogonal | 0.15310 | 0.20331 |

All nine fresh `n in {8,12,16}`, `L in {2,3,4}` cases used 32,768 antithetic
paths and fresh network, probe, and next-row seeds. One completed audit was
performed. An earlier launch stopped at module import before generating any
case or result; the import was repaired without changing the frozen design.

## Exact constant-modulus obstruction

Every frozen probe has `v_i^2=1/n`. Ordered Gram-Schmidt makes the second
matrix-algebra direction, when present, the trace-free part of `diag(d)`.
For any trace-free diagonal matrix `D`,

```text
<D, vv^T> = sum_i D_ii v_i^2 = tr(D)/n = 0.
```

The measured maximum response of this blind coordinate is `2.78e-17`.
Therefore an entire matrix coordinate is invisible. K3 loses every core
coefficient incident to it; K4 loses the corresponding symmetric row/column.
Additional polynomial symmetries create still more null directions.

Across cells, the minimum identifiable fractions are only `0.3611` for k3 and
`0.2051` for k4, with maximum nullities 47 and 62. At n=12/16 the typical
nonzero spectrum is reasonably conditioned, but this does not repair exact
zeros. At n=8 even the nonzero k3 condition reaches `6.20e6` iid and `6.62e6`
orthogonal, above the frozen `1e6` gate.

Antipodal pairing also cannot help. Degree-three equations and responses both
negate under `v -> -v`; degree-four equations and responses repeat. Its exact
additional rank is zero.

## The deeper observability obstruction

The current conditional state contains probabilities, means, diagonal
covariance residuals, and four covariance factors. These determine moments
through order two, not the directional third and fourth cumulants required on
the right-hand side.

This nonidentifiability is exact. For any factor `A`, let `X=A Z`. Independent
standard Gaussian coordinates and independent standardized non-Gaussian
coordinates can both satisfy

```text
E[X] = 0,       Cov(X) = A A^T,
```

while their k3/k4 tensors differ. Centered exponential coordinates, for
example, have scalar cumulants 2 and 6 instead of zero. Hence no deterministic
function of the preserved mean/covariance state can return the required probe
responses for both laws.

The fixed network weights do contain more information than this compressed
state, but the probe inverse supplies no recurrence or gate-region integral
that extracts it. Such a weights-only Price/Hermite response identity remains
an unresolved complementary mechanism. Orthogonal probes are an inversion
tool, not an information source.

## Compression score law at n=256, L=32

If exact scalar responses were free, the arithmetic fits comfortably:

```text
conditional recurrence model       3.959423 B
terminal <=12D contraction         6.444519 B
128-line designs                    1.691576 B
fixed small-core solves             0.244252 B
------------------------------------------------
total                              12.339770 B
headroom below 80 B                67.660230 B
```

So the representation and contraction are not the budget problem. Response
formation is.

The direct sampling substitute must propagate particles through the network
and project every layer onto 128 directions. Under the frozen billed-like law,

```text
F_response(S) = 6,311,936 * S
F_total(S)    = 12,339,770,368 + F_response(S).
```

The 80B envelope allows at most 10,719 paths, only 670 per conditional cell.
Even under an ideal Gaussian noise law, standard errors are approximately
`0.095` for skewness and `0.189` for excess kurtosis; non-Gaussian tails can be
worse. This is neither an analytic response nor a credible accurate k4
transport, and no recurrence has been derived.

## Recursive disposition

Passed components:

- contraction geometry is genuinely compressible;
- the fixed covariance algebra still preserves all material signs;
- terminal state/contraction arithmetic fits under 80B;
- exact H8/H12/H16 construction, parity, and algebra tests pass.

Failed links:

- constant-modulus probes are not identifiable;
- the current state has no observable scalar higher-cumulant response;
- sampling the response consumes the analytic headroom while leaving noisy
  per-cell fourth cumulants.

Preserve the `<=12D` algebra and its rank-four terminal factors. Do not retune
probe count, pseudoinverse threshold, or seeds. A legitimate reopening must
change the failed mechanism: use nonconstant-amplitude probes and, crucially,
derive an explicit weights-only higher-moment response recurrence before any
new accuracy screen.

Machine-readable evidence is in
[`probe_audit_results.json`](probe_audit_results.json) and
[`decision.json`](decision.json); the frozen contract is
[`PREDECLARED_GATE.md`](PREDECLARED_GATE.md).
