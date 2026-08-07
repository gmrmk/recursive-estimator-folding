# M147 independent hostile re-audit -- 2026-08-07

## Verdict: REPAIR before any downstream integration

The mathematical **pair bridge** and the restricted conditional `[2,1,1]`
oracle survive this audit.  The literal `48/64 x 16/32` central rule remains
correctly **cost-killed** as a target coefficient implementation.  However,
two fail-closed/domain-contract defects prevent promotion of M147 as the
claimed general endpoint-safe local interface:

1. `collision211_local_state_dot` does **not** accept every rank-deficient
   three-variable PSD state with a feasible tangent.  It only works when the
   selected repeated variable leaves both conditional singleton variances
   strictly positive.  A rank-one all-equal state, and a rank-two state in
   which the repeated and a singleton are identical, reach
   `bivariate_relu_raw_dot_endpoint` with a zero conditional marginal and
   fail `positive marginal variances are required`.
2. The public bivariate routine admits arbitrary finite inputs but can return
   `inf` / `nan` for large finite standardized means instead of raising
   `EndpointCertificationFailure`.  For example, at `alpha=beta=1e308`,
   `rho=+1`, the exact powered moment overflows to `inf`, and the product-rule
   tangent becomes `nan`; the analogous `rho=-1, alpha=beta=1e200` case does
   the same.  This violates M147's stated fail-closed numerical contract.

Neither defect licenses clipping, ridging, an M143 retry, a response cell, an
efficacy run, or contest action.  They are local repairs: explicitly restrict
the local API to positive conditional marginal variances (and test/reject the
other singular strata), then add checked finite-output/overflow handling at
every public bivariate return.  A future implementation may supply a separate
degenerate-conditional analytic branch, but it must not silently reuse this
one.

## Independent evidence

All commands below used the locally bundled
`work/headroom-recursion/.venv/Scripts/python.exe` with NumPy 2.5.1.  The
system Python has no NumPy, so it cannot reproduce the declared test command
without an explicit interpreter/dependency requirement.

| check | independent result |
|---|---:|
| frozen source SHA-256 | `3eab7fb9d2869c7da8c9850ff9c7fa87cf2176417daba1c62f586068791ebba0` |
| test SHA-256 | `2124228c836f309d7f78ceab29b88e644135a4a1ea079868493ef60a793b7ca9` |
| static-runner SHA-256 | `6606f5730b56706d3b9f7fd774b703c8b5e3683d89b006f429b7c868f8afb509` |
| frozen static JSON SHA-256 | `c7a0b7dd5e7c5c0997b079101efd11d0e01aba88daa5ad01da3c42371ecc79a6` |
| published M147 unit tests | `10/10` pass |
| re-run static pair/central checks | matches frozen values except nonportable wall time |
| independent direct conditional 1-D pair check | 288 values over `a,b` in `{−8,−3,−.1,0,1.2,5}` × `{−7,−1.1,0,.4,3,8}` and `rho` through `+/- (1-1e-12)` agree after splitting at the narrow conditional transition; max observed absolute discrepancy `2.78e-17` |
| endpoint directional derivatives | forward feasible paths agree; at the `rho=-1, alpha+beta=0` cusp the finite quotient decays as `sqrt(t)` to the reported one-sided derivative zero, so it is not an ambient Frechet derivative |
| literal cost boundary | confirmed: 10,848 angular evaluations gives even the favorable float64 core lower bound `108,480 > 102,400`; `.999` conditional adversary is `606,720` |

The independent re-run produced the same deterministic quantities in
`M147_STATIC_AUDIT_20260807.json`: pair defects `9.714e-17` / `1.041e-17`,
moderate `[2,1,1]` defects `2.984e-14` / `2.919e-14`, high-correlation count
10,848, and conditional-endpoint count 60,672.  Local wall time changed, as
expected, and has no correctness or bill interpretation.

## Mathematical red-team results

### Exact endpoints and tangent semantics: PASS

For standardized variables, at `rho=+1`, set `Y=Z`; at `rho=-1`, set
`Y=-Z`.  Direct expansion over the active interval gives exactly M147's
`endpoint_positive_power_raw` limits:

```text
rho=+1: z >= max(-a,-b)
rho=-1: -a <= z <= b.
```

For the raw first-first moment, Price gives `dF/drho=Q`, with
`Q_+=Phi(min(a,b))` and `Q_-=max(0,Phi(a)+Phi(b)-1)`.  The reported inward
endpoint covariance derivative is therefore correct.  The direction condition
`-sign(rho) * rhodot >= 0` is the 2x2 PSD tangent-cone condition.  It is
correctly not an ambient two-sided derivative.  The M147 code checks it
without a ridge or correlation clipping.

The angular Plackett representation is also correct: `rho=sin(theta)` cancels
the bivariate-normal density pole and yields a nonnegative bounded integrand.
The endpoint Price enclosure is a real enclosure; the paired 16/32 difference
is only an a-posteriori indicator, as the theory document properly states.

### Interior bridge/value chain: PASS, qualified

The chain rule in `bivariate_relu_raw_dot_endpoint` agrees with independent
finite differences and a split conditional one-dimensional integral near both
endpoints.  The latter split is material: unsplit generic adaptive integration
incorrectly reports a roughly `1e-7` discrepancy for a very narrow transition,
whereas a split at `z=-b/rho` gives machine agreement.  Thus this is a tester
pitfall, not a M147 value defect.

The value routine is nevertheless **not a formal rigorous quadrature proof**:
the endpoint width enclosure can be broad and does not bound the actual
angular quadrature error.  M147 does not claim otherwise; downstream users
must retain the paired-order certificate as numerical rather than interval
certification.

### Locality, state interface, and rank boundary: REPAIR

The width claim is structurally sound in the narrow sense: the public local
API has only `(3,)` and `(3,3)` inputs and subsequent conditional work uses
only those arrays.  It cannot materialize a width-256 cubic/quartic tensor.
The `n<=16` full builder is indeed reference-only.

But the broader statement that rank-deficient local PSD states are accepted is
false.  These adversarial response-free calls demonstrate the omitted domain:

```text
cov = ones((3,3)), repeated_slot=0, tangent=0
cov = [[1,1,0],[1,1,0],[0,0,1]], repeated_slot=0, tangent=0
```

Both are PSD with a feasible zero tangent, but fail because conditioning on
the repeated coordinate leaves a singleton with conditional variance zero.
Conversely, the tested rank-two `A independent; B=C` state succeeds because
the conditional pair has positive individual variances and rank-one
correlation.  The manifest must state this exact restriction, and the function
should raise a contextual `EndpointCertificationFailure` before entering the
pair primitive.  This is fail-closed behavior, but not the claimed complete
rank-deficient API.

### Numerical closure: REPAIR

Input validation permits every finite `alpha`, but no final finite-output
check exists after powered-moment expansion or product-rule assembly.  The
overflows described in the verdict return non-finite certificates.  Add
checked finite arithmetic, or an explicit bounded-domain precondition with an
enforced rejection.  This repair is independent of the endpoint mathematics.

## Firewall and scope: PASS

The M147 source imports only the local M122/M129 algebra references, uses no
network/scorer/contest package, and its static runner only prints generated
mathematics diagnostics.  This audit did not open a response cell, model,
truth, scorer, leaderboard, submission, or M143 authorization.  No M147
source was changed.  The newly discovered conditions are reported here only.

## Required repair gate

Before treating M147 as an enabling dependency for M143/M146 or another
candidate, freeze a new descendant with all of:

- explicit `conditional Schur diagonal > 0` support predicate or a separately
  derived zero-conditional-variance branch;
- public finite-output checks / overflow rejection;
- tests for the two rejecting rank-deficient cases, `rho=-1` conditional
  endpoint, and extreme finite inputs;
- an interpreter/dependency declaration sufficient to reproduce the static
  suite; and
- a fresh independent audit.

The static survivor pieces remain worth preserving: angular Plackett geometry,
exact rank-one raw moments, inward Price tangent, endpoint remainder handling,
and the central cumulant identity.  The target-cost-killed literal quadrature
remains killed; nested-rule work must start in a distinct frozen mutation.
