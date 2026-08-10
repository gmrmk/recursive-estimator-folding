# rayan53 forensic decomposition — U6 settling check (2026-08-10)

Public-data-only competitive intelligence (leaderboard metadata + discourse
search). No account access, no private data, no firewall crossing. Purpose:
determine whether the sole re-grade-wave survivor is honest, and what it
tells us — NOT to co-opt its method (a compute-multiplier position is the
wall-tier accounting this corpus has refused from the start).

## The metadata (observed 2026-08-10 ~14:10 UTC)

Score law S = MSE * max(0.1, C/B), B = 2.72e11.

| entry | final-layer MSE | adjusted | implied C/B | implied FLOPs | last sub | entries |
|---|---|---|---|---|---|---|
| rayan53 #1 | 1.35e-8 | 1.5e-9 | 0.111 (~floor) | 3.0e10 | Aug 9 13:27 | 50 |
| joe_wanza #2 | 4.0e-9 | 2.11e-8 | 5.27 | 1.4e12 | Aug 6 00:30 | 1067 |
| ednacob | 9.11e-8 | 4.62e-8 | 0.507 | 1.4e11 | Aug 6 19:12 | 119 |
| us #326094 | 2.818e-7 | 1.832e-7 | 0.650 | 1.8e11 | — | — |

Discourse search for "rayan53": ZERO posts/topics/writeups.

## The decomposition (the reversed solve)

1. rayan53's rank-1 is a COMPUTE-MULTIPLIER position, not accuracy:
   joe_wanza has BETTER raw MSE (4.0e-9 vs 1.35e-8) and ranks below it
   purely because joe_wanza's compute was repriced to 5.27x budget while
   rayan53 sits at the 0.11 floor. The entire #1-vs-#2 gap is accounting.
2. rayan53's claimed 1.35e-8 at C/B 0.11 is ~180x past our PROVEN honest
   frontier: our exact-2-design sampler is near-optimal at ~2.8e-7 MSE /
   0.65 budget (proven this campaign), and no analytic closure beats
   9.6e-5 (measured). No method we characterized, sampling or analytic,
   crosses that gap honestly.
