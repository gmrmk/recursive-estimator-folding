# M239 disposition -- durable transport passed; frozen M238 G0A failed

Status: `PASSED_DURABLE_EVIDENCE_TRANSPORT_ONLY`.

M239 changed only evidence transport and successfully published the complete
result of exactly one invocation of M238's six frozen G0A tests. The parent
module, test, disposition, and durable helper hashes were identical before and
after execution. The result contains six exact method names, complete stderr,
return code 1, no execution exception, and explicit records that G0B, G0C, and
variance were not run.

Frozen receipts:

```text
predeclaration SHA256
  48AB88813BC197CF97774B7C938DEA77302C3BF24AED1B1D8E39D58BAEC9FCCA
manifest SHA256
  6246C3528A200E541DEE1C6BA9F1D0DB5ED00F78CFBD1E60F54D13D0104D3EF7
prelaunch erratum SHA256
  785F2174CD586D8BF62EF5EA718CAFD6D687EF355FC740B6C04428C126EB16D8
runner SHA256
  13A4A3770BC3B624F881FFC5FCCA5BA1751A1FCDBEB0B505E555524B49C1956C
launch intent SHA256
  921601EEF9150F4026DCA657C5EBA18B868D6CC90E7E785264E9B1D62E1DADBF
result SHA256
  9271F2E9426B5FF1AB9882DE6787250EAE61C0D7C16EE4411D0E2FD86C6E6EAE
```

The frozen M238 outcomes were two passes and four errors. The two dependency
and symbolic-census tests passed. Three numerical/interface tests reached the
same production defect: `fnp.isfinite(input, out=WhestArray)` billed the call
but passed the unstripped `out` subclass into NumPy. The fourth error occurred
inside the hostile test before candidate issue: it made `j` writable but then
attempted tuple assignment into still-read-only `k`.

Therefore M238's updated evidentiary disposition is
`KILLED_FROZEN_G0A_IMPLEMENTATION_AND_HARNESS_FAILURE`. The receipt does not
falsify the nine-monomial tree identity, the exact 20-column map, gauge or
permutation covariance, or the downstream M224/M226 numerical mechanism,
because none of those three executed numerical tests crossed the finite-scan
boundary. M239 earns no estimator, cost, variance, wall, memory, integration,
or score credit.

Only a newly predeclared compatibility child may repair the metered finite-scan
output views and the audit-only hostile fixture. It must preserve all math,
inputs, thresholds, refusal semantics, and test order. G0B, native, variance,
response, truth, scorer, challenge weights, and integration remain closed.

