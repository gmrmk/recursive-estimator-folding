# V31-G4 grouped-call component: synthetic receipt

Status: **component synthetic PASS only**. GUARDS remains the campaign incumbent
and sole integrated artifact. This directory is not a submission package.

## What changed

The child preserves the parent analytical Winograd formula and frozen 4,096-row
leaf partition. It groups four adjacent leaf calls under one leading batch
axis, with the exact production grouping `4,4,4,3,1`; the final group is the
3,072-row remainder. Direct-dispatch arithmetic remains ungrouped. The setup
owns the full activation buffer and prebinds all group views so the hot path
does not reshape, stack, concatenate, pad, or materialize a broadcast RHS.

The intended effect is fewer participant-side FlopScope/NumPy wrapper calls,
not fewer billed arithmetic operations and not a guaranteed reduction in the
backend's internal GEMM count.

## Final sealed synthetic run

- Manifest: `PREEXECUTION_MANIFEST.json`, schema
  `v31-g4-preexecution-manifest-v7`, SHA-256
  `F1F04CCD5858BA3A1BC93851CCF64324B4DDA5F1E93A98BBB00CB2FB8722182C`.
- Hash census: all nine source/assets and all six fixtures match the manifest,
  both externally and inside the suite.
- Tests: 25 run, zero failures/errors/skips in both forward and reverse module
  order.
- NumPy fixture: word-exact parent/child equality across aliasing, nonaliasing,
  direct dispatch, even L1, odd-tail L1, `n<k`, `n=k`, `n>k`, and the full
  64,512-row production partition.
- Pinned FlopScope 0.10.0 fixture: word-exact equality and identical analytical
  charge on five deterministic hand-matrix cases. It loads a private module
  instance so the full suite is order-independent.
- Production-row pinned-FlopScope fixtures: word-exact equality and identical
  analytical charge at `(m,k,n)=(64512,256,256)` and
  `(64512,256,253)`. The even product bills `7,427,768,320`; the odd-tail
  product bills `7,345,191,168`. Both use the exact `4,4,4,3,1` partition and
  change sixteen parent core dispatches to five grouped core dispatches; the
  odd path separately preserves five pre-core tail dispatches.
- Frozen analytical bill: unchanged for every positive `(k,n)` in `1..256`.
- Call receipts at production geometry: direct `16`; even L1 `5`; odd L1
  `5` core plus `5` tail calls. The package's public
  `row_blocked_bill_identity` reports these child values; the byte-preserved
  parent helper is retained under `parent_row_blocked_bill_identity`.
- Declared grouped workspace: `63,438,848` bytes.
- Setup-only probes passed at width 256 and validator width 4, producing bound
  activation shapes `(64,512,256)` and `(64,512,4)` respectively. Every group
  passed executable exact row-coverage, sharing, shape, stride, nonoverlap, and
  in-place-list-alias assertions. Neither probe constructed an MLP or called
  `predict`.
- The inherited GUARDS wrapper executable AST is identical to the parent after
  removing documentation strings. Its child documentation now correctly says
  that three downstream source files change and that full-wrapper/guard parity
  remains unearned.

The v1 run is discarded because receipt semantics changed afterward. The v2
run is discarded because the combined suite exposed shared-module backend
contamination. V3 is discarded because it missed the public receipt helper,
recursive package surface, manifest self-check, and replayable setup fixture.
V4 is discarded because it did not bind the mandatory no-bytecode replay flag.
V5 is discarded because it retained false inherited-wrapper provenance and
did not execute the bound-group stride/nonoverlap contract. V6 is discarded
because its new production fixture passed in forward order but failed to import
in reverse order, exposing an unbound `sys.path` dependency. Only the post-seal
v7 runs above carry component credit. Both commands use
Python `-B`; the recursive package census confirms zero `__pycache__` or `.pyc`
files.

## Still required

No benchmark MLP, truth, scorer, held-out data, or hosted evaluator was touched.
Before this can become a candidate, it still needs official Phase-2 rule
binding, independent source review, setup-inclusive dynamic receipts,
whole-wrapper RSS/wall measurement, generated-network and guard-path parity,
package validation, and the normal promotion gates. Any numerical mismatch,
resource overrun, hidden setup charge, or absent residual-time score term kills
the child locally and leaves GUARDS unchanged.

The synthetic suite still does not earn full-estimator replay for `k=0` or
`n=0`, M186/M187 guard/branch parity, or numerical coverage of every dynamic
active-width transition. Those remain generated-network/full-wrapper gates.
