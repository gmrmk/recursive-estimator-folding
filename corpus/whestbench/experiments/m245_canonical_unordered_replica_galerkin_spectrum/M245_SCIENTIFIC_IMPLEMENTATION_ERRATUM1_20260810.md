# M245 scientific implementation erratum 1 -- closed meter-overlap domain

Date: 2026-08-10

Status: proposed append-only authority repair; ineffective until the activation
conditions below are satisfied.

## E1.1 Purpose and bindings

This document repairs one temporal contradiction in section E2.7 of
`M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md`. It changes no scientific
formula, fixture, event assignment, quadrature rule, resource cap, process
topology, ownership rule, no-retry rule, test byte, or launch permission.

It binds these exact authorities:

```text
979f7c35334ff0df09ad134255fddf23f944237f  committed Erratum2 authority
8641de9ec301ba402b87e50dd8c5e3322a6532313f1d603c54356a4137e21587  M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md
401629468b5ec1f2eb5447b650b10f27fb47ba7ce3af74c740a230feeefcceaf  M245_SHA256SUMS_V2_OVERLAY2_20260810.txt
9886acd7d1eb9f7e887bed70c516e6b0de22b58b  committed dummy-only implementation authority
46ba45dcb35fa93fcbe17b399a67e61cb03cfe13b9f2bbca30807b65ca79ee75  M245_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.md
e0cd1409e45d2397f4a9dbbf849fa9e7e02dc9d76ea6540a0b1475d300f3b514  M245_SHA256SUMS_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.txt
130391c3210ef800083049889893a2262ccee7ad  immediate coordination-only parent
```

The four test authorities remain byte-exact:

```text
355820f372c0e0b7b466ed98f3db2a36b92142927c494406b3f5dbdb5c26d626  test_m245_primary_core.py
e7eceb023b725badb06d59773b7813d2083d3dfd33fffa7fd35fcedf2055fa21  test_m245_replica_core.py
112869bf75a127ae706dcc1346c070f128c15c74a125d1818646fbf46fd5294d  test_m245_scientific_transport.py
6d723cde0a9784cc20bf0a41b25ab4599f8c103f1c3de04cba0d6e8b9336a4e6  test_m245_aggregation.py
```

This erratum is ineffective while uncommitted. It becomes effective only when:

1. an independent read-only audit returns
   `PASS_M245_IMPLEMENTATION_ERRATUM1_AUTHORITY_ONLY` on its exact bytes and
   checksum;
2. this file and
   `M245_SHA256SUMS_SCIENTIFIC_IMPLEMENTATION_ERRATUM1_20260810.txt` are
   committed byte-identically in one docs-only commit whose sole parent is
   `130391c3210ef800083049889893a2262ccee7ad`; and
3. that commit contains no source, test, fixture, shard, trigger, result, or
   execution-evidence change.

If the immediate parent changes before the docs-only commit, this proposal is
ineffective until an append-only rebind names the actual parent. Untracked
six-file implementation drafts may remain in the working tree, but neither
they nor any unrelated untracked file may enter the activation commit.

## E1.2 The contradiction

Erratum2 requires `O` to sample before spawning `S` and requires `S` to sample
only after `S` exists. Therefore the first raw outer tick is necessarily earlier
than the first raw inner tick. Erratum2 also says to merge the union of all raw
ticks while failing any union tick with no prior sample from either stream.
Taken literally, the first legitimate pre-spawn outer tick has no possible
prior inner sample and every compliant invocation must fail. The same problem
can occur in the opposite direction after the inner stream closes while `O`
finishes terminal durability work.

This is an evidence-domain contradiction, not permission to omit process
lifetime evidence or relax a cap.

## E1.3 Complete raw streams remain mandatory

Both complete raw streams remain immutable and hash-bound.

- The outer raw stream begins before `S` spawn, with `O=ALIVE` and
  `S=NOT_CREATED`, and continues through verified `S` exit and any
  invocation-two final-shard publication.
- The inner raw stream begins before `L` creation and continues through clean
  `W` and `L` exit and its frozen close boundary.
- Every adjacent gap in each complete stream is at most `0.100000000` seconds.
- QPC frequency, QPC/FILETIME affine clock relation, PID plus creation FILETIME,
  image identity, state transitions, cumulative CPU counters, current working
  set, and lifetime peak working set remain fail-closed exactly as in Erratum2.
- Every raw row remains in the immutable meter and contributes to the bound raw
  sample count. No pre-overlap or post-overlap row may be deleted from the raw
  evidence merely because it is outside the concurrent merge domain.

## E1.4 Closed concurrent-RSS merge domain

Let the first and last QPC ticks of the complete inner stream be
`i_first, i_last`, and those of the complete outer stream be
`o_first, o_last`. Define:

```text
d_first = max(i_first, o_first)
d_last  = min(i_last,  o_last)
D = {t in union(inner_ticks, outer_ticks) : d_first <= t <= d_last}
```

`d_first <= d_last` and nonempty `D` are mandatory. Sampled concurrent RSS is
computed only on `D`. At every `t` in `D`:

1. each required stream must have a sample at or before `t`;
2. every carried sample must be no older than `0.100000000` seconds;
3. frequency, affine clock, PID plus creation FILETIME, image identity, and
   process-state agreement must be exact;
4. each process identity is counted once; duplicated `S` contributes
   `max(inner_S, outer_S)` for current and peak bytes; and
5. missing prior evidence, over-age carry, counter rollback, identity
   ambiguity, interpolation, or a tick outside the closed definition fails.

This supersedes only the phrase "the union of inner and outer QPC ticks" and
the associated missing-prior application in Erratum2 E2.7 lines 392--398. The
correct reading is "the union restricted to the exact closed common raw-stream
domain `D`, with missing-prior and carry gates at every emitted tick in `D`."

## E1.5 Full-lifetime gates cannot use the restriction

The overlap restriction applies only to the instantaneous merged-concurrency
series. These values continue to use the complete raw streams and may not be
trimmed to `D`:

- full wall time from retained `O` creation FILETIME through the terminal
  endpoint;
- final cumulative kernel plus user CPU for `O,S,L,W`, without baseline
  subtraction;
- per-role maximum observed lifetime `PeakWorkingSetSize` over every raw row;
- raw sample counts and maximum adjacent gap for each complete stream; and
- all startup, exit, durability, and final-publication milestones.

The RSS gate remains:

```text
max(maximum merged concurrent RSS on D,
    sum of complete-stream per-role lifetime peaks for O,S,L,W)
```

Consequently excluding non-overlapping ticks from the concurrency merge cannot
reduce the conservative lifetime-peak upper bound, CPU charge, wall charge, or
sampling-gap evidence.

## E1.6 Narrow implementation adoption and stop boundary

The six implementation drafts were written before this contradiction was
formally isolated. Once this erratum is active, the implementation owner may
adopt, edit, and statically review those already-written drafts under the
existing implementation authorization. This cures chronology only; it does not
grandfather any source defect or bind any candidate source hash.

No dummy GREEN command may run until this erratum is active, all six candidate
bytes are frozen, and the complete I1.6 static gate independently passes. The
four commands remain one-shot and serial under I1.7. All real science, fixture
evaluation, shard/census/trigger creation, production dispatch, aggregation,
provider inference, FLOP credit, and submission claims remain forbidden. The
mandatory stop in I1.9 is unchanged.

