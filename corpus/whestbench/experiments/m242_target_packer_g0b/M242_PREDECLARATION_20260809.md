# M242 predeclaration -- target-size event-packer G0B

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_RUNNER_OR_EXECUTION`.

M242 changes no estimator, fixture, production code, formula, threshold, seed,
or test. It authorizes exactly one durable execution of the existing M241
method:

```text
test_m241_isolated_g0a_fixtures.M241AlgebraAndInterfaceTests.
test_target_digests_non_degeneracy_and_static_flopscope_contract
```

This is the sole target-size G0B gate for the byte-frozen M240 packer. The six
M241 G0A methods may not be rerun. Native G0C, variance, response, truth,
scorer, challenge weights, integration, and submission remain forbidden.

## Frozen authority and parents

```text
M240 production module SHA256
  29B86374FF3A9B7ADC6D2B86F2C03A6F7F676303E5F100C46BEF1AC478B8C89E
M241 test SHA256
  BAFCAB1CD2FA1FAE368160490FD1B6639119386ADA3F3F9B13197E09E71ECFD4
M241 launch intent SHA256
  960CB2B9C43E0AED791777F6037858323CFA4860B5C5B6DBC02DC7B5E41CF869
M241 result SHA256
  8E26F1AAD37A339B15AE5D9B933BD6177325168BA57B0CF07B716E1202C953CD
M241 disposition SHA256
  FED9F52B8C1FB7C3208A178511AC733009F7D2131318A46396784432F9F8EEDB
M237 durable helper SHA256
  774CEF483C33B149524121144A4C5EDE9141F094AA6FE5037414E31BDDAC873C
```

The durable runner must verify these and the M241 predeclaration, manifest,
erratum, and runner before launch and after completion. It must create an
exclusive write-ahead intent, run only the exact one-method command with the
pinned starter-kit interpreter and M241 working directory, capture complete
stdout/stderr/return code/duration, and publish one no-overwrite result through
the validated M237 fsync/hard-link protocol. Existing intent/result/temp paths
fail closed; there is no rerun.

## Frozen pass gate

The test itself freezes the target tape and five receipt digests, strict
nondegeneracy, and these response-free resource/ownership requirements:

- no pack failure;
- billed FLOPs at most 4,000,000;
- operation calls at most 192;
- setup-owned storage at most 4 MiB;
- no in-budget `empty`, `reshape`, `concatenate`, or `sort` operation;
- exact twenty-column output names and completed layer bitmap;
- `g` aliases the immutable receipt;
- every output is float64 and read-only;
- tape/receipt ownership remains stable; and
- every output is finite.

M242 passes only with return code 0, one exact parsed outcome `ok`, warning-free
output, stable before/after parent hashes, no timeout/exception, and every
later-gate flag false. Any mismatch kills M242 and closes this packer branch.

