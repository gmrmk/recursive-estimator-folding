# M242 disposition -- killed at frozen target-fixture provenance gate

Status: `KILLED_FROZEN_G0B_FIXTURE_PROVENANCE`.

M242 executed its one authorized target-size G0B method once. The durable
transport passed, parents remained stable, and all forbidden later gates stayed
closed. The test failed before constructing a packer or entering FlopScope:

```text
frozen target-tape digest
  2012133C1CDA19C695B94F0E54A033DD3B1694AC2A009DADA9DADE68AA36FE3C
pinned-interpreter observed digest
  84E53D17F9775C968E655C1A79AE8FA84931737DD5E6F665C7C978110FBF6AA5
```

Receipts, pack arithmetic, target FLOPs, calls, storage, output ownership, and
finiteness were therefore not evaluated.

```text
runner SHA256
  C93A1006183E6ECDB978FC1D8BB6A53E864FF98EE255EAEAFC06CFA414990A99
launch intent SHA256
  ADDE558B15DECFCAD5180C410E669ADD3BF982E9946AF59329A72B99E634BF04
result SHA256
  B0D3B8875ADBFEE264BC1871660577EA301FFD8332BA546D71EB164A67806B2B
```

The pinned runner used Python 3.12.13 and NumPy 2.4.6. The system environment
available during earlier fixture work is Python 3.14.4 and NumPy 2.4.4. M238's
erratum froze the first digest but did not bind the environment or serialize a
canonical fixture artifact. That missing provenance is a fixture failure, not
evidence against M240's already-validated G0A algebra.

Post-result replacement of the digest or deletion of the byte-identity gate
would weaken a failed predeclaration and is forbidden. M242 receives no rerun.
The live-packer promotion branch stops here; only the byte-frozen G0A component
is preserved. Native, variance, response, truth, scorer, challenge weights,
integration, and submission were not run.

