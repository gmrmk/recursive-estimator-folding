# M232 predeclaration -- retained M205 marginal-sigma seam

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CODE_AND_TESTS`.

M232 changes exactly one mechanism: retain the already-required M205 diagonal
sqrt result `marginal_sigma=sqrt(diag(V))` as a layer/epoch/object-bound vector
alongside M205's factor `u=marginal_sigma/sqrt(n_active)`, then feed frozen
M224 event labels through charged gathers into M228's unchanged kernel.

The retained vector is exact for positive and zero diagonal entries. It is not
a conditional sigma, pair sigma, copied vector, later epoch, or reconstructed
M230 substitute. M224 algebra, rho `.08`, Phi terms, 32 panels, radii,
31x128 shape, seeds, 171-call kernel, `5467N` kernel bill, raw wall limit
`0.016133916999970098`, and strict `>100x` speed gate are frozen.

Before target timing, generated tests must prove M205 factor semantics,
M224 gathered marginal equality/value parity, gauge and permutation behavior,
and layer/epoch/vector identity rejection. The future inclusive trace starts
from live stacked covariance diagonals, bills the M205 sqrt, factor division
and any copy, charges label packing plus gather, and runs all of that inside
the same FlopScope/timer as M228 compute. No setup is free.

Current M205/M212 exposure is a separate hard seam: this child must not claim
that either current parent actually retains or passes the vector. If their live
caller ABI lacks it, M232 is `SEAM_PROTOTYPE_INTEGRATION_BLOCKED`, with no
inclusive trace, reuse credit, wall claim, or variance work.
