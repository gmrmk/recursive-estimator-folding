# M244 predeclaration — exact terminal-observable projection

Date: 2026-08-09  
Status: frozen before candidate code, tests, native traces, or results  
Initial disposition: `PREDECLARED_G0A_COMPONENT_ONLY`

## Objective and single causal mutation

M244 changes exactly one operation in the corrected M200 causal chain.  The
terminal `W_32/J_32` stage will compute only the final Gaussian-ReLU baseline
mean and first-order response that the scorer observes.  It will not construct
the full terminal pre/post covariance, bivariate Jacobian, pair moment archive,
or terminal tangent covariance.

M244 changes no Source211 law or provider, no source count, no interior M179 or
M125b step, no stochastic sampler, no closure assumption, and no response or
efficacy premise.  Output sketching and Hutchinson reconstruction are outside
this mutation.

## Exact differentiable-stratum theorem

The borrowed live inputs are native finite float64 objects:

- M179 layer-31 post-ReLU background row mean `mu` and covariance `V`;
- M125b/M200 accumulated row-mean tangent `u` and signed central-covariance
  tangent `U`, after 31 source injections and 30 interior transports; and
- the exact terminal square weight `W=W_32`.

For output coordinate `j`, define

```text
a = mu @ W
TV = V @ W
c = sum(W * TV, axis=0) = diag(W.T @ V @ W)
d = u @ W
TU = U @ W
q = sum(W * TU, axis=0) = diag(W.T @ U @ W)
```

For `c_j>0`, let

```text
sigma_j = sqrt(c_j)
alpha_j = a_j / sigma_j
p_j = Phi(alpha_j)
r_j = phi(alpha_j) / (2 sigma_j)
m_j = sigma_j phi(alpha_j) + a_j Phi(alpha_j)
dm_j = p_j d_j + r_j q_j.
```

The formulas are exactly the mean component of the frozen M179/M125b terminal
stage.  A univariate Gaussian-ReLU mean depends only on `a_j` and `C_jj`; no
terminal off-diagonal moment or bivariate Jacobian entry can affect `m_j` or
its first derivative.

For `c_j=0` and `a_j!=0`, the exact limit is

```text
m_j = max(a_j,0)
p_j = 1[a_j>0]
r_j = 0
dm_j = p_j d_j.
```

At `(a_j,c_j)=(0,0)` the Gaussian-ReLU mean is not Frechet differentiable.
M179 nevertheless freezes the implementation convention `m=p=r=dm=0` at that
coordinate.  M244 must reproduce this convention for ABI parity, report the
coordinate as `inherited_zero_subgradient_convention`, and claim no exact
tangent theorem there.  A separate strict-theorem receipt must exclude these
coordinates.  No clipping, floor, one-sided reinterpretation, or claim that
the kink is differentiable is allowed.

If the incoming source tangent is conditionally unbiased under the existing
Gaussian closure on the differentiable stratum, this deterministic projection
preserves that bias class.  It creates no new statistical guarantee.

## Frozen generated fixtures

All generation uses NumPy 2.4.6 `Generator(Philox(seed))`; no retry, redraw, or
post-result selection is allowed.

### Generic dense fixtures

For widths `1,2,3,5,7`, use four fixtures with seeds:

```text
w1: 244001000, 244001001, 244001002, 244001003
w2: 244002000, 244002001, 244002002, 244002003
w3: 244003000, 244003001, 244003002, 244003003
w5: 244005000, 244005001, 244005002, 244005003
w7: 244007000, 244007001, 244007002, 244007003
```

Each fixture forms a dense signed QR-normalized `W`, a diagonally dominant SPD
`V`, a dense exactly symmetric signed indefinite `U`, and dense `mu,u`.  The
realized arrays, generator procedure, dtype/shape, and byte hashes must be
written to the test receipt before evaluation.  Failure of any frozen domain
assertion kills the fixture; it may not be replaced.

### Boundary and structural fixtures

- Ill-conditioned but SPD widths `2,5,7`, seeds
  `244102002,244105005,244107007`, with frozen eigenvalues and a full-reference
  terminal pair-correlation maximum at most `0.90`.
- Exact zero-variance coordinates at widths `2,3,5` with `a<0`, `a=0`, and
  `a>0`; strict theorem and inherited-convention receipts are separate.
- An off-diagonal visibility witness with `diag(U)=0` but
  `diag(W.T@U@W)!=0`.
