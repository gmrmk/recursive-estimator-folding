# fold3cap rebuild — 2026-08-10 (post-_tally-fix gate re-run + repackage)

Status line (honest, verbatim per tasking): **engineering-gated rebuild; score
remains unknown until graded; submission and nomination decisions are Jonah's.**

Trigger: commit 931285d applied the U2-recommended one-line fix to
`capped_fold3.py::Estimator._tally()` — `get_active_budget().flops_used` (O(1)
current-context read) replacing `budget_summary_dict()["flops_used"]`
(O(process-history) rescan whose wall time lands in the scored residual channel;
bound in `../u2_fold3cap_bound/U2_FOLD3CAP_BOUND.md`). The sealed package
`4_fold3cap.tar.gz` (sha256 d3f5aefa…, 11,643 B) contains the UNFIXED source.
U2 §5 predicted the fix is behavior-preserving: within one predict the
accumulator is constant, so `_tally` deltas — and therefore n_eff, G1, G2, G3 —
are bit-identical.

## Deviations (recorded loudly)

1. `run_t3_gates.py` writes `t3_gate_results.json` in place, so the re-run
   overwrote the frozen 2026-08-08 record. The frozen bytes were snapshotted
   FIRST and preserved as `t3_gate_results_FROZEN_20260808.json` (sha256
   EB5E0E228223FE2D967874301E5BF4E1E95605F809C8978D4A7A8423339F9353). The
   on-disk `t3_gate_results.json` now holds the 2026-08-10 re-run, which is
   field-identical to the frozen record except the 7 `wall_s` timing leaves
   (below). Its `date` field still reads "2026-08-08" (hardcoded in the runner;
   left untouched).
2. `package_source/estimator.py` was edited: the identical `_tally` fix hunk
   from committed `capped_fold3.py` was applied (the package source still held
   the unfixed body; it is byte-derived from `capped_fold3.py` modulo the flat
   package import-path adaptation). This edit was required to build the fixed
   tar; it was not explicitly named in the tasking.
3. No git commands were run (orchestrator commits). Nothing was submitted; no
   whest login; `whest package` / `whest validate-package` are local-only
   operations. No sealed tar was run with `--dry-run` (only `tar -tzf` listing
   and extraction of copies to the session scratchpad).

## 1. Gate re-run (G1–G3, fixed source) — VERDICT: IDENTICAL, ALL PASS

Command (pinned toolchain, PYTHONIOENCODING=utf-8):

```
work\whest-v014\Scripts\python.exe  ...\t3_fold3_deterministic_cap\run_t3_gates.py
```

Console output, verbatim (2026-08-10 run):

```
G1: cost-model calibration on 3 He-init synthetic nets
  net 11: C_uncapped=2.3617e+11  C_pred(39936)=2.4295e+11  ratio=1.0287  n_eff=39936  C_capped_metered=2.4295e+11  [PASS]
  net 22: C_uncapped=2.4212e+11  C_pred(39936)=2.4908e+11  ratio=1.0287  n_eff=39168  C_capped_metered=2.4445e+11  [PASS]
  net 33: C_uncapped=2.2142e+11  C_pred(39936)=2.2790e+11  ratio=1.0293  n_eff=39936  C_capped_metered=2.2791e+11  [PASS]
G1: PASS

G2: adversarial low-pruning worst case
  adversarial design m0=0.002: cold units (layers 1..31) = 2155
  adversarial design m0=0.004: cold units (layers 1..31) = 1922
  adversarial design m0=0.008: cold units (layers 1..31) = 836
  adversarial design m0=0.016: cold units (layers 1..31) = 15
  adversarial design m0=0.032: cold units (layers 1..31) = 0
  m0=0.032 design_cold=0 realized_active=[256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256]
  n_eff=31232 (<39936: True)  completed=True  finite=True
  C_capped=2.4303e+11 <= 2.4970e+11: True
  diagnostic: uncapped C=2.9949e+11 (would breach B=2.720e+11: True)
G2: PASS

G3: bitwise no-op off the tail (G1 nets with C_pred(full) <= CAP)
  net 11: applicable, n_eff=39936, bitwise_equal=True [PASS]
  net 22: not applicable (C_pred(full)=2.4908e+11 > CAP), n_eff=39168
  net 33: applicable, n_eff=39936, bitwise_equal=True [PASS]
G3: PASS

VERDICT: PASS: G1, G2, G3 all pass
```

### Structured diff vs the frozen record (second signal)

A recursive leaf-by-leaf JSON diff of the re-run `t3_gate_results.json` against
the frozen snapshot (`t3_gate_results_FROZEN_20260808.json`):

```
total differing leaves: 7  (wall_s: 7, non-wall: 0)

NON-WALL DIFFS (must be empty for IDENTICAL verdict):
  (none)

wall_s diffs (timing diagnostics, not gate outputs):
  $.gates.g1.nets[0].capped_wall_s: frozen=3.766  new=5.123
  $.gates.g1.nets[0].uncapped_wall_s: frozen=3.684  new=4.933
  $.gates.g1.nets[1].capped_wall_s: frozen=3.818  new=5.597
  $.gates.g1.nets[1].uncapped_wall_s: frozen=3.69  new=5.168
  $.gates.g1.nets[2].capped_wall_s: frozen=3.615  new=5.315
  $.gates.g1.nets[2].uncapped_wall_s: frozen=3.536  new=4.93
  $.gates.g2.capped_wall_s: frozen=3.4  new=4.515

verdicts: frozen='PASS: G1, G2, G3 all pass' new='PASS: G1, G2, G3 all pass'
```

