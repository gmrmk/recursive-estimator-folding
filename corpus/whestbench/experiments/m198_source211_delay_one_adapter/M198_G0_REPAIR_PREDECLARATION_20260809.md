# M198-G0 predeclaration: provenance and frozen-carrier repair

Status: `PREDECLARED_NOT_EXECUTED`. This repair follows an adversarial ABI
failure. It changes only the response-free Source211 input/carrier contract;
it does not open source construction, variance, efficacy, native accounting,
contest truth, scorer, leaderboard, or submission work.

## Failure being repaired

The first M198 implementation reproduced the M124 delay-one algebra, but a
frozen dataclass still aliased writable arrays; `(layer, epoch)` did not bind a
source to the exact archived pre-ReLU state; the M125 carrier discarded labels;
and a fixed ownership-policy tag did not carry the M172 conservation evidence.
Its dense parity test also called the same M124 formula and therefore was not an
independent numerical oracle. Until all gates below pass, M198 remains
`REPAIR`, not a validated component.

## One changed mechanism

Replace the permissive input/carrier ABI with a fail-closed, immutable,
digest-bound contract:

1. every array is copied to canonical contiguous float64 storage and marked
   read-only before validation completes;
2. the source and delay-one context share one exact provenance record binding
   network digest, weight-trace digest, one-based ReLU layer, producer epoch,
   dtype/cast provenance, and a canonical digest of `(pre_mean, pre_covariance)`;
3. the source carries a conservation witness whose arrays verify
   `physical_K22/2 = control_ijj + residual_ijj`, with the legacy owner retired,
   collision re-zeroing forbidden, and the unchanged `[4]`/`[3,1]` owners
   retained externally;
4. converted tangents retain source identity and labels through a labelled
   suffix map; the recurrence rejects reorder, missing/incorrect suffix maps,
   duplicate source identity, and terminal reinjection;
5. a small generated-only numerical oracle differentiates independently
   evaluated Gaussian ReLU moments and never calls M124's delay-one routine.

## Frozen G0 gates

- **Immutability:** mutations through original aliases cannot change a
  constructed object; direct writes to every stored array raise.
- **Provenance:** changing any digest/label/state while preserving shape must
  fail before formula evaluation. Two lawful contexts with equal layer/epoch
  but different pre-states must not accept the same source.
- **Ownership:** exact conservation passes. Retaining the old K22 owner,
  collision re-zeroing, or changing residual/control without updating the
  physical coefficient must fail.
- **Carrier:** labelled M125b equals explicit labelled superposition on widths
  2..7; shuffled sources, swapped maps, duplicate source IDs, and terminal
  reinjection fail closed.
- **Independent oracle:** on fixed moderate-SPD generated cells, rank-one
  symmetric fourth tensors are checked against a numerical fourth directional
  derivative of independently evaluated univariate/bivariate Gaussian ReLU
  raw moments. Maximum absolute error must be at most `2e-6`; the oracle may be
  tightened after observation but not loosened.
- **Existing algebra:** dense M124 parity, linearity, permutation covariance,
  positive ReLU-gauge covariance, and M179 archive parity continue to pass.

## Kill and scope rules

Any failed gate leaves M198 closed at the input ABI. Passing all gates promotes
only a generated-only algebra/carrier component. It does not show that a
physical Source211 provider exists, that the component improves MSE, that it
fits the native FlopScope budget, or that the full M163/M172 ownership pipeline
is integrated. No retry, retuning, official data, benchmark response, truth,
or scorer access is authorized by this gate.
