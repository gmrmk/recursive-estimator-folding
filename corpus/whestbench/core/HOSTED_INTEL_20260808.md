# Hosted intel (2026-08-08, browser session): five campaign assumptions corrected

Read first-hand from the live AIcrowd site with the user's signed-in browser.
All OBSERVED unless labeled. This supersedes the dossier where it conflicts.

## 1. WE ARE IN PHASE 1, NOT PHASE 2 — and it closes in days, not weeks

Site header: "WARM-UP ROUND: COMPLETED · PHASE 1: LIVE · PHASE 2: UPCOMING".
Prize split: **$50K Phase 1 + $100K Phase 2** (the dossier treated the whole
$150K as Phase 2). Phase 2 closes Sep 19; Phase 1's own close is the Aug-3
organizer extension (Aug 10) — i.e. THE ACTIVE DEADLINE IS ~2 DAYS AWAY, not
Sep 12/19. Every "latest-safe date" in the dossier was computed for the wrong
phase.

## 2. Our team HAS a graded entry, and it is weak

Submission **#318609** (account **jonah_butterbaugh**, Phase 1, 15 days old):
**GRADED**, adjusted **5.47e-7**, final-layer MSE 1.81e-6, 50/50 public MLPs,
**0 failures**, mean effective compute 8.24e10 = **30.3% of budget**, ~1.0 s
wall/MLP. Versus the hosted Monte-Carlo baseline (6.47e-7) that is only
**1.2x better than sampling**. The corpus's "still grading after 14400s" log
line was stale — it graded fine. The runbook's "#318609 check" step is closed.

## 3. Grading is fast and the feedback is RICH (the D-PM red team's attack 1
is refuted)

Public score posts **within ~6 minutes**. Every submission page exposes, per
MLP: adjusted score, final-layer MSE, all-layer MSE, **billed FLOPs**, **wall
time**, a time breakdown, budget utilization, headroom, IQR, best/worst MLP,
and per-layer MSE heatmaps. The dossier's "degraded-mode branch" (adjusted
score only) is unnecessary — we get the full compute ledger, so the hosted
residual-scale k that gates the L1-vs-L2 decision is DIRECTLY MEASURABLE from
two graded runs.

## 4. The arbitrage is confirmed from the grader's own telemetry

Rank-2 **ely2sh #326033** (adjusted 4.96e-10): per-MLP **wall 36,484-46,618
ms** (36-47 s!) with **budget used 8.75%** and mean effective compute 2.38e10.
At the documented residual rate (1e11 FLOP-equiv/s), 40 s alone = 4e12 = 14.7x
the entire 2.72e11 budget — so the wall is being charged at ~zero. Their
all-layers MSE is **0.7537** (vs our 4.79e-5): they compute only the scored
layer and let every other layer go to garbage. Honest entries run ~1 s/MLP.
This is the accounting channel, now verified from primary per-MLP data rather
than forum reports — and it stays off-limits (ledger legality invariant; the
organizers are reviewing it).

## 5. Two corrections in our favour

- **Designation slots: TWO.** Official facts panel: "Fresh private rerun of
  each team's **up to two nominated submissions, per phase**." The one-vs-two
  conflict is resolved; plan for two.
- **Memory risk was overstated.** Grader has **64 GB**; the campaign's
  512-MiB gate was self-imposed. Kerdock v3's "1.445 MiB margin" worry is
  moot at the hosted level.
- Quota confirmed: **50 entries/team/UTC day, each phase**; today's page
  showed "50 remaining today".
- Upload path: the Create Submission page takes a **drag-and-drop .tar.gz
  (<= 50 MB, <= 50 files)** — "The tarball `whest package` produced is exactly
  what this page accepts." All five of our tars qualify (largest 33.3 MB).

## What this changes, concretely

The honest field on the hosted suite currently grades ~8.6e-8 to 2.4e-7
adjusted. Our best local candidate (Kerdock v3, local descriptive 1.62e-7)
would, if it transfers, improve our team's standing from 5.47e-7 by ~3.4x and
land mid-field — a real Phase-1 position, established with ~2 days left, at
zero risk to the Phase-2 program. The submission queue in the dossier is
unchanged in order but now URGENT and cheap (6-minute feedback, 50/day).

Blocked: the agent cannot execute the upload (the permission classifier gates
every submission-adjacent action, and credentials are out of scope in any
case). The user performs the upload; everything else is prepared.
