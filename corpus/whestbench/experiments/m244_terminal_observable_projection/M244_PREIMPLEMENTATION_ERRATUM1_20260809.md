# M244 preimplementation erratum 1 — fixture and metering closure

Date: 2026-08-09  
Status: frozen after commit `e1d0854` and before any M244 test, candidate,
native harness, or result

This erratum is append-only.  It supersedes conflicting or underspecified
language in the original M244 predeclaration and manifest.  All other frozen
rules remain in force.

## E1. Hash path roots and runtime weights

Every `parent_sha256` path is resolved relative to the repository root
`publish/recursive-estimator-folding`.  Every `runtime_sha256` path is resolved
relative to the shared workspace root, the parent of `publish/` and `work/`.
No verifier may try both roots or silently ignore an absent file.

The active FlopScope weight sources are additionally bound:

```text
9ff1647a0048d2bd23a7a3d76ee0c60bfd3670d03b15ad8bf2b911c2ae19539f
  work/whest-v014/Lib/site-packages/flopscope/data/default_weights.json
4fbfe5bf50eb7e86e73372e9d314f86de179aad49bcffd689143570918794f35
  work/whest-v014/Lib/site-packages/flopscope/_weights.py
```

Any root, file, or hash mismatch is `BLOCKED_PARENT_DRIFT` before import.

## E2. Metered production univariate policy

The original instruction to use M179 `_Phi`, `_phi`, and its univariate mean
is narrowed to the **reference policy only**.  Those helpers invoke plain
`math.erf` and `math.exp`, so they cannot be the production kernel while M244
claims a fully metered native ledger.

Production must implement a vectorized, predicated version of the hash-bound
M178 `_Phi_cert/_phi_cert` charts through `flopscope.numpy`, reusing exactly
M178's constants, 52-term central erf polynomial, four-term asymptotic erf
chart, `|x|>=27` erf saturation, and Gaussian-density exponential.  It may not
call M178's scalar `FlopscopeBackend` once per coordinate because that would
materialize thousands of one-element arrays and change the frozen topology.

The vectorized policy is fixed:

1. `x=alpha*INV_SQRT_TWO`, `ax=abs(x)`.
2. The central polynomial receives
   `x_c=where(ax<=3.5,x,0)` so inactive huge coordinates cannot overflow its
   Horner powers.
3. The asymptotic chart receives
   `ax_t=where((ax>3.5)&(ax<27),ax,4)` and the corresponding signed value;
   inactive coordinates use only this harmless fixed surrogate.
4. The saturated chart returns exact signed one for `ax>=27`.
5. Two final predicated `where` calls select central/asymptotic/saturated
   outputs.  Surrogate values are never observable.
6. For `phi`, use `alpha_p=where(abs(alpha)<=40,alpha,0)`, evaluate the M178
   exponential on `alpha_p`, and select exact zero outside `|alpha|<=40`.
   This avoids a nonfinite inactive square while matching the binary64 tail
   policy; no finite nonzero binary64 density is discarded beyond that cut.
7. Exact zero-variance coordinates bypass division and both charts and use the
   inherited M179 convention already classified by the original authority.

Every add, subtract, multiply, divide, comparison, boolean combination,
absolute value, exponential, and `where` is a real `flopscope.numpy` call with
preallocated `out=` storage where supported.  Constants and persistent vector
scratch are setup-owned.  The static operation census and actual native log
must agree exactly; no unmetered scalar loop, Python `math` kernel, SciPy call,
or manual/dummy FLOP surcharge is permitted.

G0A separately compares the production chart with (a) M179 `_Phi/_phi` and
`relu_gaussian_mean`, and (b) 100-dps mpmath.  The original parity tolerance
binds both comparisons.  The M178 analytic enclosure must also contain the
mpmath value coordinatewise.  Any chart-membership mismatch, inactive-chart
nonfinite value, or enclosure miss is `KILL_NUMERICAL`.

All production univariate calls, guards, masks, and scratch allocations count
toward the unchanged raw `0.150000000B`, native `0.500000000B`, and 16 MiB RSS
caps.

## E3. Exact deterministic generic-fixture constructor

The five width groups and twenty seeds in the original authority remain
unchanged.  For each `(n,seed)`, use NumPy 2.4.6 and exactly this draw/order:

```python
rng = np.random.Generator(np.random.Philox(seed))

raw_w = rng.standard_normal((n, n), dtype=np.float64)
Qw, Rw = np.linalg.qr(raw_w)
sign_w = np.where(np.diag(Rw) < 0.0, -1.0, 1.0)
Qw = Qw * sign_w[None, :]
scale_w = rng.uniform(0.65, 1.35, size=n)
W = Qw * scale_w[None, :]

raw_v = rng.normal(0.0, 0.08, size=(n, n))
off_v = 0.5 * (raw_v + raw_v.T)
np.fill_diagonal(off_v, 0.0)
diag_v = rng.uniform(0.65, 1.25, size=n) + np.sum(np.abs(off_v), axis=1)
V = off_v.copy()
np.fill_diagonal(V, diag_v)

raw_qu = rng.standard_normal((n, n), dtype=np.float64)
Qu, Ru = np.linalg.qr(raw_qu)
sign_u = np.where(np.diag(Ru) < 0.0, -1.0, 1.0)
Qu = Qu * sign_u[None, :]
if n == 1:
    eig_u = np.asarray([-0.625 if seed % 2 else 0.625], dtype=np.float64)
else:
    eig_u = np.linspace(-0.9, 0.9, n, dtype=np.float64)
    if n % 2:
        eig_u[n // 2] = 0.15
U = Qu @ np.diag(eig_u) @ Qu.T
U = 0.5 * (U + U.T)

mu = rng.uniform(-0.9, 0.9, size=n)
u = rng.normal(0.0, 0.35, size=n)
```

