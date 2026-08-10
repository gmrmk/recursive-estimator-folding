# M234 disposition -- static kill at explicit-Philox timing premise

Status: `KILLED_STATIC_EXPLICIT_PHILOX_TIMED_PREMISE`

M234 was sealed before implementation with hashes:

```text
M234_PREDECLARATION_20260809.md
  DE95A56EF1C07BBC89BE06FC547E5759E69E14468831C891777A05E039D756E8
M234_FROZEN_MANIFEST_20260809.json
  A26CEEC8390BE336DA38E6CAA5CA2B219D86EC5795C3E824D2BAD2A927056A7E
```

Immediately after that seal, an independent fresh-process diagnostic supplied
by the parent falsified the cheapest binding premise. Narrow workspace hoist
plus removal of M231's allocation ledger, while retaining the current
`default_rng`, still produced M231 correction residuals of approximately
`3.81..4.80 ms` and combined residuals of `4.88..6.11 ms`; every process
missed the inherited `3.227021568 ms` cap.

More decisively, constructing explicit `fnp.random.Philox(seed)` after M212
cost approximately `3.00..3.63 ms` of residual by itself. Explicit
`fnp.random.Generator(np.random.Philox(seed))` followed by the integer-bank
`arange/broadcast/permuted` receipt cost approximately `3.35..3.80 ms`.
M234 froze the constructor inside timed production with an M234-only residual
allowance of only `2.025121700262334 ms`. The constructor premise therefore
fails before any estimator algebra or native implementation is needed.

Per the predeclared stop rule, no M234 implementation, M234 test, M234 native
runner, or G0 artifact is created. The estimator algebra and exact Philox
SRSWOR law remain preserved components; only the fully specified timed-
constructor topology is killed. A lawful child must move data-independent RNG
work into the official setup lifecycle or introduce and revalidate a genuinely
different cheap receipt law.

No compiler-retirement, source-efficiency, MSE, score, submission, rank,
prize, or winner credit is granted.
