---
name: recursive-estimator-folding
description: Recursively generate, falsify, promote, combine, and document mathematical estimator mutations under fixed legality and compute constraints. Use for competition estimators, Monte Carlo or quasi-Monte Carlo variance reduction, recursive Headroom-style searches, unusual cross-domain analogies, and any task where apparent wins must survive matched experiments and untouched holdouts.
---

# Recursive Estimator Folding

Turn unconventional ideas into auditable operators. Preserve a stable champion, mutate one causal mechanism at a time, fold only validated improvements back into the champion, and keep every rejection as evidence rather than silently retuning it.

## Non-Negotiable Invariants

Write these before proposing a mutation:

1. Objective and official score formula.
2. Legality/accounting boundary and package versions.
3. Resource ceiling with a safety margin.
4. Bias class: exact, unbiased, asymptotically unbiased, or deliberately biased.
5. Disjoint development, validation, and untouched holdout units.
6. Champion artifact hash and reproducible randomization.

Reject accounting bypasses, hidden compute, private-data leakage, and behavior that depends on undefined evaluator quirks. When a rule is ambiguous, preserve the stricter interpretation and request an official clarification before submission.

## Recursive Fold

For generation `g`, apply:

`champion_g -> mutations -> premise tests -> paired screen -> validation -> interaction test -> champion_(g+1)`

At each generation:

1. State the proposed mechanism, equation, assumptions, predicted signature, and kill condition.
2. Translate metaphors into ordinary mathematics before implementation.
3. Run a static legality and worst-case budget check.
4. Test the cheapest premise that could falsify the mechanism.
5. Compare against the frozen champion on matched evaluation units and randomizations.
6. Promote only when the prespecified primary metric and uncertainty gate pass.
7. Before composing two winners, run a factorial interaction or residual-covariance test.
8. Fold the winner into a new immutable champion; retain the previous champion for rollback.

Do not mutate a failed candidate merely because it once had a favorable small-screen score. Mutate it only when a new operator addresses its diagnosed failure mode.

## Promotion Ladder

Use whole independent problem instances as statistical units. Adapt sizes to the available data, while preserving this order:

- Premise: 2-5 units, enough only to kill impossible mechanisms.
- Screen: at least 20 matched units.
- Development: cross-validation on the large public split.
- Final gate: one evaluation on an untouched split.
- Deployment: fresh private instances with no further holdout tuning.

Require zero resource failures, a predeclared minimum effect, a paired uncertainty interval below parity, and stability across subprocess runs. Correct for multiple comparisons within each mutation family or label the result exploratory. Never promote on an aggregate score alone; inspect tails, bias, runtime, and per-unit differences.

Use `scripts/fold_ledger.py` to initialize and audit the promotion record.

## Operator Families

Load [operator catalog](references/operator-catalog.md) when a task invokes fractals, tau folding, memristive dynamics, biological patterning, retinal/quantum analogies, or theoretical physics.

Prefer operators in this order:

1. Exact identities and Rao-Blackwellizations.
2. Unbiased controls with known expectations.
3. Randomized QMC transforms with preserved marginals.
4. Multilevel or multifidelity estimators with explicit coupling.
5. Certified sparsification or pruning with rescue tests.
6. Cross-validated biased hybrids only when the competition metric permits them.

For qualitative analysis, use mechanism tracing: observation -> latent mechanism -> mathematical operator -> measurable signature -> rival explanation -> falsifier. For quantitative analysis, include units or scale, bias, variance, covariance, complexity, numerical stability, confidence intervals, and worst-case resource use.

## Offline Headroom Integration

Headroom-Recursion is an orchestration and memory layer, not evidence. Run it without an API when required: pass a deterministic local adapter the champion, ledger, constraints, surviving mechanisms, and failed mechanisms; capture the returned mutations as proposals. The validation ladder remains external and authoritative.

Each recursion packet should contain:

- champion hash and score distribution;
- evaluator/version hashes and budget margin;
- promoted, killed, and unresolved candidates;
- residual-error correlations among survivors;
- next mutation request limited to one mechanism;
- holdout firewall statement.

Never expose untouched holdout outcomes to subsequent mutation generation.

## Completion Standard

A result is ready only when it includes executable code, locked dependencies, artifact hashes, a complete experiment ledger, legality rationale, matched per-unit results, uncertainty analysis, negative results, and a concise account of how each unusual analogy became a classical computation. Distinguish a locally best candidate from a demonstrated competition winner.
