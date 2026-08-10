# Gen-8 forum intelligence — public information crossed against our solve (2026-08-10)

Run wf_eecee1e3-477 (Opus-5 orchestrator, solo mode). 3 Sonnet deep-readers on
the six load-bearing topics; 4 Opus hybridizers each seeing the FULL 32-item
cached harvest plus the deep reads; Opus skeptics attacking survivors from our
own 258-record ledger.

**Headline: 9 proposals, 4 adversarially verified, 0 survived. The value is in
the reconciliations, not the proposals — including two defects in OUR record.**

Scope honesty: the verify phase was capped at 4 proposals by the orchestrator's
own agent budget, so **5 proposals were never adversarially tested** and are
recorded as untested, not as survivors. The 4 that were tested died on: a
re-presentation of Door B (ledger 226) without its committed corrections;
inflated gain arithmetic (~4x); and misread ledger state on the Winograd
lineage, which the record shows was already worked (exact_sampler_rectangular_
strassen -> preallocated_strassen_winograd -> integrated_batched_winograd, all
killed), not unexplored.

## 1. DEFECT IN OUR RECORD: M183's instrument is void (retract the evidence,
## keep the verdict)

M183 ("float32 hot-path recast — the free 2x") reported **f64 lane billing
0.00%**, and Gen-7's fidelity re-litigation used exactly that number to
"formally retire the dtype-repricing flag."

The detector is structurally incapable of reporting anything else.
`run_m183_falsifier.py:58` reads `dts = getattr(op, "dtypes", None) or ()`.
The installed flopscope 0.10.0 `OpRecord` dataclass has **no `dtypes` field**
— its fields are `count, cumulative, flop_cost, flopscope_backend_duration_s,
flopscope_context_start_offset_s, flopscope_overhead_duration_s, index,
namespace, op_name, resolved_dtype, shapes, subscripts`. The guard therefore
evaluates `any(...)` over an empty tuple for every op, on every program.

Two independent signals, both collected this session: (a) STRUCTURAL — the
dataclass field list above, read from the pinned venv; (b) EMPIRICAL — the
detector run against a deliberately 100%-float64 program (five 64x64 f64
matmuls) reports `f64_share 0.0`, while the corrected `resolved_dtype`
detector reports `1.0` on the same log.

**Disposition.** The VERDICT survives on independent evidence: the corrected
measurement puts the real f64 charge at 1.193e8 FLOPs (0.0755% of predict)
with a recast ceiling of 59,656,312 FLOPs — reproducing the Gen-7 cost-remap
attacker's independently derived 59.66M to the digit. So there is no material
f64 lane and M183's kill stands. What does NOT stand is the 0.00% figure and
any claim resting on it. The filed write-up's ledger table carries "0.00% f64-
lane billing — already clean"; the honest figure is 0.0755%, and the
conclusion (no material f64 lane) is unchanged. An erratum is available to
Jonah if he wants it; the substance of the filing is unaffected.

**Live hazard, now pinned.** dipam (18127, organizer) confirms all 24
`flopscope.stats` callables promote f32 -> f64 permanently, and that "a single
stats.norm.ppf call generating the sample matrix was enough to put all 32 hot
matmuls in float64" — a ~2x total-cost effect. Our champion makes
`stats.norm.pdf` x32 and `stats.norm.cdf` x32 calls per MLP. The corrected
measurement shows the promotion does NOT propagate into the matmul lane today,
so there is no current damage. But those 64 callsites are one refactor away
from moving a 145.138e9-FLOP matmul lane into the 2x rate, and v0.11.0 will
emit FlopscopeWarning at each. **Standing guard for any Phase-2 edit: an
explicit float32 cast at every stats callsite.**

## 2. THE RIVAL 5-DESIGN QUESTION: closed, in our favour, and we had already
## answered it ourselves

Topic 18145 (skye_nygaard, ~1.55e-7 public vs our 1.832e-7) publishes a fixed
spherical 5-design: 66,048 Kerdock-based directions, 8 Walsh-Hadamard passes.

- **Their strength claim is TRUE.** DGS for a spherical 5-design in d=256 is
  N >= 2*C(257,2) = 65,792; their 66,048 = d(d+2) sits 0.389% above it — a
  near-tight construction. The 129 real MUBs (128 Kerdock + coordinate) hit the
  Welch/frame-potential minimum exactly: sum |<x_i,x_j>|^4 = 33,024 + 16,512 =
  49,536 over N^2 gives 1/22,016 = 3/66,048 exactly.
- **We had already proved and priced it.** Our own S11 §2 verified the identical
  fact numerically on the frozen asset ("1.5 exactly (min=max)", Phi4/Welch =
  1.0000000000) and measured the completion worth **<= 0.176% against a 2.326%
  break-even** — i.e. the upgrade costs more than it returns.
