# Codex ultraplan — the work program from 2026-08-11 (written by opus-5, acting /root)

Companion to `CODEX_HANDOFF_20260810.md` (state) — this file is the *program*.
Read the handoff first for the mathematics; read this for what to do with it.

## The frame that reorders everything

**Your work has zero effect on Phase 1 and full effect on Phase 2.**

- Phase-1 selection is LOCKED and reload-verified: #326094 + #327519. It cannot
  be changed and it will not be revisited.
- The Algorithmic Contribution write-up is FILED on both channels (private PDF
  to arc-whestbench@aicrowd.com against #326094, verified in Sent; public
  tact-scoped companion at Discourse topic 18147).
- Prize rankings come **exclusively** from the private re-evaluation of those two
  nominated entries on fresh seeds, Sep 20-30.

Therefore: no result you produce can move Phase-1 Best Score, and the only
Phase-1 lever left is *integrity* (the erratum question, below). Everything else
you do pays into **Phase 2, which opens 18 August 2026 00:00 UTC** — seven days
out — and into the science.

This is a de-escalation, and it is deliberate. The M245 one-shot adjudication
felt urgent at the baton because the flip was hours away. The flip has happened.
Nothing is racing. **Do the careful thing, not the fast thing.**

## Ordering principle

Rank by (probability the answer changes what we build) x (magnitude if it does)
/ (cost to find out). Under that metric the order below is not the order of
intellectual interest — it is the order of expected value, and the first item is
first precisely because it is cheap.

---

## PHASE A — ungated, start immediately, no dependencies

### A1. U-F1: the Strassen/Winograd question, settled at R0 arithmetic (HIGHEST EV)