The constructor then asserts, without repair: exact shapes/dtypes/finiteness;
bitwise `V==V.T` and `U==U.T`; positive strict diagonal-dominance margin for
`V`; strictly positive eigenvalues of `V`; full rank `W`; and both signs in
`eig_u` when `n>=2`.  Width one is exempt only from the impossible
indefiniteness condition.  Failure kills the frozen fixture and does not
authorize a redraw.

The QR sign rule, scaling side, draw order, constants, and NumPy routines are
part of the authority.  No alternate QR, orthogonalization, or distribution is
allowed.

## E4. Exact ill-conditioned fixture constructor

For `(n,seed)` equal to `(2,244102002)`, `(5,244105005)`, and
`(7,244107007)`:

```python
rng = np.random.Generator(np.random.Philox(seed))
exponents = np.linspace(0.0, -24.0, n, dtype=np.float64)
vdiag = np.exp2(exponents)
V = np.diag(vdiag)
wdiag = rng.uniform(0.8, 1.2, size=n)
W = np.diag(wdiag)
sigma_terminal = np.sqrt(vdiag) * np.abs(wdiag)
alpha_pattern = np.resize(
    np.asarray([-35.0, -8.0, 0.0, 8.0, 35.0], dtype=np.float64), n
)
mu = alpha_pattern * np.sqrt(vdiag)
u = rng.normal(0.0, 0.35, size=n)
raw_u = rng.normal(0.0, 0.2, size=(n, n))
U = 0.5 * (raw_u + raw_u.T)
```

The terminal background covariance is diagonal, so its maximum pair
correlation is exactly zero.  The constructor asserts exact symmetry,
`min(vdiag)>0`, condition number at least `2^20`, the declared terminal alphas
within `5e-12`, and finite candidate inputs.  No eigensystem is synthesized
numerically and no fixture is replaced.

## E5. Exact boundary and structural fixtures

These fixtures are deterministic and seed-free.

1. **Zero variance, nonzero mean**, each `n in {2,3,5}`: `W=I`,
   `V=diag(0,1,...,1)`, `mu[0]` separately `-0.75` and `+0.75`, all other
   `mu=0.25`; `u=linspace(-0.4,0.4,n)`; `U=diag(linspace(-0.6,0.6,n))`.
   Coordinate zero must take the exact differentiable zero-variance limit.
2. **Structural zero kink**, each `n in {2,3,5}`: `W=I` with column zero
   overwritten by exact zeros; `V=I`, `mu=u=0`, `U=diag(linspace(-.5,.5,n))`.
   Then `a=c=d=q=0` structurally at that output.  It is convention-parity only.
3. **Off-diagonal visibility**, `n=2`: `V=I`, `mu=u=0`,
   `U=[[0,1],[1,0]]`, and
   `W=[[1,1],[1,-1]]/sqrt(2)`.  Require `diag(U)==0` and nonzero
   `diag(W.T@U@W)`.
4. **Terminal kernel**, `n=3`: `W=I`, `V=I`, `mu=u=0`, and
   `U=[[0,1,-2],[1,0,3],[-2,3,0]]`.  Require exact zero projected diagonal.
5. **Trace-free visible**, `n=3`: `W=I`, `V=I`, `mu=u=0`,
   `U=diag(1,-1,0)`.  Require exact zero trace and visible projected diagonal.

All exact-zero assertions are bitwise and include sign-bit checks after the
required `-0.0 -> +0.0` canonicalization.  No synthesized nullspace or inverse
is used.

## E6. Transform fixtures and target inputs

Hidden transformations are deterministic.  For each generic width, use the
cyclic permutation matrix `P[r,(r+1) mod n]=1` and the positive diagonal
`D_rr=2^(((r mod 3)-1))`, i.e. repeating `1/2,1,2`.  Apply exactly
`mu'=mu S`, `V'=S.T@V@S`, `u'=u S`, `U'=S.T@U@S`, `W'=solve(S,W)` for
`S=P` and `S=D` separately.  Output permutation is the reverse-column order
`n-1,...,0`.  Width one transformations remain identity but are not counted as
nontrivial probes.

Each target seed `244256001..244256005` independently uses the E3 generic
constructor at width 256.  Each of the five fresh processes must separately
pass every hash, call, arithmetic, p95, allocation, scratch, and RSS gate.
Results may be summarized, but no pooled or average value can rescue a failing
seed.  There is no warmup sharing between seeds.

## E7. Frozen pre-code fixture receipt

Before candidate or test creation, a docs-only fixture authority receipt must
materialize E3-E6 once using the pinned NumPy runtime and record, for every
array: `repr`-roundtrippable decimal values for widths at most seven, shape,
`dtype.str`, C-order byte SHA-256, and all declared diagnostics.  For width 256
it records only shape/dtype/hash/diagnostics, not the full decimals.

The materializer is authority-only, may not import M244 candidate code, and
must be committed before the missing-module RED.  Its own source and output
hashes enter an append-only V3 checksum receipt.  Any second materialization,
hash drift, partial output, or diagnostic failure blocks implementation.

## E8. Effective order

Authority precedence is:

```text
M244_PREIMPLEMENTATION_ERRATUM1_20260809.md
M244_FROZEN_MANIFEST_V2_20260809.json
M244_PREDECLARATION_20260809.md
M244_FROZEN_MANIFEST_20260809.json
```

After this erratum and V2 checksum receipt are committed, obtain a fresh
read-only audit.  Only then may the authority-only E7 materializer be written,
audited, and invoked exactly once.  No candidate/test code or scientific
execution is authorized by this erratum alone.
