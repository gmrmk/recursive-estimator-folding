# Campaign judgment — 2026-08-07 (adversarial five-judge panel + synthesis)

Status: response-free strategic judgment. No sealed cell, truth, scorer, or
leaderboard was read. This document revises the campaign THESIS; it kills no
mutation and changes no champion. Evidence: five independent adversarial
judges (closure-bias, M179 circularity, resource-arm value, thesis
reachability, process/firewall), each with quoted-line/computation evidence;
full panel output preserved in the session task log.

## Verdicts

| Facet | Verdict | Core finding |
|---|---|---|
| Closure-bias ceiling | **FATAL** (8/10) | The exact Gaussian closure M179 completes caps at 8.76e-7 raw — 2.84x WORSE than the champion; 94.6% of its residual is k3/k4 content the closure structurally cannot hold (Gaussian has k3=k4=0); terminal k3/k4 is theorem-obstructed (M137) and empirically dead (0.493% gain; ARC closure worsens with depth, graded 9.97e-7 externally). "Closure-as-estimator at 4.7e-8" is not a route. |
| M179 math/tests | SOUND (8/10) | G1/G2 passes are real: independently reproduced via raw Monte Carlo and finite differences; references genuinely bypass M178; limits disclosed, not hidden. |
| Resource arm | FLAWED (7/10) | A1 proved classic-Strassen exactness (variant-independent, not the billed 0.944); A1/A3 is ~1.8% strict-path insurance that A2 would moot; A2 (the only big lever) is organizer-blocked and floor-contingent; the levers are substitutes, not complements. |
| Thesis reachability | FLAWED (8/10) | Honest P(#1) ~2-5%. The 9.2e-9/7.39e-9 bar is a Phase-I PUBLIC-HALF artifact (11/12 leaders at <0.1% instrumented share, "final-row-only/placeholder" fingerprint) that may not survive the fresh Phase-II rerun. Demonstrated native re-pricing is 4.44x, not the ~7x the floor needs: multiplier lands ~0.157, and 4.7e-8 x 0.157 = 7.4e-9 TIES the visible leader at best. |
| Process/firewall | SOUND (8/10) | Predeclare-before-code, one-mutation gates, and component-vs-efficacy labeling all verify; both gates re-passed fresh. One hardening: the m86 read was proximity-safe self-discipline, not a hard partition — the design math is now fully re-derived inside the firewalled tests, so no future read of the sealed-adjacent tree is needed. |

## Synthesis (the judgment)

1. **The craft stands; the headline falls.** M178 and M179 G0-G2 are correct,
   verified, honest machinery — and the specific #1 thesis "science arm =
   Gram-Charlier closure family reaching 4.7e-8, times multiplier at the 0.1
   floor, beats 9.2e-9" is FALSIFIED as stated, on three independent grounds:
   the closure-as-estimator ceiling (8.76e-7 > champion), the floor arithmetic
   (4.44x demonstrated vs 6.98x needed), and the bar itself (a public-half
   artifact measured on a different suite than Phase-II grades).

2. **The science chain survives under its ORIGINAL purpose, not the plan's.**
   The corpus never designed the M125b/M163/M172 chain as
   "ship-the-closure"; it designed it as an exact CONTROL VARIATE for the
   sampling champion: deterministic control c with known expectation, sampled
   residual (Delta - c) — a bad control costs variance, never bias, and a
   control needs only a known expectation, which sidesteps both the closure
   ceiling and (partly) the M137 identifiability wall. M179's producer is the
   prerequisite for exactly that chain (M176 archive -> Source211 conversion
   -> M175 trace -> the frozen M172 source-variance gate). Its payoff is
   UNPROVEN and sits behind the M172 gate with predeclared thresholds
   (upper-90 < 0.25); the honest label is "live, gated, uncertain" — not
   dead, and not 4.7e-8.

3. **Revised campaign objectives (in order):**
   a. **Best honest Phase-II score**: champion (2.12e-7 adjusted) is the
      deployable baseline; the control-variate chain is the only live route
      to a material MSE cut; the accounting arm (if organizers bless native
      pricing) multiplies whatever MSE stands by up to ~4.4x — magnitude now
      stated from the demonstrated 4.44x, not the aspirational floor.
   b. **The USD 20k Algorithmic Contribution prize**: the corpus itself
      designates this the clean fallback; the certified-provider line
      (M178 + M179) is exactly PDF-able contribution material regardless of
      Best-Score outcome.
   c. **Rank claims: none** until organizer answers (floor 0.1 vs 0.5,
      native-pricing stance, regrade intentions) and a graded baseline
      exist. The visible board is not a valid target.

4. **Resource re-prioritization:** stop polishing A1/A3 (~2% substitute
   lever); hold A2 built-but-undeployed pending the organizer answer; the
   organizer packet is now the campaign's single highest-leverage unsent
   artifact.

5. **Loop re-aim:** Track B continues (M179 G3-G5, then the chain) under the
   control-variate label; Track A pauses except A2-prep; every future report
   states objective (a)/(b) language, never #1-product arithmetic.

## Preserved tissue from the falsified thesis

The two-arm compounding OBSERVATION remains true arithmetic (multiplier and
MSE multiply); what died is the claimed reachability of each arm's endpoint.
The organizer questions, the A2 port design, the M179 producer, and the
judgment evidence above are all retained assets.

## Deepened synthesis (Fable direct, ultrathink redo, 2026-08-07)

I re-derived the panel's FATAL independently rather than adopt it, and it holds
— but the deeper reading sharpens both the one binding constraint and the one
genuinely creative move the panel underpriced.

**The unavoidable constraint, stated exactly.** The board leaders already sit
at or near the multiplier floor: joe_wanza is adjusted 7.39e-9 at raw MSE
5.21e-8 (multiplier 0.142), SKIBIDI is 9.2e-9 at raw 9.24e-8 (multiplier
0.0996). So the multiplier arm, driven to its own 0.1 floor, can at best MATCH
their compute efficiency; it cannot pass them. Passing them requires lower raw
MSE. To beat joe_wanza at the 0.1 floor needs MSE < 7.39e-8; the champion is
3.089e-7, a **4.18x cut**; beating at his own 0.142 needs a 5.85x cut. This is
independent of the multiplier and independent of native pricing. **#1 = a
4-to-6x raw-MSE reduction, full stop** — the multiplier only decides whether
you arrive at the leaders' altitude or below it, never whether you clear them.

**The creative move the plan gestured at but never sharpened — the floor
frees compute.** Below C/B = 0.1 (C <= 27.2B) the multiplier is clamped, so
every FLOP under that line is SCORE-FREE. If native re-pricing (Rules 5.2,
wall-time-billed) runs the champion's 184.8B matmul fast enough to sit under
the floor, the slack between the sampling wall-cost and 27.2B is a FREE
analytic budget for an expensive control variate that cuts MSE. This is the
real compounding: the accounting arm does not merely multiply the MSE arm, it
FUNDS it. That reframes the whole campaign — the corpus killed cheap analytic
controls on cost, but a control that is free under the floor changes the
cost side of every one of those kills.

**Why it is still a long shot, quantified honestly.** The free budget depends
on native throughput, and the only demonstrated number is itsjustmarsel's
4.44x (one CPU, one 4096-matmul). At 4.44x the champion sampling costs
184.8B/4.44 = 41.6B wall-equivalent — still ABOVE the 27.2B floor, so there is
no free budget and the floor is not even reached. The frame needs native
throughput ~7x+ (unmeasured; ~1 TFLOP/s sustained on 16 AVX cores makes it
plausible but unproven), at which sampling costs ~18B and ~9-70B is freed for
a control. And the corpus has not found a control that delivers 4-6x MSE in
any budget: the exact k3/k4 SIMPLE recurrence is 290B, terminal k3/k4 gave
0.493%, and M137 caps a four-moment control's irreducible residual at the
0.211-wide identifiability interval. So the binding open problem is precise:
**a control variate that cuts raw MSE 4-6x within a ~10-70B native budget** —
neither found nor proven impossible.

**Revised probability and objective — my number, not the panel's.** P(#1)
~3-8%, gated on that one control-variate breakthrough times a favorable floor
ruling times native throughput above the demonstrated point. That is a real
long shot, not a plan. The reachable, high-probability targets are unchanged:
best honest top-tier Phase-II score, and the $20k Algorithmic Contribution
prize (the M178/M179 certified-provider line is the paper). **The single most
decision-relevant unknown is native throughput on the grading hardware** — it
sets whether the floor and the free budget exist at all — and it is empirically
answerable the moment a graded baseline submission runs. That, not more local
gates, is the highest-information next step; it is user-gated (submission).

## Ultrathink 2 (after the N1-N4 measurements): #1 is engineering; retire Track A

Three measured/derived facts turn the model into an actionable plan.

1. **Under wall pricing, FLOP count is irrelevant — only wall-clock time is.**
   Strassen/Winograd (Track A) trades multiplications for additions; both cost
   CPU cycles, so it does NOTHING for wall time. It optimized the INSTRUMENTED
   regime (its 5.99% is already banked in the champion) and is the WRONG
   optimization for the wall-priced regime any #1 run must use. **Retire Track A
   (A1/A3): the resource lever is a fast wall-clock kernel, not fewer FLOPs.**

2. **v is effectively pinned at the champion's ~0.0199.** N4 measured the cheap
   geometric levers and killed them (radial NULL, confirming the champion's
   disabled setting; antipodal already in the champion). The champion's 2x over
   plain is Sobol-Owen QMC + the q3 weight polynomial; the corpus says the exact
   controls beyond that give only marginal further v reduction (M137
   non-identifiability; terminal k3 0.493%; RB marginals ~6e-8). So the #1 win
   does NOT come from the variance lever; v ~ 0.0199 is the working constant.

3. **Therefore #1 is an engineering problem: S ~= 24x.** With v pinned,
   adjusted 7.39e-9 = 0.0199 * 8.74e-6 / S -> S ~= 24x this laptop's numpy.
   S = grading-hardware (16 vCPU AVX-512 ~ 8x this ~4-core AVX2 laptop) times a
   native fused-forward kernel avoiding numpy's 32-sequential-call and
   intermediate-allocation overhead (~1.5-3x) ~= 12-24x. Top-6 (S ~ 9x) is
   comfortable; #1 (24x) is the optimistic end. **The grading box is the SAME
   for every competitor** — the leaders' edge over our numpy baseline is their
   native KERNEL, not exotic hardware or math; sitting at 7.39e-9 they prove
   ~24x is achievable there. The win is: bundle a fast native fused-forward
   kernel (Rules 5.2-legal precompiled artifact) and run the champion-family
   sampler through it at ~382k samples under the floor budget.

Consequences:
- PRIMARY #1 effort = the native fused-forward kernel (S-lever): standard MLP
  inference engineering (fused 32-layer f32 forward, ~8 MB cache-blocked
  weights, threaded over 16 vCPU), bundled precompiled per 5.2.
- M178/M179 exact-control chain DEMOTED from "the #1 v-lever" to "marginal v +
  the $20k Algorithmic Contribution paper" — completed for the paper, not
  relied on for #1.
- Track A (Winograd) RETIRED.
- **Organizer Q2 (native-pricing legality + regrade intent, Rules 5.3) is now
  BLOCKING**: the entire #1 strategy is the native wall-priced kernel, and if
  the organizer patches that channel (the <0.1%-instrumented-share gap they
  flagged "under clarification") it dies. Do not build the kernel before that
  answer. Q1 (floor 0.1 vs 0.5) still sets the ceiling.
- The graded baseline submission remains the highest-information action — now
  doubly, since it also reveals whether native wall-pricing is honored.

Bottom line, sharper in mechanism: **top-tier is an engineering deliverable
(the native kernel), #1 is that same deliverable at the optimistic end of
grading-hardware throughput, and the whole strategy is contingent on the
organizer honoring Rules 5.2 wall-pricing — the one answer to get before
building.**
