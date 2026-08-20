# C1 predeclaration — calibrate the local suite against the hosted MC baseline

Date: 2026-08-08 (before the run). Not a candidate mutation: a MEASUREMENT
that decides how to read every local score we hold.

## Why

The hosted grader prints a Monte-Carlo reference of **6.47e-7** adjusted on
its 50-MLP public split (observed on every submission page). Our corpus's
local per-sample variance (v ~ 0.0199) predicts a budget-matched MC score of
~3.1e-7 on OUR local suite — a factor of ~2.1 apart. Exactly one of these is
true:

- (A) The two suites are comparable and the hosted MC reference is computed
  differently (fewer samples, overhead included). Then our local scores
  transfer roughly 1:1, and Kerdock v3 (local adjusted 1.62e-7) lands mid-
  field hosted.
- (B) The hosted suite genuinely has ~2x the per-sample variance of our local
  suite. Then EVERY local number we hold overstates hosted performance by
  ~2x, Kerdock would grade ~3.3e-7 hosted (barely better than our existing
  5.47e-7 entry), and the dossier's ranking claims need rescaling before the
  user spends submissions.

## Mechanism

Write a plain budget-matched Monte-Carlo estimator (iid standard normals,
dense forward, mean of the final post-ReLU layer; intermediate layers
returned as zeros exactly as the observed hosted leaders do, since only the
final layer is scored) and run it under the pinned v0.14 subprocess runner on
local public indices 0..24 (already burned; DESCRIPTIVE only).

## Predeclared reading

local_MC_adjusted / 6.47e-7 = the suite-difficulty ratio R.
- R in [0.8, 1.25]: suites comparable -> local scores transfer; case (A).
- R < 0.8: our local suite is EASIER; multiply every local adjusted score by
  1/R for an honest hosted expectation; case (B).
- R > 1.25: our local suite is harder; our candidates are better than they
  look.

## Status of the output

DESCRIPTIVE calibration on burned public rows. Confers no validation and no
promotion. It changes only how we REPORT expectations to the user before
submissions are spent.

## Firewall

Local dataset weights only (standard estimator input), no truth/scorer/
private-target reads, no submission, frozen candidates untouched.
