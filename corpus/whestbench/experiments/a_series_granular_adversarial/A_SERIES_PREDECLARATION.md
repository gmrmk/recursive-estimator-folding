# A-series predeclaration — granular + adversarial testing program

Date: 2026-08-08 (before analysis). User mandate: reject the easy close;
granular testing detail and adversarial testing. Three attack surfaces, each
with predeclared success criteria; findings feed mutations only through the
normal predeclare-falsify ladder.

## A1 — Hosted tail autopsy (#326094 per-MLP ledger)

The graded score is the MEAN over 50 public MLPs; our spread is 5.42e-8 to
5.96e-7 (11x). Scrape the full per-MLP ledger (name, adjusted, final MSE,
all-layer MSE, billed FLOPs, wall) and test, with rank correlations and a
top-vs-bottom-decile contrast: (i) is the tail explained by billed-FLOP
variation (pruning behaving differently), wall variation (fold pathologies),
or neither (pure v_m variance heterogeneity)? (ii) does the all-layer MSE
(our analytic intermediate predictions) predict the final-layer tail —
i.e., is a weight-derived tail flag available a priori?
SUCCESS = a reproducible tail signature; NULL = tail uncorrelated with every
observable (pure variance heterogeneity, irreducible for a fixed design).

## A2 — Local tail hunt (500 nets, per-net diagnostics)

Run the v3 estimator (or its plain-antipodal G0 surrogate where sufficient)
across ~500 synthetic He nets with per-net diagnostics: estimated v_m
(replicate variance), pruning fraction per layer, rescue counts, fold
partition sizes (kink/on/dead at 29-31), per-layer MSE vs a per-net MC truth
on the worst decile. Question: is the local tail (worst 5%) STRUCTURAL
(pruning/rescue/fold misbehavior with an identifiable signature -> fixable
mutation M185) or STATISTICAL (v_m spread only)? KILL the structural
hypothesis if the worst-decile diagnostics are indistinguishable from the
median's (standardized difference < 0.5 on every diagnostic).

## A3 — Kill-verdict heterogeneity re-audit (the skeptic pass on ourselves)

Re-open the per-net / per-arm / per-seed data of all twelve kills and attack
each verdict: which kill could flip under a per-regime split the aggregate
gate hid? Specific pre-registered suspicions: M180 Arm C k=4 measured 0.894
on net 202 (sub-unity on one net; heterogeneity vs its 1.196 aggregate);
M181 Arm 3 per-net lambdas -0.035/0.005/0.040 (sign flips — is there
per-NEURON lambda signal the net-level fit averaged away?); N8a per-net
ratios 1.43-2.99 (what makes net 202 different?); N7's second MC control
slope -0.78 (marginally outside sanity). For each: state whether the kill
STANDS (heterogeneity within noise), WEAKENS (a regime exists where the
mechanism helps -> conditional mutation candidate), or FLIPS (aggregate gate
error). Verdicts require the existing artifacts' raw npz/json only — no new
compute unless a suspicion needs one targeted rerun.

## A4 — Hostile-inputs battery on the champion

The operating manual's hostile list adapted to estimators, on v3 exactly as
packaged: near-zero weight scales (He gain x1e-3), large scales (x1e3),
heavy-tailed weights (t_3 entries scaled to He variance), rank-deficient
weights (rank 32 of 256), correlated columns, all-negative-mean nets
(alpha<0 everywhere -> rescue storm), subnormal-range weights (f32
denormals), and a determinism check (two subprocess runs bitwise-equal).
Per input: completes / score / billed C vs budget / wall vs 60s / memory.
SUCCESS = a failure mode with a plausible hosted analogue (-> guard
mutation); NULL = robust everywhere (a private-rerun robustness certificate
worth a writeup paragraph).

## Discipline

Findings are EVIDENCE, not mutations; anything actionable gets its own
predeclared M185+ with a cheapest falsifier. All analysis on synthetic nets
or our own graded artifacts; firewall unchanged (no truth/scorer, hosted
data = our own submission pages only, no accounting levers).
