# M179 G0 — index / ABI reconciliation (before any code)

Status: response-free reconciliation deliverable. The cheapest M179 falsifier:
a spec contradiction between the M176 1-based recurrence indices, the depth-32
scored task, and the consumer ABI would void every downstream sub-gate. No
challenge instance, target, scorer, model loop, or sealed cell is read. This
is not a producer pass.

Governing sources (read first-hand):
- M176 contract: `../m176_background_archive_producer/M176_EXACT_BACKGROUND_ARCHIVE_NO_GO_20260807.md`
- consumer ABI: `../m125_source_batched_forward_tangent/m125_forward_tangent.py:14-63`
- production estimator: `../base_estimator.py:23-48, 111-229`
- M178 provider: `../m178_certified_phi2_owent/m178_certified_phi2_owent.py`

## 1. The index hazard, resolved

The MLP is `width d = 256`, `depth L = 32`. `mlp.weights` is a length-32 list
of `(256, 256)` matrices, 0-based `weights[0..31]` (`base_estimator.py:31`).
The M176 recurrence is written 1-based, `W_l` for `l = 1..31`, with `V_0 = I`,
`mu_0 = 0` (`M176…md:26-35`). These reconcile exactly:

```
M176 1-based    0-based mlp.weights    role
------------    -------------------    ----
mu_0, V_0       (none; the input)      standard-normal input state
W_1 .. W_31     weights[0] .. [30]     recurrence weights producing (mu_l,V_l), l=1..31
W_32            weights[31]            terminal readout weight (= weights[depth-1])
```

- `V_0 = I`, `mu_0 = 0` is the input distribution (standard normal), BEFORE
  `weights[0]`.
- `a_l = mu_{l-1} W_l`, `C_l = W_l^T V_{l-1} W_l`, then `(mu_l, V_l)` are the
  post-ReLU zero-order moments, for `l = 1..31` (0-based weights[0..30]).
- The SCORED quantity is `mu_32[i] = E[ReLU(X_i)]`, `X ~ N(a_32, C_32)`,
  `a_32 = mu_31 W_32`, `C_32 = W_32^T V_31 W_32` — one terminal application
  using `weights[31]`. "Only final-layer MSE is scored" (resume prompt §1);
  the scored row is index `depth - 1 = 31` of the estimator's
  `(depth, width)` output (`base_estimator.py:229` stacks
  `(*analytic_means[:-1], final_mean)` — 31 intermediate rows + the terminal).

**M179 scope:** produce the labelled background archive of `(mu_l, V_l)` for
`l = 1..31` and `J_(l+1)` for `l = 1..30` (i.e. `J_2..J_31`). The terminal
`mu_32` readout and any source/efficacy work are OUT OF SCOPE (separate later
mutations).

## 2. Jacobian-index reconciliation

`BackgroundEntry` carries `J_(l+1)` derived from `(a_{l+1}, C_{l+1})` for
`l < 31` (`M176…md:76`). So entry `l` (l=1..30) stores the Jacobian bundle of
the NEXT pre-ReLU state. There are 30 such bundles, `J_2..J_31`, each an
n-vector/n×n-matrix set `{p, r, K, Hmu, Hv}`.

Cross-check against the consumer chain contract
(`m125_forward_tangent.py:114-122`, `_validate_chain`): a full source-carrier
chain requires `len(weights) == len(jacobians)` and
`len(sources) == len(weights) + 1`. That chain (Source211 → TangentState) is a
LATER mutation; M179 only supplies the `J` bundles it will consume, in the
`LocalReluJacobian` field order below. The exact chain length is fixed when
the source-conversion mutation is specified, not here.

## 3. Consumer-ABI conformance targets (bit-for-bit)

Each `J_(l+1)` bundle must construct a `LocalReluJacobian`
(`m125_forward_tangent.py:34-63`) without raising:

| M176 symbol | LocalReluJacobian field | shape / dtype | hard invariant |
|---|---|---|---|
| `p_i = Phi(alpha_i)` | `probability` | (256,) f64 | finite |
| `r_i = phi(alpha_i)/(2 sigma_i)` | `mean_variance_derivative` | (256,) f64 | finite |
| `K` (K_ij; K_ii = p_i) | `price_kernel` | (256,256) f64 | **`np.array_equal(price, price.T)`** (bitwise symmetric) + finite |
| `Hmu` (Hmu_ij; Hmu_ii = 2 m_i (1-p_i)) | `h_mu` | (256,256) f64 | finite (NOT required symmetric) |
| `Hv` (Hv_ij; Hv_ii = p_i - 2 m_i r_i) | `h_variance` | (256,256) f64 | finite (NOT required symmetric) |

`V_l` archived as an exactly-symmetric (256,256) f64 covariance (mirrors the
`TangentState.covariance` invariant, `m125…py:28`). The bitwise-symmetric
requirement on `K` and `V_l` is load-bearing: the two-sided GEMM
`W^T V W` and the pair-symmetric `K_ij` are algebraically symmetric but not
bit-identical across triangles after float GEMMs, so the producer must
canonicalize (`0.5*(M + M.T)` — and CHARGE that add+scale, per
`m125…py:105-109`), then assert `array_equal`.

## 4. The load-bearing divergence (why this is a NEW producer)

`base_estimator._diagonal_gaussian_pass` (`:23-48`) propagates a DIAGONAL
variance **vector** (`var = fnp.ones(width)`, `var_pre = var @ (weight*weight)`)
— it never forms an n×n `V_l`. The M176 recurrence needs the FULL covariance
`C_l = W_l^T V_{l-1} W_l`. Therefore M179 is a distinct full-covariance
recurrence and MUST NOT reuse the diagonal pass — exactly the M174/M175
finding ("production base propagates only diagonal variance"). Likewise the
only existing full-cov closure, `fullcov_gaussian_mm/estimator.py`, is the
BANNED donor: its `_phi2_gauss10`, `1e-24` variance floor, and correlation
clip re-trigger the M176 no-go. The producer's per-pair bivariate values and
derivatives come from the M178 provider
(`evaluate(a, b, rho, backend=FlopscopeBackend())`), on the SPD stratum, with
the M177 exact rank-one / zero-variance / non-PSD strata handled by their
closed limits (not clipping).

## 5. What G0 does NOT settle (deferred to the predeclared protocol + G1..G5)

- The exact assembly of `E[ReLU(X_i)ReLU(X_j)]` from univariate `Phi, phi` and
  `Phi2` (M177: "an algebraic sum of Phi(alpha_i), phi(alpha_i), and
  Phi2(alpha_0,alpha_1;rho)"), and which M178 outputs feed `K/Hmu/Hv`
  (value vs `dV/drho` = bivariate density vs `dV/da` conditional term).
- The inclusive FLOP ledger and the B=8 liveness schedule (G4).
- The endpoint-strata dispatch wiring (G2/G3) and its hostile grid.

These are the next deliverables. G0's sole claim: the index map, the scored
row, the archive scope, the ABI conformance targets, and the diagonal-vs-full
divergence are mutually consistent and contradiction-free. **G0 PASS.**
