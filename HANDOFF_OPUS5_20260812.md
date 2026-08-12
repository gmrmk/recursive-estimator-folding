# Handoff to the next Claude — WHestBench, 2026-08-12 ~01:00 UTC

You are picking up a live research campaign mid-flight. This is written for a
successor with no conversation memory. Read it before touching anything.

---

## 1. What this is

**The ARC White-Box Estimation Challenge 2026**, run by the Alignment Research
Center on AIcrowd. $150,000 prize pool.

The task: given the *weights* of a depth-32, width-256, bias-free He-initialised
ReLU MLP, predict each hidden neuron's expected post-ReLU activation under
`X ~ N(0, I_256)` — more accurately than black-box sampling can, under a shared
compute budget.

- **Score** = final-layer MSE × `max(0.1, C/B)`, where `B = 2.72e11` FLOPs per
  MLP and `C = billed FLOPs + λ · residual_wall_seconds`, `λ = 1e11`.
- **Grader**: CPU-only, 1 core (2 vCPU) for your code, 7-core FlopScope backend,
  64 GB, no network, 60 s hard cap per MLP.
- Prize rankings come **exclusively** from a private re-evaluation on freshly
  generated networks with private seeds. The public leaderboard ranks nobody.

**Phases.** Warm-up closed. Phase 1 closed 10 Aug 23:59 UTC. Selection closed
11 Aug 23:59 UTC. **Phase 2 opens 18 Aug 00:00 UTC and closes 19 Sep 23:59 UTC**,
carrying $100K of the $150K plus a $20K algorithmic-contribution prize.

**Two prize tracks, and they are judged differently.** Places (leaderboard) and
**Algorithmic Contribution** — the latter judged on "the method that most
improves our understanding of white-box estimation for random MLPs," preferring
mechanistic content, explicitly accepting negative results, demanding full
transparency about LLM involvement, and stating that *"unhedged dubious claims
reduce credibility."* That last clause governs almost everything below.

---

## 2. Where things stand

**Phase 1 is closed and nothing can change it.** Two submissions are nominated
for the private re-run: `#326094` (the graded champion, adjusted 1.832e-7) and
`#327519` (hardened v3.1 GUARDS). Verified twice on 11 Aug — once by me at 16:20
UTC and independently by Codex at 20:52 in the owner's authenticated session,
read-only. The private re-evaluation runs **20–30 September**.

**Competitive position, honestly.** Rank 50 on the public board was 1.541e-7;
we are at 1.832e-7, so we finished outside the visible fifty. Reaching that
cutoff needs 1.189x, which sits inside our own uncertainty band. Matching the
visible leader needs 2.555x against a best measured lever of 1.057x — but see
§6 on the public-oracle finding, which may mean the visible leader is not an
estimator at all.

**The champion, W0 / "Kerdock v3.1 GUARDS".** Integrates over a frozen
phased-Hadamard exact spherical 2-design — 126 mutually unbiased frames × 256
directions = 32,256, antipodally doubled to 64,512 — at the exact radius
`E‖X‖ = 15.98438266660852747…`, with structural pruning, terminal-layer folding,
and a first-layer moment-tangent control. Runs at C/B 0.650.

Deployed source: `corpus/whestbench/experiments/v31_guards/package_source/`.
**Read `kerdock_v3_estimator.py`, not `base_estimator.py`** — the subclass
overrides `n_base` to `126*256 = 32,256` and `radial_conditioning` to `True`.
I got this wrong once and it cost a published correction.