- **Their own ablation agrees.** The posted write-up attributes their entire
  1.5412x gain to **arithmetic, not directions** ("entirely because the second
  technique is cheaper").
- **Their k^-1.21..1.24 exponent is confounded**, and our record contains the
  clean control: they measured the exponent while shrinking 129 -> 96/64/32,
  which destroys the design as it removes points. S11's point-count-matched
  control adds 3 RANDOM frames (+3.25% MSE) versus 3 COMPLETING frames (+3.42%)
  — statistically identical against a +2.38% cost. Their exponent > 1 is an
  artifact of the confound and does not license "buy more directions."
- **Their near-optimality ceiling strengthens our position**: Kerdock within
  0.0233% of optimal among positive-weight fixed rules, <= 6.29% even allowing
  negative weights. Corollary worth stating plainly: **nobody in the sub-1e-7
  tier is getting there by choosing better directions.**
- **Cost parity, so the gap is raw MSE**: their published post-Strassen budget
  is 64.27% against our C/B 65.01%. We are already at their cost efficiency.
  Their 2.2819e-7 raw is on 100 self-chosen dev nets versus our graded
  50-public+50-private; cross-suite raw comparisons carry no information at the
  10-20% level (C1 shows suite offsets reaching 1.65x).

## 3. DEFECT IN OUR EXPECTATIONS: C1's 1.65 ratio is a mean/median artifact,
## and the band is missing the anchor's own error

The pre-run hypothesis — that the forum's "public 50 are unusually easy" claim
(18141) was corroborated by our C1 local-vs-grader ratio of 1.65 — is **WRONG,
and the orchestrator (me) proposed it**. Recomputing the committed 22-net C1
panel: the LOCAL MEDIAN is 6.47355e-7 against the grader's printed 6.470e-7 —
a **0.05% match**. The 1.65 is a pure right-tail artifact of the mean. There is
no easiness shift to apply to the band.

What the band IS missing: S1b treats the hosted 1.830e-7 anchor as exact when
it is a 50-net measurement carrying a **9.83% standard error**. Folding the
anchor's own error in widens the honest 50-net fresh-seed band from
**[1.54e-7, 2.16e-7] to [1.46e-7, 2.25e-7]**, and raises P(private > 2.5e-7)
from 0.034% to **0.57% — a 17x increase**. Still small; no longer negligible.

## 4. Standing intelligence (no action, monitor)

- **18129 (organizer):** the `C_m > B_m` rule that should zero over-budget
  predictions was implemented in the local harness but **never wired into the
  production evaluator** — the mechanical explanation for over-budget entries
  holding real leaderboard scores.
- **18132 (organizer, mohanty):** the private re-evaluation **will audit
  instrumented share against telemetry** for prize-contending submissions,
  distinguishing legitimate control-flow optimization from metering
  circumvention. We are ~95.5% instrumented with zero fitted components.
- **18122 (organizer):** evaluation servers expose only flopscope-client with
  RemoteArray proxies — no `.base`, no local buffer — so unmetered compute via
  raw NumPy buffers is structurally impossible. Confirms the metering boundary.
- **18105:** a Lean-scaffolded, dipam-reproduced "unbiased budget-respecting
  floor" of ~3.7e-7 adjusted is **falsified by our own graded 1.832e-7** at bias
  share -0.034 with zero unmetered compute — we beat a public floor by 2.02x,
  for the reason dipam gives himself: it bounds pure Monte Carlo, and we are an
  exact design, not MC. Sharpest available paper citation for P1.
- **Rival replication of our kills** (for P1/P3): control-variate correlation
  decay with depth (18085) replicates our CV kill; the subspace/noise
  co-concentration finding (18097) replicates our information-gating results;
  structure-aware dead/on/kink pruning (18106) is an independent rediscovery of
  our pruning+folding.

## 5. Ethics boundary held

The `fnp.linalg.solve` batched-RHS undercount (18082) is a known billing bug
that charges one batch regardless of batch size. It was killed on sight as an
accounting exploit, regardless of its legality-in-rules. Bit-packing for a 32x
discount (18125) is policy-permitted but organizers flag heavy reliance as an
eligibility risk — declined. No proposal in this run depends on either.

## 6. What this run establishes

The public forum contains no mechanism that beats our estimator, and the one
rival who published our own family did so with a construction we had already
built, priced, and rejected on measured grounds — with their own ablation
agreeing that their advantage is arithmetic, not directions. What the forum DID
produce is two corrections to our own record: a structurally void measurement
instrument (M183) and a mis-attributed calibration ratio (C1), both now
recorded with their evidence. That asymmetry — external attack finds nothing,
internal audit finds real defects — is the same result the Gen-7 adversarial
campaign produced, and it is the strongest available argument that the record
is honest.
