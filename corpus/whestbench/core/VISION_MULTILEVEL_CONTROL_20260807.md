# The fold: sampler and closure are one object (multilevel control variate)

Status: research-direction note produced by a reverse-oracle ideation ("assume
the elegant #1+contribution solution exists; extract its mechanism"). The
VICTORY is the oracle's hypothesis; the MATH here is real and checkable; the
v-reduction magnitude is an UNTESTED prediction gated at M172. No claim of
having solved or won. Response-free; champion unchanged.

## The elegant object (real math)

Let z_L(X) be the final pre-activation of the fixed net, X ~ N(0, I), and
target m = E[ReLU(z_L)]. Take the filtration F_l = sigma(activations through
layer l), F_0 trivial, F_L full. The Doob martingale decomposition is EXACT:

  ReLU(z_L) = m + sum_{l=1}^{L} D_l,   D_l = E[ReLU(z_L)|F_l] - E[ReLU(z_L)|F_{l-1}]

The D_l are orthogonal martingale increments; Var(ReLU(z_L)) = sum_l Var(D_l).
Monte-Carlo's per-sample variance v is exactly this sum. Each increment is the
"new non-Gaussian information injected at layer l."

**The control variate:** replace each true increment by an ANALYTIC
approximation D_l^ from the Gaussian closure and subtract it. Because
martingale increments have mean zero, the control is UNBIASED for ANY analytic
D_l^; the residual variance is Var(sum_l (D_l - D_l^)). If the closure captures
a fraction f_l of each increment, v drops to sum_l Var(D_l)(1 - rho_l^2) where
rho_l is the correlation between true and analytic increment. This is a
MULTILEVEL / telescoping control variate.

## Why this IS our machinery (the fold)

- M125b's `inhomogeneous_source_recurrence` ("propagate one accumulated tangent
  and inject the next source") is precisely the increment-injection recurrence
  for the D_l.
- M178/M179 produce the EXACT per-layer (mu_l, V_l) and the local Jacobian
  bundle {p,r,K,Hmu,Hv} — exactly the analytic D_l^ (the closure's prediction
  of the remaining forward from a perturbed layer-l state).
- So "recursive estimator folding" is realized literally: recursively decompose
  the target over layers (Doob), then FOLD the analytic closure into the
  champion sampler as the per-level control. The two arms (analytic, sampling)
  are ONE object, not two.

This SIDESTEPS the corpus's kills: M137 (four-moment non-identifiability) and
the 0.493% terminal-k3 result are about TERMINAL-ONLY corrections. The
multilevel control is per-layer and unbiased regardless of closure accuracy —
a genuinely different, untested mechanism (fold rule: reopen by changing the
failed mechanism / exposing a new observable = the per-layer increments D_l).

## Grounding (what is already evidence)

Control variates demonstrably reduce v HERE: the champion's QMC + q3 + tangent
control already cut v ~2x (plain ~0.04 -> champion 0.0199; N4). That is a
first-order, mostly-terminal control. The multilevel EXACT control is the
extension: it uses every layer's exact increment, not just the terminal moment.
Whether it beats the champion's 2x is the untested delta.

## Testable prediction (honest)

Under the M172 source-variance gate, the multilevel-control residual variance
v_mc satisfies v_mc / v_champion < 1, with the predeclared M172 thresholds
(upper-90 ratio < 0.25 would be a 4x v-cut; p99 <= 1.25). The reverse-oracle's
"win" corresponds to v_mc ~ 0.005 (a 4x cut), which via adjusted = v*8.74e-6/S
drops the #1 throughput bar from ~24x to ~6x — comfortably reachable. That 4x
is the HYPOTHESIS the M172 gate exists to test; it is not established.

## How it changes the plan

1. REOPENS the v-lever as an ELEGANT analytic path, not just the engineering
   S-lever: ultrathink-2 wrote off v as "pinned at 0.0199" based on TERMINAL
   controls; the multilevel control is the untested per-layer mechanism the
   M179 chain was already building toward. Both #1 levers (v via multilevel
   control, S via native kernel) are alive; they MULTIPLY (adjusted = v/S).
2. Makes the M179 -> M125b -> M172 chain the PRIMARY science path with a
   concrete, measurable payoff (v_mc/v_champ at M172), not just the
   Algorithmic-Contribution paper.
3. The Algorithmic Contribution writes itself: "an exact, certified,
   FlopScope-metered multilevel (Doob) control-variate estimator for deep-ReLU
   final-layer means, folding an endpoint-complete Gaussian-closure provider
   into a Monte-Carlo sampler" — novel, rigorous, prize-shaped, regardless of
   the Best-Score outcome.
4. Concrete next mutations: finish M179 G4/G5 (the exact increments D_l^);
   build the M125b control-variate injector (the fold); then the M172 gate
   MEASURES v_mc/v_champ — the single number that says whether the elegant
   v-path is real. This is autonomous and response-free up to M172 (which is a
   source-variance measurement on generated nets, not a sealed efficacy cell).

## The honest one-liner

The vision is elegant and the machinery to test it is exactly what we have been
building. The victory is a hypothesis with a named measurement (v_mc/v_champ at
M172) and a named payoff (4x v-cut -> #1 bar falls to ~6x throughput). It is
the best real shot at #1 via mathematics rather than engineering — and it is
still gated on that one untested variance ratio.