Every gate-relevant field is bit-identical to the frozen record: all billed-FLOP
totals (`c_uncapped_metered`, `c_capped_metered`), `c_pred_full`,
`c_pred_chosen`, ratios, `n_eff` choices (39936 / 39168 / 39936 / 31232), the
`_tally`-delta observables `sim_cost_observed` (6784399632 / 6968410237 /
6491132347) and `dp_cost_observed` (20053248 on all three), G2's realized active
counts and pass triple, and G3's bitwise-equality flags. Only wall-clock timing
differs (machine load; not a gate output). **U2's behavior-preservation
prediction is confirmed.** Note the gates run three predicts per fresh
BudgetContext in one process, so the old absolute `_tally` values would have
included accumulator history — the identical deltas are exactly the invariance
U2 §5 argued.

## 2. Packaging recipe (determined from the old tar + installed packager)

- `4_fold3cap.tar.gz` (Desktop) sha256
  D3F5AEFAFC1CD91B77E92F060E143A4B56510A26C092840668680D7354E21A6C, 11,643 B —
  byte-identical to the in-repo `submission_fold3cap_n39936_20260808.tar.gz`
  (same sha256). Members (flat, in order): base_estimator.py, estimator.py,
  estimator_n39936.py, fold3_estimator.py, fold_estimator.py,
  orthogonal_fold3.py, manifest.json. PAX format, uid/gid 0, source mtimes
  preserved, manifest appended last with build-time mtime — the exact output
  shape of `whestbench/packaging.py::package_submission` (folder mode, sorted
  members, generated manifest with per-file sha256; `packager_version: 0.1.0`
  matches the manifest).
- All six `.py` members of the old tar were byte-identical to
  `package_source/*.py` before the fix (hash-verified), so `package_source/` is
  the build root.
- Rebuild: apply the `_tally` fix hunk to `package_source/estimator.py`, then
  `whest package --estimator package_source --output
  submission_fold3cap_n39936_FIXED_20260810.tar.gz --yes` → `ok: true`.
- Cross-check that the packaged source matches the gate-tested source: the full
  `diff -u capped_fold3.py package_source/estimator.py` is exactly ONE hunk —
  the pre-existing flat-package import-path adaptation (sys.path lines). The
  `_tally` regions are identical, so the gate re-run's results transfer to the
  packaged estimator.

## 3. Tar diff proof (old vs new, both extracted to session scratchpad)

- Member lists: IDENTICAL (7 members, same order).
- base_estimator.py, estimator_n39936.py, fold3_estimator.py,
  fold_estimator.py, orthogonal_fold3.py: byte-IDENTICAL.
- estimator.py: differs by exactly the fix hunk, verbatim:

```diff
@@ -258,8 +258,12 @@

     @staticmethod
     def _tally() -> int:
+        # O(1) live read; budget_summary_dict() re-scans the process-global
+        # accumulator and its cost grows with suite position (U2 bound:
+        # ~11% of B at net 100, C>B breach for near-cap nets past ~92).
         try:
-            return int(flops.budget_summary_dict()["flops_used"])
+            from flopscope._budget import get_active_budget
+            return int(get_active_budget().flops_used)
         except Exception:
             return 0
```

- manifest.json: differs in exactly two fields, both derived consequences of
  the fix/rebuild, verbatim:

```diff
     {
       "name": "estimator.py",
-      "sha256": "3d52613dcfd04fa572ec6aab164afb3ebade4a2e7f5f1f7ae55c46812cefd0b1"
+      "sha256": "43f4d0030421563105d1d2124dcafe6014a82b75df94e80abf8c5d6ffce2bbaa"
     },
@@
-  "created_at_utc": "2026-08-08T07:24:34.341781+00:00",
+  "created_at_utc": "2026-08-10T09:01:23.258461+00:00",
```

No other content differences exist between the two archives. (Member metadata:
the estimator.py member's mtime is its 2026-08-10 edit time and the manifest
member's mtime is the build time, as in the original recipe.)

## 4. Validation + hashes

- `whest validate-package <new tar> --json` → `{"ok": true, "issues": [],
  "whestbench_version": "0.14.0"}`.
- New tar sha256:
  **A8CAFBEF04A4F42B475BAE3E784158A3AA13D9A60078A28A3CD081E914395151**
  (11,776 B), file
  `submission_fold3cap_n39936_FIXED_20260810.tar.gz` (this directory).

## 5. Staged artifact

- `C:\Users\strid\Desktop\whest-submit\6_fold3cap_FIXED_a8cafbef.tar.gz`
  — copy of the new tar; staged-copy sha256 re-read and identical
  (A8CAFBEF…9151). No existing file in `whest-submit` was overwritten or
  modified; `0_kerdock*` untouched; `4_fold3cap.tar.gz` read-only accessed.

## Files touched by this rebuild

- `run_t3_gates.py` re-run → `t3_gate_results.json` (rewritten in place;
  wall_s-only deltas), `t3_gate_results_FROZEN_20260808.json` (new; frozen
  2026-08-08 bytes).
- `package_source/estimator.py` (fix hunk applied).
- `submission_fold3cap_n39936_FIXED_20260810.tar.gz` (new).
- `FOLD3CAP_REBUILD_20260810.md` (this file).
- Staged: `C:\Users\strid\Desktop\whest-submit\6_fold3cap_FIXED_a8cafbef.tar.gz`.

Not committed to git (left for the orchestrator's review). Submission and
nomination decisions are Jonah's.
