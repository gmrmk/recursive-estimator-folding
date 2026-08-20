# T4 predeclaration — Kerdock M71 v3 descriptive re-score (NEW protocol)

Date: 2026-08-08 (before the run). Task T4 of the reset plan.

## Standing of the old gate (unchanged)

The original single-use descriptive gate
(kerdock_l1_owned_buffer_production/PREDECLARED_DESCRIPTIVE_GATE.md) is
BURNED: its one permitted launch failed before process creation (PowerShell
Start-Process env-map duplicate-key collision, 'Path' vs 'PATH';
LAUNCH_FAILURE_ADJUDICATION.md), and its own text forbids any rerun under
that gate. That disposition is not relabeled. This is a NEW, separately
predeclared protocol, as the adjudication itself says a later benchmark
requires.

## Mechanism

Execute the FROZEN v3 candidate entrypoint
(work/scorefloor_generation/kerdock_l1_owned_buffer/
candidate_source_validator_v3/estimator.py — untouched; the packaged tar
b55a1d8d…30af is not modified) exactly once under the pinned v0.14 runner
with the same frozen argv the burned gate declared:

    whest run --estimator <v3 estimator.py> --dataset work/whest-full
      --split full --n-mlps 100 --runner subprocess --seed 0
      --flop-budget 272000000000 --detail full --format json

Launcher fix: direct shell invocation with stream redirection (no
Start-Process, no constructed environment map) — the failure mechanism of the
burned gate cannot occur.

## Status of the result (predeclared, non-negotiable)

DESCRIPTIVE ONLY. Public indices 0..99 are burned by prior score-bearing
development (ledger invariant: "any further local public read is descriptive
only"). Whatever number this produces:
- confers NO validation, NO promotion eligibility, NO winner representation;
- informs exactly one thing: whether the Kerdock lottery ticket enters the
  graded-submission queue at user-return (it already validates as a package),
  and with what expected standing relative to L1/L2/fold3cap.

## Prediction

Genuinely unknown — this candidate has never produced a score. Wide prior.
The run is expected to complete (package/contract gates passed 2026-08-06)
in roughly 13-30 minutes wall.

## Outcome recording (all outcomes are reportable; none is retried)

- Completes, 0 failed MLPs, finite: record adjusted/raw/mean-C as descriptive.
- Completes with failures/budget breaches: record the failure breakdown —
  that IS the result.
- Launcher or runner fails: record first-broken-link with full diagnostics.
  No second attempt under this protocol.

## Resources / firewall

One run, single subprocess protocol, pinned env, PYTHONIOENCODING=utf-8.
No sealed cells, no truth/scorer reads, no submission, frozen sources and
tars untouched (hash-checked before and after).
