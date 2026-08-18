"""Suite tier 4: LAYER 1 is billed at the design's 32,256 BASE rows, not 64,512.

ONE SUBSTANTIVE CHANGE
======================
The suite incumbent's docstring names four frozen constants; tier 3 unfroze the
third ("W-side transforms re-billed per tile").  This tier unfreezes the first,
"the design billed as anonymous rows", at exactly one place and in its weakest
possible form:

    The layer-1 product has 32,256 rows.  The other 32,256 rows of the design
    are produced by NEGATING that product's output, not by multiplying.

Nothing else moves.  Layer 2 keeps tier 2's CReLU route verbatim; layers 3..32
keep tier 3's generic price verbatim; every layer including layer 1 still pays
exactly one hoisted W-side operand stack, so the stack lane is unchanged at 32
per net.  The only lane that moves is layer 1's ROW-PROPORTIONAL lane, which
halves, minus one added charge for the negation pass.

THE FROZEN CONSTANT, AND WHY IT IS A FICTION
============================================
The incumbent prices every layer as 15.75 tiles of 4,096 rows = 64,512 rows.
For layers 2..32 that is the true row count: the sampled activation buffer is
``(2 * n_base, width)`` and every deep product consumes all of it.  For layer 1
it is a matmul the deployed code never performs.  Three observations, all read
out of the shipped source rather than remembered:

  (F1) ``n_base = 126 * 256 = 32,256``.
       [experiments/v31_guards/package_source/kerdock_v3_estimator.py:47]

  (F2) The layer-1 product writes 32,256 rows.  Its output buffer is the FRONT
       HALF of the activation array, sliced at ``n_base``:

           activation = fnp.empty((2 * self.n_base, mlp.width), ...)
           first_pre = self._first_sample_matmul(
               z, mlp.weights[0], out=activation[: self.n_base]
           )
       [fold3_estimator.py:86-89]

       The same holds on the unfolded path, where the product is written out in
       full: ``first_pre = z @ mlp.weights[0]`` with ``z`` of shape
       ``(n_base, width)``.  [base_estimator.py:66, 125]

  (F3) The back half is filled by NEGATION, before any ReLU:

           # Fill the disjoint antipodal half before overwriting first_pre.
           fnp.multiply(first_pre, -1.0, out=x[self.n_base :])
           fnp.maximum(x[self.n_base :], 0.0, out=x[self.n_base :])
           fnp.maximum(first_pre, 0.0, out=x[: self.n_base])
       [fold3_estimator.py:94-97]

       and on the unfolded path the same thing spelled as one concatenate:
           x = fnp.concatenate((maximum(first_pre, 0.0), maximum(-first_pre, 0.0)))
       [base_estimator.py:126-129]

The project's own handoff states the discrepancy in one sentence, and names the
doubled figure as a PRICING convention rather than a computation:

    "the code's output is (32256, 256) with antipodes by negation.  Priced at
     the doubled count, direct(64512,256,256) = 8,439,201,792 -- which is
     exactly the 8.4392B direct baseline the entire Strassen lineage uses ...
     Same formula, two row counts."
    [core/CODEX_HANDOFF_20260810.md, "Antipodal accounting" paragraph]

The suite incumbent inherited the doubled row count.  This tier bills the row
count the code has.

EXACTNESS IDENTITY
==================
The identity is not an equivalence between two routes; it is the observation
that only ONE route exists and the incumbent priced the other one.  The route
this tier bills is fold3_estimator.py:86-97, line for line: one product over
``z`` (32,256 rows), one negation pass over its output, two ReLU passes over the
64,512-row buffer.  Its results are the deployed results by construction, so
"identical results" is satisfied by identity rather than by argument.

For completeness, the fiction the incumbent bills would also have agreed, and
exactly, which is why this tier is a pure accounting correction and not a route
change.  The network is bias-free [core/CORPUS.md:15; the deployed ``MLP``
carries ``weights`` and no bias term], so layer 1 is linear and the antipodal
partner of design row ``u`` has preactivation ``(-u) W = -(u W)`` over the
reals.  Over f32 the agreement is bit-exact, not merely real-valued: IEEE-754
round-to-nearest is an odd function, ``RN(-t) = -RN(t)``, and every operation in
a dot product or in a Winograd schedule (multiply, add, subtract) is
sign-symmetric.  So negating one operand negates every intermediate and the
result, bit pattern for bit pattern, in the same accumulation order.  The single
edge case is the sign of zero -- an accumulation that cancels to ``+0.0`` on one
side lands on ``-0.0`` on the other -- and it cannot survive the very next
operation the code performs: ``fnp.maximum(v, 0.0)`` maps both zeros to the same
value, and the network is bias-free so no later constant can separate them.
``_selfcheck`` runs both halves of this: the integer identity, and the float
odd-symmetry including the signed-zero case and its collapse under ReLU.

WHAT MOVES, AND WHAT PROVABLY DOES NOT
======================================
Write  call = 303,096,592 (tier 7 at 4096, 256, 256),
       W    = 1,915,152   (the hoisted W-side stack, tier 3's measured lane),
       row(m) = call(m) - W  (the row-proportional part, exactly linear in m).

  layer 1, THIS TIER:
      7 * row(4096) + row(3584)   (32,256 rows)      2,371,803,840
      W-side stack, ONCE                                 1,915,152
      antipodal negation pass, 32,256 x 256              8,257,536
                                                    ----------------
                                                     2,381,976,528
      layer 1 under tier 3 (generic)                 4,745,522,832
      saving                                         2,363,546,304

  layers 3..32 (30 of them), tier 3's generic layer, unchanged:
      15.75 * row(4096) + W        each              4,745,522,832
                                                   142,365,684,960

  layer 2, tier 2's CReLU route with tier 3's hoist, unchanged:
                                                     2,547,651,536

  total                                            147,295,313,024
  incumbent (tier 3)                               149,658,859,328
  saving per net                                     2,363,546,304

Disjointness, so nothing is deducted twice:

  * From tier 3.  Tier 3 moved the W-STACK lane only: 496.25 stacks per net down
    to 32.  This tier leaves that lane bit-for-bit alone -- layer 1 still pays
    exactly one stack, the net still pays exactly 32 -- and moves only the
    ROW-PROPORTIONAL lane, which tier 3 asserted it had left untouched.  The two
    lanes are the two terms of an affine function that tier 3 measured apart;
    they cannot overlap.  ``_selfcheck`` asserts the stack lane is identical to
    tier 3's and that the whole delta lives in the row lane.
  * From tier 2.  Tier 2 moved layer 2 and only layer 2.  This tier moves layer
    1 and only layer 1.  ``_selfcheck`` asserts every one of tier 2's layer-2
    terms reappears here at its own value: 2,371,803,840 of even-channel row
    work, 1,915,152 of stack, 8,257,536, 65,536, 33,488,896, 115,605,504 and
    16,515,072.
  * From tier 1, which was REJECTED.  Tier 1 claimed layer 1 costs a butterfly
    (115,605,504) instead of a matmul.  This tier claims nothing of the kind and
    takes no butterfly credit at layer 1: it charges layer 1 the FULL generic
    per-row Winograd price for 32,256 rows, which for the deployed width-256
    path is an overcharge of more than twenty to one against the butterfly the
    code actually runs.  The rejected claim is not re-litigated, and this tier
    is orthogonal to it -- tier 1's premise was that "layer 1 consumes those
    [64,512] rows directly", which (F2)/(F3) contradict, so if the FWHT claim
    were ever revived it would compose with this one by acting on 32,256 rows.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The negation pass is CHARGED at full price, 32,256 x 256 = 8,257,536, though
    a sign flip is the cheapest operation on the machine and the incumbent bills
    no elementwise work anywhere.  It is the one op present in the deployed route
    and absent from the incumbent's doubled-matmul fiction, so it is charged.
  * The two ReLU passes are charged to NEITHER route, because both routes run
    exactly the same two passes over the same 64,512 rows.  Charging them here
    would inflate this tier's bill relative to the incumbent's for no reason and
    would break the comparison; leaving them out of both is the neutral choice.
  * Layer 1 keeps a full W-side operand stack, 1,915,152, although the deployed
    width-256 layer-1 hook is a phased-WHT butterfly that builds no Winograd
    stack at all.
  * The exact tiling and the linear convention agree here to the FLOP, so no
    rounding is taken in either direction: 32,256 rows tile as 7 full 4,096-row
    calls plus one 3,584-row call, and because row(m) is exactly proportional to
    m, ``7 * row(4096) + row(3584) == 7.875 * row(4096)`` exactly.
    ``_selfcheck`` asserts that equality rather than assuming it.
  * No credit is taken for the halved layer-1 output buffer, the halved
    first-product traffic, or the 8 fewer row blocks.  Only the arithmetic moves.

NO APPROXIMATION, NO FLAG
=========================
No value is approximated, no rank is reduced, no term is dropped, and no
summation is reordered.  This tier changes the ROW COUNT ATTRIBUTED to a product
the code already performs at that row count; it changes nothing about what is
multiplied, in what order, or at what precision.  The certified per-call floor
(303,096,592 at anonymous (4096, 256, 256)) is untouched: no op inside any call
is rescheduled or reweighted, and the per-call price is used verbatim, at both
4,096 and 3,584 rows, exactly as tiers 2 and 3 use it.  Every op counted here is
one f32 multiply, add, subtract or copy priced at 1.  No f32 repricing, no
compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
or new dispatch.  This one adds none of the three, because the shape it bills is
the shape already running:

  * There is no new route to implement.  fold3_estimator.py already computes the
    first product at 32,256 rows and already fills the antipodal half by
    negation; this tier writes down what that costs.  The residual schedule after
    the change is byte-identical to the residual schedule before it, so the
    metered win has nothing to be repaid out of.
  * The negation is a single contiguous strided pass over 8.25M f32 with unit
    stride in and out, fused in the deployed code with the ReLU that follows it
    on the same half-buffer.  It is memory-bound and already resident: the
    32,256 x 256 output has just been written by the product.  What it replaces
    would have been a second 32,256-row GEMM reading the same weight matrix.
  * Kernel sizes do not shrink.  The layer-1 product keeps BLOCK_ROWS = 4,096 and
    the same 7-full-blocks-plus-3,584 tiling that tier 2's layer-2 even channel
    already runs; the tail block is the same 3,584 rows the deployed operator
    already handles at every 32,256-row product.  No block smaller than 3,584
    rows is introduced anywhere.
  * Peak memory falls rather than rising: the layer-1 product's output region is
    ``activation[:n_base]``, half the buffer, and the negation writes into the
    other half that is allocated regardless.  Nothing new is allocated.
  * The win scales with the design, not against it.  A larger frame count means
    more base rows and the same one negation pass per row, so the ratio between
    the halved matmul and the added elementwise pass improves with size; it never
    fragments.
  * Layer 2's butterfly, precompute, |z| pass and recombination, and layers
    3..32's generic shape, are carried through verbatim from tiers 2 and 3.  This
    tier adds exactly zero new seams to the schedule.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from dataclasses import dataclass

_T7_PATH = "corpus/whestbench/headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py"

# Production shape, observed in kerdock_v3_estimator.py and CODEX_HANDOFF Sec.3.
FRAMES = 126                      # phase_stop - phase_start = 128 - 2
WIDTH = 256                       # ctx.width
BASE_ROWS = FRAMES * WIDTH        # n_base = 126 * 256 = 32,256
DESIGN_ROWS = 2 * BASE_ROWS       # antipodally doubled = 64,512
LAYERS = 32
TILE_ROWS = 4096                  # BLOCK_ROWS in row_blocked_winograd.py

# Tier 2's layer-2 auxiliary terms, restated locally so this file stands alone.
# FlopScope v0.10 butterfly convention: 1 seed multiply + log2(n) stages at
# 1.5/element (copyto + add + subtract, movement billed at 1) + 1 final scale.
_BUTTERFLY_PER_ELEMENT = 14


def _t7():
    spec = importlib.util.spec_from_file_location("t7base", _T7_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def direct_cost(m: int, k: int, n: int) -> int:
    """The source's own counterfactual price, cost_model.py:8-11."""
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def _selected_levels(strategy: str) -> int:
    """Depth the tier-7 sweep chose, read off its own strategy string."""
    head, _, _rest = strategy.partition("_inplaceleaf")
    tag = head.rsplit("_", 1)[-1]
    if not tag.startswith("l") or not tag[1:].isdigit():
        raise ValueError(f"cannot read a Winograd depth from {strategy!r}")
    return int(tag[1:])


