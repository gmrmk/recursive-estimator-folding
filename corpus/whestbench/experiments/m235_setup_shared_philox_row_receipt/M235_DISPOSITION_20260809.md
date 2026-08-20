# M235 disposition -- killed by the frozen official-worker RSS gate

Date: 2026-08-09. Final status:
`KILLED_FROZEN_NATIVE_RSS`. Generated-only and response-free. G0 was never
opened. The ten-process native aggregate was never opened.

## What survived

M235's algebra and accounting survived intact:

- the setup-issued Philox receipt is exact SRSWOR and immutable;
- exhaustive generated widths `3..9` passed the cubic M205 oracle, independent
  row loop, positive gauge, zero, marginal subset mean, and pathwise hidden-row
  covariance gates at the frozen tolerances;
- all 31 target layers matched the independent M227 collision-row oracle;
- setup billed exactly `32,768` with exactly 18 setup-owned empty calls;
- every official prediction billed M212 `1,249,253,376`, M235
  `864,960,512`, and combined `2,114,213,888`, with the exact frozen calls;
- all three component and combined residual-wall gates passed;
- receipt bytes and every live object/data pointer remained stable;
- all source slots were finite and symmetric;
- `A -> B -> A` reproduced `aaaa`, `aaab`, and `aabb` bitwise.

The final algebra suite passed `5/5` in `0.469s` after disposition.

## Same-worker audit chronology

The first native prototype was rejected before execution because it started
and closed an official worker and then replayed a separate local state. A new
static RED gate forbade that split lifecycle.

The repaired harness kept one estimator instance alive across the complete
official sequence. The worker's f32 payload packed 31 source weights in layers
0..30 and 31 factors in rows 0..30 of layer 31. Two setup-owned list slots fed
the unchanged two `stack(..., out=f64)` calls. M212 and M235 ran under named
FlopScope scopes. Setup wrote pointer/object metadata only; after every
official predict the host read receipt, workspace, timing, identity, and full
source bytes from that same worker with Win32 `ReadProcessMemory`.

Two hostile transport REDs were preserved:

1. Philox `permuted(axis=1)` produced a Fortran-contiguous rank receipt with
   strides `(8,248)`, so a C-only reader refused it. The lawful repair read the
   physical span and reconstructed the declared strides.
2. The pinned venv `python.exe` is a redirector. `SubprocessRunner._process.pid`
   names the launcher, while the manifest pointers live in the executing
   worker's `os.getpid()`. A minimal falsifier showed launcher PID `4968`,
   worker PID `28128`, and exact remote bytes `b'HELLO'` only from the worker.
   M235 thereafter recorded both PIDs separately and never called the launcher
   the worker.

The identity audit initially enumerated a setup-frozen tuple, which could miss
field rebinding. A hostile rebind test failed as intended; the repaired
post-kernel audit re-enumerates current `state.staged/base/row` and receipt
fields. This is audit-only instrumentation, not production binding logic, and
its overhead remains inside the official residual. The production M235
correction contains no pointer scan.

## Binding failure

The exact one-process same-worker receipt was:

```text
prediction     combined residual     M235 residual     peak worker RSS
A1                1.551700 ms          0.648900 ms       468.613281 MiB PASS
B                 1.985300 ms          0.473700 ms       554.625000 MiB FAIL
A2                1.670400 ms          0.403400 ms       557.644531 MiB FAIL
frozen RSS cap                                           512.000000 MiB
```

The maximum deficit is `45.644531 MiB`. The pinned worker keeps the previous
JSON request live while parsing the next request; the audit stage slots also
retain roughly one f32 fixture (`~8 MiB`) until rebound. Clearing those slots
is an untested next-child hypothesis, not an M235 repair. Even the full
estimated `~8 MiB` recovery is substantially below the observed
`~42-46 MiB` deficit. A credible successor needs a different memory topology,
such as traced layer-batched M212 staging, with a new predeclaration, bills,
calls, wall/RSS gates, and source-efficiency audit.

Under the frozen stop rule, one RSS failure kills fixed M235. No threshold,
slot lifetime, workspace layout, layer batching, seed, `k`, or operation was
retuned after seeing the result.

## Preserved artifacts

- `M235_PREDECLARATION_20260809.md` and errata 1-4: frozen contract;
- `M235_TDD_RECEIPT_20260809.md`: strict-TDD provenance;
- `test_m235_setup_and_algebra.py`: five passed algebra/provenance gates;
- `test_m235_native_contract.py`: split-lifecycle, live-rebind, and official
  same-worker contracts;
- `m235_setup_shared_philox_row_receipt.py`: production component;
- `m235_official_setup_estimator.py`: audit-only official entrypoint;
- `run_m235_native_process.py`: same-worker hostile harness;
- `M235_NATIVE_ONE_PROCESS_RESULT_20260809.json`: exact final receipt.

No retirement credit, integrated ABI credit, source-efficiency credit,
submission credit, leaderboard claim, or prize claim is granted.
