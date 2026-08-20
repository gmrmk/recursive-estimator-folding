# M245 predeclaration -- canonical-unordered replica Galerkin spectrum

Date: 2026-08-10

Status at creation: `PREDECLARED_AUTHORITY_ONLY_FIXTURE_V2_REQUIRED`.

This file and `M245_FROZEN_MANIFEST_V1_20260810.json` were written before any
M245 fixture materializer, candidate, reference, test, runner, checkpoint,
result, shard receipt, aggregation, response, truth, scorer, native trace,
challenge-weight, leaderboard, or submission work.  V1 authorizes only the
dummy-only transport test/static review and the single fixture-materialization
step in section 10.  It does not authorize an M245 spectrum run.

## 1. One changed mechanism

M243 used the ordinary Gaussian-Hermite projection of the conditional pair
function `b(g)` as a proposed polynomial.  M245 asks a different, finite
question: what is the exact degree-by-degree projection of the *antithetic
folded event itself* under its actual repeated-node weight?

For each generated strict-SPD Gaussian event, M245 constructs the weighted
Galerkin Gram matrix and right-hand side through normalized probabilists'
Hermites of degree 0 through 8.  It solves every leading system by unpivoted
Cholesky, records the explained-variance ladder, and compares that optimum
with the ordinary unweighted Hermite coefficients.  A separately implemented
conditional-iid replica calculation checks the target mean and variance.

This changes exactly one scientific mechanism: the coefficient inner product,
from the unweighted projection of `b` to the variance-optimal projection of
the folded target.  Canonical unordered ownership, high-precision Plackett
integration, the replica path, finite-ladder curve reports, and durable shard
receipts are validation machinery.  No estimator/provider is implemented.

M245 is a fresh child of the M243 failure disposition.  It inherits no M243
formula, provider, total-support, variance, cost, response, or score credit.

## 2. Canonical event and exact scalar functions

An event is `(i,{j,k})`, with `i`, `j`, and `k` pairwise distinct.  The
singleton pair is unordered mathematically and is stored exactly once as
`j < k`.  Every input permutation is re-canonicalized before hashing or
evaluation.  A second `(i,k,j)` occurrence is forbidden rather than compared
by raw binary64 bytes.

Let `X ~ N(mu,C)`, with finite `mu`, exactly symmetric strict-SPD `C`, and

```text
sigma_a = sqrt(C_aa)
alpha_a = mu_a / sigma_a
m_a     = E[relu(X_a)]
G       = (X_i-mu_i)/sigma_i ~ N(0,1).
```

For the canonical event define

```text
r(g) = (relu(mu_i + sigma_i g) - m_i)^2
b(g) = E[(relu(X_j)-m_j)(relu(X_k)-m_k) | G=g].
```

For any scalar function `f`, define the canonical antithetic operator on
`t >= 0`

```text
S[f](t) = 0.5 * (f(t) + f(-t)).
```

Expectations over `T=|G|` use density `2 phi(t)` on `[0,infinity)`, so
`E_T S[f](T)=E_G f(G)`.

Use the orthonormal probabilists' Hermites

```text
h_q(g) = He_q(g) / sqrt(q!),  q=0,...,8,
h_0=1, h_1=g,
h_(q+1)=(g h_q-sqrt(q) h_(q-1))/sqrt(q+1).
```

No unnormalized `He_q`, factorial-divided M243 coefficient, monomial fit, or
post-hoc basis rescaling is allowed.

## 3. Scale-normalized weighted Galerkin theorem

To remove irrelevant repeated-coordinate scale, define

```text
rbar(g) = r(g) / sigma_i^2
a(t)    = S[rbar b](t)
u_q(t)  = S[rbar h_q](t)
mu_rb   = E_T[a(T)]
R_q     = E_T[u_q(T)] = E_G[rbar(G) h_q(G)]
y(t)    = a(t)-mu_rb
v_q(t)  = u_q(t)-R_q.
```

For `Q=0,...,8`, with `v^(Q)=(v_0,...,v_Q)`, freeze