def weight_side_stack_cost(t7, k: int = WIDTH, n: int = WIDTH,
                           m: int = TILE_ROWS) -> int:
    """The m-independent lane of the crowned call bill: the W-side stack."""
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(k, n, levels)
    return cost


@dataclass(frozen=True)
class SuiteBill:
    strategy: str
    call_total: int
    weight_stack: int
    row_part_full: int
    row_part_tail: int
    layers: int
    layer1_row_part: int
    layer1_negation: int
    layer1_total: int
    generic_layer: int
    generic_layers_total: int
    layer2_even_rows: int
    layer2_aux: int
    layer2_total: int
    total: int

    def breakdown(self) -> dict:
        return {
            "weight_side_stack_per_layer": self.weight_stack,
            "row_part_per_full_tile": self.row_part_full,
            "layer1_base_row_part_32256": self.layer1_row_part,
            "layer1_weight_side_stack": self.weight_stack,
            "layer1_antipodal_negation": self.layer1_negation,
            "layer1_total": self.layer1_total,
            "generic_layer_total": self.generic_layer,
            "generic_layers_3_to_32": self.generic_layers_total,
            "layer2_even_channel_row_part": self.layer2_even_rows,
            "layer2_weight_side_stack": self.weight_stack,
            "layer2_auxiliary_terms": self.layer2_aux,
            "layer2_total": self.layer2_total,
            "total": self.total,
        }


