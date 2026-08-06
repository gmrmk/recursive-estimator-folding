# Cumulant polynomial quotient

## Decision

**Screen the quotient geometry and preserve the independent RHS observability
block.** The raw `84` cubic and `78` quartic coefficient systems contain
exactly 20 gauge coordinates each in every nontrivial covariance-algebra cell.
After quotienting, the physical dimensions are `64` and `58`. The complete
symmetrization ranks, frozen amplitude-design ranks, and reduced-design ranks
match in every one of 144 cells.

This is a mathematical coordinate certificate, not yet a performance win. It
removes a false rank failure and gives the right target for a future response
mechanism, but constructing the quotient still requires the already charged
response-free SVD. The missing weights/current-state-only directional k3/k4
right-hand side remains unresolved.

No WHest row, target, scorer, API, submission, or holdout was touched. Exact
dense cumulants were used only to create evaluation-oracle responses after the
quotient had been constructed.

## The quotient theorem

Let `l_a` be a column of the frozen linear basis and let `B_b` be the symmetric
matrix represented by a column of the frozen matrix basis. Define

```text
S3(c)(v) = sum_ab c_ab (l_a.v)(v^T B_b v),
S4(d)(v) = sum_bc D_bc (v^T B_b v)(v^T B_c v),
```

where `d=svec(D)`. Expanding these homogeneous polynomials in the ordinary
degree-three and degree-four monomial bases defines linear coefficient maps
`M3` and `M4`. The implementation includes the exact off-diagonal factors from
both matrix `svec` and core `svec`.

Full tensor symmetrization and monomial expansion are two coordinate systems
for the same homogeneous polynomial. Therefore

```text
ker(M3) = {c : Sym(sum_ab c_ab l_a tensor B_b) = 0},
ker(M4) = {d : Sym(sum_bc D_bc B_b tensor B_c) = 0}.
```

The proof is direct: a homogeneous polynomial is identically zero iff every
ordinary monomial coefficient is zero, because distinct monomials are linearly
independent. Thus the kernel is precisely the coefficients annihilated by full
symmetrization--not a numerical probe artifact.

For a frozen probe design `D`, evaluation factors through the complete map:

```text
D = E M,
```

so `ker(M)` is always contained in `ker(D)`. The audit finds equal ranks for
`D` and `M` in every cell. Equal nullities plus containment prove
`ker(D)=ker(M)` cellwise. Hence the 128 frozen amplitude lines observe the
entire physical polynomial quotient.

## Deterministic parameterization

One response-free SVD of each frozen design gives

```text
D = U Sigma V^T,  Q = V[:, :r],  c_id = Q theta.
```

Directions are ordered by decreasing singular value. Each column of `Q` has a
fixed sign: its largest-absolute coordinate, with the first index resolving a
tie, is positive. The reduced inverse uses `D Q`, which is full column rank.
Neither oracle core coefficients nor response values influence `Q`.

## Frozen results

| quantity | result |
|---|---:|
| nontrivial cells | 141 / 144 |
| cubic literal -> quotient | 84 -> 64 |
| quartic literal -> quotient | 78 -> 58 |
| trivial-cell profiles | 1 -> 1, 1 -> 1 |
| max cubic quotient condition | 30.3514 |
| max quartic quotient condition | 52.5370 |
| max cubic response error | 3.748e-15 |
| max quartic response error | 5.482e-15 |
| max cubic physical-core error | 5.052e-15 |
| max quartic physical-core error | 5.492e-15 |
| max prediction equivariance defect | 6.412e-15 |
| max reconstructed-core equivariance defect | 9.819e-15 |
| standardized k3 fidelity | 0.983631 |
| standardized k4 fidelity | 0.979608 |
| combined standardized fidelity | 0.980382 |
| Edgeworth-correction fidelity | 0.991939 |
| material signs | 97 / 98 (98.98%) |

Every predeclared geometry, recovery, fidelity, sign, equivariance, and finite
arithmetic gate passes. Five post-result tests pass.

## Compression interpretation

The quotient reduces the *physical coefficient counts* by

```text
cubic:   20/84 = 23.81%,
quartic: 20/78 = 25.64%.
```

It does not reduce the dominant recurrence or terminal contraction, and this
cleanroom still computes the full response-free SVD to discover the quotient.
The conservative n=256 total is `12.343391296 B`, only `0.0004752 B` above the
parent audit because canonical sign/order work is explicitly charged. Headroom
under the 80 B analytic envelope is `67.656608704 B`.

So this is not yet real score compression. It is valuable because it prevents
wasting response-estimation effort on 40 unphysical coordinates per cell and
replaces the false literal full-rank requirement with the correct `64/58`
targets. A future analytic response recurrence could operate directly in those
coordinates and then realize a cost reduction; no such recurrence is claimed
here.

## Recursive disposition

Passed and preserved:

- the amplitude probe design spans the complete cubic/quartic polynomial image;
- the 20+20 rank losses are exactly symmetrization gauge;
- quotient inverse, physical cores, downstream contractions, and equivariance
  are stable to roughly `1e-14`;
- the algebra remains comfortably within the response-free cost envelope.

Failed link repaired:

- raw-coordinate full rank was an ill-posed gate; the nonredundant quotient is
  full rank and well conditioned.

Still blocked:

- no legal, weights/current-state-only mechanism supplies the 128 directional
  k3/k4 response values. Quotienting cannot create information absent from the
  RHS.

Artifacts: [`PREDECLARED_GATE.md`](PREDECLARED_GATE.md),
[`polynomial_quotient.py`](polynomial_quotient.py),
[`run_audit.py`](run_audit.py), [`audit_results.json`](audit_results.json),
[`test_polynomial_quotient.py`](test_polynomial_quotient.py), and
[`decision.json`](decision.json).