```text
K        = E_T[y^2]
G_Q[m,q] = E_T[v_m v_q],             0<=m,q<=Q
d_Q[q]   = E_T[v_q y],               0<=q<=Q
G_Q c_Q* = d_Q                       (unpivoted Cholesky only)
P_Q      = d_Q^T c_Q*
V_Q      = K-P_Q.
```

The corresponding unnormalized physical `K,G,d,P,V` are exactly `sigma_i^4`
times the reported scale-normalized values.  The coefficient vector is
unchanged because `G` and `d` receive the same scale factor.

If `G_Q` is SPD, `c_Q*` uniquely minimizes

```text
E_T[(y-c^T v^(Q))^2] = K-2 c^T d_Q+c^T G_Q c.
```

Therefore `P_Q` is explained variance and `V_Q` is the exact residual within
the declared finite span.  M245 does not assume the span is complete.

In fact, strict SPD of the event covariance makes every finite `G_Q`
mathematically SPD.  As `t -> infinity`, the `+t` repeated-node branch is
active and the `-t` branch is inactive.  Consequently `u_q(t)` has a nonzero
highest term of degree `q+2`; subtracting the constant `R_q` does not change
that degree.  In any nonzero linear combination of `v_0,...,v_Q`, the largest
indexed term therefore has a unique uncancelled highest degree.  The
combination cannot vanish almost everywhere under the positive half-normal
density, so its squared norm is strictly positive.  Cholesky and conditioning
gates test the implementation of this theorem, not an assumed empirical rank.

The Cholesky definition here expressly supersedes the preliminary mailbox and
Fable reuse-map shorthand `G_Q^+`.  M245 has no pseudoinverse branch.

## 4. Ordinary-beta comparator and exact dominance certificate

Independently integrate the ordinary coefficients

```text
beta_q = E_G[b(G) h_q(G)],  q=0,...,8.
```

For each leading block, report

```text
V_beta,Q = K - 2 beta_Q^T d_Q + beta_Q^T G_Q beta_Q
V_beta,Q - V_Q = (beta_Q-c_Q*)^T G_Q (beta_Q-c_Q*) >= 0.
```

This identity is a finite-dimensional theorem, not an empirical efficacy
claim.  A numerical violation outside the frozen tolerance kills the M245
implementation.  A tiny or zero measured gap is a valid result and may not be
retuned into a different basis.

## 5. Primary high-precision construction of `b(g)`

The primary path is pure `mpmath`; it may not import M243 code or M178.  For a
fixed `g`, set

```text
nu_j = mu_j + (C_ij/sigma_i) g
nu_k = mu_k + (C_ik/sigma_i) g
s_j^2 = C_jj-C_ij^2/C_ii
s_k^2 = C_kk-C_ik^2/C_ii
s_jk  = C_jk-C_ij C_ik/C_ii
rho_c = s_jk/(s_j s_k),  delta_c=1-rho_c^2
A=nu_j/s_j, B=nu_k/s_k.
```

Strict SPD must imply `s_j>0`, `s_k>0`, and `abs(rho_c)<1`; otherwise the
frozen event fails with no repair or redraw.  Construct

```text
P = Phi2(A,B;rho_c)
  = Phi(A)Phi(B) + integral_0^rho_c phi2(A,B;s) ds
Pa = phi(A) Phi((B-rho_c A)/sqrt(delta_c))
Pb = phi(B) Phi((A-rho_c B)/sqrt(delta_c))
D  = phi2(A,B;rho_c)
M_jk = s_j s_k ((A B+rho_c)P + B Pa + A Pb + delta_c D)
e_j  = s_j (A Phi(A)+phi(A))
e_k  = s_k (B Phi(B)+phi(B))
b(g) = M_jk - m_j e_k - m_k e_j + m_j m_k.
```

The Plackett integral uses exactly 16 directed equal panels from `0` to
`rho_c`; the decreasing orientation is retained when `rho_c<0`.  It uses
`mp.quad(..., method='tanh-sinh', maxdegree=14, error=True)` and no other
Phi2 formula, endpoint provider, binary64 radius, fallback, clipping, or
retry.

## 6. Analytic `R` and `G`, quadrature `K,d,beta`

