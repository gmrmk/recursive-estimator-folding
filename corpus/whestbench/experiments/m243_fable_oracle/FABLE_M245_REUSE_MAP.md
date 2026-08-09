# Fable M245 reuse map — read-only planning, nothing launched (2026-08-10)

Per Sol's 23:25 directive: a mapping of which preserved M243-oracle pieces
adapt to the M245 canonical-unordered weighted-Galerkin spectrum lane, and
the smallest exact changes required. NO evidence, NO launches, NO resumes —
this file is planning only. Adaptation begins only after the final M245
authority documents and the immutable shard manifest are committed by Codex.

## Reusable as-is (no changes)

1. Hash-verification bootstrap: find-by-sha256 of the governing
   predeclaration + manifest before any read; hard-fail on absence;
   re-verify at every entry-point start. (Swap in the M245 hashes when
   Sol commits them.)
2. Checkpoint/resume engine: per-event durable checkpoints, safe resume
   across multiple wall-capped invocations — directly needed if M245
   shards run long like M243's would have.
3. Resource discipline: 5400 s wall-cap in-loop exits, RSS probe, typed
   refusals, run-transcript logging.
4. run_shard.py CLI shape (--shard {0..N}): re-parameterized to the M245
   shard map once the manifest defines it.
5. Receipt format: unedited durable receipts to Codex; no fable-side
   aggregation (Codex owns aggregation/adjudication — the M243 paired-
   bootstrap aggregator module is NOT carried over; receipts only).

## Requires replacement (the arm core)

6. The event-oracle computation core is fully replaced by the Galerkin
   spectrum core per the M245 predeclaration when frozen. Anticipated
   modules, pending Sol's exact definitions: (a) fresh strict-SPD event
   generation exactly as the manifest prescribes; (b) independent
   high-precision construction of r(g), b(g); (c) assembly of K, G_Q,
   d_Q and P_Q = d_Q^T G_Q^+ d_Q for Q = 0..8 (pseudo-inverse with an
   explicit rank/conditioning policy — I will implement whatever policy
   the predeclaration states and will NOT choose one silently);
   (d) the conditional iid replica-identity cross-check as an internal
   second signal; (e) the descriptive second-difference reporter for the
   geometric/logistic/Gompertz transformed ladders — REPORTING ONLY,
   with a structural guard that no extrapolation or tail certification
   is computable from the module's outputs.

## Firewall carried forward unchanged

No M243 candidate import; no M151 source arrays; no M178 provider claim;
no response/scorer/truth/sealed anything; M245 authority folder read-only
to me; writes confined to a new fable-side shard directory named in the
manifest.

## Smallest-change estimate

Bootstrap/checkpoint/CLI/receipts: reused verbatim (~70% of the harness).
Arm core: new, sized by the predeclaration's formulas (est. one focused
implementation pass + self-tests on synthetic fixtures, as before).
Standing by for the authority documents.
