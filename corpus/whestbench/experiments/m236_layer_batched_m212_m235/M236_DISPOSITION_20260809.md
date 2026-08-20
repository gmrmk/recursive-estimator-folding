# M236 disposition -- native receipt unobservable

Date: 2026-08-09. Final status:
`KILLED_FROZEN_NATIVE_RECEIPT_UNOBSERVABLE`.

M236's one authorized official seed-0 `A -> B -> A` runner invocation was
launched exactly once. The orchestration cell completed, but the caller used a
content-block forwarding expression on a shell return that did not expose a
`content` array. Consequently the runner's stdout was discarded when the
isolate ended. The runner intentionally used an ephemeral `TemporaryDirectory`
and did not write a result file, so bounded read-only recovery found neither a
surviving scratch directory nor a native result artifact.

This is an evidence/transport failure, not an observed RSS, wall, algebra, or
bill failure. It is nevertheless binding: no native metric can be reconstructed
or inferred honestly, and an absent receipt cannot be credited as a pass. The
frozen one-run rule forbids rerunning to recover the lost output.

Invocation receipt:

```text
date: 2026-08-09 (the discarded wrapper did not preserve an exact wall clock)
tool cell: 47
command:
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\whest-v014\Scripts\python.exe
  C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m236_layer_batched_m212_m235\run_m236_native_process.py
```

The wrapper awaited `shell_command` and then iterated only
`r.content ?? []`; this shell return did not expose a content-block array, so
the completed command's return was never appended with `text(r)`. The V8
isolate then ended and the return became unrecoverable.

Bounded exhaustive searches of the runner's only declared persistence
locations found no pre-disposition artifact:

```text
C:\Users\strid\AppData\Local\Temp\m236_seed0_primary_*
candidate folder patterns: *RESULT*, *DISPOSITION*, *stdout*
matches before sealing disposition: 0
```

## Preserved evidence

- Five algebra/ownership tests passed in `0.954s`.
- Both frozen target f32 fixtures matched full M235 byte-for-byte in every
  `aaaa`, `aaab`, and `aabb` byte.
- The exact static bill was `2,114,213,888`, with the frozen operation calls.
- The exact setup-owner ledger was 18 empty owners and a calculated numerical
  peak of `61,812,736` bytes (`58.94921875 MiB`).
- Four prenative static lifecycle tests passed after the payload-borrow erratum.
- The official runner, entrypoint, tests, REDs, and both errata remain preserved.

None of those facts proves the required actual-worker `<496 MiB`, wall,
identity, slot-release, response, or replay gates for the lost invocation.

## Stop

There was no second worker invocation, no threshold or block retune, no
ten-process aggregate, and no G0. M236 receives no native, memory-safe,
source-efficiency, MSE, score, submission, leaderboard, or prize credit.

A future child may predeclare write-ahead native receipt persistence before
launch so tool-output loss cannot destroy the sole admissible result. That is
an untested child hypothesis, not an M236 repair.
