# Gen-8 fold ladder: the recursion ladder, the perturbation ladder, and where
# the width-transfer gate actually belongs (2026-08-10)

## Ultrathink verdict, stated first

The parallel session's width-transfer gate is **the right instinct in the wrong
shape**, and adopting it verbatim would leave us exposed to the same disease on
axes it does not cover.

Its diagnosis is correct and important: *our promotion ladder changes regime
between rungs, and nothing tests the regime change.* Screens run at widths 3, 4
and 64 because they are cheap; production is width 256. Two measured laws change
qualitatively across that gap (trace-share dilution 88.4% at n=4 -> 3.02% at
n=256; PSD loss 0/22 replicates at width >= 96 reaching depth 32 vs 21/32 at
widths 32-56, Spearman rho = -0.743), which predicts a "passed the screen, died
at production" signature.

But width is **one axis of one ladder**. Today alone produced two failures of
exactly the same disease on other axes, neither of which a width gate would
have caught:

- **M183** — the *instrument* was in a different regime from its claim. Its
  detector read an attribute (`op.dtypes`) that does not exist on flopscope's
  `OpRecord`, so it returned a structural zero on every program. No width
  requirement touches that.
- **C1** — the *statistic* was in a different regime from its use. A mean was
  read as a difficulty ratio on a right-skewed panel whose median matches the
  grader to 0.05%. No width requirement touches that either.

So the correct Gen-8 construction is **not** "add a width gate." It is: build
the general transfer ladder, make width its first rung because that is where the
measured evidence is strongest, and make crossing the ladder a promotion
condition. That subsumes the proposed gate and covers the two failures it misses.

## Ladder R — the RECURSION ladder (escalating cost of inquiry)

Answers *"is this true?"*. **Stop at the first rung that RESOLVES.** Escalate
only on inconclusive. This is our existing resolution/promotion discipline with
one rung inserted (R3) whose absence is the defect the parallel session found.

| rung | what it is | cost | resolves when |
|---|---|---|---|
| R0 | ARITHMETIC — closed form, or arithmetic on numbers already committed | minutes, no compute | the answer falls out of algebra (e.g. DGS bounds, break-even) |
| R1 | CACHED — recompute from committed artifacts, no new truth generation | minutes | committed data already contains the answer (e.g. re-reading a kill record) |
| R2 | SCREEN — new measurement at screen scale (small width, few nets) | ~CPU-hour | the effect is absent or overwhelming at screen scale |
| **R3** | **TRANSFER — the same measurement at >= 2 scales spanning the production gap** | 2-3x R2 | the effect's scale-dependence is established, not assumed |
| R4 | PRODUCTION — full width, full suite, pinned seed, CRN, twice-run determinism | hours | the effect survives at the real operating point |
| R5 | ADVERSARIAL — independent agents mandated to refute the surviving claim | fleet | majority fails to break it |
| R6 | OWNER GATE — irreversible, outward-facing, or a genuine scope fork | Jonah | he decides |

R3 is the new rung. **The width-transfer gate is exactly the rule "you may not
skip R3 on the way to promotion."**

## Ladder P — the PERTURBATION ladder (escalating stress on a surviving claim)

Answers *"where does this stop being true?"*. **Stop at the first rung that
BREAKS it — that rung IS the answer**, because it names the claim's domain of
validity. Rungs are ordered by how often each has actually broken something in
our 261-record history.

