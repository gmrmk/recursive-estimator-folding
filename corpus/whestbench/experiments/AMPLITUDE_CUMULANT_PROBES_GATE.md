# Predeclared gate: amplitude-coded cumulant probes

Written before any amplitude-coded design rank, condition, core-recovery, or
contraction result. This is a recursive child of the killed constant-modulus
probe-formation implementation. It changes only the probe-amplitude law.

## Frozen parent and boundary

- Preserve the conditional residual covariance algebra: 16 cells, ordered
  linear dimension `h<=7`, ordered symmetric-matrix dimension `q<=12`, and
  canonical rank-four truncation.
- Preserve the equations

  ```text
  y3(v) = a(v)^T C3 b(v),  a(v)=Q_L^T v,
  y4(v) = b(v)^T C4 b(v),  b(v)=Q_M^T svec(vv^T).
  ```

- Change only the probe distribution. Use `P=128` unoriented lines per cell
  with representatives `v=z/||z||_2`, `z_i iid N(0,1)`, and the exact
  antipodal pair `{v,-v}`.
- `P=128` is fixed from the largest full-core unknown counts, `7*12=84` for
  k3 and `12*13/2=78` for k4, not selected from an outcome.
- Use one SVD pseudoinverse with fixed `rcond=1e-10`; no ridge ladder, retries,
  adaptive line selection, or seed selection.
- Use fresh synthetic iid-He cases only: `n in {8,12,16}`, `L in {2,3,4}`,
  seeds `73000+100*n+L`; 16,384 fresh Philox base inputs plus their negatives.
  Probe seeds start at `830000`; independent next-row seeds start at `930000`.
- Exact dense empirical k3/k4 tensors and cores are evaluation oracles only.
  They may generate response right-hand sides for a geometry audit. No result
  is a deployable response-formation claim.
- No WHest row, target, scorer, API, submission, or holdout is touched.

## Predeclared mechanism and signature

For uniform-sphere probes, `v_i^2` is not constant. Consequently a nonzero
trace-free diagonal matrix `D` has a nondegenerate response

```text
v^T D v = sum_i D_ii v_i^2
```

with probability one. This specifically changes the failed link in the
constant-modulus design. Because a normalized Gaussian is Haar-uniform on the
sphere, its law is invariant under every orthogonal coordinate transform; it
is therefore stronger than merely signed-permutation covariant.

Predicted signature: the formerly blind diagonal-algebra coordinate becomes
observable; all `h*q` k3 and `q(q+1)/2` k4 core coordinates become full rank
with moderate condition; exact-oracle recovery returns the frozen rank-four
algebra fidelity.

## Metrics and promotion gate

Report across every cell:

- full k3/k4 design rank, nullity, and nonzero condition number;
- unoriented duplicate count and formerly blind coordinate response;
- core relative recovery error;
- exact coordinate-permutation and dense-orthogonal covariance defects;
- oracle-fed standardized k3, k4, combined, correction fidelity, and material
  sign accuracy after the unchanged rank-four contraction;
- the n=256 billed-like probe-design/solve cost under the same parent law.

Promote **probe geometry only** iff all are true:

1. every active full core is full rank;
2. every full-rank design condition number is `<=1e6`;
3. standardized k3, k4, and combined fidelity are each `>=0.80`;
4. material-sign accuracy is `>=0.80` and every case has material output;
5. maximum permutation/orthogonal covariance defect is `<=1e-10`;
6. the oracle-free-response arithmetic remains `<80e9` at n=256;
7. all outputs are finite and all algebra/parity tests pass.

Even if these gates pass, the legal right-hand side remains unresolved. The
decision must say `promote_probe_geometry_preserve_rhs_observability_block`,
not deployable estimator. Failure localizes either to amplitude geometry or
numerical conditioning; it does not erase the parent representation.