`R_0,...,R_8` and the full `9 x 9` Gram matrix are primary analytic
quantities.  Expand `rbar(+/-t) h_q(+/-t)` piecewise at the sole positive
kink `t=abs(alpha_i)` and integrate the resulting polynomials against the
Gaussian density with

```text
I_0(a,b)=Phi(b)-Phi(a)
I_1(a,b)=phi(a)-phi(b)
I_n(a,b)=a^(n-1)phi(a)-b^(n-1)phi(b)+(n-1)I_(n-2)(a,b), n>=2,
```

using zero boundary terms at infinity.  Multiply every interval moment by the
explicit half-normal factor `2`; no implementation may silently treat `phi`
as the `T` density.  Products for `G` require moments only through degree 20.
No numerical quadrature defines `R` or `G`.

`mu_rb`, `K`, every `d_q`, and every `beta_q` are independently integrated at
80 and 100 decimal digits over the half-normal panels

```text
sorted_union([0, .25, 1, 2.5, 5, 8, 10, 16, infinity],
             [abs(alpha_i)]),
```

sorted with exact duplicate removal.  The integrand uses both signs through
`S`.  Every panel call is exactly

```text
mp.quad(..., method='tanh-sinh', maxdegree=14, error=True).
```

Each engine/event/precision starts with fresh caches.  No 80-digit value or
cache may seed the 100-digit computation, and no cache crosses events or
shards.  There is no algorithm fallback or precision retry.

## 7. Independent conditional-iid replica core

The replica implementation may read the authority/fixture manifest and a
generic durable-receipt helper only.  It may not import the primary M245
module, its Plackett implementation, any M243 module, or any cached primary
value.

This path is an independently implemented conditional-factorization/unary
construction of `b_rep` followed by the displayed replica identity.  A direct
generic 5-dimensional augmented-Gaussian moment quadrature is not M245's
replica backend and is forbidden as a substitution.

At fixed `g`, reconstruct `b(g)` using a separate one-dimensional unary
factorization.  With `H,E_j,E_k` independent standard normals, set

```text
ell=sqrt(abs(rho_c)), s=sqrt(1-abs(rho_c)), eta=sign(rho_c)
Z_j=ell H+s E_j
Z_k=eta ell H+s E_k.
```

Conditional on `H=h`, the two ReLU means factor into univariate positive-part
means.  Integrating their centered product over `H` gives `b_rep(g)`.  The
inner `H` expectation uses antithetic half-normal panels

```text
[0, .25, 1, 2.5, 5, 8, 10, 16, infinity]
```

and the same frozen `tanh-sinh`, `maxdegree=14`, `error=True` call.  For
`M_same`, this is the conditional-iid replica identity: two conditionally
independent, identically distributed copies of `(j,k)` share the same signed
`G`, so the product expectation is `b(g)^2`.

The replica core then constructs, without a primary import,

```text
M_same  = E_G[rbar(G)^2 b_rep(G)^2]
M_cross = E_G[rbar(G) rbar(-G) b_rep(G) b_rep(-G)]
mu_rep  = E_G[rbar(G) b_rep(G)]
K_rep   = 0.5*(M_same+M_cross)-mu_rep^2.
```

The outer replica integrals use the section-6 panel set.  The equality follows
from squaring the antithetic average, not from an independence assumption
between `G` and `-G`.  The `M_cross` construction uses conditionally
independent *sign-reversed* replicas, one loaded by `G` and the other by
`-G`; they are generally not identically distributed conditional on
`T=abs(G)`.

Before any integrated replica credit, compare `b_rep(g)` directly with the
primary Plackett `b(g)` at both 80 and 100 digits on every event and every
frozen node

```text
g in {0, +/-2^-8, +/-0.25, +/-1, +/-2.5, +/-5, +/-8, +/-10, +/-16}.
```

This node census includes both signs, near-zero, moderate, and Gaussian-tail
arguments.  It audits `b`, which has no repeated-node `r` kink.  No node may
be dropped after observing difficulty.

## 8. Frozen event census and shard ownership

The binding census is exactly `E00` through `E07` in
`M245_FROZEN_MANIFEST_V1_20260810.json`.

