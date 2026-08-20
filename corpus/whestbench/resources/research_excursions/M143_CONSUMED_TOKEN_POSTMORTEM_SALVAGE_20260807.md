# M143 consumed-token postmortem and salvage map -- 2026-08-07

## Decision

**KILLED IMPLEMENTATION -- PROTOCOL FAILURE; TOKEN CONSUMED; NO RETRY.**

The exact M143 runner/manifest pair listed below is killed.  Its one-shot
development authorization was consumed, the run terminated after 49.2 seconds,
and the authorized result file was never created.  This is not an efficacy
result: there are no inspectable MSE records, ratios, gates, or confirmation
evidence.  No replacement authorization, seed retry, family deletion, or
rerun of the same implementation is permissible.

The **suffix-energy plus physical-source-scale mechanism is a preserved
component in an unresolved family**.  It was not causally reached in the
failing cell and was not screened.  Reuse requires a genuinely changed
descendant that repairs the exact-response certification boundary under a new
frozen protocol.

This postmortem is source-only.  It did not execute `build_cell`, generate a
state, inspect a partial response, or read/alter the authorization, receipt,
authorized output, confirmation artifacts, contest artifacts, or champions.
The traceback and wall-time facts come from the authoritative root incident
record.

## What happened

The enforced sequence was:

```text
authorization validates
  -> nonce receipt created O_CREAT|O_EXCL (token irreversibly consumed)
  -> run_split
  -> build_cell
  -> build_state_frechet
  -> m122_nonzero_bridge.build_state
  -> NonzeroBridgeFailClosed(
       "small state has a pair too close to a Gaussian endpoint")
  -> exception escapes run_split
  -> process exits before exclusive result-file creation
```

The firewall therefore behaved correctly: the receipt was created before any
response construction and remains consumed despite the absent output.  Partial
in-memory work from any earlier cell, if any, was not serialized or inspected
and supplies no evidence.

## Exact causal boundary

M122 fixes `_SERIES_RHO_LIMIT = 0.80`.  `build_state` normalizes covariance to
a correlation matrix and deliberately refuses any off-diagonal pair with
`abs(rho) > 0.80`.  This is a certification-domain guard for its truncated
Hermite reference, not a claim that the Gaussian state is mathematically
invalid.  Its exception is declared as:

```python
class NonzeroBridgeFailClosed(RuntimeError):
    ...
```

M129's `build_state_frechet` calls `build_state` directly.  M143 calls
`build_state_frechet` at the beginning of `build_cell`, before suffix-energy
recursion, any of the three proposal snapshots, or the cell's exact defect
table.  Thus the failing cell rejected the shared M122/M129 state needed by
M133, scale-only, and M143 alike; the M143-specific proposal law did not cause
the rejection.

M143's per-cell recorder catches only:

```python
except (ArithmeticError, ValueError):
    record_protocol_failure()
```

`RuntimeError` is not a subclass of either caught class, so
`NonzeroBridgeFailClosed` escaped.  This is an exception-coverage/reporting
gap.  Had it been caught, the frozen manifest still required the family
certification failure to make `protocol_complete=false`, fail every promotion
gate, and prohibit confirmation.  The missing catch changed whether a failure
JSON was written; it did not change the correct disposition.

Merely catching `RuntimeError` and rerunning is not a valid descendant.  It
would only serialize the same killed certification failure and could also hide
unrelated programming defects.  A future runner should catch an explicit
shared `CertificationFailure` base (including `NonzeroBridgeFailClosed`) and
re-raise unexpected runtime errors, but that bookkeeping repair is not itself
a new estimator mechanism or authority to execute another response.

## Recursive-fold salvage map

### Preserved components

- Exact sign-scrambled diagonal suffix-energy recurrence
  `G[r]=p[r]^2*E[r+1]`, `E[r]=(W[r]^2)@G[r]`.
- Physical ReLU source scale and the frozen scale-only causal-attribution arm.
- Positive-gauge invariance, layer-permutation covariance, exact zero-strength
  law, immutable proposal snapshots, and conditional Hansen--Hurwitz
  unbiasedness proved before the run.
- Pooled-and-both-family promotion gates and the prohibition on choosing or
  deleting a family after seeing a failure.
- One-shot authorization/receipt firewall and the protected proposal cost
  crosswalk.

These remain algebraic or structural evidence only.  None is a validated
variance improvement.

### Failed link

- The frozen generated-state family produced at least one state outside the
  inherited M122/M129 Hermite oracle's certified `abs(rho)<=0.80` domain.
- The runner's expected-failure taxonomy did not include M122's deliberate
  `RuntimeError` subclass, so the protocol failure was not serialized.

### Untested claims

- M143/M133 and M143/scale-only response-MSE ratios.
- Pooled or per-family uncertainty bounds and width trends.
- Confirmation behavior and any target-width or contest benefit.

## Genuine descendant A: endpoint-safe exact state and cumulant oracle

This is the preferred repair because it retains both frozen family concepts
and changes the failed mathematical link rather than the seeds.

