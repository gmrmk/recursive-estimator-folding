# M240 predeclaration -- meter-safe finite-scan compatibility child

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CODE_TEST_OR_EXECUTION`.

M240 changes one diagnosed compatibility boundary in frozen M238. It retains
the M238 tree algebra, 20-column map, deterministic tapes and receipts, event
labels, chart, refusal thresholds, output ownership, and M226 topology exactly.
It may make only these two tightly coupled repairs:

1. Production: prebind plain `numpy.ndarray` views of the already-owned boolean
   output slabs during `PersistentEventPacker` construction, and pass those
   views only as `out=` to the same three billed `fnp.isfinite` calls. Inputs,
   billed `fnp.isfinite` operations, reductions, refusal order, and numerical
   semantics remain unchanged. The views perform no numerical work, allocate
   no data buffer, and must identity/pointer-bind to the original boolean slab.
2. Audit-only test: construct fresh mutable copies of both hostile `j` and `k`,
   swap the selected values, make both copies read-only, and verify the original
   receipt digest is unchanged before issuing the malformed receipt.

No raw NumPy numerical fallback, library patch, unmetered finite scan, floor,
clip, threshold change, retuning, or parent edit is permitted.

## Frozen parent evidence

```text
M238 module SHA256
  25A44983642BAD7136C3486DF71BE9A3476EB76A28D2F9BA656EAB446241C603
M238 test SHA256
  618D1EF92917166325458FA2D51CC7B2402DB0261589D013A601F1D4A6617C7A
M238 disposition SHA256
  842EE3E6AB58D1622CC8AD2D4F6CA4159C40609D9162A51D9E9A06A69BC959F0
M239 result SHA256
  9271F2E9426B5FF1AB9882DE6787250EAE61C0D7C16EE4411D0E2FD86C6E6EAE
M239 disposition is the post-result audit record in its experiment folder.
```

The interpreter remains the pinned WhestBench starter-kit environment. M240
must preserve the same six G0A method bodies and order, changing only the module
under test and the hostile fixture construction described above.

## G0A gate

Before implementation, preserve a missing-module RED receipt. After the child
module and test exist, run exactly the six static G0A methods once through a
durable write-ahead result transport. All six must pass. Kill M240 on any error,
failure, unsupported wrapper, parent-hash drift, missing/extra method, hidden
allocation, raw NumPy numerical computation, changed refusal, or non-durable
receipt.

The hostile test must additionally prove:

- both mutated arrays are fresh copies and become read-only before issue;
- the original receipt arrays and digest do not change;
- the malformed canonical ordering is rejected by the production issuer; and
- zero-write/lifetime checks still execute after that rejection.

G0B is not authorized by this predeclaration. If G0A passes, G0B requires a
new sealed gate record before execution. Native G0C, variance, response,
scorer, truth, challenge weights, integration, and submission are forbidden.

