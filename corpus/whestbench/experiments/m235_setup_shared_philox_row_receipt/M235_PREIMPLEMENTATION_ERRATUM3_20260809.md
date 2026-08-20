# M235 preimplementation erratum 3 -- overwrite-complete workspace reuse

Date: 2026-08-09. Sealed before all M235 tests, implementation, native traces,
and G0. This final native-lifecycle invariant supplements erratum 2 without
changing its seeds, costs, or estimator.

The official lifecycle reuses one estimator instance and its setup-owned
mutable workspaces across predictions. Therefore each of the five frozen
native processes must execute the already-frozen first source `A`, second
source `B`, and then source `A` again, in that exact order, after one setup:

```text
setup(ctx_seed) -> predict(A) -> predict(B) -> predict(A).
```

Every prediction independently must match the exact M212 and M235 call/bill
receipts and pass the component, lawful-combined, conservative-combined, RSS,
finite, and symmetry gates. The first and third A outputs must be bitwise
identical in all `aaaa`, `aaab`, and `aabb` source slots; a numerical tolerance
is not allowed. Their output SHA-256 digests must match.

Before setup return and after each of the three predictions, hostile audit
also records object identity and underlying data pointers for every setup-owned
M212/M235 workspace array. They must remain identical. The immutable setup
receipt object, selected-view object, data pointers, and digest must likewise
remain identical at all four observations.

This A-B-A replay proves the kernel and upstream staging are overwrite-
complete under intervening different MLP state. A stale workspace value,
order-dependent output, reallocation, receipt mutation, different bill, or
different call count kills fixed M235. No warmup prediction may be discarded
from the gate.