3. Circumstantial: entered Aug 9 (AFTER the Aug 3 accounting patch);
   every comparable-accuracy entry (joe_wanza, the old wall tier) was
   repriced to multiplier >> 1; NO writeup exists (a genuine
   180x-frontier method would need one for the Algorithmic prize and
   would be the competition's headline result).

## Verdict (U6)

rayan53 is, to a high confidence from public data, either (a) the last
un-repriced entry awaiting its turn in the ongoing re-grade wave, or
(b) a new hole in the patched (v0.10.0) cost meter. It is NOT a
reproducible honest method: honest raw accuracy in the 1e-9..1e-8 MSE
class demonstrably costs multiplier >> 1 (joe_wanza is the control), and
rayan53 alone claims that class near the compute floor. Level: derived
(from public metadata + our own optimality proof); the disambiguation
between (a) and (b) is the organizers' to make.

## What we take / refuse

REFUSE: co-opting the compute-multiplier position — this is exactly the
§5.2 metering-circumvention the corpus has never touched and the re-grade
is punishing. FIREWALL intact.

TAKE (intelligence): (1) the honest raw-MSE frontier is real and multiple
parties reach ~4e-9 at ~5x budget — the game above the honest band is
entirely compute-multiplier positioning, not accuracy; (2) the Sep 20-30
private re-run + manual validation is the winnow mechanism, and an
accounting position cannot survive fresh-seed re-execution under review;
(3) our correction-proof posture (zero measured bias, ~95% instrumented,
hostile-tested, artifact-backed writeup) is precisely the counter — we
are, by construction, the entry that cannot be winnowed. No action of
ours changes based on rayan53's fate before September.

---

# joe_wanza forensic decomposition (added 2026-08-10 ~14:30 UTC)

Public-data only. joe_wanza is a DIFFERENT failure mode than rayan53 and
the more instructive one for our posture.

## Profile
- raw final-layer MSE 4.0e-9 — BEST on the board (70x better than us,
  better than rayan53's 1.35e-8).
- adjusted 2.11e-8 -> multiplier 5.27 -> C = 1.43e12 = 5.27x budget
  (heavily compute-penalized; repriced in the wave, previous rank 1).
- 1067 entries — an order of magnitude more than anyone (ednacob 119,
  rayan53 50). No discourse writeup.

## Reversed technique
1067 submissions vs a 50-net PUBLIC suite = ~21 feedback cycles per net:
the signature of overfitting to the public seeds. Variance check: at
5.27x budget, honest sampling-scaling (MSE ~ 1/N) predicts ~5.3e-8, but
joe_wanza reports 4.0e-9 — ~13x better than scaling allows, a gap our
optimality proof says no honest estimator crosses but a thousand rounds
of public-leaderboard tuning manufactures by fitting the specific 50
nets. Level: derived (metadata + our scaling proof); the alternative
(a genuinely 13x-better estimator) would require a writeup that does not
exist.

## Verdict
joe_wanza is DOUBLE-exposed on the Sep private re-run: (a) the 5.27x
compute penalty follows identically to fresh seeds; (b) the overfit
component regresses when the seeds change. Likely September trajectory:
DOWNWARD. Not an accounting artifact (its compute is honestly metered
and penalized) — an over-budget, over-tuned honest estimator.

## Why this is the important reverse (posture validation)
joe_wanza is the CONTROL proving our thesis: the honest raw-MSE frontier
(~4e-9) is reachable, but only via 5x budget + heavy public-suite tuning
— exactly the two things a fresh-seed manual-validated re-run winnows.
Our champion is the negative: 0.65x budget (headroom, no penalty) + ZERO
fitted component (single Haar rotation, exact design, N8c-proven zero
bias — nothing tuned to public nets to regress). The C1 lesson (structured
estimators grade near local value) applies to us and NOT to joe_wanza,
whose local value is a public-seed mirage.

## Field synthesis
The top of the board decomposes cleanly: (1) ACCOUNTING positions
(rayan53, the re-graded wall tier) — winnowed by fresh-seed execution;
(2) OVERFIT/OVER-BUDGET positions (joe_wanza) — winnowed by fresh seeds
+ persistent compute penalty; (3) the HONEST band (ednacob 4.6e-8 etc.).
We sit at 1.83e-7, behind the honest band on the public board but
CORRECTION-PROOF by construction — the only class immune to BOTH winnow
mechanisms. The public rank understates our private-run standing relative
to categories (1) and (2); the question that decides prize money is how
DEEP the honest band runs and where the prize cutoffs fall (U9), not our
position vs the artifacts above us.

---

# ednacob orthogonal decomposition (added 2026-08-10 ~14:50 UTC)

The honest-band leader, reversed using OUR theorems as the coordinate
system. Profile: raw 9.11e-8 / adjusted 4.62e-8 / C/B 0.507 / 119 entries
(2.4 probes/net — light tuning, winnow-resistant) / last sub Aug 6 /
ZERO public trail (no corpus profile, no discourse posts).

## The decomposition

AXIS 1 (budget positioning): ELIMINATED — C/B 0.507 vs our 0.650, same
metered regime; adjusted is scale-invariant along the sampling curve.
The 4.62e-8 vs 1.83e-7 gap = a 3.96x variance-per-FLOP MECHANISM
advantage. Real, honest, survives the winnow.

AXIS 2 (better uniform sampling): EXCLUDED BY OUR PROOFS — uniform
design sampling of the homogeneous speckle field is certified
near-optimal in class (2-design exactness, N_eff 1-2% of independent,
dispersion no-gos, conditioning no-gos). ednacob cannot be a better us.

AXIS 3 (orthogonal candidates, ranked by our own measurements):
1. CROSS-NEURON COHERENCE EXPLOITATION (strongest): S7 measured the 256
   per-neuron targets at 0.975 coherence (~2 effective dof) — the one
   enormous structure we measured and never exploited. Shrinkage/pooling
   across coherent neurons is textbook Stein on exactly the per-neuron
   scored metric. Corpse in family: m79 (one specific James-Stein arm,
   killed); S7's coherence number is a NEW external fact about why the
   family could work — a legal reopen shape, NOT reopened here.
2. STRUCTURE-AWARE CONDITIONAL SAMPLING at strength (natasha-family,
   firing-rate stratification): removes value-explained variance, which
   is NOT excluded by S5's energy-homogeneity (different observable).
3. A certified hybrid with a working control outside our tangent class.

## Settling checks

(a) The Aug 17 writeup deadline is the flush: a silent 4x honest leader
    who wants the Algorithmic prize must publish within the week; the
    armed pre-Aug-17 discourse watch catches it. HOLD until then.
(b) Hypothesis 1 has a purely internal diagnostic: the Stein-gain upper
    bound from our committed per-neuron field data (candidate S14
    premise, cheap). Per the joint no-mutation verdict + the m79 corpse,
    this goes to Sol for review BEFORE any predeclaration. Proposed in
    channel; not launched.

## Posture

ednacob is the one competitor worth LEARNING from rather than refusing:
honest, efficient, winnow-resistant, and 4x ahead by mechanism. If its
writeup appears, it feeds Gen-6 legally; if hypothesis 1 is its engine,
the door was in our own measurements all along.

---

# ednacob hypothesis RE-RANKING after reading m79 (added 2026-08-10 ~15:05 UTC)

SELF-CORRECTION (attack-your-own-conclusion). I over-ranked hypothesis 1
before reading m79's specifics. m79_common_axis_output_shrinkage already
ran cross-neuron coherence in its strongest form (common-axis positive-
part James-Stein shrinker on the streamed 256-output mean, using
within-run contrast-variance statistics) and MEASURED it at 1.05x on
four whole networks (NO gain — slightly worse), with the decisive
diagnostic: optimal lambda ~ 0.0025 (~zero shrinkage) because true
per-neuron contrast energy is 328-401x the noise. The neurons have
genuinely different means -> nothing to pool toward; pooling injects bias
>> variance saved. m79's within-run contrast statistics already see
through S7's noise coherence. So hypothesis 1 is substantially
WEAKENED, and the proposed S14 Stein-bound diagnostic would mostly
re-derive m79 — I withdraw it as low-value.

RE-RANKED ednacob hypotheses:
1 (now leading). STRUCTURE-AWARE CONDITIONAL SAMPLING / firing-rate
   stratification (natasha family at strength). Our measurements do NOT
   exclude it: S5 tested energy-HOMOGENEITY, not value-STRATIFICATION;
   removing variance explained by a cheap firing-rate covariate is an
   orthogonal axis we never probed. This is the one door still standing
   after contact with the ledger.
2 (demoted). Cross-neuron coherence / shrinkage — measured-near-dead by
   m79 (1.05x, lambda~0.0025).
3. Certified hybrid with a working control outside our tangent class.

DISCIPLINE: even the leading hypothesis is Gen-6 MECHANISM territory =
Sol's blade + full predeclaration before anything runs; the joint
no-mutation verdict stands; nothing launched. The honest deliverable is
the corrected competitive read, not a new arm 2h before the flip.
