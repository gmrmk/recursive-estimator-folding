# M224 disposition: validated numerical component

M224 repairs the numerical-chart failure isolated by M221.  Promote this chart
and normalized factorization to the salvage bank; do **not** call M224 a full
estimator promotion.  M221's native speed failure remains inherited, no native
timing was rerun, and variance stayed closed.

## What passed

The new chart uses only positive-gauge invariants:

```text
conditional sigma / marginal sigma,
(ReLU(mu_i+sigma_i g)-m_i)/sigma_i,
alpha, t, and rho.
```

The estimator is the same strict-distinct antithetic identity, evaluated after
factoring out `K=sigma_i^2 sigma_{j|i} sigma_{k|i}`.  Under a positive gauge,
the normalized bracket and chart coordinates are invariant while `K` carries
the exact required `d_i^2 d_j d_k` covariance.

All predeclared numerical gates pass without threshold or seed changes:

- original M221 census: 2,730 events, zero fallback, maximum parent error
  `4.163336342344337e-15`;
- fresh untuned census: 2,730 events, zero fallback, maximum parent error
  `7.077671781985373e-15`;
- all five frozen M221 native issuers: 19,840 events, zero fallback, including
  the old tail at `|rho|=0.07885550264503906`;
- gauge/permutation gate: 90 probes, zero membership mismatches, normalized
  coordinate error `1.665341651575243e-16`, scaled value error
  `3.3113030210003974e-16`;
- independent 80/100-digit gate: 32 probes, zero oracle disagreement, maximum
  midpoint error `3.3410774147313305e-15`; and
- returned radius ratio `1e-8`, below the frozen `2e-7` requirement.

The real-axis derivative proof improves the old coarse complex-disk estimate.
On `|alpha|<=.8`, `|rho|<=.08`, it gives
`max|d^4 phi2/drho^4| < 13.129531`; the unchanged 32-panel Simpson remainder is
at most `2.2794323711956567e-13`, inside the unchanged `2.5e-12` Phi2
enclosure.

## What remains blocked

M224 deliberately did not modify, meter, or optimize M221's 58 allocation
calls, 23 copies, reductions, or pair-kernel call topology.  The inherited best
speedup remains only `89.04x`, below the frozen strict `>100x` gate.  Therefore:

- status is `VALIDATED_NUMERICAL_COMPONENT`, not champion;
- no native speed credit is claimed;
- no source-level variance experiment exists or was run; and
- the next child may change call/allocation execution only, while taking this
  exact normalized chart and rho-.08 proof as frozen inputs.
