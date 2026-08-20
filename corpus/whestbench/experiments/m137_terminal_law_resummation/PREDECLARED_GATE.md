# M137 predeclared terminal-law gate

## Scope and firewall

This is a generated-only, terminal-law falsifier.  It may use iid-He Gaussian
ReLU networks created in `run_m137_generated.py` and independent Gaussian input
banks.  It must not read a contest dataset, scorer, leaderboard, submission,
champion, public/private evaluation target, or any network supplied by a
competition.

The question is deliberately generous: suppose final preactivation moments
`(mu, variance, kappa3, kappa4)` were known.  Can a **single frozen univariate
closure** map them to `E[ReLU(Z)]` much better than order-four Edgeworth?
Moment acquisition is explicitly out of scope.

## Frozen candidates

1. Gaussian closure.
2. Order-(k3,k4,k3^2) Edgeworth / Gram--Charlier formula, as a numerical
   baseline only (not presumed to be a density).
3. Quartic maximum entropy `exp(theta1*y + theta2*y^2 + theta3*y^3 +
   theta4*y^4)` only if the normalizable, residual-certified moment solve
   succeeds.  Otherwise it returns the Gaussian fallback.
4. Equal-within-component-variance two-Gaussian mixture only if its frozen two
   standardized-cumulant equations have a feasible exact solution.  Otherwise
   it returns the Gaussian fallback.
5. The midpoint of the stated certified moment interval, as a minimax point
   under **that interval only**, never selected from outcomes.

Finite-cumulant saddlepoint/tilted-CGF rules are disallowed as probability-law
closures unless `kappa3=kappa4=0`: a nonquadratic finite polynomial log
characteristic function is ruled out by Marcinkiewicz's theorem.  A
Pearson/Johnson rule is not admitted as a free-moment solution because it adds
an untestable family/tail prior; the four-moment counterexample below applies
to it exactly as to every other deterministic moment-only selector.

## Exact information gate

For the exact four Gaussian moments `(0,1,0,3)`, compare the standard normal
law to

```text
P(X=0)=2/3,    P(X=+sqrt(3))=P(X=-sqrt(3))=1/6.
```

Both have the same first four moments but their positive-part means are
`1/sqrt(2*pi)` and `1/(2*sqrt(3))`.  A four-moment rule is therefore not
identified by the information supplied.  This theorem-level gate precedes any
generated-network numerical result.

## Numerical falsifier and promotion condition

The fixed run uses width 8, depth 32, 12 generated networks; one independent
moment bank of `2^20` paths, an independent stability bank of `2^17` paths,
and an independent direct-ReLU reference bank of `2^20` paths per network.
Networks, not output coordinates, are bootstrap units.

Promotion requires a single proper-law candidate to have both:

```text
mean MSE / Edgeworth MSE <= 0.1
upper 95% network-bootstrap ratio < 0.2
```

This gate is intentionally stronger than a point win.  This small width has
dying-network / zero-output degeneracy, so no result may be extrapolated to a
target shape; it is a falsifier only.  No width/depth retry is permitted after
the result.
