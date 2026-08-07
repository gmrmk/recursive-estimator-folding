# M125b generated carrier component report -- 2026-08-07

## Verdict: PASSED_CARRIER_COMPONENT

This verdict covers only the source-agnostic M125b inhomogeneous forward
tangent carrier.  Explicit per-source suffix superposition and the coalesced
recurrence agree for every generated final mean and central-covariance entry;
the row-oriented affine map and every local Gaussian-ReLU Jacobian block are
also checked independently.

It is not a passed M122 source builder or full estimator candidate.  The
complete mutation remains **REPAIR** at the alternating fourth-order `ABAB`
Khatri--Rao source node.  No outcome grid, benchmark datum, scorer, champion,
or submission was used.

The exact installed-FlopScope protected bill for the 30-stage carrier,
31 source additions, final response, and audited Gaussian background is
`12.819347280B`.

## Generated verification

```text
test_inhomogeneous_recurrence_equals_explicit_source_superposition ... ok
test_row_oriented_affine_and_complete_relu_blocks ... ok

Ran 2 tests
OK
```

## SHA-256

| artifact | SHA-256 |
|---|---|
| `m125_forward_tangent.py` | `FBC9FE32357801B22F0313D4043022E81E2764FF3BF4BE94F0DFE3DDB3D1ED32` |
| `test_m125_forward_tangent.py` | `1FEA02791ADB9E29E6913EC3A1E4A4A46AC765C999725C3F128A729A1516643B` |
| `PRETHEORY.md` | `5A6B5B96C74093B5FD90BDD475E86D5AAAC68DF4770CA807FAE41BCE33B7AD9C` |
| `M125_SOURCE_BATCHED_FORWARD_TANGENT_THEORY_20260807.md` | `99DEA1651ECB6C73F6368B461DFC2BB23864D45B15F06C32F35C83DEA393C69E` |

