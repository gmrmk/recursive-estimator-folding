# M177 — endpoint-complete bivariate noncentral Gaussian ReLU primitive

## Disposition

**FORMAL RUNTIME NO-GO UNDER THE INSTALLED FLOPSCOPE API; preserve the
endpoint algebra and the fail-closed stratum contract.**  M177 repairs the
logical classification gap identified by M176, but does not manufacture an
unavailable certified special-function evaluator.  It creates neither a
`BackgroundArchive` producer nor a candidate estimator.

The pinned FlopScope 0.8 public surface has a *metered* univariate normal CDF
(`48` FLOPs/element) and PDF (`27` FLOPs/element).  Its CDF is documented as
equivalent to a SciPy-style `erf` implementation, but exposes no rounding or
remainder enclosure.  It exports neither Owen `T`/`S` nor a bivariate normal
CDF.  Therefore it cannot lawfully be called an **exact elementary/Owen-T
evaluation**, and using it as though it were one would violate M176's
no-opaque-CDF constraint.  The issue is not that it is unmetered; it is that
the billed black-box value has no auditable numerical-error contract.

No clipping, ridge, adaptive retry, hidden NumPy/scipy CDF, response/source
work, model prediction, scorer, leaderboard, submission, or champion state
was used.

## Exact identities that a future provider must implement

For positive variances, write `sigma_i=sqrt(C_ii)`,
`alpha_i=a_i/sigma_i`, and `rho=C_01/(sigma_0 sigma_1)`.

* **SPD, `|rho|<1`:** Rosenbaum's positive-part product is an algebraic sum
  of `Phi(alpha_i)`, `phi(alpha_i)`, and
  `Phi2(alpha_0,alpha_1;rho)`.  The M176 blocks follow exactly from
  `K=P(X0>0,X1>0)`,
  `Hmu_ij=E[1_i ReLU(X_j)]-p_i m_j`, and
  `Hv_ij=.5 f_i(0)E[ReLU(X_j)|X_i=0]-r_i m_j`.
* **Rank-one positive/negative endpoint:** `rho=+/-1` reduces exactly to the
  one-dimensional truncated moments
  `E[(alpha0+Z)_+(alpha1 +/- Z)_+]`.  These are finite polynomials of normal
  tail moments, so they still require certified `Phi` and `phi` at the moving
  endpoints.  Only an inward/one-sided PSD tangent is admissible.
* **One zero variance:** PSD forces that covariance row/column to zero.  The
  value is the deterministic ReLU factor times a univariate ReLU mean.  A
  generic JVP is not determined by `(mu_dot,C_dot)` at this face: for example
  `C(t)=[[t^2,t],[t,1]]` is PSD for `t>=0` but has a nonzero off-diagonal
  first derivative while its first standard deviation has a cusp.  A caller
  must supply a declared one-sided conic path; M177 refuses a generic tangent.
* **Both variances zero:** value is the elementary product
  `max(mu0,0) max(mu1,0)`.  At a mean kink the tangent is one-sided and must
  likewise be declared.

This is endpoint complete as a *mathematical dispatch*: every finite symmetric
2x2 input is classified as non-PSD/refused, deterministic, zero-variance,
rank-one `+`, rank-one `-`, or SPD.  It does not pretend that the correlation
chart exists on a zero-variance face.

## Fixed cost accounting and why it cannot close

Even before a `Phi2` service, each unordered positive-variance pair requires
at least six charged CDF evaluations and four charged PDF evaluations for
the two means, two boundary terms, and two conditional ReLU means.  With a
conservative `160` scalar algebra operations, this is

```text
6*48 + 4*27 + 160 = 556 billed FLOPs per unordered pair,
plus Phi2/Owen-T value and its certified enclosure.
```

The final addend is **not zero** and has no fixed inclusive bound in the
installed API.  A fixed Plackett quadrature order is not a substitute: M162
already falsified the corresponding common-node line near a rank face, and
without a derivative/remainder bound no number of nodes establishes the
required tolerance.  Adaptively subdividing M147's reference is also not an
answer: its call count is data-dependent and its paired-order disagreement is
an indicator, not a rigorous error interval.

Accordingly no target-width cost can be certified for M176's `256x256` local
kernel.  Charging only `556 * 32640 = 18,147,840` FLOPs for a layer would omit
the dominant special-function work and would be an accounting bypass.

## Response-free validation

`test_m177_bivariate_relu_primitive.py` checks high-precision (90-decimal
`Decimal`, fixed 240-term elementary erf series) one-dimensional endpoint
references over signs, negative/positive means, and
far tails; it checks exact positive scale homogeneity, a `rho=nextafter(1,0)`
SPD point that must not be clipped to rank one, all finite PSD strata, and the
zero-variance feasible-path counterexample.  These tests validate the
classification and identities, not an unavailable numerical provider.

There is therefore no honest M177 runtime ``worst error`` to report: the
generic value/Jacobian primitive is deliberately never evaluated.  The frozen
reference's algebraic scale reconstruction error was below `1e-70` on its
hostile endpoint grid; that is a reference consistency check, not a certified
FlopScope error bound.

## First remaining link

The first link remains exactly:

```text
certified bounded-cost Phi + Phi2/Owen-T evaluator
  -> endpoint-aware Rosenbaum K/Hmu/Hv arrays
  -> labelled B=8 zero-order BackgroundArchive
```

An admissible future mutation must introduce a documented fixed numerical
kernel with a predeclared, inclusive operation count and a rigorous value and
derivative remainder bound on a stated scale-normalized domain.  It may then
be tested separately against the M177 endpoint contract.  It must not inherit
an implementation pass from this formal no-go.
