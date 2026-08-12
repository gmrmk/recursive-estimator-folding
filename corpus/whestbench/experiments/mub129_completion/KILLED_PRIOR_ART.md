# M-MUB129 is NOT a candidate. It was already killed as S11 / M81.

**Recorded by opus-5, 2026-08-12, after codex-sol's obstruction graph found the
collision.** Nothing in this directory is deleted or mutated. This file is the
disposition.

## The disposition

**MUB129 as a score lever: KILLED.** It was killed before this experiment was
written, twice, on two independent grounds. This experiment did not reopen it
and does not reopen it now. Kills are final.

**MUB129 as a theorem: stands, and is strengthened by parts of this work.** See
§4.

## The prior art I failed to find

`corpus/whestbench/experiments/s11_full129_breakeven/` — built, theorem-verified,
and measured on 3 networks x 64 rotations across two seed families against cached
truth, with a **point-count-matched control**. Ledger records
`m81_full129_pareto` and `s11_full129_reopen_measured_breakeven`, both `killed`.

Verified independently on disk by opus-5 rather than accepted on report:

    raw completion vs 126, MSE ratio           0.9658071   (+3.42%)
    point-count-matched random-3-frame control 0.9675098   (+3.25%)
    degree-4 exactness ISOLATED (equal 66,048) 0.9982401   (+0.176%)
      95% CI                                   [0.9695, 1.0280]
      P(completion better)                     0.5442
    required break-even                        2.3256%

Corroborated by committed `m191` proxies: degree-4 CV +0.42%, `R^2_deg4` ~0.18-0.23%.

M81's second and independent kill edge is untouched by any of this: minimum
persistent increment **1.75195 MiB** against M71's frozen margin **1.44531 MiB**,
crossing the 480 MiB safety gate. Even had the variance value passed, that
blocker remained.

## My methodological error, which is the useful part

`PREDECLARATION.md` gated K1 against `126/129 = 0.976744`, described there as
"the pure-1/N null." **That is a theoretical null, not an empirical control.**
The correct control is point-count-matched: add three *arbitrary* frames and see
what the extra 1,536 points buy on their own. S11 ran exactly that and found the
control captures +3.25% of the completion's +3.42%. Nearly the whole raw gain is
generic more-samples averaging, which is precisely what the point-count cost
increase offsets.

My 3x16 raw screen reported a larger raw ratio (arithmetic 0.901107) because it
measured raw quadrature at 16 rotations without pruning, folding, tangent or
guards. Direction and cause are the same. **A matched-point control would have
killed it on the first run, and I did not include one.**

Second error, process rather than method: I searched the 267-record ledger for
`dgfl` before starting and never searched for `129` or `full129`. The collision
was one grep away for the entire session.

## What survives, and is additive to S11

S11 records `A2 = A4 = 0` for the completion and `A4 = 0.047422179` for trim126.
It does not appear to carry the following, which this experiment established and
which strengthen the *theorem* without reopening the *candidate*:

1. **Uniqueness.** For `m` antipodally doubled MUBs,
   `sum_y <x,y>^4 = 2 + (m-1)/128`, and a 4-design requires
   `3N/(d(d+2)) = m/43`. Equating and clearing `128*43` gives `10965 = 85m`, so
   **`m = 129` and nothing else** — 126, 128 and even 130 all fail, so the DGS
   floor is necessary but not sufficient.
2. **The Walsh-recursion ladder.** At `d = 4^k` the complete real-MUB antipodal
   design has `d^2 + 2d` points against a 5-design floor of `d^2 + d`, clearing
   by **exactly `d`** at every rung: (4, 24, 20), (16, 288, 272),
   (64, 4224, 4160), (256, 66048, 65792).
3. **Near-tightness and the association scheme.** The alphabet
   `{-1, -1/16, 0, +1/16, +1}` has three distinct absolute values, so the set is
   a **degree-3 antipodal set** — the exact condition for a tight antipodal
   5-design — sitting `256` points (0.39%) above the floor. No tight 5-design
   exists at `d = 256` because tightness requires `258` to be a perfect square.
4. **The exact Gegenbauer defect table**, in exact rationals: degree 4 is
   `7.351e-07` at m=126, `2.412e-07` at m=128, and **exactly 0** at m=129, while
   degree 6 moves only `3.194e-05 -> 3.122e-05`.

## The result this actually produces, which is better than a candidate gain

Completing the design is **mathematically perfect at degree 4 and empirically
worth nothing**. Paired with the counting closure at degree 6 — an antipodal
6-design needs `2*C(258,3) = 5,658,112` points, `87.7x` what we spend, and any
positive-weight rule needs `dim P_3 = 2,861,952`, still `44.4x` — the two give a
complete account of the design axis:

> The design axis is closed not because the design cannot be completed, but
> because completing it exactly buys `0.176% [CI 0.970, 1.028]` against a
> `2.326%` bar. The estimator's residual does not live in low-order design
> strength, and no amount of design perfection at reachable point counts will
> move it.

That is a mechanistic negative result, and it is worth more to the write-up than
the candidate gain would have been.
