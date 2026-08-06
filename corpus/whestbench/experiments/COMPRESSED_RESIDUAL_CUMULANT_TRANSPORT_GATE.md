# Predeclared gate: compressed residual-cumulant transport

Written before any new probe rank, conditioning, coefficient-recovery, or
contraction result. This is a `recursive-estimator-folding` coefficient-
formation mutation of the frozen conditional residual covariance algebra.

## Immutable parent and scope

- Preserve the parent's exact total-cumulance identity, 16 conditional cells,
  rank-four-plus-diagonal covariance state, ordered `<=7` linear algebra,
  ordered `<=12` matrix algebra, and rank-four terminal contraction.
- The parent oracle ceiling is combined standardized fidelity
  `0.9727414592487679` with `97/97` material signs.
- Change one link only: formation of the `h x q` k3 and symmetric `q x q` k4
  small cores from directional probes.
- Fresh synthetic iid-He cases only: `n in {8,12,16}`, `L in {2,3,4}` with
  seeds `71000 + 100*n + L`; 16,384 Philox base inputs plus negatives.
- Fresh probe seeds start at `810000`; fresh independent next-row seeds start
  at `910000`.
- Dense empirical k3/k4 tensors and their exact cores are evaluation oracles
  only. They may generate an oracle response vector used to audit the inverse
  map, but no deployable candidate may read it.
- No WHest row, public target, official scorer, API, or post-outcome tuning.

## Frozen probe designs

Use `P=128` unoriented probe lines per conditional cell and degrees 3 and 4.
Every line is symmetry paired as `{v,-v}`. The two compared designs are:

1. `iid_rademacher`: iid entries `+-1/sqrt(n)`;
2. `orthogonal_hadamard`: consecutive independently signed/permuted normalized
   Hadamard frames of order `n` (Sylvester for 8/16, Paley for 12), truncated
   after 128 lines.

No direction is selected from an outcome. Duplicate lines remain charged and
reported. Pairing forms

```text
y3(v) = (k3(v)-k3(-v))/2,
y4(v) = (k4(v)+k4(-v))/2.
```

For exact cumulants these are the original scalar responses, so pairing is a
parity certificate, not a second independent equation.

For `a(v)=Q_L^T v` and `b(v)=Q_M^T svec(vv^T)`, the frozen inverse designs are

```text
y3(v) = a(v)^T C3 b(v),       row vec = vec(a(v)b(v)^T),
y4(v) = b(v)^T C4 b(v),       row vec = svec(b(v)b(v)^T).
```

Recover minimum-norm coefficients with one SVD pseudoinverse at fixed
`rcond=1e-10`; symmetrize k4, then take the same canonical rank-four SVD/eigen
truncation as the parent. No ridge ladder or retry is permitted.

## Predeclared structural prediction

Both probe families are constant modulus. After the ordered algebra
orthogonalizes `diag(d)` against identity, its surviving diagonal generator is
trace-free. Therefore

```text
<diag(d)-tr(diag(d))I/n, vv^T> = 0
```

for every Rademacher/Hadamard probe. If that generator is nonzero, one matrix-
algebra coordinate is exactly blind; k3 loses at least `h` core directions and
k4 loses all symmetric core directions incident to that coordinate. Antipodal
pairing duplicates rather than repairs this nullspace.

This prediction is recorded before numerical ranks are read.

## Legal observability boundary

The preserved deployable state contains conditional probabilities, means,
diagonal residuals, and four covariance factors. It has no k3/k4 directional
response field. Orthogonal probes create an inverse design but not its right-
hand side. A response is legal only if derived explicitly from weights and the
current state without dense tensors or activation samples.

The oracle audit asks what the probe inverse would preserve if exact scalar
responses were free. If no weights/state-only response identity is present,
the implementation is killed locally even if oracle recovery is accurate.

## Metrics and gates

Report for iid and orthogonal designs:

- k3/k4 design rank and nullity, duplicate-line count, nonzero condition;
- oracle small-core recovery error;
- rank-four next-row standardized k3/k4/combined contraction fidelity;
- combined Edgeworth-correction fidelity and material sign agreement;
- state, arithmetic, and sample-response cost laws at `n=256,L=32,B=16`.

Promotion requires all of:

1. every active core is identifiable with condition `<=1e6`;
2. standardized k3, k4, and combined contraction fidelity each `>=0.80`;
3. material-sign accuracy `>=0.80` with material output in every case;
4. an explicit scalar-probe response computable from weights/current state;
5. total analytic cost, including the existing conditional recurrence and
   terminal contraction, `<80e9` billed-like operations;
6. finite outputs and exact parity/rotation/algebra tests.

If oracle recovery passes but the response is inaccessible, kill only
matrix-free coefficient formation and preserve the `<=12D` representation.
If constant-modulus blindness is the only algebraic failure, record amplitude-
coded nonconstant probes as an unresolved complementary family; do not mutate
this frozen run.
