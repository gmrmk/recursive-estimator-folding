# M240 disposition -- frozen G0A killed; production repair preserved

Status: `KILLED_FROZEN_G0A_TEST_FIXTURE_AND_OBSERVABILITY_FAILURE`.

M240's one authorized durable six-method G0A invocation completed with return
code 1. Parent hashes were stable, G0B/G0C/variance/integration stayed closed,
and the complete stderr is stored in the immutable result.

```text
launch intent SHA256
  C8EB887E05BE8F3B08EED16B19FCDBCF49B6041CA2A13F6127EB59BE406CA484
result SHA256
  456B8E6897474BC48112BC2671A46B180EA28AE150700614FBD6DDD0F6202FF1
production module SHA256
  29B86374FF3A9B7ADC6D2B86F2C03A6F7F676303E5F100C46BEF1AC478B8C89E
frozen test SHA256
  A5AE1A9A2C20B8E67C70E2771B6AEE4674A03315BC3CB1CE88DA40E0CABBF84B
```

The production compatibility repair crossed the former failure boundary: the
dependency/source tests and the complete frozen-grid 20-column, tree, and M224
parity test passed. The later failures were outside production arithmetic:

1. the gauge fixture formed C and V through sequential row/column products,
   losing the issuer's required bitwise symmetry through rounding before pack;
2. the hostile interior-refusal case mutated the shared `p` owner and then
   reused that poisoned owner for the intended successful pack; and
3. the co-permutation test passed, but FlopScope warnings inserted inside its
   verbose unittest line, so the conservative durable parser recorded only
   five outcomes.

M240 receives no rerun and no estimator, native, variance, integration, or
score credit. Its byte-identical production module is preserved as validated
through the complete frozen-grid parity boundary only.

One test-only child may repair fixture representation/state isolation and
warning-free audit operands against this exact production hash. It may not
alter production, seeds, formulas, tolerances, thresholds, method order, or
gate scope. Failure of that one durable six-method run closes the branch.

