# M132 — P8 reduced-source pre-outcome protocol

Date: 2026-08-07.  This is a target-free protocol for a proposed first-order
child: M126's exact easy repeated-output source plus shared mixed-float32
Rademacher probes, coupled only to the M125b source-batched carrier interface.
It opens no contest model, scorer, truth, public/private row, champion,
submission archive, or upload path.

## Disposition

**KILL before execution.**  The protocol and hash-bound inert manifest are
complete, but the independent small-width M122 oracle confirms that the
reduced source convention omits a nonzero `[2,1,1]` collision.  M130 supplies
only the quadratic leading jet, with neither an interval-certified full vertex
remainder nor a variance-qualified transport.  It is therefore not honest to
activate the M126+M125b child as a full first-order source.

This is a kill of this *reduced-source deployment*, not of the exact easy
contractions, M125b carrier, or the Rademacher hard-table mechanism.  Those
remain preserved components.

## Frozen candidate definition

The proposal would use the explicitly reduced M124/M126 collision convention:
`[3]`, `[2,1]`, `[4]`, `[3,1]`, and `[2,2]` are present; `[2,1,1]` is absent.
Its M126 tree/stars/paths and sparse collisions are exact easy source terms.
The `AABB` path residual and `[2,2]` hard table use the same outcome-
independent Rademacher probes, with each rounded sample symmetrized before
float64 accumulation.  Only dense probe operands are float32; easy analytic
source work and all accumulation are float64.

The probe counts are frozen at `P in {2,4,6,8}`.  If every gate had passed,
selection would be

```
argmin_P (estimated one-delay response variance(P) * effective_flops(P)),
ties resolved toward smaller P.
```

No contest outcome, score, or final-network error is an input to that rule.
`P=8` is only the named, pre-costed option; it is not selected by this pass.

## Required pre-outcome gates

For each generated cell and each P, the intended inert runner must require:

1. exact same-sign f32/f64 comparison of all `k3_aaa`, `k3_aab`, `k4_aaaa`,
   `k4_aaab`, and `k4_aabb` tables;
2. comparison of the frozen one-delay linear response, with complete response
   variance across independently seeded probe blocks (not only entrywise
   relative errors);
3. finite, symmetric output tables and deterministic replay;
4. hidden-coordinate permutation covariance and explicit positive-gauge
   interface checks;
5. static cost no larger than the bound below;
6. an independent M122 small-width source oracle, including the `[2,1,1]`
   collision, and a predeclared omission-bias bound;
7. an independent audit before a generated selection run is permitted.

The exact M122 oracle evaluates its trivariate normal-ordered collision source
at widths at most eight.  It is a development/reference oracle only, never a
target-width implementation.  It isolates the `[2,1,1]` exact-minus-tree
delta, transports it densely on the small cell, and applies the existing
one-delay Edgeworth map.  On one fixed generated width-four oracle cell it
obtained nonzero source mass (`1.0000006453` relative to the full exact small
source under the specified norm) and one-delay response RMS
`1.1642568e-6`.  This is sufficient to fail a zero/near-zero omission gate;
it is not a prediction of contest accuracy.

The previous fixed width-eight M124 shared-reference audit independently saw
the same mechanism at materially larger scales (three-label tree relative
error `0.69718`, transported repeated change `0.07395`).  M132 does not
recycle that outcome as a selection measurement; it records it as the causal
reason the reduced convention is barred.

## Cost lock

The installed FlopScope bill is `33,488,896` for a float32 `256x256` square
GEMM and twice that for float64.  The M126 worksheet plus protected M125b
carrier is:

| P | effective FLOPs |
|---:|---:|
| 2 | 63.345578320B |
| 4 | 73.727136080B |
| 6 | 84.108693840B |
| 8 | 94.490251600B |

The `P=8` line leaves only `5.509748400B` below a nominal 100B child
envelope.  It excludes the exact `[2,1,1]` repair, M130's full-vertex
remainder, extra response work, and runtime residual.  Consequently it is a
cost gate for the deliberately reduced convention, not a cost claim for the
correct full source.

## Implementation and target-free evidence

Files:

* `m132_p8_reduced_source_protocol/m132_reduced_source_protocol.py`
* `m132_p8_reduced_source_protocol/test_m132_reduced_source_protocol.py`
* `m132_p8_reduced_source_protocol/M132_DRAFT_MANIFEST.json`

The six generated tests pass:

1. frozen `{2,4,6,8}` set and cost table;
2. same-sign f32/f64 full-table and one-delay parity;
3. complete-sign replay through the reduced-source assembly;
4. output symmetry, permutation, and standardized positive-gauge interface;
5. independently evaluated M122 `[2,1,1]` omission is nonzero;
6. predeclared variance-times-cost selection has no outcome argument.

The manifest is intentionally `execution_authorized:false`, has no outcome
file, and is marked `DRAFT_INERT_KILLED_BY_211_OMISSION_GATE`.  Its source
hashes bind M126, M125b, M122, and the M132 code/test surfaces.

Run only the target-free unit suite:

```powershell
& 'work\headroom-recursion\.venv\Scripts\python.exe' -m unittest -v `
  'work\scorefloor_generation\m132_p8_reduced_source_protocol\test_m132_reduced_source_protocol.py'
```

## Reopen condition

Reopen only as a different mutation: an exact or rigorously bounded
three-label source must replace the omission, with full ownership against the
M126 source, its new hard `aabb` variance budget, one-delay propagation,
mixed-precision parity, and an end-to-end cost trace.  M130's quadratic
operator is a potential ingredient, not fulfillment of that contract.
