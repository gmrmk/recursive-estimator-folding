# M178 predeclared protocol: certified fixed-cost normalized Phi2/Owen-T value-and-derivative evaluator

Status: PREDECLARED BEFORE IMPLEMENTATION. This document and its frozen
manifest are committed before any M178 implementation code exists. Response
free. No challenge instance, target, scorer, model loop, leaderboard,
submission, champion, or sealed cell is touched. A pass opens only M176's
response-free producer work; it grants no source-conversion, variance,
efficacy, score, champion, or submission credit and predicts no MSE, rank,
prize, or runtime win.

Base commit at predeclaration: b72a3ffbec2b6c48ec548023df80766812951af6
Branch: agent/compression-survivor-corpus
Canonical governing spec: corpus/whestbench/handoff/FABLE5_ASCII_RESUME_PROMPT_20260807.txt (sec. 7-8, 11)

## Predeclared prediction (deliberately narrow)

A scale-normalized, finite-stratum Phi2/Owen-T evaluator can return value and
first-derivative enclosures that contain high-precision references over the
declared hostile grid, including near-rank SPD points, with one fixed,
statically bounded inclusive FLOP count and deterministic fail-closed
behavior. It establishes only a numerical-provider component; it predicts no
estimator MSE, score, rank, prize, or runtime win.

## (a) Exact formulas and domain reductions

Inputs are the M159-normalized SPD coordinates `(a, b, rho)` = normalized
means `alpha_0, alpha_1` and correlation, with dyadic scale reconstruction
handled by the caller per the M159 ABI (the evaluator is dimensionless).

Value: `V = Phi2(a, b; rho) = P(X <= a, Y <= b)` for standard bivariate
normal with correlation `rho`.

Owen decomposition (Owen 1956), with `s = sqrt(1 - rho^2)` computed as
`s^2 = (1-rho)*(1+rho)` (anti-cancellation; `1-rho` is exact by Sterbenz for
`rho >= 1/2`):

```text
q_a = (b - rho*a) / (a*s),  q_b = (a - rho*b) / (b*s)
Phi2(a,b;rho) = (1/2)*Phi(a) + (1/2)*Phi(b) - T(a, q_a) - T(b, q_b) - delta
delta = 0 if a*b > 0 or (a*b == 0 and a + b >= 0), else 1/2
```

Zero-mean specializations are dispatched exactly (no division by zero):
`a = 0` and/or `b = 0` use the closed limits
`T(0, q) = arctan(q)/(2*pi)` and
`Phi2(0,0;rho) = 1/4 + arcsin(rho)/(2*pi)` (arcsin via
`arctan(rho/s)`).

Owen T with second-argument reduction to `q in [0, 1]`
(`T(h,-q) = -T(h,q)`, `T(-h,q) = T(h,q)`, and for `h >= 0, q > 1`):

```text
T(h, q) = (1/2)*(Phi(h) + Phi(q*h)) - Phi(h)*Phi(q*h) - T(q*h, 1/q)
```

Core integral on the reduced domain (`0 <= q <= 1`, `h >= 0`), with
`c = h^2 q^2 / 2`:

```text
T(h, q) = (q * exp(-h^2/2) / (2*pi)) * I(h, q)
I(h, q) = Integral_{0}^{1} exp(-c u^2) / (1 + q^2 u^2) du
```

Derivatives (exact closed forms; these ARE the "needed derivatives" the
Rosenbaum K/Hmu/Hv assembly will consume; that assembly itself is the NEXT
arrow, not M178):

```text
dV/da   = phi(a) * Phi( (b - rho*a) / s )
dV/db   = phi(b) * Phi( (a - rho*b) / s )
dV/drho = phi2(a,b;rho) = exp( -((a - rho*b)^2 + s^2 b^2) / (2 s^2) ) / (2*pi*s)
```

The quadratic form uses the algebraically exact positive form
`a^2 - 2 rho a b + b^2 = (a - rho*b)^2 + s^2 b^2` (no cancellation).

Phi and phi are NOT taken from `flopscope.stats.norm` (its installed contract
exposes no remainder; inheriting it would repeat the exact M177 violation).
They are built from charged elementary operations:

```text
Phi(h) = 1/2 + (1/2) * erf(h / sqrt(2))
erf chart A (|x| <= 3.5):  fixed 52-term Taylor sum, Horner in x^2;
  truncation bound = first omitted term (alternating, decreasing for n >= x^2).
erf chart B (x > 3.5):     two-sided 4-term asymptotic (Mills) enclosure
  erfc(x)*x*sqrt(pi)*exp(x^2) in [1 - 1/(2x^2) + 3/(4x^4) - 15/(8x^6),
                                  1 - 1/(2x^2) + 3/(4x^4)]
phi(h) = exp(-h^2/2) / sqrt(2*pi)
```

## (b) Normalized domain, scale reconstruction, output contract

