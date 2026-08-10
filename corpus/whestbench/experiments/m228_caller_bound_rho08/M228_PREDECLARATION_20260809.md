# M228 predeclaration -- caller-bound rho-.08 execution boundary

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CODE_AND_TESTS`.

M228 changes exactly one mechanism from M226: the ownership and timing boundary
for the two marginal singleton-sigma columns. It reuses M226's frozen 171-call
preallocated compute kernel, but caller setup must construct and own all 20
input columns before a kernel is bound. The measured entrypoint accepts an
already-bound kernel only; it may not prepare, bind, reshape, allocate, or
perform arithmetic before its timer and `BudgetContext` begin.

The frozen mathematical parent remains M224 code hash
`6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B`.
Estimator algebra, antithetic identity, normalized chart, `|rho|<=.08`,
`|alpha|,|t|<=.8`, 16 Phi terms, 32 Simpson panels, radii, 31x128 event
shape, context seeds `221730001..221730031`, and outer seeds
`221720001..221720005` are immutable. No response, truth, scorer, weights,
leaderboard, MSE, or variance result may be used.

## Ownership and accounting boundary

`caller_owned_inputs(packed)` is setup, not an invocation. It creates the two
singleton-sigma arrays, verifies their actual ownership and byte counts, and
binds them with the other 18 caller-owned packed columns before measurement.
The persistent kernel still owns exactly its two slabs: `268N` float64 values
and `2N` booleans, measured from the allocated arrays' `nbytes` rather than
ledger literals. The external caller-owned inputs are reported separately.
They are event-dependent preprocessing, not free challenge setup: M228 earns
zero integrated-cost credit unless an upstream caller separately proves both
singleton-sigma columns already exist as live operands. M228 is therefore a
kernel-only execution component, not an inclusive predictor trace.

`run_billed_bound_kernel(kernel)` accepts only an already-bound kernel. It
starts its raw timer immediately before entering `BudgetContext`; no input
preparation, input binding, marginal-sigma work, allocation factory, reshape,
or arithmetic may precede that point. Its allocation report is derived from
actual slab data pointers/nbytes and a `tracemalloc` delta attributable to M226
and M228 source frames; it contains no hard-coded runtime-allocation value.
Any positive source-attributed runtime allocation, changed slab pointer/size,
or unbound kernel fails closed.

## Frozen runtime ledger and gates

The kernel runtime census remains 171 calls and `5467N` FLOPs, hence
`21,693,056` at `N=3,968`. The exact operation census, forbidden operation
set (`empty`, `copyto`, `sum`, `max`, `reshape`), setup slabs (`2,146N` bytes),
and M214 component ceiling `6,824,272,176` are inherited unchanged.

Each of five frozen fresh processes and the additional adversarial fresh
process with seed `221720001` must independently satisfy raw wall
`<0.016133916999970098` seconds and raw M216 speedup `>100x`; no threshold,
seed, package, or event-count drift is permitted. Any failed process kills
M228 locally. Variance remains closed.
