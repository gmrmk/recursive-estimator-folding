# PB-1 — the Premise Battery (recursion acceleration) + the failure-cross set

Date: 2026-08-08 (before code). User mandate: mutate the failures together;
accelerate the mutation loop with the recursion skill. Two deliverables.

## Part 1 — The acceleration method: a standing premise battery

Bottleneck analysis of the 16 G0s run so far: ~80% of wall time is truth
computation (3.5M-sample MC per net) and baseline replication — both
IDENTICAL across mechanisms. The battery amortizes them:

- **Fixed net panel + cached truths** (read-only reuse):
  m181_truth_net{101,202,303}.npz (3.5M, floor ~1.5e-8) for high-precision
  arms; the m185 stage-1 80-net panel (300k truths, floor ~7e-8) for
  wide-panel arms.
- **Cached baseline stacks**: the Kerdock arm-A replicate estimates already
  stored in m180/m181 partial npz (16 rotation seeds, paired).
- **Arm contract**: a mechanism enters as a function
  (weights, samples, shared_state) -> final-layer estimate, evaluated under
  the SAME rotation seeds against the cached truth; paired MSE ratio + CI vs
  the cached baseline. Gates unchanged (kill < 10%, promote >= 15% CI-excl).
- **Batching**: one delegated agent runs ALL pending arms in one session;
  one results json; one ledger batch-append (statuses individual).
- Discipline preserved: every arm predeclared in this file (or a successor)
  BEFORE the battery runs; kills final per arm; no post-hoc arms in the same
  run.

Throughput: ~2 min/arm marginal vs ~20 min/mechanism serial — an order of
magnitude, which is the acceleration the recursion skill's ladder permits
without weakening a single gate.

## Part 2 — The failure crosses (kill-respecting: each changes a failed link)

### ARM M188 — fold-threshold recalibration (M184-machinery x A1b-evidence)
The strongest cross. A1b measured the tail's shape: worst nets carry +22%
MORE always-on classifications and -25% fewer kink columns (fold_on_total is
the top positive MSE correlate, rho +0.459) — on/kink MISCLASSIFICATION in
the terminal fold. M184's certainty calculus (alpha margins with explicit
misclassification probability) applies to the fold's on_alpha dial: RAISE
on_alpha (currently 3.0 -> arms at 3.5 / 4.0 / 5.0), demoting marginal "on"
columns to sampled kink columns. Exactness IMPROVES (fewer wrongly-linearized
columns); billed cost rises (more kink sampling) and MUST respect the A4
constraint (pruning-hostile nets bill 95.5% of B) — arms report billed delta
and any arm projecting >0.95B worst-case is killed regardless of MSE.
Battery gates: kill < 10% panel-MSE reduction; promote >= 15% CI-excluding-10%
AND worst-decile improvement >= 20% (the tail is the target).

### ARM M189 — dead_alpha broad relaxation (the P1-broad form; M185 stage-2
companion). dead_alpha -2.0 -> arms at -2.5 / -3.0. Same cap constraint.
(If M185 stage-2 lands first and kills relaxation causally, these arms are
withdrawn before the battery runs — recorded here to keep the predeclaration
honest.)

### ARM M190 — joint (M188 x M189) at the best single-dial settings, only if
both survive alone (interaction test per the skill).

### NO-GO (recorded so it is not respun): N6 x N7 pre-integration cross.
Smoothing the kink (N7's failed link) via exact 1-D integration (N6's valid
mechanism) requires propagating a line/cloud through the front 28 layers per
sample (N6's failed link: ~17k breakpoints, ~1000x sample cost) OR injecting
Gaussian randomness at an intermediate layer (M181's failed link: the
intermediate law's non-Gaussianity, bias 4-6x MSE). The two failure modes are
the SAME WALL seen from two sides (cost of exactness vs bias of Gaussian
surrogacy); no composition escapes both. Constraint stands for Generation 4.

### Already queued elsewhere: Gen3-P2 rotation selection (M180-C failure x
A1 finding) — premise runs in the battery as ARM P2 (oracle-of-8 rotations on
the m185 worst-decile nets; >= 20% oracle headroom on tail nets to promote).

## Firewall
Cached artifacts read-only; synthetic nets only; frozen sources subclassed
never edited; no submissions from the battery; ledger append per arm.
