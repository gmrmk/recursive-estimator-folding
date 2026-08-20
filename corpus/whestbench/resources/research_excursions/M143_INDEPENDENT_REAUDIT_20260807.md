# M143 independent hostile re-audit -- 2026-08-07

## Decision: REPAIR -- do not authorize the development response screen

M143's repaired algebra, proposal law, static cost arithmetic, manifest-bound
runtime code, and pre-outcome tests are sound.  This audit did **not** run a
response, efficacy, contest, scorer, truth, leaderboard, submission, champion,
or confirmation outcome.  It did execute only compilation, static JSON/hash
checks, the 16 named algebra/protocol test functions, and a deliberate
no-authorization denial check.

The frozen runner nevertheless has two material authorization/firewall gaps.
They mean the stated “exactly one” development screen and the stated hashed,
passing-development prerequisite for confirmation are not enforced by the
implementation.  These require repair and a new manifest/re-audit before root
may authorize any response screen.

## What independently passes

### Algebra, index contract, and invariance

The implemented recurrence is the repaired one:

```text
G[r] = p[r]^2 o E[r+1]
E[r] = (W[r]^2) @ G[r]
tau[r] = s[r] sqrt(E[r]).
```

`diagonal_path_energies` applies the gate after `W[r]` (source lines 117--125).
The direct helper names and requires `gated_downstream_energy` (129--156), and
the direct-vs-cached test passes.  The sign-scrambled claim is appropriately
limited to its diagonally integrated Rademacher path sketch; it does not claim
the full coherent M121/M125 response.

The three-map simultaneous gauge/permutation test passes, including proposal
probabilities with permuted bridges.  The source scale is the specified
Gaussian ReLU standard deviation and fails closed for nonpositive/nonfinite
variance (184--212).  This supports the explicit composite attribution:
M143 is `s_i sqrt(E_i)`, `scale_only` is `s_i ||W_i||`, and the original M133
arm remains `||W_i||`.

### Proposal law, zeros, and HH scope

`make_output_aware_proposal` passes `tau` without a hidden floor (250--284).
For ordered distinct triples its inherited M133 `Factored211Proposal` computes
the stated three-term `h`, adds exactly 5% uniform rescue, and returns exact
uniform when its structured normalizer is zero.  The zero-strength and
all-zero tests pass.  The immutable deep-copy proposal snapshot is read-only,
is digested before draws, and is rechecked after every draw.

M133's parent implementation hash matches its manifest pin.  Its sampled
scale is `Delta/(2*K*q)` (M133 lines 544--550), so the exact unbiasedness claim
is valid **conditional on the frozen full-support proposal** and the retained
left/right singleton symmetry of `Delta` and the feature.  It is not an
unconditional claim over an adaptive proposal, nor a claim for a weight
tangent.  M143 correctly prohibits the latter.

### Runner gates, RNG, M131 failure, and non-outcome firewall

The runner constructs all three layer proposals before `exact_defect_table`
(301--355).  HH streams use explicit PCG64DXSM child keys containing split,
family, width, cell seed, method, repetition, layer, and purpose
(146--150, 375--378); method codes differ, so no cross-method common random
numbers are used.  Bootstrap streams use distinct scope codes.

An M131 paired-quadrature certificate disagreement raises `ArithmeticError`
(268--280).  `run_split` catches this per cell, records the no-retry/no-family-
removal disposition, and makes `protocol_complete` false, which makes both
gates false (479--490, 585--610).  This is the required failure behavior.

Both primary and attribution gates are enforced as pooled **and** separately
for exactly the two frozen families.  The bootstrap threshold is strict and
the width condition is included (440--463); tests exercise a failing family,
incomplete protocol, equal-upper-bound failure, and adverse width trend.

Without an authorization file, the runner stops at `authorize` before creating
an output.  The re-audit denial check exited 1 with `PermissionError` and
verified no result file was created.

### Manifest, compilation, tests, and cost crosswalk

All three JSON documents parse.  Every one of the seven
`execution_artifact_hashes` in the manifest equals the current SHA-256:
the M143 module, runner, and M120/M125/M126/M129/M131/M133 dependencies.
The five M143 Python sources compile with `py_compile`.

All 16 pre-outcome free-function tests pass when directly invoked (the
available Python environment did not contain pytest).  The tests import only
the proposal/runner and do not call `build_cell` or `run_split`.

The cost arithmetic is internally consistent:

```text
94,940,940,240 - 121,896,960 + ceil(1.25 * 67,900,646)
= 94,903,919,088.
```

The stored trace JSON binds that billed number and declares float32.  The
current environment lacks FlopScope, so this audit did not rerun the structural
trace; that limitation is not a response outcome.  The trace remains a
structural proposal-only crosswalk, not an integrated target-estimator
measurement, as the proposal correctly says.

## Required repairs

1. **Confirmation prerequisite is forgeable.**  `authorize("confirmation")`
   verifies only that an authorization-supplied file hashes to an
   authorization-supplied digest, has `split == "development"`, and contains
   two literal `true` fields (runner 172--181).  It does not require that file
   to bind the current M143 manifest hash, runner hash, candidate, frozen
   CONFIG, or complete two-family result.  A root authorization can therefore
   point to a hand-written JSON asserting both gates.  Require at least
   `candidate == "M143"`, exact current manifest/runner hashes, and a
   configuration/family-completeness check before accepting the result; bind
   the expected development output path/hash in the separate confirmation
   authorization.

2. **“Exactly one” development screen is not enforced.**  A valid development
   authorization can be reused with any number of fresh `--output` paths.
   The no-overwrite check only protects an already used path (621--633), not
   authorization reuse.  Bind an expected canonical output path and a unique
   authorization identifier to the development authorization, then record and
   reject a consumed identifier (or otherwise use an immutable root-controlled
   authorization ledger).  Do not count an administrative instruction alone as
   machine enforcement.

After those repairs, update the manifest hashes and rerun this independent
pre-execution audit.  Root may then authorize one and only one frozen
development screen.  Even then it will establish only generated proposal-
variance evidence for this composite and not an integrated target estimator,
confirmation result, contest evaluation, champion replacement, or submission.

## Evidence hashes at re-audit

| artifact | SHA-256 |
|---|---|
| pre-theory | `4b28b6c07b488fa1f58acd5166ee1853da37b58c8849647f916b2cac4deb9c76` |
| prior independent audit | `3e0b451a34341e2fc11e94ae1a23cedb15d8a11c51b56c74c8525f09df531c50` |
| manifest | `4c612e8c1bd4f893ce0cb2d4e4026753cb508d97eea77adf60bf157179d5a7ac` |
| M143 module | `5dab449d9ceff7099e04f4521415e781592e6eec260636dd4e81688c9dc6d9bb` |
| M143 runner | `8c410bf2511e8f41d15aff48124d2dac7131b14df2b388e750574fe7e4a2c520` |
| proposal algebra tests | `e81cb683b61876f69efcdbc9ccd3d07ae090dc35f9d6a3c9a9bf342256b46b5d` |
| protocol tests | `f48f4b7e998501282900881919400c09398aacbbf6cdbe1b55f4b67239faf4c2` |
| trace script | `5e43d90af6d519e7deef29ba242ab53eb6f4ecfbd1d6a9c491495acc778e9a52` |
| stored structural trace | `1e63e4520863d368363a2d6c5c3b0f84f8438ba2aaa07202c9b5812ae0ade341` |
| cost crosswalk | `24a28714a8d1735ae0cf4261c5cc3a2d37fc3c17e8084fb13cd0722c623e7617` |