Domain (every branch fail-closed, refusal is a typed result, never an
exception path silently swallowed):

- accept: finite `a, b` in binary64, `|rho| <= 1 - 2^-52` (SPD stratum
  exactly as classified by the frozen M177 dispatcher; no clipping, no ridge,
  no variance floor — `|rho| > 1 - 2^-52` refuses with reason
  `NON_SPD_OR_RANK_ONE_CHART`);
- rank-one, zero-variance, deterministic, and non-PSD inputs are OUT OF
  SCOPE: they belong to M177's other strata and are refused by this evaluator
  (kill gate 1 if silently evaluated as SPD).

Output contract (ulp-aware absolute-plus-relative; the impossible universal
absolute contract of M158 is not claimed):

```text
value V:        enclosure half-width w_V  <= 2e-8      (V in [0,1]; absolute)
dV/da, dV/db:   |err| <= 2e-7 + 2e-7 * |D|             (absolute + relative)
dV/drho:        |err| <= 2e-7 + 2e-7 * |D|             (absolute + relative)
```

2e-8 / 2e-7 are the locked M147/M173 campaign tolerances. Enclosures may be
intersected with the proven mathematical range (`V in [0,1]`,
`dV/da in [0, phi(a)]`, `dV/drho >= 0`); interval intersection with a proved
range is not input clipping.

Scale reconstruction: none inside the evaluator (inputs are normalized);
the M159 dyadic ABI owns reconstruction. Positive scale homogeneity is
therefore tested as invariance of the evaluator under the caller's
normalize-then-evaluate path.

## (c) Fixed orders, static branch count, inclusive FLOP bound

- erf Taylor order: exactly 52 terms (chart A), fixed.
- Owen-T quadrature: exactly n = 20 Gauss-Legendre nodes on [0,1], fixed.
  Nodes/weights are compile-time hex-float constants generated at 50 decimal
  digits, certified in-repo by (i) monomial exactness residuals
  `|Q(x^k) - 1/(k+1)| <= 1e-28` for k = 0..39 evaluated in Decimal at 60
  digits, and (ii) the perturbation lemma of the report (node/weight error
  -> quadrature error), so the exact-GL remainder theorem transfers.
- Chart thresholds (all fixed constants): erf chart boundary `x0 = 3.5`;
  Owen-T deep-tail chart `c = h^2 q^2/2 > 18` returns the certified enclosure
  `[0, q*exp(-h^2/2)/(2*pi)]` whose width is `< exp(-18)/(2*pi) < 2.4e-9`;
  reduction branch at `|q| > 1`; zero-mean branches at `a == 0`, `b == 0`.
- Static branch count: the dispatch tree has <= 32 leaves; every leaf's
  operation count is a static constant (no data-dependent loop bounds, no
  retries, no caches).
- Inclusive FLOP ceiling, charged on the measured installed FlopScope 0.10.0
  cost table (add/sub/mul/div/sqrt/abs/max/compare = 2, where = 8,
  exp/log/arctan = 32 per element):

```text
F_M178 <= 20000 charged FLOPs per full evaluator call
          (value + all three derivatives + enclosure bookkeeping),
          worst case over all dispatch leaves.
```

`run_m178_static_audit.py` computes the exact per-leaf static table and the
audit fails if any leaf exceeds the ceiling. A billed FlopScope trace of the
counted execution mode is additionally recorded; billed-native credit is
claimed only for what that trace shows, per the M173 convention.

## (d) Remainder proofs required (value AND derivative, per chart)

The report must contain line-by-line proofs of:

1. GL-n truncation on the reduced Owen integral via the Bernstein-ellipse
   argument: integrand `g(u) = exp(-c u^2)/(1 + q^2 u^2)` is analytic on the
   rho0 = 2 ellipse of [0,1]; on it `|1 + q^2 u^2| >= Re(1 + q^2 u^2) >=
   1 - q^2 * 0.375^2 >= 0.8594` and `|exp(-c u^2)| <= exp(0.140625 c)
   <= exp(2.53125)` for `c <= 18`; explicit constant times `4^-20`.
2. erf chart A truncation (alternating series bound) and rounding
   (max-term times op-count times u argument), chart B two-sided asymptotic
   enclosure width `<= (15/(8 x^6)) * exp(-x^2)/(x sqrt(pi))` at `x >= 3.5`.
3. Reduction-identity and assembly rounding: forward error through the fixed
   DAG under the predeclared op model (IEEE binary64 correctly rounded
   +,-,*,/,sqrt with u = 2^-53; exp/arctan <= 2 ulp faithful-rounding
   assumption, declared per (f) and validated on the hostile grid).
4. Derivative charts: the three closed forms with the positive quadratic
   form; relative-error propagation through exp (absolute exponent error
   bounds), including the near-rank-face SPD region up to
   `|rho| = 1 - 2^-52` where `s^2 = (1-rho)(1+rho)` carries <= 2u relative
   error.
