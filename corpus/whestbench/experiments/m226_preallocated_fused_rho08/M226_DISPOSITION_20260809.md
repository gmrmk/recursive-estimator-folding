# M226 disposition: validated execution child

M226 clears the exact native wall failure inherited from M221 while preserving
M224's validated mathematics unchanged.  Promote the execution topology and
rho-.08 normalized chart together as a validated child.  This is not yet a
variance or contest-score result.

## Static gate

The frozen affine ledger matches at both pre-target sizes:

- 171 timed calls;
- 5,467 FLOPs/event;
- 2,146 persistent setup bytes/event;
- zero runtime allocation and zero `empty`, `copyto`, `sum`, `max`, or
  `reshape` calls; and
- maximum M224 parity error `4.092863201132779e-18`.

The first TDD implementation correctly exposed a billing-shape defect: a
one-sign Simpson constant was implicitly broadcast into a two-sign output.  It
was repaired by using a setup-hoisted two-sign view, which is the operand shape
the frozen ledger had declared.  The ledger was not edited and no dummy work
was added.

## Five-process native gate

Every binding process passes every predeclared check:

- exact bill `21,693,056` and setup allocation `8,515,328` bytes;
- raw wall `13.5961..15.4465 ms`, below `16.13391699997 ms`;
- speedup `104.45..118.67x` versus M216, strictly above 100x;
- hostile component `389.29M..429.69M`, at most 6.30% of M214's
  `6.824272176B` allowance;
- zero fallback, zero chart mismatch, zero runtime allocation, zero forbidden
  operation, and no exceptions;
- value agreement with frozen M224 to `3.8163916471489756e-16`, only
  `3.751478165824106e-8` of M224's radius; and
- peak RSS `56,987,648` bytes.

The worst wall margin is `0.687416991 ms`, and the worst speedup margin is
`4.4503x` above the strict threshold.  This is a real pass but not a lavish
margin; the two persistent slabs, direct-bound ABI, operand shapes, and
fresh-process runner must remain locked for any downstream child.

## Boundary

M226 did not run a source estimator, responses, truth, MSE, scorer, challenge
weights, or variance comparison.  The validated component is now eligible to
be consumed by a separately predeclared variance generation; M226 itself does
not open that gate.
