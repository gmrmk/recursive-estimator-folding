# N8c predeclaration — offline-trained per-neuron corrector (sanctioned family)

Date: 2026-08-08 (before measurement). Last mutation of the honest stack.

## Mechanism

Train, entirely offline on SELF-GENERATED He nets (never public rows), a
per-neuron ridge corrector consuming cheap analytic features (diagonal-pass
mu/sigma/alpha and closure statistics) to predict and subtract the Kerdock
v3 estimator's residual error; ship frozen weights in the package
(organizer-sanctioned pattern: offline training is legal, weights ship as
assets).

## Premise gate G0 (cheapest falsifier, before any training)

A corrector can only remove the PREDICTABLE (bias-like) part of the error;
sampling variance is untouchable. Decompose Kerdock's per-net error on 3+
synthetic nets: replicate the estimator over its Haar-rotation seeds (its
only randomness); variance = var across seeds; bias^2 = mean squared error
vs a high-precision MC truth minus variance minus truth noise.
KILL if the bias^2 share of total MSE < 25% — the corrector's ceiling would
be < 1.33x raw, below the composed value bar once private-rerun fragility
risk (overfitting the He distribution's finite training sample) is priced.
Prior evidence pointing at a kill: N8a measured Haar-seed variance
~2.0-5.7e-7 on synthetic nets, the same order as the T4 raw MSE 2.49e-7 —
variance appears to dominate.

## Build gates (only if G0 survives)

- G1: features are weight-derived only; training nets fresh-seeded;
  corrector ridge (closed form, no iterative tuning against any gate).
- G2: fresh-seed holdout (nets never seen in training): raw-MSE paired
  improvement >= 1.25x with CI excluding 1.0; NO degradation on any holdout
  net worse than 5% (tail guard).
- G3: package with shipped weights; validate-package + contract + member
  listing; billed inference cost of the corrector < 1% of B.

## Bias class / firewall

Deliberately biased corrector on a deliberately biased base; all training
data self-generated; descriptive only until graded. No sealed cells, no
public rows, no submission.