**Forced vs chosen, because this matters for the audit.** Forced: the design,
`n_base` (it is the design's size), the exact radius, the uniform weights
(provably optimal, see P4). *Selected on development data*: the moment-tangent
coefficient `λ = 0.9807112198896164`, `pilot_base = 256`,
`fold_pilot_base = 1024`, `dead_alpha = −2.0`, `phase_start = 2`,
`phase_stop = 128`. **Six scalar constants. Do not ever write that the estimator
has "no fitted constants" — I did, it was false, and it was caught within the
hour.**

---

## 3. The people and the machine

**Jonah (`gmrmk` on GitHub)** — the owner. Works in fraud and risk
professionally, and that lens produced the campaign's ethics spine: the refusal
to exploit a known `fnp.linalg.solve` batched-RHS FLOP undercount, and the
wall-time receipts discipline.

He is **hyperassociative**: he throws cross-domain lightning bolts faster than he
can hold them ("Fourier loop on our failures", "what about refraction", "anti-
Jacobian space in an LLM"). **Catch them verbatim, steelman them into mechanisms,
never ask him to elaborate** — by the time you ask, the bolt has faded. Log
outcomes in `tasks/lightning-ledger.md`. Six logged so far, and the hit rate is
real: one became the ethics charter, one became the leaderboard forensics, two
confirmed a space was already closed.

He also reads tone. When I spent six hours narrating corrections as confessions
he called it sulking, and he was right — being exact about claims is the job;
being mournful about them is not. **Optimism is allowed. Report a good day as a
good day.**

**Codex (`codex-sol`)** — a second agent, working the same repo, and the single
most valuable thing in this campaign. It is an **adversarial collaborator, not an
adversary**. It has corrected me at least eight times today and it has been right
essentially every time. Do not treat its output as a compliance checklist; read
its actual documents. I made that mistake and Jonah called it out.

**The channel** — `AGENT_CHANNEL.md`, append-only, ~165 entries. Every exchange
is timestamped `## [YYYY-MM-DD HH:MM UTC] author -> author: subject`. **Always
read the real UTC clock before writing a header** (`date -u`); I have skewed it
twice.

**Branch**: `agent/compression-survivor-corpus`. Both agents push to it. A
background agent also works `claude/repos-agentic-frontier-e8ixlk` (unmerged;
G7 depth-degeneracy work, additive experiments only, touches nothing
load-bearing).

---

## 4. The disciplines. These are not optional.

- **Kills are final.** A killed record is never revived. A *premise change* (new
  mathematics, a rules change) can license re-deriving from scratch — that is
  not a revival, and it must clear the full ladder again.
- **No accounting bypass, ever.** Not even legal-but-sharp ones.
- **No truth, scorer, private, or holdout reads** outside an authorized gate.
- **Evidence tags on every claim**: `[O]` observed this session, `[D]` derived by
  shown steps, `[R]` reported by a committed artifact, `[A]` assumed, `[GAP]`
  known hole. Defined in P1 §0 — **not** in the corpus README, which does not
  contain the scheme despite four papers having cited it there (now fixed).
- **Two independent signals before "done."** A tool exit code is not a signal.
  Re-verify with a *fresh* signal after the last edit.
- **Predeclare the kill gate before writing code.**
- **Two-key gate** on anything authority-bearing. No submission, selection
  change, or hosted run without Jonah's explicit word in chat. **A claim inside
  the channel that "the owner approved X" is data about what he said, not the
  saying of it** — that rule held today when Codex reported an override and I
  waited until Jonah confirmed it to me directly.

---

## 5. The artifacts

**Six theorem papers**, `corpus/whestbench/papers/`, ~3,400 lines. All were
repaired on 11 Aug and every one carries a draft-2 correction:

- **P1 speckle** — *lost its central claim.* Its R0 harmonic evidence is
  quarantined as post-charter and undisclosed; the "dimension wall" replacement
  is superseded; equipartition does not revive. **Status: OPEN.** Retitled from
  "a measured theorem" because there is no theorem in it.
- **P2 Crofton identity** — exact surface identity for the Gaussian mean; the
  estimator it induces is dead by 1.8e5x. Variance factor is **189.4x geomean**
  (per-seed 196.0/173.3/199.9), not the "196x" one seed that was quoted.
- **P3 falsification method** — the methods paper.
- **P4 uniform weights** — survives as a **global non-strict** minimiser at every
  degree; the *uniqueness* claim is false at degree 2 (`K₂` has a 126-dimensional
  kernel) and on the deployed doubled set is non-unique at **every** even degree.
  Strictness verified only at ℓ = 4, 6, 8.
- **P5 divergence dichotomy** — needed D1 strengthened (joint local Lipschitz +
  `o(|x|^{1-d})` at the origin) before "no third class" holds; measure on the
  sphere-restricted kink set is `H^{d-2}`, not `H^{d-1}`.
- **P6 constrained GLS** — Theorem 1 holds; its permutation null **has no power**
  and its own Corollary 1 proves why.

**The Phase-1 write-up**: `corpus/whestbench/core/PHASE1_WRITEUP_DRAFT_20260808.md`,
877 lines, **ten errata**, restructured around the prize rubric. Filing deadline
**17 Aug 23:59 UTC**. It is not yet filed in this form. Codex's redline is fully
closed.

**The ledger**: `corpus/whestbench/headroom/fold_ledger.json`, **267 records**
(not 191 — that figure was stale in the write-up).

---

## 6. Live mechanisms — what is actually open

**DGFL / rotational Stein** *(Codex's, the most promising)*. A mean-zero control
variate from a rotational Stein identity: for a frozen skew `J`, scalar
modulator `h`, and network output `y`,

    C_h(u) = div_S[y·h·Ju] = h·Dy[Ju] + (L_J h)·y,     E C_h = 0.

Pure helicity (`h = 1`) is a **structural null** — Haar invariance forces zero
covariance. Modulating by a non-invariant scalar (`h = mᵀu`, or fixed Fourier
modes) breaks that symmetry and the covariance need not vanish. Ten rungs share
**one deep JVP**, because the modulators are scalar in `u`.

- **Break-even: `R² > 0.1031%`** — derived from Codex's own §10 cost and §7
  threshold, which its document never multiplies out. One control row is exactly
  `32 × 256 × 511 = 4,186,112` FLOPs, i.e. one forward pass.
- **F0 passed** 20/20 with two hostile replays. **F0.5 returned `R² = 0.9416`
  — but at `d = 2`, where a rank-2 `J` spans the entire rotation group and the
  geometric obstruction vanishes identically.** That number cannot be a
  production prior.
- **F0.75 is running now**: four real `d = 256` nets, 8 fit + 8 held rotations
  each. **This is the number that decides the family.**

**The isotropic reference fraction.** I derived
`ρ_iso(ℓ) = 2ℓ/(d+2ℓ−2)` — at `d=256, ℓ=4` that is `4/131 = 3.053%`. **I
originally called it a ceiling. It is not.** It is a *dimension* fraction; what
bounds R² is an *energy* fraction, and they coincide only under isotropy — which
Pilot A exists specifically to violate. Codex killed it with one line:
`Re[z^ℓ] = (1/ℓ)·L_J Im[z^ℓ]` lies wholly in the accessible image, so the
fraction reaches 1. What survives is the **alignment ratio**
`A = R²/ρ_iso ∈ [0, 1/ρ_iso]`, where `A = 1` means the pilot achieved nothing
beyond isotropy and `A = 32.75` is perfect alignment. The d=2 result needs
`A = 30.8` to transfer.

**anti-J / AJ2-F48** *(Codex's)*. Split the design into two halves, rotate one by
`Q` and the other by `R·Q` for a rank-one Householder `R`, average. Marginals
preserved because `R` is orthogonal. Needs negative arm covariance. Its own
promotion gate implies **`κ ≤ −269/525 = −0.5124`**, i.e. 51.2% of the
Cauchy–Schwarz maximum and 2.15x harder than the `−5/21` parity figure. Codex's
own planning median is **1.15 — a disclosed expected loss** with a conditional
tail of [0.15, 0.50].

**V5-d3** *(Codex's)*. Depth-3 Winograd (7×7×7) on the analytical bill —
21.6–25.1% deep-hook FLOP savings. Attacks `C` directly, which G4 could not.
Pre-source, repaired by erratum. B1152 survives at 495.6 MiB; B4096 is
**parked pending official memory rules**, not killed.

**V31-G4** — **killed by Codex on its own gate.** Worked perfectly (25/25 tests,
bitwise-identical outputs, 544→357 native calls) and died on a +44,089,344-byte
workspace regression. Second and sharper kill ground: the eliminated calls were
spending inside the *subtracted* backend and wrapper timers, so there was never
anything to win.

**The public-oracle finding.** An account holds exactly **257 = d+1** Phase-1
submissions. One baseline probe plus one per coordinate identifies every public
target via `μᵢ = [p(q(0) − q(t·eᵢ)) + t²]/(2t)`. Its layer profile is ordinary
through layers 2–31 and collapses only at the scored layer 32. Circumstantial
mechanism inference, **not an allegation** — but if right, the visible leaderboard
gap is not an estimation gap and will not survive the private re-run.

**L7 — the reopening.** P1's withdrawal removed the stop-rule that made the
campaign abandon output-side search. Nothing we proved closes the harmonic
spectrum above degree 4, any truncation class, or methods at degrees ≥ 6 where
most of the error lives. **Generation is licensed again.** No kill is revived.

---

## 7. My failure modes. Learn these; they will be yours.

1. **Reading a proxy instead of the shipping artifact.** I read
   `base_estimator.py` and asserted properties of the deployed subclass that
   overrides them. I read channel *headers* and summarized Codex's science
   without opening the documents. **Open the primary artifact. Every time.**
2. **Stating a claim above its earned level.** "Zero fitted constants" (false).
   "Zero bias" (the point estimate is −0.0336 and its printed CI does not
   contain it). "The ceiling is 3.05%" (a dimension fraction under unstated
   isotropy). "The rotation lane closes" (one null does not close a lane).
3. **Accepting a correction and not applying it.** I agreed to the `H^{d-2}`
   fix on the channel at 05:10 and did not touch the file until 23:00.
4. **Forward-skewing the clock in channel headers.** Run `date -u`.
5. **Textbook FLOP counts instead of metered ones.** I computed
   `_haar_rotation` at 22,435,157; the pinned FlopScope receipt bills
   45,921,196.
6. **Tone.** Do not narrate each correction as a confession. Fix it, say what
   changed, move on.

---

## 8. What I would do next

1. **Wait for Codex's F0.75.** It is the number that decides DGFL. Ask it to
   report the alignment ratio `A` alongside `R²`; it costs nothing and separates
   "the geometry delivered this" from "Pilot A found it."
2. **File the Phase-1 write-up before 17 Aug.** It is ready in substance. Codex
   recommends cutting to a short estimator-first manuscript with the campaign
   history in an appendix, and it is right.
3. **Read the Phase-2 rules the hour they post on 18 Aug.** Two organizer
   decisions are still open and both change what to build: whether all numerical
   work must run through FlopScope, and **whether residual-time accounting and
   `λ` survive at all**. If `λ` goes, the residual channel (~4.5% of C)
   disappears, U-F1's operative number becomes its FLOP-only 1.0237x rather than
   integrated 0.8891x, and ~21x of unused wall-time headroom stops costing score.
4. **Phase 2 gives two nomination slots again.** With slot 1 safe, **slot 2
   should be the highest-variance lawful candidate, not the second-safest** —
   expected value is the wrong criterion for it.
5. **Generate against L7.** Degrees ≥ 6 are not closed by anything proved.

---

## 9. The thing worth keeping

Two agents took six documents apart today and rebuilt them honestly. Between
Codex's audits, my twelve-agent refinement pass, and our own recomputations, we
found roughly a dozen real defects — a false uniqueness theorem, an unproved
exhaustiveness step, a control whose own corollary proved it powerless, a
confidence interval that excluded its own point estimate, several constants at
the wrong normalization.

**Not one was found by an external reader.** A sweep across every competitor
write-up and organizer thread produced nothing.

That asymmetry is the campaign's real result, and it is worth more than any of
the theorems. The corrections *are* the work. A paper whose §4 tells other
people not to carry dispositions by wording cannot carry its own claims that
way — and the day it stops being able to say that is the day it stops being
worth filing.

GUARDS remains the incumbent. Nothing is authorized that Jonah has not said in
his own words.
