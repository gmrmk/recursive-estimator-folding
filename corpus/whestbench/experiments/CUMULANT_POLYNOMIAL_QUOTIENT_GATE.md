# Predeclared gate: nonredundant cumulant polynomial quotient

Written before any quotient rank, condition, recovery, fidelity, sign, or
equivariance result. This is a recursive child of the amplitude-coded probe
audit. It changes only the coefficient parameterization.

## Frozen parent

- Keep the nine fresh synthetic cases, 16 cells, 16,384 Philox base inputs
  plus negatives, next-row weights, probe seeds, and covariance seeds exactly
  as in `amplitude_coded_cumulant_probes/run_audit.py`.
- Keep `P=128` normalized-Gaussian unoriented lines, exact antipodal
  interpretation, `rcond=1e-10`, rank-four truncation, `h<=7`, and `q<=12`.
- Keep the physical equations

  ```text
  y3(v) = (Q_L^T v)^T C3 (Q_M^T svec(vv^T)),
  y4(v) = (Q_M^T svec(vv^T))^T C4 (Q_M^T svec(vv^T)).
  ```

- Change only `vec(C3)` and `svec(C4)` to coordinates in their identifiable
  polynomial row spaces. No probe, case, seed, threshold, contraction, or
  downstream metric may change.
- Dense empirical k3/k4 tensors and exact cores remain evaluation oracles only.
  They may create audit right-hand sides but may not construct the quotient.
- No WHest row, scorer, target, API, submission, or holdout is touched.

## Quotient construction

For each cell, build the response-free amplitude design `D3,D4` from the
frozen bases and frozen directions. Compute one SVD with `rcond=1e-10`, order
singular directions by decreasing singular value, and make each right-singular
vector canonical by requiring its largest-absolute coordinate (first on a
tie) to be positive. The resulting columns `Q3,Q4` parameterize

```text
vec(C3)_id = Q3 theta3,   svec(C4)_id = Q4 theta4.
```

The inverse designs are `D3 Q3` and `D4 Q4`. This construction uses bases and
directions only, never response values or oracle coefficients.

Independently, construct complete monomial coefficient maps for

```text
(l_a.v)(v^T B_b v)                 in Sym^3(R^n),
(v^T B_b v)(v^T B_c v)             in Sym^4(R^n),
```

with the exact `vec/svec` scaling. Their kernels are, by definition and
monomial independence, the coefficients annihilated by full cubic/quartic
symmetrization. This complete map is an audit certificate at n<=16, not the
n=256 implementation.

## Gates

Classify the quotient geometry as a **screened survivor**, while explicitly
preserving the separate RHS observability block, iff all hold:

1. In every cell, the quotient dimensions equal both the frozen amplitude
   design ranks and the complete symmetrization-map ranks.
2. Every quotient design is full column rank and has condition `<=1e6`.
3. Exact physical cores are reproduced to relative error `<=1e-10`; all
   frozen oracle responses are reproduced to relative error `<=1e-10`.
4. Standardized k3, k4, and combined fidelity are each `>=0.80`; material-sign
   accuracy is `>=0.80`, with material output in every case.
5. Coordinate permutation and dense orthogonal equivariance defects are
   `<=1e-10` for quotient predictions and reconstructed coefficients.
6. The n=256 billed-like response-free arithmetic is `<80e9`, with finite
   outputs and all tests passing.

Passing does **not** resolve the missing directional response. The only passing
decision is `screen_quotient_geometry_preserve_rhs_observability_block`.