1. Replace the pair Hermite series used for the ReLU bridge with the exact
   nonzero-mean bivariate truncated-Gaussian expression.  M131 already contains
   an endpoint-stable `bivariate_relu_raw_dot` based on quadrant probability
   plus Bonnet/Price derivatives and accepts every comfortably nonsingular
   `abs(rho)<1`; move the primitive into a lower shared module to avoid an
   import cycle.
2. Compute the normalized bridge and its Frechet derivative from that exact
   pair value/tangent.  Local `gamma2` and `gamma3` stay in the existing exact
   univariate formulas.
3. Remove the hidden triple-series dependency from the `[2,1,1]` coefficient.
   M131 already obtains `E[Y_i^2 Y_j Y_k]` and its tangent by paired conditional
   one-dimensional quadrature.  Reconstruct the fourth cumulant directly from
   the moment--cumulant partition identity, using exact univariate moments and
   endpoint-safe conditional one-dimensional rules for every required
   bivariate powered moment.  Differentiate the same identity term by term.
4. Certify every numerical integral with independent coarse/fine orders.  For
   genuinely near-singular correlations, use a derived one-dimensional
   coalesced endpoint limit with an explicit remainder bound; never clip rho,
   add an unreported ridge, or simply increase the Hermite cutoff.

Required premise tests before any response authorization:

- agreement with the old Hermite oracle throughout `abs(rho)<=0.75`;
- high-precision checks on a signed grid through `rho=+-0.999`, including
  nonzero means and all powered moments needed by `[2,1,1]`;
- Frechet finite-difference checks, gauge/permutation tests, SPD-boundary
  refusals, and paired-order certificate tests;
- a response-free domain preflight proving every newly frozen generated state
  is either analytically certified or fails through the explicit caught
  certification type; and
- a new manifest, runner hash, independent hostile audit, and one new token
  only after all premise gates pass.

## Genuine descendant B: certification-safe generated families

If the endpoint-safe oracle cannot be completed in time, define an entirely
new premise protocol whose state generator stays inside the old oracle domain
by construction.  This cannot be post-hoc seed filtering.

A defensible construction predeclares a sequence of well-conditioned target
correlation matrices with an analytic off-diagonal cap below 0.80, then chooses
each generated weight by a whitening/rotation/coloring factorization so the
next ReLU covariance equals that target.  Use at least two fixed families -- a
near-coordinate family and a dense orthogonal-mixing family -- and prove the
cap and eigenvalue margin for every layer and every seed before response work.
No rejection sampling, family removal, seed replacement, or observed-response
conditioning is allowed.

This descendant asks a narrower question and has weaker target extrapolation:
it can test whether output-aware suffix energy helps on certified moderate-
correlation chains, but it cannot establish behavior in the high-correlation
states that killed M143.  It therefore ranks below the endpoint-safe analytic
descendant and cannot by itself support a target-ready promotion claim.

## Next-time protocol constraint

Every future generated-response branch must separate three stages before a
one-shot response token is issued:

1. response-free generator/domain certification;
2. explicit exception-taxonomy injection tests showing every anticipated
   certificate refusal is serialized and closes all gates; and
3. only then, an independently audited one-shot response protocol.

This is not permission to apply those checks to M143 now.  M143's token is
spent and its exact implementation remains killed.

## Evidence hashes

| artifact | SHA-256 |
|---|---|
| authoritative root incident record | `66fb3b5ad00162004db8574e6ff229f1a9510c399614b3d81de789f9688dfee9` |
| consumed receipt (hash supplied by root; receipt not read here) | `f2c7251bf80ea895d0a0e9cbbf19870e7888da0918099064a1c6debce454fdab` |
| authorization (hash supplied by incident record; file not read here) | `be1f33d5d354001d59f7b9e5eed2003950ac85e713c2da9ad8922e5099b43ec1` |
| M143 manifest | `6338584fdf89813c6e6f0c2c46bc72ccbcb22b5d600a6766ba8d6bf319bce215` |
| M143 runner | `1f0d31ec7e28d98cd84fc64fac3bc3a67293f6060d14f085f8f0005c92a9a81c` |
| M143 suffix-energy module | `5dab449d9ceff7099e04f4521415e781592e6eec260636dd4e81688c9dc6d9bb` |
| M122 nonzero bridge | `c765fe24818f4ec8928a879e217a530077edff98f729555739202c1f7286f927` |
| M129 source Frechet state | `b7b9d4b0228331972f7fd7b5bd2fb6081ba3053d25daf64f3f8dd0f84e31a6bf` |
| M131 conditional boundary oracle | `1bb1912b82f8d7b7a204bc19d0d260a9050f02e83b8e87d322188632882ecac3` |
| pre-run M143 report | `ca8cd457647027cd1bd5742cd540aaa2c27ffa92cda9532d2527ae8b0e550be0` |

The postmortem's own SHA-256 is intentionally reported externally after the
file is closed, avoiding a self-referential hash.