- `E00` and `E01` are literal 3-dimensional cells.
- `E02` through `E07` are fresh NumPy-2.4.6 Philox cells with seeds
  `24501101` through `24501106`; the exact generator and no-redraw rule are
  frozen in the manifest.
- Every event is `(0,{1,2})`, serialized as `(0,1,2)` after canonicalization.
- `E00` has `C_i,{j,k}=0`, so `b(g)` is constant and the degree-zero weighted
  control must satisfy `P_0=K`.  This is the frozen positive control.
- Shard 0 owns `E00,E01`; shard 1 owns `E02,E03`; shard 2 owns `E04,E05`;
  shard 3 owns `E06,E07`.  No shard may evaluate another shard's event.

V1 intentionally contains only literal `E00/E01` and the exact generator for
`E02:E07`, because this docs-only lane is forbidden from importing NumPy.
Before any M245 primary, replica, scientific test, or shard-runner file may
exist, Codex must perform the one fixture-materialization action in section
10.  V1 may authorize only the isolated fixture materializer, its
transaction-helper unit/static test, and its static-validation receipt.  The
resulting committed V2 manifest must contain Python decimal `repr` rows,
float64 byte hashes, and SPD diagnostics for all eight events.  V1 alone
cannot trigger a shard.

The float64 bytes and matching hex values in V2 are scientific authority.
Decimal `repr` strings are display and round-trip aids only.  Each primary and
replica engine must verify the byte hash, decode each float64 with
`as_integer_ratio()`, and construct the exact binary rational as
`mp.mpf(numerator)/mp.mpf(denominator)`.  Constructing scientific inputs with
`mp.mpf(repr(x))`, reparsing rounded diagnostics, or regenerating from seeds
inside a shard is forbidden.

## 9. Binding numerical and finite-ladder gates

All eight events must pass separately; pooling cannot hide an event failure.
Every reported primary and replica scalar must be finite.

### Precision and quadrature

For every primary or replica scalar `z`, independently constructed 80- and
100-digit values must obey

```text
abs(z_80-z_100) <= 2e-12 * max(1,abs(z_100)).
```

For every `mp.quad` call save `mp.eps` before entry.  Its returned error must
be finite and `<= saved_mp_eps/8`; a larger result is the observable
declaration that degree 14 did not converge.  For each composite top-level
scalar, sum only its returned *outer-panel* absolute error estimates and
require

```text
top_level_error_sum <= 2e-14 * max(1,abs(z)).
```

Raw sums of nested Plackett/unary error estimates are recorded as diagnostics,
not advertised as propagated interval bounds: unweighted inner-error sums are
not conservative after outer multipliers.  Correctness is gated by every
observable per-call error, the top-level returned errors, 80/100 agreement,
and independent primary/replica agreement.  An exception, nonfinite or
over-threshold returned error, missing panel, panel reordering, or alternative
algorithm is binding failure.  No unobservable "maxdegree cap hit" flag is
claimed.

### Analytic and solve gates

1. At both 80 and 100 digits, direct quadrature must match every analytic
   `R_q`, `q=0,...,8`, and all 45 upper-triangle analytic `G_mq` entries,
   `0<=m<=q<=8`, within `2e-11*max(1,abs(reference))`.  This census must
   exercise even, odd, and mixed-parity paths; symmetry supplies only the
   lower triangle.
2. Every leading `G_Q`, `Q=0,...,8`, must pass unpivoted Cholesky at both
   precisions, with `lambda_min/lambda_max >= 1e-25` and 2-norm condition
   number `<=1e25`.  No ridge, pseudoinverse, eigenvalue clipping, basis
   deletion, pivoting, or rank repair is allowed.
3. Every solve must satisfy
   `norm(G_Q c_Q*-d_Q,inf)/max(1,norm(d_Q,inf)) <= 2e-20`.
4. With `K>0` and `tau_K=2e-10*K`, require
   `-tau_K<=P_Q<=K+tau_K`, `V_Q>=-tau_K`, and
   `P_(Q+1)>=P_Q-tau_K` for every leading block.