- A terminal-kernel witness `U=W^-T S W^-1` for symmetric zero-diagonal `S`,
  proving the covariance contribution is invisible.
- A trace-free visible witness `W=I`, `U=diag(1,-1,0,...)`, proving trace-free
  is not a terminal null condition.
- Hidden coordinate permutations and positive diagonal scalings
  `S=diag(s)`, `s in {1/2,1,2}`, acting as
  `mu'=mu S`, `V'=S.T V S`, `u'=u S`, `U'=S.T U S`, `W'=S^-1 W`.
- Output-column permutations, which must permute both returned vectors exactly
  as coordinates.

## G0A parity gate

For every fixture, compare three routes:

1. an independent 100-decimal mpmath implementation of the displayed scalar
   formulas;
2. the existing full path
   `C=W.T@(V@W)` -> exact M179 symmetrization -> `build_jacobian(a,C)` ->
   M125 `tangent_stage(TangentState(u,U),W,jacobian)`; and
3. the projected M244 implementation.

For each differentiable coordinate and for `m` and `dm` separately, require

```text
abs(observed-reference) <= 5e-12 + 5e-11*abs(reference).
```

The full path and high-precision reference must independently agree under the
same bound.  Bitwise equality is not required because the quadratic diagonal
is intentionally reassociated.  The `(a,c)=(0,0)` fixture instead requires
bitwise parity with M179's declared zero-subgradient convention and is excluded
from the strict theorem count.

Any nonfinite value, domain mismatch, hidden-transform/output-permutation
failure, or tolerance miss is `KILL_NUMERICAL`.

## Poisoned full-builder topology gate

In a separate generated test, replace each of the following with an immediate
exception:

- `m179_jacobian_archive.build_jacobian`;
- `m179_background_producer.relu_moments`;
- `m179_relu_pair_assembly.pair_moments`;
- `m178_certified_phi2_owent.evaluate`; and
- `m125_forward_tangent.tangent_stage`.

M244 must still return both terminal vectors.  Its operation receipt must show
zero Phi2/Owen-T evaluations, zero K/Hmu/Hv assembly, zero terminal covariance
allocation, zero terminal Source211 injection, and no full
`W.T @ intermediate` square product.  Any poisoned call or hidden substitute
is `KILL_TOPOLOGY`.

## Input, numerical, ownership, and lifetime ABI

- Inputs are finite, native float64, correctly shaped, read-only, and
  digest-bound.  No cast or silent copy is allowed.
- `V` and `U` are bitwise symmetric.  `U` may be signed and indefinite.
- Compute both diagonals in the fixed order
  `sum(W*workspace,axis=0,dtype=float64)`.
- Reject negative projected variance.  Canonicalize exact `-0.0` to `+0.0`.
  Never clip or floor variance.
- Use the hash-bound M179 `_Phi`, `_phi`, and univariate-mean policy.  No SciPy
  substitution or alpha clipping is allowed.
- Check finiteness after each GEMM, reduction, and univariate stage.
- Pairwise rank-one refusal is irrelevant because no pairwise terminal object
  is queried; the incoming M179 provenance must nevertheless be valid.
- Background owner: exact live M179 layer `H=31` state.
- Tangent owner: exact M200 accumulator after `H=31` injections and `H-1=30`
  internal transports.
- Terminal-weight owner: the exact borrowed `W_(H+1)` under the same
  network/weight/epoch digest.
- Before M244: zero terminal responses and zero terminal injections.
- After M244: exactly one terminal event with `source_injection=false`.

M244 owns one reusable `n*n` float64 workspace, bounded vector scratch, and two
fresh result vectors `terminal.baseline_mean` and `terminal.response_mean`.
The workspace first holds `V@W`, is fully overwritten by `U@W`, aliases no
input, and survives neither return nor the next prediction.  Only the two
result vectors may survive.  Every input object, pointer, and digest must be
unchanged after return.  A `TerminalObservableResult` is a new explicit ABI;
it must not masquerade as M200's covariance-carrying `TangentState`.

## Target FlopScope and native gate

Runtime: pinned `work/whest-v014`, Python/NumPy/BLAS identity recorded,
FlopScope distribution 0.10.0 and runtime tag `0.10.0+np2.4.6`, width 256,
native float64, fixed single-thread settings recorded.

The required dense calls are exactly:

```text
V @ W     one 256x256 @ 256x256 f64 GEMM
U @ W     one 256x256 @ 256x256 f64 GEMM
mu @ W    one 1x256 @ 256x256 f64 row GEMM
u @ W     one 1x256 @ 256x256 f64 row GEMM
multiply  two 256x256 f64 calls for W*workspace
sum       two axis-0 f64 reductions
```

The complete dense contraction floor is

```text
two square GEMMs                 133,955,584
two row GEMMs                        523,264
two elementwise multiplies           262,144
two axis-0 reductions                 261,120
floor before unary/guards/copies 135,002,112 FLOPs = 0.135002112B.
```

The earlier `0.134478848B` number is only the GEMM floor and may not be called
inclusive.  Every univariate kernel, validation, copy, allocation, and
reduction must be traced and charged.  Require:

- exact four-GEMM/two-multiply/two-reduction census;
- no other matrix multiplication;
- raw inclusive arithmetic at most `0.150000000B`;
- no allocation of rank greater than two;
- incremental peak RSS at most 16 MiB;
- zero retained scratch after return.

Native wall protocol: generated inputs/imports outside timing; ten warmups;
101 measurements; report p50 and higher-method p95.  A fresh-process run must
record RSS and structural allocations.  Charge

```text
F_inclusive = max(F_arithmetic, 1e11 * p95_seconds)
```

and require `F_inclusive <= 0.500000000B`.  Any arithmetic, wall, allocation,
or RSS miss is `KILL_COST_COMPONENT`; the algebra may remain preserved tissue.

## Strict accounting and credit boundary

The official score remains `S=MSE*max(0.1,C/B)`, `B=2.72e11`, and
`C=FlopScope FLOPs + 1e11*residual_seconds`.  M244 may fill only M199's
previously unknown `U_TERMINAL` with its measured inclusive cost.

The gross named work absent from the specialized endpoint, relative to the
full terminal path, is provisionally:

```text
one background square GEMM       66,977,792
one tangent square GEMM          66,977,792
32640*(4048+42) pair work       133,497,600
gross named removal             267,453,184 FLOPs.
```

This is not net credit until an integrated call/buffer deletion trace proves
the exact full-terminal operations absent.  M244 may not subtract anything
from M199's existing `98.013128528B` strict partial, delete any of M179's 31
interior stages, delete M125b's 30 interior transports or 31 injections,
reduce M151/M172/M198 work, revive M243, or claim the conditional
`7.736750160B` legacy-background deletion.  It earns no efficacy, variance,
response, scorer, truth, challenge-weight, submission, or leaderboard credit.

M244 supplies the missing `mu_32` scope endpoint needed by a later replacement
audit.  That audit is separately predeclared and must prove identical caller
scope, numerical policy, call deletion, lifetime, and inclusive cost.

The strict M199 headroom before unknowns is `1.986871472B`; this is not an M244
allowance.  At the arithmetic cap, at least `1.836871472B` remains before all
other unknowns; at the native cap, at least `1.486871472B` remains.  M206's
M204 kill remains unchanged.

## Frozen execution order and dispositions

1. Commit this predeclaration, manifest, and checksum receipt before any test
   or candidate file.
2. Obtain one independent read-only preimplementation PASS.
3. Preserve a missing-module RED.
4. Implement and run generated algebra/topology tests.
5. Only after those pass, freeze and run the target FlopScope/native gate.
6. No integrated M199 trace is authorized by a component PASS.

Dispositions:

- parent/runtime hash mismatch: `BLOCKED_PARENT_DRIFT`, no execution;
- parity/domain failure: `KILL_NUMERICAL`;
- poisoned call, full-builder use, or ownership/lifetime failure:
  `KILL_TOPOLOGY`;
- arithmetic/wall/RSS failure: `KILL_COST_COMPONENT`;
- every component gate passes: `PROMOTE_EXACT_COMPONENT_ONLY`.

Any frozen gate failure stops later M244 gates.  No tolerance, seed, cap,
fixture, call census, kink classification, or accounting boundary may be
changed after code or evidence exists.  Partial completion is failure, not
credit.

## Bound parent and runtime artifacts

Exact paths and SHA-256 values are mirrored in
`M244_FROZEN_MANIFEST_20260809.json`.  The bound lineage is M125, M178, M179,
M199, M200, M206, and M243's binding-kill disposition.  M243 formulas and code
are not imported or inherited.