5. Rank-one/zero charts are refused, never silently evaluated as SPD
   (dispatch proof: the acceptance predicate is exactly `|rho| <= 1 - 2^-52`
   with finite inputs).

## (e) References, precision, hostile grid (fixed before execution)

References are internal mathematical constants only; no challenge data.
Reference engine: mpmath at mp.dps = 50 in the isolated frozen venv
(mpmath 1.3.0). Two independent representations per value point:

- R1: `Phi2 = Integral_{-inf}^{a} phi(x) * Phi((b - rho x)/s) dx` by
  mpmath.quad with explicit truncation at 45 sigma and a rigorous truncation
  bound added to the enclosure radius;
- R2: the Owen assembly with `T(h,q)` computed by mpmath.quad on the T
  integral directly.

Agreement gate `|R1 - R2| <= 1e-30`; reference radius
`max(1e-30, 10*|R1 - R2|)`. Derivative references use the closed forms with
mpmath `ncdf`/`exp` at dps = 50 (declared reference assumption).

Hostile grid (deterministic, no RNG):

```text
RHO  = {0, +-2^-52, +-0.1, +-0.5, +-0.9, +-0.99, +-0.999999,
        +-(1 - 2^-45), +-(1 - 2^-52)}
AB   = {0, +-2^-30, +-0.5, +-1, +-2, +-3.4999, +-3.5, +-3.5000001,
        +-4.95, +-5, +-7, +-8.48, +-10}
grid = all (a, b, rho) in AB x AB x RHO with |rho| <= 1 - 2^-52
     + the diagonal family a = b over AB x RHO
     + the reduction-boundary family: for each rho in RHO and each
       t in {1 - 2^-52, 1, 1 + 2^-52}, the (a, b) solving q_a = t at a = 1
     + deep-tail points (a, b) in {+-37.5, +-40}^2 at rho in {0, +-0.9}
```

Every grid point is evaluated for value + three derivatives; the containment
gate is: reference inside the implementation enclosure AND enclosure width
within the (b) contract.

Determinism check: the full grid is evaluated twice in separate processes;
the SHA256 of the serialized outputs must be identical.

## (f) Environment (frozen)

```text
Python 3.14.4 (C:\Python314), isolated venv C:\Users\strid\.venvs\whestbench-frozen-m178
numpy 2.4.6, whestbench 0.14.0, flopscope 0.10.0, mpmath 1.3.0 (all PyPI)
Windows 11 Pro 10.0.26200, x86-64
No API, no network at runtime, no RNG (seed policy: none; no random test
generator is used), no adaptive anything.
Declared numerical assumptions: IEEE-754 binary64 correct rounding for
+,-,*,/,sqrt (u = 2^-53); numpy exp/arctan faithful within 2 ulp (validated
empirically on the hostile grid against 50-digit references; violations are
a kill-gate-2 event).
```

Source/test hashes of all M178 files are recorded in
`M178_SHA256SUMS_20260807.txt` at completion; the frozen manifest records
this protocol's own hash.

## (g) Bias class

Deterministic numerical primitive with certified enclosures. Not an
estimator; no bias/variance claim of any kind attaches to it.

## (h) Failure disposition (exactly one of)

- `PASS`: all kill gates green, all hostile-grid containment green, static
  audit under ceiling, determinism green. Opens only M176 response-free
  producer work.
- `FORMAL_NO_GO`: a remainder proof cannot be completed for a claimed chart;
  the report states the first broken link and preserves the proven charts.
- `KILLED_IMPLEMENTATION`: any kill gate fires at test time.

No iteration inside M178: a different order/constant/chart is M179 only.

## Kill gates (any one kills this implementation)

1. Nonfinite output, non-deterministic output, non-PSD acceptance, clipping/
   ridge/floor anywhere, or a generic zero-face/rank-face JVP without a
   declared feasible path (out-of-scope strata must refuse).
2. Missing line-by-line remainder proof for value OR derivative on any
   claimed SPD chart, or any high-precision reference outside its claimed
   enclosure, or an elementary-function assumption violated on the grid.
3. Input-dependent or adaptive operation count, retry, opaque numerical CDF
   (including `flopscope.stats.norm.cdf`, `scipy`, `math.erf`), unmetered
   work, or missing inclusive F_M178 accounting.
4. Failure of positive scale homogeneity under the M159 caller path,
   symmetry `Phi2(a,b;rho) = Phi2(b,a;rho)` beyond proven rounding bounds,
   endpoint classification error, or near-endpoint SPD not kept distinct
   from exact rank one.
5. Hash/test/manifest failure, resource failure (any budget context error in
   the counted trace), or any scope violation (archive, carrier, ownership
   conversion, sampler, model, or score work appearing in this mutation).

## Artifacts

Exactly the nine files of resume-prompt sec. 11 in
`corpus/whestbench/experiments/m178_certified_phi2_owent/`, this protocol and
the frozen manifest being the first two, committed before implementation.
