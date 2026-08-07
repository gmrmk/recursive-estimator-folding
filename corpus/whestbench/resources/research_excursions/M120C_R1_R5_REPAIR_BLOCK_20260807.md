# M120C R1-R5 repair attempt — 2026-08-07

## Verdict: REPAIR / BLOCKED AT R3

No 27-network grid was run.  No M120C canonical `out/` directory, claim,
result, failure, or terminal record exists.  M116b and every other champion
were not opened or changed.

I did **not** add an apparent one-shot runner around the current reference.
Doing so would falsely label a clipped, floored, finite-difference calculation
as the frozen exact/fail-closed dense reference.  The requested R1/R2/R4/R5
work is contingent on R3: a durable runner can make a permanent false
falsification just as effectively as a permanent true one.  The retained old
M120C and deprecated M120B entry points remain inert.

## Exact unresolved mathematical gap

For a Gaussian hidden preactivation `(mu,C)`, the dense reverse needs the
Jacobian of the *central* ReLU covariance map

```text
V_ij(mu,C) = E[ReLU(Z_i) ReLU(Z_j)] - m_i(mu_i,C_ii) m_j(mu_j,C_jj).
```

At every hidden layer this entails exact or certified values for the two
cross-block matrices

```text
Hmu[i,j] = d V_ij / d mu_i,
Hv [i,j] = d V_ij / d C_ii,
```

together with the off-diagonal Price derivative
`d V_ij / d C_ij = P(Z_i>0,Z_j>0)`.  The existing implementation does not
provide those quantities to a suitable contract:

- `fullcov.phi2_gauss10` is a 10-node rule and clips correlation;
- `relu_gaussian_moments` floors variance and clips correlation;
- `local_kernels` obtains `Hmu,Hv` by finite differences of that same
  approximate routine;
- `terminal_relu_adjoint` floors terminal variance.

Removing those clamps without replacing them is not a repair: the bivariate
normal formula is singular as correlation approaches `+/-1`, and an arbitrary
float64 finite-difference scale has no enclosure for the resulting derivative
error.  Agreement between two such scales is a heuristic, not an independent
error certificate.  It cannot honestly establish that the reference error is
far below the `.05/.10` gates, nor prove the required `<=1e-10` degeneracy
rejection throughout the real call graph.

The inspected pinned `work/whest-v014` runtime contains no SciPy (`import
scipy` raises `ModuleNotFoundError`).  The workspace also contains no interval,
ball-arithmetic, arbitrary-precision, or certified bivariate-normal primitive
that could supply an enclosure.  Importing a system-dependent solver or
silently lowering the contract would violate the requested closed dependency
and runtime-pin requirements.

## What a valid R3 repair must add

One of the following must be implemented and independently audited before any
runner is authorized:

1. Closed-form analytic expressions for `Hmu` and `Hv`, including exact
   diagonal limits and a proved branch/domain policy for near-correlation-one
   inputs; or
2. a bundled, hash-bound numerical primitive with a documented quadrature
   remainder bound and an independently checked differentiation enclosure,
   rejecting rather than clipping/flooring every unsupported or near-singular
   argument.

The error budget must be attached to each local derivative and propagated (or
upper-bounded) through the dense reverse, with a declared bound materially
below the `.05/.10` decision thresholds.  It must reject variance at or below
`1e-10` before any square root, quotient, clamp, or terminal initialization.

Only then can the remaining mechanical repairs be truthfully sealed:

- **R1:** fixed-path `O_EXCL` claim before the first Philox draw; fsync/atomic
  result or failure and terminal ledger; any interrupted/duplicate path is
  permanently consumed.
- **R2:** exactly 27 `Generator(Philox(seed))` jobs, one each in frozen order,
  producing all 648 JSON-safe records with standardized `(D*b,D*A*D)` states
  and four signed, independent directional contractions.
- **R4:** an exact source/dependency key set, a separately pinned manifest
  hash, runner byte self-seal, and Python/NumPy runtime identities.
- **R5:** frozen valid permutation/positive-gauge schedules applied to the
  real dense and CP reverse recurrences at every hidden layer, with transformed
  standardized state, complete error, and transported signed contractions
  compared at `1e-10`; actual zero/near-zero inputs must fail before a
  reference quotient.

## Current identity and untouched-state evidence

| file | SHA-256 |
|---|---|
| M120C config | `e184385a6021c44653c5168768e2912ff94119806e66e9921987117087cbc3bf` |
| M120C harness | `58b91067c13a66ada75f5e32e4d8883ce8495b8b7a167fbfce97a4b62569a788` |
| M120C manifest | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` |
| named inert runner | `d9eeb0e4a16d98cafc2507ea748091a388fab046211e459610de5be7b291fe10` |
| old wrong-grid inert runner | `221ffec93fec343dedef8479db89fa8dbc3522ab32a3699c3ddbb92e7237c3c5` |
| corrected CP implementation | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| full-covariance dependency | `091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6` |
| Gaussian background dependency | `f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd` |

Source-only checks confirmed `out/` and the fixed result path are absent.
The no-SciPy result above is a read-only environment check; it sampled no
network and produced no M120C protocol artifact.

## Disposition

This preserves the frozen plan, gates, seeds, and surviving M120 shared-CP
mechanism, but it does **not** repair R1-R5.  Status is `REPAIR`, not
`PASS_TO_REAUDIT`.  Do not create a manifest, runner, claim, or binding result
until R3 has a genuinely certified reference.
