# Drop-in manuscript section: the design axis, closed from both sides

**Status:** draft section for `PHASE1_WRITEUP_DRAFT_20260808.md`, written
2026-08-12 by opus-5. Sized for the boundary-results slot at ~470 words. Not yet
inserted; `SECTION` below is the text, everything outside the rule is notes.

**Provenance.** The counting and uniqueness arguments are new tonight
(`experiments/mub129_completion/`). The falsification is prior campaign work,
`experiments/s11_full129_breakeven/` and ledger records `m81_full129_pareto` and
`s11_full129_reopen_measured_breakeven`. Framing follows codex-sol's
recommendation of 2026-08-12 03:31 UTC: lead with the theorem *and* the
point-count-matched falsification rather than with a candidate gain.

**Why this belongs in the manuscript.** P1 lost its central claim and is OPEN,
which left the paper's mechanistic core thinner than the rubric rewards. This
replaces it with a statement of the same kind — about what no method of a given
shape can achieve — that is proved rather than measured, and then falsifies its
own most attractive corollary. Rules v12 §6 criterion (iii) is "the ease of
determining the actual performance impact of the contribution from the code and
writeup together"; the whole section turns on one control a reader can check.

---

## SECTION — Why structured spherical designs plateau, and why completing them does not help

Our estimator integrates over 126 phased-Hadamard frames, each an orthonormal
basis `H_256 diag(phi_s)/16`, antipodally doubled to 64,512 points on `S^255`.
It is an exact spherical 2-design, and antipodally therefore a 3-design. The
natural next question is whether pushing to degree-4 exactness would help. It
can be answered exactly, in both directions, and the answer is instructive.

**The design cannot reach degree 4 at its current size.** [D] The
Delsarte–Goethals–Seidel bound for an antipodal spherical 4-design in `S^255` —
which is automatically a 5-design, since odd harmonics cancel pairwise — is
`2*C(257,2) = 65,792` points. We spend 64,512. We are 1,280 points short, so no
reweighting of these nodes under antipodal pair symmetry reaches degree 4.

**Exactly one frame count fixes it.** [D] For `m` mutually unbiased bases
antipodally doubled, every point sees one inner product at `+1`, one at `-1`,
510 at `0`, and `512(m-1)` at `+-1/16`, so `sum_y <x,y>^4 = 2 + (m-1)/128`. A
4-design requires `3N/(d(d+2)) = m/43`. Equating and clearing `128*43` gives
`10965 = 85m`, hence **`m = 129` and no other integer** — 130 clears the counting
floor and still fails. And `129 = d/2 + 1` is the maximum number of real mutually
unbiased bases in `R^d` when `d` is a power of four, which `256 = 4^4` is. Under
the Walsh doubling the complete set has `d^2+2d` points against a floor of
`d^2+d`, clearing by exactly `d` at every level: 24/20, 288/272, 4224/4160,
66048/65792. The completed design is a near-tight antipodal 5-design, over the
floor by 0.39%.

**And we can say in advance what completing it is worth.** [D] For a bias-free
He-initialised ReLU network the rotation-averaged two-point function is exactly
the iterated arc-cosine kernel `K(c) = (E||X||^2/d)·kappa^32(c)`, so the
estimator's variance decomposes as `sum_l ||f_l||^2 A_l` against the design
defects above. That predicts `V126 = 2.4977e-7` against a measured geomean of
`2.6697e-7` over sixteen fresh networks — **the variance of this estimator is
predictable from first principles to 6.4%** — and it puts the degree-4 share of
that variance at **0.4497%**.

**So completion is worth about half a percent, against a 2.33% break-even** set
by the point-count cost. [O] Measurement agrees from two further directions: a
point-count-matched experiment isolating degree-4 exactness at equal 66,048
points returns `0.176%, CI [0.970, 1.028], P(better) = 0.54`, and a committed
degree-4 control variate returns `+0.42%`. Three routes, one predictive, all
landing an order of magnitude below the bar.

That agreement is worth more than any of the three alone, because the analytic
route explains the other two. Most of the variance is simply not where design
strength lives: **86% of it sits at degrees 8 and above**, which no reachable
design touches.

**And degree 6, where the error actually lives, is unreachable.** [D] The
measured angular error sits at degree 4 (11% of the iid level) and degree 6
(40%). An antipodal 6-design needs `2*C(258,3) = 5,658,112` points, 87.7x our
budget; any positive-weight rule needs `dim P_3(S^255) = 2,861,952`, still 44.4x.

The design axis is therefore closed from both sides at once, and not for the
reason one would guess. It is not that the design cannot be completed — it can
be, exactly, and we did. It is that **completing it perfectly buys nothing
measurable**, because the estimator's residual does not live in low-order design
strength. Perfecting a design is not the same as reducing its error, and on these
networks the two come apart.

---

## Notes for whoever inserts this

- Companion numbers, all committed and independently reproducible: exact
  Gegenbauer defects in rationals are `A_4 = 7.350908201315546e-07` at m=126,
  `2.4120167535566633e-07` at m=128, exactly `0` at m=129, with `A_6` moving only
  `3.194089008420301e-05 -> 3.122025216144244e-05`. Worth a footnote; they make
  "exactly zero" checkable.
- **Scope the defect formula to even degrees.**
  `A_l = (1/N)[2 P_l(1) + 510 P_l(0) + 512(m-1) P_l(1/16)]` is valid only for even
  `l`; at odd `l` the true defect is zero by antipodal cancellation and the
  formula returns nonzero. Only even degrees are used here, so nothing above
  depends on it, but the formula is wrong as written and must not be published
  unscoped.
- The tail law is worth one sentence if space allows: because `P_l(1/16) -> 0`,
  `A_l -> 2/N`, so `A_l(129)/A_l(126) = 126/129` to six digits for every even
  `l >= 8`. The design's own high-degree behaviour is the 1/N law, which is why
  adding points cannot beat adding points.
- **Do not** state that no arbitrary positive-weight non-antipodal rule can reach
  degree 4 on 64,512 nodes. The general even-degree bound is `dim P_2 = 33,152`,
  which 64,512 clears twice over. The claim is scoped to pair-symmetric antipodal
  reweighting, which is the class we deploy. This was over-claimed once already
  and corrected by codex-sol.
- The completion also carries a separate memory blocker recorded in M81 —
  minimum persistent increment 1.75195 MiB against a 1.44531 MiB margin. It is
  not needed for the argument and can be omitted from the manuscript, but it
  should not be contradicted.
- This section supersedes the reachable part of §3b. It does not revive anything:
  the completion is and remains a killed candidate, and the section says so by
  reporting the falsification rather than by asserting a disposition.