def _layer2_auxiliary_cost() -> int:
    """Tier 2's non-matmul layer-2 terms, unchanged and re-derived here."""
    abs_pass = BASE_ROWS * WIDTH                             # 8,257,536
    halfscale = WIDTH * WIDTH                                #    65,536
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)            # 33,488,896
    butterfly = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH   # 115,605,504
    recombine = DESIGN_ROWS * WIDTH                          # 16,515,072
    return abs_pass + halfscale + precompute + butterfly + recombine


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Layer 1 priced at the design's 32,256 base rows plus one negation pass."""
    t7 = _t7()
    bill_full = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    bill_tail = t7.inplace_verbatim_leaves_candidate_bill(
        BASE_ROWS % TILE_ROWS, k, n
    )
    if bill_full.core_k != bill_tail.core_k or bill_full.core_n != bill_tail.core_n:
        raise ValueError("full and tail calls do not share a right-hand stack")
    if _selected_levels(bill_full.strategy) != _selected_levels(bill_tail.strategy):
        raise ValueError("full and tail calls sit at different Winograd depths")

    call = bill_full.total
    w_stack = weight_side_stack_cost(t7, k, n, m)
    row_full = call - w_stack
    row_tail = bill_tail.total - w_stack

    # --- generic layers 3..32: tier 3's layer, carried verbatim ---------------
    generic_rows = int(row_full * DESIGN_ROWS // m)
    if generic_rows * m != row_full * DESIGN_ROWS:
        raise ValueError("tile count is not exact; refusing a rounded bill")
    generic_layer = generic_rows + w_stack
    generic_total = (LAYERS - 2) * generic_layer

    # --- layer 1: the design's BASE rows, 32,256, plus the negation pass ------
    full_tiles, remainder = divmod(BASE_ROWS, TILE_ROWS)
    if remainder == 0:
        raise ValueError("base row count is not the frozen 7 x 4096 + tail")
    base_rows_part = full_tiles * row_full + row_tail
    negation = BASE_ROWS * WIDTH
    layer1 = base_rows_part + w_stack + negation

    # --- layer 2: tier 2's CReLU route with tier 3's hoist, carried verbatim --
    layer2_even_rows = base_rows_part
    layer2_aux = _layer2_auxiliary_cost()
    layer2 = layer2_even_rows + w_stack + layer2_aux

    return SuiteBill(
        "layer1_base_row_count",
        call,
        w_stack,
        row_full,
        row_tail,
        LAYERS,
        base_rows_part,
        negation,
        layer1,
        generic_layer,
        generic_total,
        layer2_even_rows,
        layer2_aux,
        layer2,
        generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  Two halves: the integer identity (the antipodal rows
# ARE the negation of the base rows, so no second product exists), and the
# float odd-symmetry of round-to-nearest including the signed-zero edge case.
# ---------------------------------------------------------------------------


def _rng(seed: int):
    state = seed

    def nxt(lo: int, hi: int) -> int:
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return lo + state % (hi - lo + 1)

    return nxt


def _matmul(A: list, B: list) -> list:
    inner = len(B)
    return [[sum(A[i][t] * B[t][j] for t in range(inner))
             for j in range(len(B[0]))] for i in range(len(A))]


def deployed_layer1(base: list, W: list) -> tuple:
    """fold3_estimator.py:86-97, transcribed.  ONE product over ``base``."""
    products = 0
    pre = _matmul(base, W)                      # activation[:n_base]
    products += 1
    negations = len(pre) * len(pre[0])
    back = [[-v for v in row] for row in pre]   # multiply(first_pre, -1.0)
    front = [[v if v > 0 else 0 for v in row] for row in pre]
    back = [[v if v > 0 else 0 for v in row] for row in back]
    return front + back, products, negations


def _selfcheck() -> None:
    t7 = _t7()
    call_of = t7.inplace_verbatim_leaves_candidate_bill

    # ---- 1. Shape anchors, from the deployed source's own constants. --------
    assert BASE_ROWS == 32256, BASE_ROWS
    assert DESIGN_ROWS == 64512, DESIGN_ROWS
    assert DESIGN_ROWS == 15.75 * TILE_ROWS
    assert BASE_ROWS == 7 * TILE_ROWS + 3584
    assert BASE_ROWS == 7.875 * TILE_ROWS

    # ---- 2. The call bill is affine in m; the constant is the W-side lane. ---
    probes = (512, 1024, 2048, 3072, 3584, 4096)
    bills = {rows: call_of(rows, WIDTH, WIDTH) for rows in probes}
    lo, hi = probes[0], probes[-1]
    slope_num, slope_den = bills[hi].total - bills[lo].total, hi - lo
    constant_num = bills[hi].total * slope_den - slope_num * hi
    assert constant_num % slope_den == 0, "affine fit is not integral"
    constant = constant_num // slope_den
    for rows in probes:
        assert slope_num * rows + constant * slope_den == bills[rows].total * slope_den, (
            f"call bill is not affine in m at m={rows}")
    assert constant == 1915152, constant

    params = tuple(inspect.signature(t7.best_operand_grade).parameters)
    assert params == ("a_dim", "b_dim", "levels"), params
    levels = _selected_levels(bills[TILE_ROWS].strategy)
    assert levels == 6, bills[TILE_ROWS].strategy
    w_stack, _grade = t7.best_operand_grade(WIDTH, WIDTH, levels)
    assert w_stack == constant, (w_stack, constant)

    # The row lane really is exactly proportional to m, so the exact tiling of
    # 32,256 rows and the 7.875-tile linear convention agree to the FLOP.
    row_full = bills[TILE_ROWS].total - w_stack
    row_tail = bills[3584].total - w_stack
    assert row_tail * TILE_ROWS == row_full * 3584, "row lane is not proportional"
    assert 7 * row_full + row_tail == (row_full * 63) // 8, "7 x + tail != 7.875 x"

    # ---- 3. THE IDENTITY, executed over the integers. -----------------------
    # The deployed route's ONE product is over the base rows; the antipodal half
    # is its negation.  Both routes give the same activation, so the incumbent's
    # second half-product buys nothing that the negation has not already bought.
    for rows, width, cols in ((5, 4, 3), (8, 8, 8), (3, 6, 5), (7, 3, 9)):
        nxt = _rng(40404 + rows * 131 + width * 17 + cols)
        base = [[nxt(-9, 9) for _ in range(width)] for _ in range(rows)]
        W = [[nxt(-9, 9) for _ in range(cols)] for _ in range(width)]

        deployed, deployed_products, negations = deployed_layer1(base, W)
        doubled = base + [[-v for v in row] for row in base]
        reference_pre = _matmul(doubled, W)
        reference = [[v if v > 0 else 0 for v in row] for row in reference_pre]

        assert deployed == reference, (
            f"negation route differs from the doubled product at "
            f"{rows}x{width}x{cols}")
        # The point being billed: one product over `rows`, not over `2*rows`.
        assert deployed_products == 1
        assert len(doubled) == 2 * rows
        assert negations == rows * cols, (negations, rows * cols)
        # And the doubled product really does cost twice as much, so the
        # incumbent's row count is the thing being corrected.
        assert direct_cost(2 * rows, width, cols) == 2 * direct_cost(rows, width, cols)

    # ---- 4. Float odd-symmetry, including the signed-zero edge case. --------
    # IEEE round-to-nearest is odd, so negating an operand negates every
    # intermediate bit-for-bit in the same accumulation order.
    nxt = _rng(90909)
    for _trial in range(200):
        a = [nxt(-10**6, 10**6) / 7.0 for _ in range(16)]
        b = [nxt(-10**6, 10**6) / 11.0 for _ in range(16)]
        acc_pos = 0.0
        acc_neg = 0.0
        for x, y in zip(a, b):
            acc_pos += x * y
            acc_neg += (-x) * y
        assert acc_neg == -acc_pos, (acc_neg, acc_pos)
    # The one place the bit patterns can differ is the sign of an exact zero,
    # and ReLU -- the very next deployed operation -- collapses it.
    cancelling = 1.5
    plus_zero = cancelling + (-cancelling)
    minus_zero = (-cancelling) + cancelling
    assert plus_zero == 0.0 and minus_zero == 0.0
    for z in (plus_zero, -plus_zero, minus_zero, -minus_zero):
        assert max(z, 0.0) == 0.0
        assert 1.0 + max(z, 0.0) == 1.0

    # ---- 5. Double-count gate: the crowned chain, recomputed from tier 7. ----
    call = bills[TILE_ROWS].total
    assert call == 303096592, call
    assert 504 * call == 152760682368                    # suite tier 0
    layer_slice = call * DESIGN_ROWS // TILE_ROWS
    assert layer_slice == 4773771324, layer_slice
    tier2_even = 7 * call + bills[3584].total
    assert tier2_even == 2387125056, tier2_even
    assert _layer2_auxiliary_cost() == 173932544
    tier2 = 31 * layer_slice + tier2_even + _layer2_auxiliary_cost()
    assert tier2 == 150547968644, tier2                  # suite tier 2
    generic_layer_t3 = (row_full * DESIGN_ROWS) // TILE_ROWS + w_stack
    tier3_layer2 = tier2_even - 8 * w_stack + w_stack + _layer2_auxiliary_cost()
    tier3 = 31 * generic_layer_t3 + tier3_layer2
    assert generic_layer_t3 == 4745522832, generic_layer_t3
    assert tier3_layer2 == 2547651536, tier3_layer2
    assert tier3 == 149658859328, tier3                  # suite tier 3, incumbent

    bill = suite_bill_per_net()
    assert bill.weight_stack == w_stack == 1915152
    assert bill.row_part_full == 301181440, bill.row_part_full
    assert bill.row_part_tail == 263533760, bill.row_part_tail

    # (a) Disjoint from tier 3: the STACK lane is untouched, 32 per net.
    stacks_here = LAYERS * bill.weight_stack
    assert bill.total - stacks_here == (
        30 * (bill.generic_layer - w_stack)
        + (bill.layer1_total - w_stack)
        + (bill.layer2_total - w_stack))
    tier3_stacks = LAYERS * w_stack
    assert stacks_here == tier3_stacks, "the W-stack lane moved; tier 3 overlap"

    # (b) Disjoint from tier 2: every layer-2 term reappears at its own value.
    assert bill.layer2_even_rows == tier2_even - 8 * w_stack == 2371803840
    assert bill.layer2_aux == _layer2_auxiliary_cost() == 173932544
    assert bill.layer2_total == tier3_layer2 == 2547651536

    # (c) Disjoint from tier 1 (rejected): NO butterfly credit at layer 1.  The
    #     layer-1 row charge is the full generic per-row price over 32,256 rows,
    #     more than twenty times the butterfly the deployed hook actually runs.
    butterfly_layer1 = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH
    assert butterfly_layer1 == 115605504
    assert bill.layer1_row_part > 20 * butterfly_layer1, (
        "layer 1 is being credited a butterfly; that is tier 1's rejected claim")

    # (d) The whole delta lives in layer 1's row lane, minus the negation.
    assert bill.layer1_row_part == bill.layer2_even_rows          # same 32,256
    assert bill.layer1_total == bill.layer1_row_part + w_stack + bill.layer1_negation
    assert bill.layer1_negation == BASE_ROWS * WIDTH == 8257536
    delta = tier3 - bill.total
    assert delta == (generic_layer_t3 - w_stack) - bill.layer1_row_part - bill.layer1_negation
    # 15.75 tiles of row work down to 7.875, then the negation added back.
    assert delta == (63 * row_full) // 8 - bill.layer1_negation
    assert 8 * ((63 * row_full) // 8) == 63 * row_full, "7.875 x row is integral"
    assert delta == 2363546304, delta

    # ---- 6. Conservativeness gate. -----------------------------------------
    # The negation pass is charged, not free; dropping it would pay 8,257,536
    # more, and that is the amount deliberately left on the table.
    assert bill.total > (30 * generic_layer_t3 + bill.layer1_row_part + w_stack
                         + bill.layer2_total)
    # Layer 1 keeps a full W-side stack even though the deployed width-256 hook
    # builds no Winograd stack at all.
    assert bill.weight_stack > 0
    # Exact tiling of 32,256 rows at 4,096 is 7 full calls plus one 3,584 tail;
    # no block smaller than 3,584 rows is introduced.
    exact_calls, exact_tail = divmod(BASE_ROWS, TILE_ROWS)
    assert (exact_calls, exact_tail) == (7, 3584)
    assert call_of(exact_tail, WIDTH, WIDTH).total == bills[3584].total

    # ---- 7. The bill's own arithmetic. --------------------------------------
    assert bill.layer1_total == 2381976528, bill.layer1_total
    assert bill.generic_layer == 4745522832, bill.generic_layer
    assert bill.generic_layers_total == 142365684960, bill.generic_layers_total
    assert bill.layer2_total == 2547651536, bill.layer2_total
    assert bill.total < tier3 < tier2
    assert bill.total == 147295313024, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: affine measurement of the call bill, the module's own "
          "W-side lane, exact proportionality of the row lane, executed integer "
          "identity of the negation route against the doubled product, float "
          "odd-symmetry of round-to-nearest with the signed-zero case collapsed "
          "by ReLU, double-count gates against tiers 1/2/3, and the "
          "conservativeness gate all pass")
    b = suite_bill_per_net()
    incumbent = 149658859328
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>34} {value:>15,}")
    print(f"  {'incumbent (tier 3)':>34} {incumbent:>15,}")
    print(f"  {'saving':>34} {incumbent - b.total:>15,}")
    print(f"  ratio vs tier 3                    {b.total / incumbent:.9f}")
    print("total:", b.total)
