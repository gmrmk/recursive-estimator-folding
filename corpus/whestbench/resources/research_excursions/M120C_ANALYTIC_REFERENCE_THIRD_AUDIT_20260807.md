# M120C analytic dense reference third independent audit - 2026-08-07

## Verdict: `PASS_TO_INTEGRATE`

The standalone R3 analytic dense reference is ready to be integrated into the
separately controlled M120C protocol. This verdict covers the analytic module
and its fail-closed tests only. It does not authorize the 27-job/648-record
grid, an outcome write, a retry, or promotion of the complete M120C method.

I did not edit the candidate source or tests and did not execute a generated
binding job. `m120_price_normal_ordered_adjoint/out/`, its canonical outcome
subdirectory, and result/claim/terminal artifacts were absent after every
check.

## Frozen subject

| subject | SHA-256 |
|---|---|
| `m120c_analytic_dense_reference.py` | `f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8` |
| `test_m120c_analytic_dense_reference.py` | `09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f` |
| repaired author report | `4a85ed3d6d54322cc457f0077854884680e666bae4afb2ca199e9048723fc1d6` |
| second independent audit | `49f7eeb87b4f75b0261797dfc2f643391d3b0c876a48378f1c570e5f1e837b3e` |

The source and test hashes agree with the repaired author report. The narrow
non-finite patch changes no Price, Plackett, moment, or pullback formula.

## Formula re-derivation

Write `p_i=Phi(alpha_i)`,
`m_i=sigma_i*phi(alpha_i)+mu_i*p_i`, `q=sqrt(1-rho^2)`, and
`L=P(X_i>0,X_j>0)`. The source uses the signed Plackett identity

```text
L = Phi(alpha_i) Phi(alpha_j)
    + integral_0^rho phi_2(alpha_i,alpha_j;t) dt.
```

Therefore negative correlation has the correct signed subtraction. For
`i != j`, differentiation with respect to the central Gaussian parameters
gives

```text
d_i = phi(alpha_i) Phi((alpha_j-rho*alpha_i)/q) / sigma_i
E[X_j 1_i 1_j] = mu_j L + C_ji d_i + C_jj d_j
H_mu[i,j] = E[X_j 1_i 1_j] - p_i m_j

H_var[i,j]
  = 0.5 phi(alpha_i)/sigma_i * E[ReLU(X_j) | X_i=0]
    - phi(alpha_i)m_j/(2 sigma_i).
```

The conditional mean and Schur-complement variance in the implementation are
the exact Gaussian conditional law. Direct diagonal limits are

```text
price[i,i] = p_i
H_mu[i,i]  = 2 m_i (1-p_i)
H_var[i,i] = p_i - m_i phi(alpha_i)/sigma_i.
```

The bivariate raw-second-moment formula contains the two boundary terms, the
`sigma_i sigma_j q^2 phi_2` term, and `(mu_i mu_j+C_ij)L`. The dense pullback
uses the correct symmetric off-diagonal double contraction and overwrites its
diagonal with the separate mean/variance derivative. No finite difference or
near-diagonal replacement occurs in the binding module.

A fresh 32-state Philox all-output directional audit over dimensions 2 through
6 gave maximum fine-step error `1.6185184303907363e-08`, versus coarse-step
`6.4742453620425522e-08`; the maximum coarse/fine gap was
`4.8557269316518159e-08`. The expected second-order refinement held.

## Adaptive quadrature and non-finite closure

Every interval now requires finite 32-node value, finite 64-node value, and a
finite absolute difference before it enters the active ledger. The aggregate
helper independently requires every active indicator and their `math.fsum` to
be finite. The loop returns only after the global active-partition sum is
finite and at most `1e-13`; it continues to split the largest contributor.
The final guard repeats both conditions.

Independent injected checks covered each of `NaN`, `+Inf`, and `-Inf` in both
the 32-node and 64-node positions, through each of the primitive, local-kernel,
and forward-moment call paths: **18/18 rejected** with
`AnalyticReferenceFailClosed`. A finite `-max_float/+max_float` pair whose
difference overflowed also rejected. Twelve directly forged non-finite
quadrant-value/certificate combinations were independently injected into both
forward consumers: **12/12 rejected**.

The prior deterministic counterexample can no longer reach a ledger or
return. The existing `1.48*T` regression still refines to `0.74*T`. An
independent ranked-indicator mock required two splits, selected the later but
larger child, and returned global indicator
`4.0000000000000006e-14`.

## Endpoint and small-scale stress

At zero means, signed correlations were compared with
`1/4+asin(rho)/(2*pi)`:

| `rho` magnitude | max absolute identity error | indicator | splits |
|---:|---:|---:|---:|
| `0.999999` | `4.802e-15` | `7.568e-15` | 15 |
| `0.999999999` | `1.306e-13` | `4.741e-14` | 25 |
| `0.9999999998` | `2.137e-14` | `6.441e-14` | 27 |

Both signs behaved symmetrically and every aggregate indicator satisfied the
declared paired-order tolerance. The `1.306e-13` closed-form difference is
reported explicitly: the contract is an a-posteriori 32/64 disagreement
criterion, not a rigorous absolute-error bound, and this edge discrepancy is
immaterial to the `.05/.10` downstream falsification gates. Exact endpoints,
the exact `1-1e-10` boundary, and points inside that margin all rejected rather
than clipping.

A correlated accepted state with `sigma=2.2360679774997898e-05` and minimum
covariance eigenvalue `2.5e-10` remained finite. Its fresh Philox directional
fine-step error was `1.0490672356690007e-12`, improving from
`4.1962583852573482e-12`. Variance exactly at or below `1e-10` rejected. Thus
`FLOOR` remains an input-domain rejection threshold, not a value replacement.

## Permutation and positive-gauge checks

For transformed coordinates
`X'_i=g_i X_perm(i)`, the independently checked laws were

```text
p'       = perm(p)
price'   = perm(price)
r'_i     = r_perm(i)/g_i
H_mu'[i,j]  = g_j H_mu[perm(i),perm(j)]
H_var'[i,j] = (g_j/g_i) H_var[perm(i),perm(j)]
m'       = g * perm(m)
Cov(Y')  = diag(g) perm(Cov(Y)) diag(g).
```

The largest observed discrepancy was `1.7763568394002505e-15`. The scoped
protocol representation tests also preserve their simultaneous hidden
permutation/positive-gauge identities.

## Tests and prohibited mechanisms

- Final frozen-scope run:
  `python -m unittest test_m120c_analytic_dense_reference.py`: **8/8 passed**.
- A broader source regression snapshot containing the protocol and corrected-CP
  tests passed **22/22** before this report; no dispatcher was called.
- `py_compile` passed for the analytic source and its test.
- Static inspection found no correlation clip, variance replacement,
  denominator substitution, `fullcov` call, or finite-difference binding
  machinery. Exact symmetry restoration is not a domain regularizer.

This closes the R3 analytic-reference blocker only. Any protocol manifest,
runtime seal, atomic lifecycle, exact dispatcher, and the remaining M120C
mechanism questions require their own audit before execution.
