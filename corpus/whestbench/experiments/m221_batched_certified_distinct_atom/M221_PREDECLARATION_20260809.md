# M221 predeclaration -- batched certified M216 strict-distinct atom

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_IMPLEMENTATION`.

M221 changes only the two failed links in M216: numerical enclosure and scalar
execution.  The estimator algebra remains exactly

```text
A_i;jk(g) = (Z_i;jk(g) + Z_i;jk(-g))/2,
```

with M216's deterministic global means, covariances, tree subtraction, and
strict pairwise-distinct ownership.  M221 never supplies `[4]`, `[3,1]`,
`[2,2]`, or `[1,1,1,1]`; those remain typed refusals.  There is no coefficient
fit, clipping, changed outer law, response, MSE, scorer, challenge weight,
leaderboard, or submission access.

## Frozen objective, legality, and parent evidence

The narrow objective is to determine whether one chart-grouped vector batch
can preserve a certified event radius
`<= 2e-7 * (1 + abs(midpoint))` and reduce M216's best measured 3,968-event
wall time (`1.6133916999970097 s`) by strictly more than 100x.  All runtime
operations, calls, copies, fills, gathers, reshapes, and user allocations are
charged under FlopScope 0.10.0 / NumPy 2.4.6.  Residual wall uses
`lambda=1e11 FLOPs/s` and the hostile multiplier five.  The entire component
must fit M214's unclaimed `6.824272176B` allowance, peak RSS `<=512 MiB`.
Passing this component does not reserve that allowance for deployment because
M214's other unknown nodes remain unpriced.

Bias class remains exact-in-expectation in real arithmetic.  M216's exact
normal-symmetry proof is inherited without modification.  M221 is a generated
chart/resource experiment, not a demonstrated all-state provider.

## Specialized certified chart

For every sign/event, standard conditional coordinates must satisfy

```text
|rho| <= .04
|alpha_j|, |alpha_k| <= .8
|t_j|, |t_k| <= .8,
t_j=(alpha_k-rho alpha_j)/sqrt(1-rho^2),
t_k=(alpha_j-rho alpha_k)/sqrt(1-rho^2),
.8 <= conditional sigma_j,sigma_k <= 1.2,
|ReLU(mu_i+sigma_i g)-m_i| <= 9.
```

Anything outside this chart is a typed fallback request to the unchanged M216
scalar atom.  A fallback preserves the mathematical estimator but fails M221's
native promotion gate: no frozen numerical/native run may contain one, and no
zero-cost production coverage is inferred from its rarity.

Within the chart:

1. `Phi` uses the first 16 terms of the alternating erf Taylor series.  With
   `|x|=|alpha|/sqrt(2)<=.8/sqrt(2)`, the first omitted erf term is
   `<1.12e-23`; a `1e-14` Phi enclosure includes binary64 Horner rounding.
2. `Phi2(a,b;rho)` uses Plackett's identity
   `Phi(a)Phi(b)+integral_0^rho phi2(a,b;r)dr` with fixed composite Simpson,
   32 panels.  On the declared box, Cauchy's derivative estimate on the
   complex radius-.25 disk gives `max|d^4 phi2/dr^4| < 3000`: `|z|<=.29`,
   `|1-z^2|>=.9159`, `|phi2(z)|<.410`, hence
   `4!*.410/.25^4<2520`.  The Simpson remainder is therefore
   `<1.628e-12`; `2.5e-12` covers Phi terms and rounding.
3. Plackett value plus closed Price derivatives reconstruct the same
   bivariate ReLU product used by M216.  Straight interval propagation on the
   chart bounds one physical pair product by `5e-12`, each conditional unary
   mean by `2e-13`, the centered pair by `1e-11`, and covariance-product plus
   fixed-DAG rounding by `2e-10`.  With repeated-centered magnitude at most 9,
   the event error is `<1.1e-9`.  M221 returns the deliberately wider frozen
   radius `1e-8*(1+abs(midpoint))`.

The static proof is necessary but not sufficient: every frozen high-precision
reference must lie inside that returned interval.

## Frozen generated numerical tests

- Main widths/seeds: widths `3..7`, seeds `221700003..221700007`.
- Enumerate every strict physical owner and
  `g in {0,+-2^-8,+-.25,+-1,+-2.5,+-5,+-8}`.
- Retain the inherited M216 worst adversary: width 6, seed `216700006`,
  labels `(1,1,0,2)`, `g=+-8`.
- High-precision subset: at every main width, `(0,0,1,2)` at `g=0,+-8`, plus
  both inherited adversaries.  Independent mpmath 80/100-digit M216 atoms must
  agree within `1e-12*(1+abs(reference))`; M221 midpoint error must be no
  greater than its returned radius.
- Full-census batch midpoint must agree with the unchanged scalar M216
  midpoint within M216's own certified interval, singleton swap within
  `2e-12`, positive gauge/permutation scaled error within `5e-8`.
- Any chart fallback, nonfinite value/radius, returned ratio above `2e-7`, or
  high-precision containment failure kills the numerical implementation.

## Frozen native batch gate

The target batch has exactly 31 blocks x 128 strict events = 3,968 events and
two antithetic signs.  Native seeds are `221720001..221720005`.  A generated
issuer constructs 31 width-7 local contexts outside the timed region, matching
M216's inherited archived-context assumption.  Inside one BudgetContext the
runner must:

1. allocate every staged input and workspace buffer;
2. copy every event scalar into caller-owned staged storage using charged
   FlopScope operations (no hidden NumPy pack);
3. execute the chart guards, 16-term Phi recurrence, 32-panel Plackett
   recurrence, pair/unary reconstruction, both signs, covariance/tree
   subtractands, antithetic average, and returned radius;
4. expose all operations, output finiteness, digest, peak RSS, bill, residual
   wall, and raw wall.

No per-event Python loop or scalar M178 call may occur inside the measured
kernel.  Compile-time Taylor/Simpson constants are free; runtime broadcast,
copy, sum, exponential, division, and comparison are charged.  The staged
input ABI contains only the scalar sufficient statistics consumed by the
unchanged atom; producing those statistics from M179 is outside M221 and
remains an explicit integration blocker.

Every one of five fresh-process traces must satisfy all of:

```text
raw measured batch wall < 1.6133916999970097 / 100 seconds
billed_flops + 5e11 * residual_wall_s <= 6.824272176e9
peak RSS <= 512 MiB
zero fallback rows, zero resource failures, finite output
native output agrees with pure NumPy batch within returned radii.
```

Static billing must be predicted before the first native run and match the
meter exactly; a mismatch kills resource credit rather than being patched.

## Gate order and firewall

1. TDD response-free algebra/chart tests.
2. Frozen full numerical/enclosure census and high-precision subset.
3. Static operation/buffer ledger.
4. Five fresh-process native traces.

Only if both the numerical and complete native gates pass may a separately
predeclared full-`q0`, `A(G)F/(2q0)` source-variance experiment be considered.
M221 itself stops before variance.  Failure preserves the exact atom, the
certified chart or vector recurrence components that passed, and localizes the
next mutation; no threshold, panel count, chart bound, or seed is retuned.