5. On `E00`, require `abs(P_0-K)<=tau_K` and `abs(V_0)<=tau_K`.
6. At `Q in {0,4,8}`, direct integration of
   `E_T[(y-c_Q*^T v)^2]` must match `V_Q` within
   `2e-9*K`.
7. For every `Q=0,...,8`, the two algebraic sides of the exact ordinary-beta
   dominance-gap identity must agree within `2e-20*K`, and the gap may not be
   less than `-tau_K`.  At `Q in {0,4,8}`, direct integration of the
   ordinary-beta residual must additionally match its quadratic form and the
   certified gap within `2e-9*K`.
8. At every frozen signed/tail node, primary `b(g)` and unary-factor
   `b_rep(g)` must agree within `2e-10*max(1,abs(b(g)))` at each precision.
9. For every event, `mu_rep` must match primary `mu_rb` within
   `2e-9*max(1,abs(mu_rb))`, and `K_rep` must match primary `K` within
   `5e-8*K`.

### Descriptive geometric/logistic/Gompertz ladder

Only `E01:E07` enter this report; `E00` is recorded as
`ENDPOINT_CONTROL/NA` because `x_Q=1` makes every declared transform
singular.  Set `x_Q=P_Q/K`, `Q=0,...,8`, without clipping.  Test exactly three
transforms:

```text
geometric: T(x)=log(1-x)
logistic:  T(x)=log(x/(1-x))
Gompertz:  T(x)=log(-log(x)).
```

Before transformation require the literal mathematical domains: `x<1` for
geometric and `0<x<1` for logistic/Gompertz.  A negative `x` is not accepted
by the geometric report even though `log(1-x)` is real.  Undefined,
out-of-domain, or nonfinite transforms are a typed model-domain refusal and label
that event/model `FALSIFIED`; they do not invalidate an otherwise correct
spectrum.  For each valid transform report all seven

```text
Delta2 T_Q = T_(Q+1)-2T_Q+T_(Q-1), Q=1,...,7.
```

Define

```text
tau_T = 1e-12 + 100*max_Q abs(T_Q,80-T_Q,100)
tau_x = 1e-10 + 100*max_Q abs(x_Q,80-x_Q,100).
```

Fit the authoritative 100-digit values by an unweighted affine line in
transformed space using only `Q=0,...,5`.
Without refitting, invert its predictions at `Q=6,7,8`.  An event/model is
`NOT_FALSIFIED_ON_Q0_8` only if every `abs(Delta2 T_Q)<=tau_T` and every
held-out `abs(x_pred-x_actual)<=tau_x`; otherwise it is `FALSIFIED`.  A family
label is `NOT_FALSIFIED_ON_Q0_8` only if all seven events receive that label.

These are the only permitted labels.  No fit may be called true, preferred,
asymptotic, predictive beyond Q8, or a certified tail law.  The only certified
future statement is

```text
0 <= additional explainable energy beyond Q8 <= K-P_8.
```

## 10. One Codex-owned fixture-materialization action

V1 authorizes exactly one non-scientific materialization process and nothing
else.  It runs from the M245 authority directory with

```powershell
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' '.\materialize_m245_fixtures.py'
```

Before launch, the materializer source, its dummy-only transaction test, and a
static-validation receipt must be committed and hash-bound, with two
independent read-only PASS audits.  Those tests may exercise serialization and
publication helpers only on dummy literals and dummy seeds outside the frozen
census.  They must not import NumPy to preview `E02:E07`, execute any seed
`24501101:24501106`, or write any of the four authority paths.  Thus test-first
transport work does not consume the one scientific materialization.

The future script must import only the standard library before exclusively
publishing and verifying its intent.  Only then may it import NumPy 2.4.6.
The venv command may create one inert, hash-bound Windows launcher redirector;
it is not falsely counted as the scientific worker.  Exactly one distinct
scientific worker PID may import NumPy or execute the script, and that worker
may create no child.  The watchdog must record the launcher and worker PIDs
separately and meter elapsed wall, summed CPU, and concurrent summed working
set across the complete process tree from command launch through final
receipt publication.  It must use one BLAS thread, no network, no retry, no
redraw, at most 30 wall seconds, and at most 268,435,456 bytes process-tree
peak RSS.

