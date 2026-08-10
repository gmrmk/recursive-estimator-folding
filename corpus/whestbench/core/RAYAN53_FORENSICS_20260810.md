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
