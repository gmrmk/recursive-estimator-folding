# M120C analytic dense reference — 2026-08-07

## Verdict: PASS_TO_REAUDIT for the separate R3 reference module

This repairs the analytic local dense-reference prerequisite only.  It does
not authorize the 27-network grid or a lifecycle runner, and it does not claim
R1, R2, R4, or R5 closed.  `out/` and the binding result remain absent.

The new standalone module is
`m120c_analytic_dense_reference.py`; it neither imports nor calls the old
clipped/floored `fullcov` reference.  Therefore the future binding path must
explicitly adopt this module before it can call itself an R3 repair.

## Derivation

Let `Y_i=ReLU(X_i)`, `m_i=E[Y_i]`, `p_i=Phi(alpha_i)`,
`alpha_i=mu_i/sigma_i`, and `L_ij=P(X_i>0,X_j>0)`.  For `i != j`, Price gives
the off-diagonal covariance derivative

```text
d Cov(Y_i,Y_j) / d C_ij = L_ij.
```

The central-covariance mean cross block is

```text
H_mu[i,j] = E[1{X_i>0} Y_j] - p_i m_j,
E[X_j 1{X_i>0,X_j>0}]
  = mu_j L_ij + C_ji dL_ij/dmu_i + C_jj dL_ij/dmu_j.
```

The variance cross block follows by conditioning at the moving threshold:

```text
H_var[i,j] = .5 f_Xi(0) E[Y_j | X_i=0]
             - phi(alpha_i)m_j/(2 sigma_i),
E[Y_j | X_i=0] = relu_mean(mu_j-C_ji mu_i/C_ii,
                            C_jj-C_ji^2/C_ii).
```

The direct diagonal limits used by the implementation are

```text
H_mu[i,i]  = 2 m_i (1-p_i),
H_var[i,i] = p_i - 2 m_i phi(alpha_i)/(2 sigma_i).
```

No near-diagonal finite difference is substituted for those identities.

## Plackett computation and fail-closed domain

`L_ij` uses

```text
Phi2(a,b;rho) = Phi(a)Phi(b) + integral_0^rho phi2(a,b;t) dt.
```

Each interval is evaluated by nested 32- and 64-node Gauss-Legendre rules.
The global controller retains every active interval and its indicator, always
splits the largest one, and recomputes the **sum over the whole partition**.
It returns only when that total paired-order disagreement is at most `1e-13`;
failure to converge by the fixed 4,096-split cap rejects.  Thus individually
small intervals cannot be accepted while their aggregate exceeds tolerance.
The disagreement is recorded in `AnalyticLocalKernels`, not hidden by a clip.

### Narrow non-finite certificate repair

The second independent audit
`M120C_ANALYTIC_REFERENCE_SECOND_AUDIT_20260807.md`
(`49f7eeb87b4f75b0261797dfc2f643391d3b0c876a48378f1c570e5f1e837b3e`)
found that a mocked non-finite paired estimate could evade ordinary Python
comparisons.  This repair changes no formula, tolerance, split selection,
split cap, or gate.  It rejects unless each 32-node estimate, 64-node
estimate, local indicator, every active indicator, and the aggregate
disagreement are finite before comparison or return.  Both forward consumers
also reject a non-finite quadrant value or certificate explicitly, so
`max(0, NaN)` cannot conceal it.

The module rejects nonfinite states, variance/eigenvalue `<=1e-10`, nonsymmetric
covariance, and `abs(rho)>=1-1e-10`.  It has no `maximum` variance floor,
correlation clip, or terminal denominator replacement.  This explicit domain
is preferable to silently changing a degenerate reference problem.

## Source-only validation

All tests used prospective locally generated Philox fixtures; no M120C binding
job was sampled.

- Quadrant identities: independent product and
  `P(X>0,Y>0)=1/4+asin(rho)/(2pi)` at zero means.
- Exact diagonal `H_mu`, `H_var`, symmetric Price-kernel identities.
- Complete all-output dense pullback compared with independently recomputed
  central differences at two steps.  On the fixed fixture, the fine-step
  maximum differences were `1.0053366805706787e-08` for the mean adjoint and
  `2.445176561227669e-10` for the covariance adjoint; both are more than six
  orders below the `.05` gate.  The finer error was smaller than the coarse
  error in both channels.
- The fixture's maximum paired-order Plackett disagreement was
  `1.3877787807814457e-17`, below the `1e-13` rejection threshold.
- A deterministic mocked root with an initial `1.48*T` indicator is forced to
  refine before return; the retained child indicators total `0.74*T`.
- A fresh Philox directional case is deterministic, and a Philox-derived
  near-endpoint correlation rejects rather than regularizing.
- Zero/near-zero variance and correlation-endpoint cases reject rather than
  clipping or flooring.
- Mocked `I32=NaN`, `I64=0`, and the corresponding positive/negative-infinity
  variants reject at the primitive and both forward callers after exactly one
  coarse/fine pair.  Direct mocked non-finite quadrant values/certificates are
  independently rejected by both forward callers.

The full source-only suite passed: `22` tests, including the legacy M120C and
corrected-CP tests.  No 27-network grid, result, claim, terminal, or `out/`
directory was created.

## Hashes

| file | SHA-256 |
|---|---|
| analytic reference | `f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8` |
| analytic reference tests | `09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f` |

## Reaudit scope

The next independent audit should inspect the Plackett tolerance aggregation,
all domain rejections, the formula-to-code mapping for both cross blocks, and
the reference's integration into a new closed-set manifest.  It must then
separately audit the still-open atomic lifecycle, exact Philox dispatcher,
closed source/runtime seal, and actual reverse-recurrence gauge tests before
any binding execution is considered.