It owns exactly these initially absent paths:

```text
M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json
.M245_FROZEN_MANIFEST_V2_20260810.json.tmp
M245_FROZEN_MANIFEST_V2_20260810.json
M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json
```

It may emit only:

- the V1 authority and runtime hashes;
- the exact E00:E07 census and shard map;
- row-major Python `repr(float(x))` strings for `mu` and `C`;
- for each array, dtype string, shape, float hex rows, and
  `sha256(dtype.str || NUL || canonical-shape-json || NUL || C-order-bytes)`;
- exact symmetry, finite, Cholesky, `eigvalsh` minimum/maximum, determinant,
  conditional-variance, and conditional-correlation diagnostics;
- PID, one-thread, elapsed-wall, peak-RSS, watchdog, and publication receipts.

It must not evaluate `r`, `b`, Hermites, a Galerkin matrix, a replica moment,
or a curve fit.  The four-path namespace is single-use: intent, final V2, and
receipt are permanent, while a successful transaction unlinks the temporary
name.  Any preexisting path before launch, residual temporary path after
publication, second intent, partial publication, hash drift, resource breach,
failed SPD check, or invalid receipt blocks M245 with no materialization
retry.

The one launch must perform this observable durable sequence exactly:

1. verify all four paths absent and all committed source/authority/runtime
   hashes before NumPy import;
2. exclusive-create the intent, flush and fsync it, reopen/parse/hash it, and
   verify the immutable bytes;
3. exclusive-create the temporary V2, write canonical JSON, flush and fsync,
   then reopen/parse/hash the temporary bytes;
4. publish create-if-absent with the validated M237 same-directory
   `os.link(temp,final)` hard-link pattern, verify source/final device, inode,
   byte length, bytes, and SHA-256, then unlink the temporary name;
5. exclusive-create the postpublication receipt, flush and fsync it, then
   reopen/parse/hash the receipt.

This binds the already validated M237 Windows transaction primitive.  No
directory `fsync` or directory-handle `FlushFileBuffers` support is assumed or
claimed.  A rename/replace that can overwrite a preexisting final path is
forbidden.

After publication, Codex must commit V2 and a V2 checksum receipt and obtain
two independent read-only PASS audits.  Only that committed, audited V2 may
authorize test-first implementation and later shard review.

## 11. Four-shard resource and transport contract

After audited V2 and independently audited test/reference/runner hashes,
Fable owns exactly four shards in the manifest assignment.  Each shard:

- runs exactly one scientific worker PID with no scientific child and no
  network; one inert, hash-bound venv launcher redirector is permitted and
  recorded separately;
- fixes every BLAS/thread variable to one;
- has peak RSS `<=2,147,483,648` bytes;
- has watchdog wall `<=5,400` seconds per invocation;
- stops scientific work by `5,100` seconds and reserves the final 300 seconds
  exclusively for checkpoint/result/receipt durability;
- may use at most two durable checkpointed invocations, in event order;
- may checkpoint only after a complete event and before the watchdog cap;
- treats an actual watchdog cap, exception, nonfinite quadrature error,
  over-threshold returned quadrature error, corrupted checkpoint, or hash
  mismatch as binding failure;
- has no retry, reseed, redraw, cross-shard cache, or third invocation.

Across all shards there are at most eight process launches and at most 43,200
summed process-tree CPU seconds (12 CPU-hours).  Full-tree wall, CPU, and
concurrent summed working set include any launcher redirector.  Every
invocation has exclusive write-ahead
intent and immutable result/checkpoint paths.  A second invocation must bind
the first receipt and may only continue the next unevaluated event.  Each
final shard receipt contains both primary and replica outputs, both precision
receipts, every gate, complete error accounting, runtime hashes, input hashes,
resource measurements, and an exact no-credit/firewall census.

All four final receipts must independently say `PASS` before Codex may run one
`<=120`-second, one-scientific-worker, no-network, no-scientific-import
aggregation; an inert recorded launcher redirector is again permitted.  That
aggregation may verify hashes/census, concatenate frozen fields, and render
predeclared summaries only.  It may not perform quadrature, solve a new
system, refit a curve, drop an event, alter a label, or create estimator
credit.

