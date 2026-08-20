# M240 preimplementation erratum -- observable compatibility repair

Status: `SEALED_BEFORE_CHILD_TEST_MODULE_OR_EXECUTION`.

This erratum adds observability to the already-frozen M240 repair without
changing its mechanism, mathematics, inputs, thresholds, or gate order.

## Finite-scan view contract

For each of the three production finite scans, the child test must prove that
the object passed as `out=` is:

- exactly a plain `numpy.ndarray`, not a FlopScope/WhestArray subclass;
- boolean dtype, non-owning, and a zero-copy view of the already-owned boolean
  slab;
- identical in data pointer, shape, and strides to its frozen prebound view;
  and
- stable in object identity, pointer, shape, strides, dtype, and ownership
  before and after a successful pack.

Instrumentation must observe exactly three billed `isfinite` calls inside the
same `BudgetContext`. Production may contain no call to `numpy.isfinite`,
`numpy.isnan`, `numpy.isinf`, or an equivalent raw-NumPy numerical finite test.
The three `fnp.isfinite` inputs, billed element counts, following reductions,
and refusal order remain those inherited from M238.

## Hostile-fixture contract

The malformed canonical-order fixture must create `j_bad` and `k_bad` as two
distinct, fresh, owning copies. Before issue, the test must prove that:

- neither copy shares memory with its original or with the other copy;
- both copies contain the intended swapped values and are read-only; and
- every original receipt array plus the original canonical digest is unchanged.

After the production issuer rejects the malformed receipt, the same test must
again prove the original receipt unchanged and the packer's zero-write digest
unchanged. The remaining foreign-context, one-use, mutation, interior-refusal,
and successful-lifetime checks from M238 must still execute.

These assertions belong to the same six-method G0A gate. Missing, extra, or
weakened assertions kill M240. G0B, native, variance, response, integration,
and submission remain unauthorized.

