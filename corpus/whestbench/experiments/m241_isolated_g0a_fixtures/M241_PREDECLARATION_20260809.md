# M241 predeclaration -- isolated, bitwise-valid G0A fixtures

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CHILD_TEST_OR_EXECUTION`.

M241 is test-only. It executes the frozen M240 production module at SHA256
`29B86374FF3A9B7ADC6D2B86F2C03A6F7F676303E5F100C46BEF1AC478B8C89E`
and may change only G0A fixture representation/state isolation:

1. Gauge C and V are each materialized with one bitwise-symmetric outer scale.
   The test must assert exact equality with their transposes before issuance.
2. The intentional `p=0` interior refusal uses a fresh, owning, nonaliasing
   copied tape. The canonical clean tape arrays, owners, and digest must be
   unchanged before and after rejection; the later success tape is issued from
   that clean source.
3. Only operands passed to `numpy.testing` audit comparisons are converted to
   plain base ndarrays, preventing FlopScope warning text from splitting verbose
   unittest result lines. This is audit conversion, not production arithmetic.

All seeds, labels, outer-g values, formulas, thresholds, tolerances, six G0A
method names/order, production calls, and billing behavior remain frozen.

## Frozen evidence

```text
M240 production module SHA256
  29B86374FF3A9B7ADC6D2B86F2C03A6F7F676303E5F100C46BEF1AC478B8C89E
M240 original test SHA256
  A5AE1A9A2C20B8E67C70E2771B6AEE4674A03315BC3CB1CE88DA40E0CABBF84B
M240 launch intent SHA256
  C8EB887E05BE8F3B08EED16B19FCDBCF49B6041CA2A13F6127EB59BE406CA484
M240 result SHA256
  456B8E6897474BC48112BC2671A46B180EA28AE150700614FBD6DDD0F6202FF1
```

The child test must statically prove that the production hash is unchanged;
the rejection copy owns its storage and shares memory with no clean owner; the
clean tape digest and owner identities are stable; gauge C/V are bitwise
symmetric; every `numpy.testing` packed-output operand is a plain ndarray; and
the production finite-scan call/bill assertions inherited from M240 remain.

After a read-only static audit, exactly one durable six-method G0A launch is
permitted. It passes only with return code 0, six exact ordered outcomes, every
outcome `ok`, warning-free parseable method lines, and stable before/after
parent hashes. Any production hash drift, error, failure, warning-induced parse
mismatch, extra method, or extra run kills M241.

G0B, native, variance, response, truth, scorer, challenge weights, integration,
submission, and any M240 rerun are forbidden.

