# Organizer clarification questions — WHestBench / ARC White-Box Estimation Challenge 2026

Status: DRAFT deliverable for the participant (gmrmk) to send to the
organizers. Claude cannot send this; it is prepared for user dispatch. Each
question names the exact campaign decision its answer unblocks. Sources are
the preserved corpus (dated 2026-08-03) — every live rule must be confirmed
before operational action (resume prompt §1).

## Q1 — Compute-multiplier floor: 0.1 or 0.5? (HIGHEST PRIORITY)

The score law is `S = MSE * max(FLOOR, C/B)`, `B = 2.72e11`. Our v0.14
starter-kit / official materials record `FLOOR = 0.1`; live forum/prose we
collected records `FLOOR = 0.5`. Which is authoritative for Phase-II grading?

- **Unblocks:** the entire ceiling. At 0.1 the best-case adjusted score is ~5x
  lower than at 0.5; our #1 strategy (drive the multiplier to the floor) is
  only viable at 0.1. This single answer determines whether #1 is reachable or
  whether we optimize for a top-tier-but-not-#1 target.

## Q2 — Native / non-instrumented compute priced by wall time (Rules 5.2)

Section 5.2 permits calling "any other library, backend, language, executable,
or bundled file," with work outside FlopScope charged through residual wall
time (`C = billed_FLOPs + 1e11 * residual_seconds`). Public leaderboard
forensics show many top entries run the overwhelming majority of their
arithmetic outside the instrumented path (instrumented share <0.1%),
apparently priced only by wall time.

(a) Is running the estimator's core arithmetic through a native/compiled
backend, priced solely by residual wall time, a legitimate and intended use of
the scoring model — not a §5.5 circumvention?
(b) What disclosure do you require for such native computation (we intend a
full inclusive disclosure of which arithmetic is native and how it is priced)?
(c) Do you intend to patch FlopScope / the budget conversion (§5.3) in a way
that would retroactively re-price native-backend entries during Phase-II
grading or the final rerun?

- **Unblocks:** whether to DEPLOY the native-path matmul port (built and
  numerically certified, held pending this answer) or stay on the stricter
  instrumented boundary. We will not deploy native pricing until you confirm
  it is in-bounds.

## Q3 — Deadline reconciliation

Our collected materials show inconsistent dates: Phase-I submissions closed
2026-07-31; a Phase-I writeup deadline of 2026-08-07 23:59 UTC; a Phase-I
dossier deadline of 2026-08-10 23:59 UTC; and a Phase-II final-submission
window through 2026-09-19. Please confirm the authoritative Phase-II
submission deadline and the final-entry designation lock time.

- **Unblocks:** the campaign schedule and when the single final designation
  must be locked.

## Q4 — Prize-overlap eligibility

Can one team receive BOTH a Phase-II Best-Score prize (50k/20k/10k, fresh
private rerun of one designated submission) AND the Algorithmic-Contribution
prize (20k, PDF + one graded Phase-II submission ID) using the same estimator?
Our materials flag this as not explicitly guaranteed and needing written
confirmation.

- **Unblocks:** whether to structure one submission for both awards or split
  effort.

## Q5 — Submission cadence and the graded-baseline path

(a) Is there any per-day / per-week submission quota in Phase-II, or may we
submit freely and designate one final entry at the deadline?
(b) Is there an approved path to obtain a graded score on a fresh/held
evaluation split for a validated candidate short of the final designation? Our
local public rows 0..799 are exhausted for promotion, so we rely on official
grading as the only untouched evaluation channel.

- **Unblocks:** the submissions cadence plan and how descendants are validated
  against a real (non-burned) evaluation before final designation.

## Q6 — OSI source-release requirements

Prize eligibility requires OSI-approved source release. Please confirm the
required license set, the artifacts that must be released (estimator source,
generation/training code, disclosure statement), and the timing relative to
the final designation.

- **Unblocks:** the OSI release checklist so no candidate is bottlenecked at
  the deadline.

---

Honesty note (for our own submission, per rules): we use LLM assistance and
will disclose it; we do not read private targets, grader state, or truth; we
do not tamper with FlopScope or the grader; any native computation will be
fully disclosed and priced through residual wall time as the rules specify.
