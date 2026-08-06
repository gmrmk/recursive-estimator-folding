# Amplitude-coded cumulant probes

## Verdict

**The literal full-core gate fails, but the changed mechanism works. Preserve
the uniform-sphere amplitude geometry and reopen only with an explicit
polynomial-quotient parameterization.**

Normalized-Gaussian probes remove the exact trace-free-diagonal blindness of
constant-modulus Rademacher/Hadamard probes. In every nontrivial conditional
cell, the formerly blind coordinate has RMS response `0.06967` to `0.18121`.
There are zero duplicate unoriented lines, and permutation/orthogonal
covariance defects stay below `4.09e-15`.

The frozen promotion rule nevertheless required literal full rank of all
`h*q` and `q(q+1)/2` coordinates. Actual structured cells reach only `64/84`
for k3 and `58/78` for k4, so the implementation is not formally promoted.
This failure is localized to redundant core coordinates, not missing physical
cumulant content: exact physical cores recover with median relative errors
`2.56e-15` and `2.74e-15` (maxima below `5.66e-15`).

No WHest row, scorer, target, API, or holdout was touched. Dense cumulants
entered only as an evaluation oracle for the inverse geometry.

## Frozen result

| metric | P=128 uniform-sphere lines |
|---|---:|
| k3 design rank at h=7,q=12 | 64 / 84 |
| k4 design rank at q=12 | 58 / 78 |
| maximum nonzero k3 condition | 30.3514 |
| maximum nonzero k4 condition | 52.5370 |
| median k3 core relative error | 2.565e-15 |
| median k4 core relative error | 2.738e-15 |
| standardized k3 fidelity | 0.983631 |
| standardized k4 fidelity | 0.979608 |
| combined standardized fidelity | 0.980382 |
| correction fidelity | 0.991939 |
| material signs | 97 / 98 |
| duplicate lines | 0 |
| max permutation covariance defect | 1.60e-15 |
| max orthogonal covariance defect | 4.08e-15 |

The aggregate accuracy and every numerical condition gate pass. The sole
formal gate failure is raw-coordinate rank.

## What the apparent rank failure means

The probe rows do not observe an arbitrary matrix of coefficients. They
observe homogeneous polynomials:

```text
(Q_L^T v)^T C3 (Q_M^T svec(vv^T)),
(Q_M^T svec(vv^T))^T C4 (Q_M^T svec(vv^T)).
```

The first map symmetrizes a linear factor with a quadratic factor into a cubic
tensor; the second symmetrizes two quadratic factors into a quartic tensor.
For this covariance-generated algebra, those symmetrization maps have
20-dimensional kernels in the literal 84- and 78-coordinate systems. Adding
more directions cannot distinguish coefficients that encode the same cubic
or quartic polynomial.

That is why rank stays at `64/58` while the oracle-generated physical cores
recover essentially exactly: those cores already lie in the identifiable row
space. The constant-modulus parent had this structural gauge *plus* a genuine
trace-free-diagonal blind direction. Nonconstant amplitudes remove the latter
but cannot and should not remove a coordinate gauge.

This interpretation was not used to waive the predeclared gate. It defines the
only legitimate next mutation: explicitly quotient out the symmetrization
kernel before fitting. The next gate should freeze a deterministic SVD/QR
basis for the 64-dimensional cubic and 58-dimensional quartic row spaces and
require full rank there. Probe count, law, seeds, and pseudoinverse threshold
must remain unchanged.

## Accuracy is oracle geometry, not a deployable estimator

After unchanged rank-four truncation and total-cumulance contraction, the
amplitude geometry retains `0.98038` combined standardized fidelity and
`0.99194` Edgeworth-correction fidelity. One small-n case has k4 fidelity
`0.7812`, but the predeclared aggregate k4 metric is `0.9796`, and material
sign accuracy is `98.98%`.

These values answer only: *if exact scalar directional cumulants were free,
would the probe inverse preserve the useful small-core signal?* Yes. They do
not solve the missing right-hand side. Means, diagonal covariances, and four
covariance factors still do not determine directional k3/k4 responses.

## n=256 cost

Under the unchanged billed-like model:

```text
conditional recurrence                 3.959423 B
terminal <=12D contraction             6.444519 B
128-line inverse designs               1.691576 B
fixed small-core solves                 0.244252 B
amplitude generation/setup              0.003146 B
----------------------------------------------------
oracle-free-response total             12.342916 B
headroom below 80 B                    67.657084 B
```

Thus probe geometry is cheap. Response formation remains the actual budget and
observability problem.

## Recursive disposition

Passed and preserved:

- uniform-sphere amplitudes expose trace-free diagonal state;
- the physically identifiable quotient is stable and very well conditioned;
- exact physical cores and downstream contractions survive the inverse;
- the design is orthogonally covariant and fits the analytic envelope.

Failed link:

- the redundant literal coordinate system cannot satisfy a full-coordinate
  rank requirement because cubic/quartic symmetrization has a kernel.

Unresolved link:

- no weights/current-state-only k3/k4 directional response has been derived.

Next changed mechanism:

- construct the deterministic polynomial quotient and rerun the rank gate on
  its nonredundant active coordinates. Do not retune this probe family.

The first process launch was killed by the orchestration timeout after about
1.5 seconds and wrote no result or metric. The unchanged program then produced
the single completed audit in `7.54 s`.

Artifacts: [`PREDECLARED_GATE.md`](PREDECLARED_GATE.md),
[`amplitude_probe.py`](amplitude_probe.py), [`run_audit.py`](run_audit.py),
[`audit_results.json`](audit_results.json), [`decision.json`](decision.json),
and [`test_amplitude_probe.py`](test_amplitude_probe.py).