| rung | perturbation | what it has broken in our record |
|---|---|---|
| P0 | SEED — re-run under a different seed, CRN-paired | sampling artifacts; the Gen-7 SVD-V null needed this to be readable |
| **P1** | **WIDTH — n = 4 / 32 / 64 / 128 / 256** | **trace-share dilution, PSD loss (the parallel session's finding); six suspected corpses** |
| P2 | DEPTH — L = 4 / 8 / 16 / 32 | closure accumulation; the 0.87/layer transmission law |
| P3 | DTYPE / COST — f32 vs f64, v0.10.0 pricing, stats-promotion contagion | billing regime, not mathematics; the live 64-callsite hazard |
| P4 | SUITE — different net families, difficulty strata, public vs private | every decision-layer claim; C1's mean/median artifact lives here |
| P5 | INSTRUMENT — can the measuring code return a null/zero regardless of truth? | **M183** (structural zero); the highest-yield rung and the one we had no gate for |
| P6 | ADVERSARY — an agent whose only mandate is to refute | 9 of 9 Gen-8 proposals; 20 of 20 Gen-7 attacks |

## Compare and contrast

They are orthogonal, and the confusion between them is what let both of today's
defects through.

| | Ladder R (recursion) | Ladder P (perturbation) |
|---|---|---|
| Question | is it true? | where does it stop being true? |
| Direction | escalating **cost of inquiry** | escalating **severity of stress** |
| Stopping rule | stop when RESOLVED (cheapest sufficient rung) | stop when BROKEN (the breaking rung is the result) |
| A "pass" means | the claim is established at that evidence level | the claim survived to that rung — and its boundary is the next one |
| Cost profile | most questions stop early; cheap by design | a claim that never breaks costs the **full** ladder |
| Characteristic failure | stopping too early on a cheap signal that happens to be wrong | perturbing the wrong axis, yielding **false robustness** |
| Output | a verdict with an earned evidence level | a boundary condition attached to the claim |
| Existing instances | the fold promotion ladder (premise -> screen -> dev -> final -> deploy); the resolution ladder; headroom-recursion tiers | the A4 hostile-inputs battery; the S-series falsifiers; the Gen-7 attacker lenses |

Three contrasts worth stating explicitly:

1. **R is exhaustible; P is not.** R terminates when the question is answered.
   P has no natural end — you can always invent another perturbation — so P
   needs a *declared* rung list and an honest statement of which rungs were not
   run. An unstated P rung is exactly how "false robustness" enters.
2. **R's rungs are ordered by cost; P's must be ordered by measured yield.**
   Ordering P by intuition is what produced a width-only proposal: width is
   genuinely rung 1 by evidence, but P5 (instrument) outranks P2-P4 on today's
   data and nobody had it on a list at all.
3. **They compose asymmetrically.** R gets you a claim. P gets you the claim's
   domain. **A promotion needs both**, and the specific gap the parallel session
   found is a claim resolved at R2 that was never given a P1 boundary. M183 is
   the mirror image: a claim resolved at R2 that was never given a P5 boundary.

## The Gen-8 promotion rule (what actually changes)

**Revised after the gen8_gate_audit (see §"Audit result" below) — the width
formulation is withdrawn and replaced.** A candidate may not be promoted unless
**all four** hold:

1. **R-sufficiency** — resolved at the rung its stakes require, and the rung is
   named in the record. (Existing practice, now explicit.)
2. **R3 crossed on the mechanism's OWN declared sensitivity axis** — the
   load-bearing statistic measured at >= 2 points along whichever axis the
   mechanism's effect is claimed to depend on, with the extrapolation to the
   production point reported as an interval and gated on its *unfavourable* end.
   The axis must be declared in the predeclaration, before measurement. Width is
   one such axis; the audit found the historical corpses died on width, **depth,
   angular/gate aliasing, and effect-size-at-screen**, so fixing the axis to
   width in advance is both under- and over-inclusive. Where the axis genuinely
   is width, the parallel session's own non-monotonicity at 64 -> 72 means >= 3
   points or a rank statistic, not a two-point line.
3. **Evidence at production shape, and the instrument-validity gate.** Clause 2
   does not replace measuring at the real operating point; the corpus already
   does that, just too late to prevent wasted production runs. And — new, from
   the audit — **no detector may produce a promotion-bearing or kill-bearing
   null unless it fired on a positive fixture in the same run.** M183 is the
   proof of need; the antidote already exists in our own corpus at
   `m217_.../run_m217_native_trace.py:119`, which uses `int(matmul.get("calls",
   -1))` — a loud sentinel — instead of a falsy default.
4. **Unrun P rungs declared** — the record names which perturbations were not
   attempted. Silence is not robustness.

Kills remain final. Nothing here reopens a killed record; it raises the bar for
*promotion*, which is the direction that has cost us.

## The uncertainty inventory, assigned to rungs

Everything live, with the cheapest rung that could settle it. This is the
feedstock for both ladders.

### Adjudications only the owner can make (R6)
- **U-M1** Does cmd2's `setUpClass ... ERROR` consume the M245 one-shot, or is it
  an interruption artifact? *Codex's protocol call, or Jonah's.* Blocks the lane.
- **U-M2** Are cmd3/cmd4 still legal to run? *Depends entirely on U-M1.*
- **U-I2** If any structurally-void instrument is cited in the **filed** write-up,
  does an erratum go to the organizers? *Outward-facing — Jonah's alone.*
- **U-X1** Does the parallel branch (`claude/repos-agentic-frontier-e8ixlk`,
  shares history at 102bd7c) merge into ours? *Scope fork.*
- **U-E3** Phase-2 rules — will all numerical work be required through flopscope?
  *External; determines what the exact-control components are worth.*

### Settleable at R1 (cached — cheap, do these first)
- **U-M3** ~~Was cmd2's ERROR environmental or a genuine contract failure?~~
  **RESOLVED AT R1 this session, and it is worth reading as the ladder working.**
  The ERROR is REAL, not a kill artifact: it is printed at line 7 of `cmd2.err`
  and tests continue passing at lines 8-16, so it occurred during normal
  execution well before the process died. Its locus is
  `TestM245ReplicaGatesAndSchema.setUpClass` (test file lines 568-587), which
  calls `replica.run_replica_event(...)` once per entry in `PRECISIONS_DPS` —
  i.e. **live mpmath quadrature at multiple precisions**, not a structural or
  contract check. That is precisely the class reviewer B flagged and could not
  statically resolve ("~22 methods classified bounded numeric-runtime-risk
  inherent to live quadrature"). The specific traceback is **unrecoverable from
  the artifact**: unittest defers tracebacks to an end-of-run summary that was
  never written, so the cause cannot be identified without a re-run — which the
  one-shot protocol forbids. Net: a genuine runtime error, in a risk class that
  was predicted and accepted before the run, with an unrecoverable cause. That
  is the honest input to U-M1; the disposition remains Codex's or Jonah's.
- **U-W1** Are the six corpses genuinely width-caused? *Audit running.*
- **U-W3** Which of our 261 records are width-exposed? *Audit running.*
- **U-I1** How many other detectors share the M183 structural-zero defect?
  *Audit running — the highest-yield item on this list.*
- **U-X2** Does the SPD width finding change our `gm_m179_m199` disposition?
  *It confirms it; verify the record's wording matches the stronger evidence.*
- **U-P3** `gm_m116_streams` — the BLOCKED_ESCALATE obstruction is named in the
  run-all journal; read it and decide if it is cheaply removable.

### Settleable at R0/R2 (arithmetic or one screen)
- **U-W2** Is a 2-width requirement sufficient given the 64 -> 72
  non-monotonicity? *Arithmetic on the parallel session's own 96-cell data.*
- **U-W4** Does trace-share dilution have a closed form (88.4%@n4 -> 3.02%@n256)?
  *Science value; would turn P1 from empirical into predictive.*
- **U-P2** `gm_residual_k1` — the x5-convention re-derivation is
  INCONCLUSIVE_HOLD and needs a cleaner second signal.
- **U-P4** Is the `out=` buffer lever a real residual saving on our path? *R2,
  then R4 for the adjusted-score number.*
- **U-E1** Does the fresh-seed band need further correction beyond the anchor SE
  (now [1.46e-7, 2.25e-7])?

### Perturbation-ladder feedstock (claims that survive but have no boundary)
- **U-G2 (P3)** Can any Phase-2 refactor push the stats f64 promotion into the
  145.138e9-FLOP matmul lane? *64 callsites; dipam says one call suffices.*
- **U-G3 (P1/P4)** Is the corrected 0.0755% f64 charge stable across nets and
  widths, or is it a width-256 point measurement?
- **U-P1 (P1)** `gm_rankone_bill`'s f32 parity self-declares width-256-specific —
  **this is the new gate's first real customer**; it may not promote until
  measured at >= 2 widths.
- **U-G1 (P6)** Five of nine Gen-8 proposals were never adversarially verified.
- **U-E2 (P4)** Does the private suite differ in difficulty *distribution*
  (18141's claim) and not merely in seeds? *C1's median match argues no; the
  forum argues yes; unresolved and it moves our expectations.*
- **U-E4 (P5-adjacent)** What exactly will the private re-evaluation's
  instrumented-share audit measure? *Determines whether our 95.5% is measured
  the way we think it is.*

## Audit result — the six-corpse premise is substantially WITHDRAWN

`experiments/gen8_gate_audit/` (Opus, independent, ledger pinned at sha
`60c9c72a…`). As promised above, the document says so:

**Only 1 of the 6 corpses is width-caused.** `weight_identified_latent_factor`
alone shows the claimed signature (screened at widths 4/8/16, died at 32/64).
Four of the remaining five had **no width transition at all** — screen width 64
and kill width 64 — and the decisive mechanical fact is that `aggregate.wins`
and `aggregate.ratio` are two fields of *one* artifact over *one* eight-case
bank with every case at width 64; width 256 appears only under
`cost_accounting`, a projected bill rather than a measurement. The fifth died on
**depth** (layer 0 at 8/8 versus layers 8/14/16/30 at 3/16). Collateral: only 3
of the 6 actually carry the "8/8 screen" signature, and "no kill condition names
256" rests on just 5 of 223 records naming any width at all. The corpses died on
width, depth, aliasing, and effect-size-at-screen — a mixed set. **A width-only
gate was post-hoc pattern-matching on it**, which is why clause 2 above is now
written against each mechanism's own declared axis.

**The gate as originally worded would have punished our best records.** 14
records fail a >= 2-width clause, and **10 fail it while measured AT 256** —
including the promoted `row_blocked_winograd_production` and our only
`validated` record, `v31_guards_m186_m187`. A rule that fails artifacts for
being measured only at the true operating point is mis-specified, not merely
weak. Genuine non-256 exposure is 8 of 60 promotion-eligible records
(`conditional_corr_spectrum`, `conditional_residual_cumulant_spectrum`,
`conditional_residual_covariance_algebra`, `cumulant_polynomial_quotient`,
`m86_boundary_laplace_coarea`, `m126_repeated_output_source_contraction`,
`m198_source211_delay_one_adapter`, `m200_streaming_overlap_fixture`).

**Correction to my own claim of an hour ago:** `gm_rankone_bill` is *not* the
gate's first customer. It is pinned at n=256 / layers=31 and passes both
clauses. `gm_c1_bound`, `gm_u3_grid` and `gm_u9_s4_d2` carry no width parameter,
so the gate is inapplicable to them (`gm_u3_grid`'s "48" was flagged and is a
false positive — it is the rotation-pool size).

**The M183 defect class is a class of one, and the instrument behind the width
proposal is sound.** Of 8 shape-matched detectors, 7 were cleared by an explicit
firing check against positive fixtures — including `gm_m179_m199`, the very
record that licenses this whole line of work. M183 is the sole confirmed void,
and it carries a *second* dead name at line 62 (`op.name`; the field is
`op_name`), masked by the first. It is cited twice in the **filed** write-up:
line 129 in the ledger table, and — load-bearing — **line 422, where it retires
the dtype-repricing escape**. That citation is the open item, and it is U-I2:
an outward-facing erratum decision belonging to Jonah alone.

What survives unchanged: the two-ladder structure, the R3 rung, and the
measured SPD width evidence itself (0/22 replicates at width >= 96 reaching
depth 32; Spearman -0.743), which was never in question. What changed is the
gate's specification and its justification.
