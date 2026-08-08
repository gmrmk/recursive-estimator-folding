# Headroom-Recursion — Generation 3 packet (2026-08-08)

Per the recursive-estimator-folding skill's packet specification. Generation 2
was the tangent lineage's offline run (outputs/headroom-offline-generation2-
result.json); Generation 3 recurses on the CURRENT champion with the hosted
grading as its score distribution. The validation ladder remains external and
authoritative; this packet generates proposals only.

## 1. Champion hash and score distribution

- Champion: Kerdock M71 v3, tar sha256
  `b55a1d8d5bcab8fb1dcfc68ee76c0ddfc2680b42e57778ab69ad866ba1c030af`
  (33,344,900 B), LIVE as hosted submission **#326094**.
- Hosted score distribution (50 public MLPs, the real evaluator):
  mean adjusted **1.832e-7**, IQR [1.05e-7, 2.26e-7], min 5.42e-8
  (patricia-hawkins), max 5.96e-7 (patricia-neal), 0/50 failures; final-layer
  MSE mean 2.818e-7; mean effective compute 1.79e11 (65.9% of B); wall
  4.6-6.8 s/MLP; 100/100 including sealed half COMPLETED. Full per-MLP table:
  experiments/a_series_granular_adversarial/a1_hosted_ledger.json.
- Local descriptive anchor: adjusted 1.619e-7 on burned public 0..99
  (T4), paired ratio 0.770 vs L2, 0.763 vs L1.

## 2. Evaluator / version hashes and budget margin

- whestbench 0.14.0 / flopscope 0.10.0 (post Aug-3 repricing);
  whest.exe sha256 `888a44d9c886df88cf8933398c154e113f530f3dc2705282170820a101dd674a`.
- Budget B = 2.72e11; champion mean utilization 65.9% => **34% headroom**;
  hosted wall margin ~10x under the 60 s cap; residual exposure ~5% of B.
- Score law floor = 0.1 (observed from leaderboard arithmetic).

## 3. Promoted / killed / unresolved

- PROMOTED (the winners feeding this generation): the phased-Hadamard
  126-frame spherical design under one shared Haar rotation (measured
  2.0-3.2x over conditioned MC; locally optimal per M180); exact radial
  conditioning (homogeneity); pilot-rescued structural pruning; dead/on/kink
  3-terminal-layer folding; frozen first-layer moment-tangent lambda
  0.9807112198896164; zero measured final-layer bias (N8c, M181 Arm-0
  anchor, homogeneity argument — three independent signals); full-f32 billed
  hot path (M183); T3-style deterministic budget capping (available, not in
  v3); the certified M178/M179 exact bivariate machinery (as CERTIFICATES
  and paper material — dead as estimator components at all four insertion
  points).
- KILLED (constraints on this generation — do not re-propose these forms):
  N4 cheap variance levers; N5 multilevel closure CV; N6 great-circle RB;
  N7 RQMC rate (constant 1.5-2.7x only, and only vs unconditioned iid);
  N8a lattice-vs-frames (frames dominate); N8b native backend (0.94x at one
  core); N8c offline corrector (no bias to learn); N9 tangent-on-frames
  (+2.1%, frames absorb the residual) and deeper folding (v3 already L3);
  M180 design perturbations (local optimality); M181 terminal smoothing
  (terminal law non-Gaussian; bias 4-6x baseline MSE); M183 f32 recast
  (already clean); M184 mid-layer exact composition (0.00%, structural).
- UNRESOLVED (in flight, verdicts pending): M185 tail-pruning mechanism
  (A1 signature: hosted per-net MC difficulty CONSTANT at 1.1x spread while
  our score spreads 11x; over-pruning + analytic-accuracy correlates);
  A3 kill-heterogeneity re-audit (4 pre-registered suspicions); A4 hostile
  battery (robustness certificate or guard mutations).

## 4. Residual-error correlations among survivors

From A1 (hosted, real evaluator): our per-net error is UNCORRELATED with
per-net MC difficulty (spearman -0.096 vs the implied MC baseline) — the
design's residual error is net-specific advantage collapse, not intrinsic
difficulty; correlated with billed FLOPs (-0.432) and all-layer analytic MSE
(+0.255). This is the dominant unexplained structure in the champion's error
and the primary signal for this generation.

## 5. Next-mutation request (ONE mechanism, per the protocol)

**Repair the net-specific advantage collapse.** Ranked proposal set from this
generation (each enters the external ladder at premise stage; one at a time):

- **G3-P1 (primary; = M185, premise already running): per-net pruning guard.**
  Weight-derived tail flag (diagonal-pass accuracy proxy / pruned-fraction);
  on flagged nets relax dead_alpha / widen rescue, paid from the 34%
  headroom. Premise gate: worst-net MSE improves >= 30% under relaxed
  pruning while median nets move < 10%.
- **G3-P2: per-net rotation selection (kill-respecting).** M180 killed
  rotation FRAGMENTATION at fixed budget; it did NOT test choosing among k
  candidate rotations per net using a cheap weight-derived proxy and
  spending the full n on the chosen one (selection, not stratification;
  connects A3 suspicion 1 — net 202's sub-unity k=4 arm). Premise gate:
  oracle-selection headroom across 8 rotations must exceed 20% MSE on tail
  nets before any proxy is built.
- **G3-P3: tail-targeted budget reallocation.** Per-net n_base scaling on
  flagged nets (T3's deterministic-cap machinery inverted: spend UP to
  ~0.95B on tail nets). Only the fixed-overhead leverage term moves
  (~F0/C ≈ 3-6%) unless combined with P1; premise gate: projected mean gain
  >= 5% from the a1 distribution before build.
- G3-P4 (contingent on A3): any FLIPPED kill reopens its mechanism as a
  conditional mutation.
- G3-P5 (contingent on A4): any hostile failure becomes a guard mutation
  (also feeds the private-rerun robustness case).

## 6. Holdout firewall statement

Local public 0..99 is burned-descriptive; the hosted public 50 is the
grader's iteration set (used for validation, cannot overfit beyond it: the
Phase standings add a withheld 50, and the prize adds fresh private seeds);
NO local read of hosted truth exists or is possible; the private re-eval
suite is untouched by construction. Ladder rules: premise 2-5 units, screen
>= 20 matched units, development on large local splits, final gate = one
hosted graded submission (< 1.75e-7 to count), deployment = designation.
Never promote on aggregate alone: tails, bias, runtime, per-unit differences
inspected at every rung (the a1 per-MLP table is the tail benchmark).

## 7. Generation-3 output contract

Each proposal climbs one ladder rung per loop iteration with a predeclared
kill gate; failures append to the ledger as constraints on Generation 4; the
first proposal to pass its hosted final gate becomes the champion candidate
and triggers the designation review. The recursion continues until the
Sep 19 designation locks or the user stops it.
