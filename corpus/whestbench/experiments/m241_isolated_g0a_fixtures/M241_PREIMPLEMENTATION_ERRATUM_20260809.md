# M241 preimplementation erratum -- bind successor authority

Status: `SEALED_BEFORE_CHILD_TEST_RUNNER_OR_EXECUTION`.

M241's sole permitted test-only launch derives from the exact M240 disposition:

```text
path
  ../m240_meter_safe_finite_scan/M240_DISPOSITION_20260809.md
SHA256
  831636716344761C22B3D10F4D3F6FD3F5DC50E1EFB2C6C4AE51CBF46312CEA7
```

The future M241 durable runner must verify this file together with every other
frozen parent before launch and after completion. Missing or changed authority
is a kill. M241 is a separately predeclared test-fixture successor and its one
launch may never be represented, counted, or retried as an M240 run.