A shard trigger is valid only as a committed append-only `AGENT_CHANNEL.md`
message from Codex that binds the committed V1/V2/checksum hashes, all future
implementation/reference/runner hashes, two independent static PASS audits,
the exact four-shard census, and zero prior shard intents.  Maestro frames,
an uncommitted message, V1 alone, V2 existence alone, or a partial receipt
cannot authorize execution.

## 12. Statistical rules and stop conditions

After the committed V2 and its two PASS audits, implementation order is
fixed: write the scientific tests first, preserve a missing-primary and
missing-replica RED, implement the primary and replica in separate modules,
obtain independent static review, then freeze exact test/module/runner hashes
before any shard intent.  Local transport self-tests may use only dummy events
outside `E00:E07`; evaluating a frozen event before its shard intent consumes
and invalidates that event rather than becoming an informal preview.

The eight cells are fixed diagnostic units: `E00/E01` are literal and
`E02:E07` are seed-frozen generated fixtures.  There is no population
inference.  The 80/100-digit pair is numerical replication, not a statistical
confidence interval.

- No event may be removed, replaced, regenerated, or down-weighted.
- No pooled statistic can rescue a failed event.
- No bootstrap, p-value, multiple-comparison winner, or post-hoc threshold is
  part of M245.
- Event-level `K,G,d,c,P,V,beta,V_beta`, condition diagnostics, replica
  differences, and all Q0:8 ratios are reported.  Median/range summaries are
  descriptive only.
- `Q0:5` is finite model development and `Q6:8` is a finite internal holdout;
  neither is a contest holdout or evidence about unseen degrees.

Dispositions are frozen:

```text
parent/runtime/V2 hash mismatch     BLOCKED_PARENT_DRIFT
fixture materialization failure     BLOCKED_FIXTURE_AUTHORITY_NO_RETRY
primary/replica/numeric gate fail   KILLED_M245_IMPLEMENTATION_LOCAL
resource/transport/firewall fail    KILLED_M245_EXECUTION_LOCAL
all four shards pass                PASSED_PRESERVED_GENERATED_SPECTRUM_PREMISE_ONLY
```

A successful spectrum is diagnostic tissue only.  Any estimator coefficient,
provider, total-support atlas, native compiler, response test, or composition
requires a separately predeclared child.  A failed implementation does not
close the weighted-Galerkin theorem family unless an independent theorem does.

## 13. Firewall and no-credit boundary

M245 is generated-only and offline.  It must not read, import, infer, or emit:

- the M243 candidate/reference formulas or any M243 numeric result as input;
- M151 source arrays, `dtilde`, `F_e`, B1 state, M196 residual `H_e`, or `V_H`;
- M178 code, calls, provider certificates, enclosures, or reuse credit;
- M125b response states, challenge/public/private networks or weights, truth,
  scorer, champion outputs, leaderboard, credentials, network services,
  submission paths, or sealed cells;
- clipping, rank repair, retry-until-pass, hidden compute, or uncharged work.

M243 remains killed.  M245 cannot claim formula-component, total-support,
provider, source-variance, native-cost, response, efficacy, MSE, adjusted
score, integration, deployment, designation, or submission credit.  It cannot
change the frozen Kerdock v3.1 lane or any ledger/champion status.

## 14. Authority roots

Repository-relative paths in V1 resolve from the directory containing this
repository's `.git` entry and `AGENTS.md`:

```text
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding
```

Venv-runtime-relative paths resolve only from:

```text
C:\Users\strid\.venvs\whestbench-frozen-m178
```

The venv's `pyvenv.cfg` additionally binds its base runtime root:

```text
C:\Python314
```

The exact observed parent commit, parent document hashes, interpreter/package
hashes, literals, generator, materialization paths, and shard map are in V1.
Execution must rehash them from these explicit roots.  The future commit that
first contains this predeclaration, V1, and their checksum is additionally
bound by every materialization and shard intent; it cannot be self-recorded
inside the files it commits.