**Why first.** It targets the 98.87% of the bill that is matmul (145.138e9 of
146.794e9 instrumented FLOPs). It is the one place a rival has publicly
demonstrated a *measured* gain (skye_nygaard, topic 18145, 1.5412x, MIT-licensed,
their own ablation attributing it "entirely because the second technique is
cheaper"). Our kill of `preallocated_strassen_winograd` was on a **wall-time
ratio gate** (measured 1.559 / 1.546 / 1.701 against a frozen 1.5), with the kill
text naming "one-core half-width BLAS plus Winograd memory traffic, not
allocation." And the metric bills FLOPs, not wall-time.

**The contested point, stated fairly.** Our Gen-8 cubature agent argued the
organizers have since invalidated whole-wall gating. Our Gen-8 skeptic killed the
reopening on inflated arithmetic (~4x) and on misreading the lineage state
(`exact_sampler_rectangular_strassen` -> `preallocated_strassen_winograd` ->
`integrated_batched_winograd`, all killed, i.e. worked rather than unexplored).
**Our own record disagrees with itself.** That is an uncertainty, not a
reopening, and it is yours because it is exact accounting arithmetic.

**The task, R0, no code, no compute.** Derive the FLOP-only accounting for
Strassen-Winograd at recursion depth d on the production shape
(64,512 x 256) @ (256 x 256), under flopscope v0.10.0 pricing — which now bills
data movement (copy/fill/concat at 1/element, gather/sort at 4/element), so the
additions and the temporaries that Strassen trades for multiplications are
**no longer free**. That repricing is the crux: classical Strassen wins on
multiplies and loses on adds and memory traffic, and v0.10.0 moved the second
term from zero to billed. Produce the charged ratio per depth d = 0..5 including
the movement term, and state the depth (if any) at which the FLOP-only bill
strictly decreases.

**Gates.** If the FLOP-only bill does not strictly decrease at any depth, U-F1
closes permanently and the wall-time dispute becomes moot — write that verdict
and the family is finished. If it does decrease, that is **still not a
reopening**: it becomes a predeclared Phase-2 candidate that must then cross R3
on its declared sensitivity axis (recursion depth, not width) and carry the
instrument-validity gate. Do not write kernel code on the strength of A1 alone.

### A2. The line-422 question — does the write-up's claim survive M183's retraction?

`M183`'s detector is a confirmed structural zero (`getattr(op, "dtypes", None) or
()` against an `OpRecord` that has no `dtypes` field; it also carries a second
masked dead name, `op.name` where the field is `op_name`, at line 62). It is
cited twice in the **filed** write-up: line 129 in the ledger table, and
load-bearing at **line 422**, where it retires the dtype-repricing escape.

The conclusion appears to survive on independent evidence — the corrected charge
is 1.193e8 FLOPs (0.0755% of predict) with a recast ceiling of 59,656,312 FLOPs,
reproducing the Gen-7 cost-remap attacker's independently derived 59.66M to the
digit. **Verify that independently.** You are the exact-control specialist and
this is a billing claim in a filed document. Confirm or refute that line 422's
assertion stands without M183, and say which.

Note the **live hazard** attached: organizer dipam confirms (topic 18127) that
all 24 `flopscope.stats` callables promote f32 -> f64 permanently, and that one
such call can move all 32 hot matmuls into the 2x lane. Our champion makes
`norm.pdf` x32 and `norm.cdf` x32 per MLP. They do not propagate today. Before
any Phase-2 edit of yours, pin an explicit float32 cast at all 64 callsites.

### A3. R3 retrofit on the 8 genuinely exposed records

The `gen8_gate_audit` identified 8 of 60 promotion-eligible records measured
off-production-shape: `conditional_corr_spectrum` (n16),
`conditional_residual_cumulant_spectrum` (n8/16),
`conditional_residual_covariance_algebra` (n8/12/16),
`cumulant_polynomial_quotient` (n8/16), `m86_boundary_laplace_coarea` (w2/3/4),
`m126_repeated_output_source_contraction` (n64),
`m198_source211_delay_one_adapter` (w2-7), `m200_streaming_overlap_fixture`
(w4/7). Under the revised promotion rule each needs its **declared sensitivity
axis** named and two points on it, or an explicit statement that the gate is
inapplicable. Cheap, improves the record, good work to interleave while gated
items wait.

---

## PHASE B — gated on YOUR adjudication, not on time

### B1. The cmd2 disposition (yours or Jonah's alone)

The facts, neutrally (full detail in the handoff's M245 section): cmd1
`test_m245_primary_core.py` **PASSED** — "Ran 31 tests in 554.267s / OK", exit 0,
10:37:07.8232896Z -> 10:46:23.3277048Z. cmd2 `test_m245_replica_core.py` printed
`setUpClass (TestM245ReplicaGatesAndSchema) ... ERROR` at log line 7 while tests
continued passing at lines 8-16, then the session was killed mid-test. No
traceback exists anywhere in the artifact because unittest defers tracebacks to
an end-of-run summary that never ran. The erroring `setUpClass` (test lines
568-587) calls `replica.run_replica_event(...)` once per `PRECISIONS_DPS` entry —
**live mpmath quadrature**, not a contract or schema check — which is precisely
the class your reviewer B classified in advance as "~22 methods, bounded
numeric-runtime-risk inherent to live quadrature."

**The question is yours: does that ERROR consume the one-shot?** I have not
rerun anything and will not. I offer no recommendation, because the protocol is
yours and the erratum chain is yours. What I will say is that nothing is racing:
Phase 1 is closed, so you may take the time to decide correctly.

### B2. If the one-shot survives: complete GREEN (cmd2-4) and answer the open lane

The seed-side question — whether the coefficient geometry any seed-side
estimator would need exists at all — is the **only formally open lane in the
entire campaign**. Twenty adversarial agents failed to find an output-side
mechanism; the one seed-side construction we could build (SVD-V rotation) measured
a clean null at paired t = +0.19 with bit-identical determinism. M245 is the
remaining probe. Its answer is scientifically decisive **either way** and feeds
paper P1 directly. Two-key gate unchanged: acting-root's committed GO with exact
bindings plus Jonah's explicit word.

### B3. If it does not survive: write the closure

A permanent stop is a result, not a failure. Write what the static closure
established (seven blockers repaired, six hashes frozen, two independent PASS
verdicts, three real numerical compat defects found and fixed with their
arguments) and what remains unmeasured. That document is a genuine contribution
to P1 regardless of whether the science ran.

---

## PHASE C — gated on 18 August

### C1. Read the Phase-2 rules the hour they post

The undecided question the organizers named is whether **all numerical work must
run through flopscope**. That single answer determines whether the N8b native
lever reopens and what your entire exact-control component library is worth. Do
not build before reading it.

### C2. Then, and only then, decide what to build

Inputs you will have by then: A1's FLOP-only verdict, the M245 answer, the
Phase-2 rules, and the four REVIVED_SCREENED items from the graveyard run
(`gm_rankone_bill` — f32 parity discharged, pinned n=256/layers=31, passes the
new gate; `gm_c1_bound`; `gm_u3_grid`; `gm_u9_s4_d2`). Also live:
`gm_residual_k1` (INCONCLUSIVE_HOLD — the x5 hostile-residual convention,
refuted by hosted k ~ 1.0, whose confirmation would un-kill five of **your own**
exact-control records) and `gm_m116_streams` (BLOCKED_ESCALATE, obstruction named
in the run-all journal).

---

## Standing constraints (non-negotiable)

- Kills are final. 264 ledger records. Nothing here reopens a killed record; the
  revised gate raises the bar on *promotion* only.
- No submissions, uploads, or logins without Jonah's explicit word. Blind .env
  key pattern only; the value is never read or displayed.
- No truth / scorer / private / holdout reads. The Sep 20-30 private re-run is
  the untouched holdout and is never exposed to mutation generation.
- Every mutation predeclared before code: mechanism, prediction on record, kill
  gate with exact numbers, declared sensitivity axis.
- Every measurement seeded: pinned seed, common random numbers, noise floor
  measured first, twice-run bit-identical determinism. No promotion without it.
- **New:** no detector may produce a promotion-bearing or kill-bearing null
  unless it fired on a positive fixture in the same run.
- Ethics over rules-legality: we do not exploit metering bugs. The
  `fnp.linalg.solve` batched-RHS undercount (topic 18082) is killed on sight.
- /root reclaims by your own append-only channel entry, any time.

## What I would not spend your time on

Reopening output-side estimator families (20 adversarial agents, 264 records,
and the speckle theorem all say the same thing); chasing the rival's 5-design
(adjudicated closed — their claim is true, we had already priced it at <=0.176%
against a 2.326% break-even, and their own ablation credits arithmetic not
directions); design perturbation (M180, +20-49% variance, breaks exactness); or
any wall-time channel (the metric bills FLOPs).
