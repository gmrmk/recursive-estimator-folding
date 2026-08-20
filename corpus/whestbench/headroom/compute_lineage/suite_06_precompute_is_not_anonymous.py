"""Suite tier 6: the layer-2 odd-channel precompute is not a stranger to the
route, so it stops being billed as an anonymous direct GEMM.

ONE SUBSTANTIVE CHANGE
======================
After tier 5 the suite bills exactly one matrix product at the DIRECT price.
Every other product in the suite -- all 32 layer products, the layer-1 design
product, layer 2's even channel -- is billed at the crowned tier-7 call price.
The single exception is tier 2's odd-channel precompute:

    precompute = direct_cost(WIDTH, WIDTH, WIDTH)          # 33,488,896
    [suite_05_design_operand_stack_cross_net.py, _layer2_auxiliary_cost]

That constant is the frozen one this tier unfreezes.  The precompute is the
product ``W0 @ W1h`` of two matrices the suite ALREADY Winograd-transforms in
the same prediction, at depths that contain the depth this product wants.  One
sentence states the change:

    the precompute is not anonymous, so it is billed as the route's own
    product -- tier 7's depth-5 Winograd call -- and its two operand lanes are
    the level-5 intermediates of two stacks the suite has already paid for.

Nothing else moves.  Layer 1 keeps tier 4's 32,256 base rows and tier 5's
suite-once design stack; layer 2 keeps tier 2's CReLU route with tier 3's
hoist; layers 3..32 keep tier 3's generic layer.  Every one of those terms
reappears below at its own value and ``_selfcheck`` asserts each.

THE FROZEN CONSTANT, AND WHY IT IS THE ONE LEFT
===============================================
LAW 2 names the ways the suite ladder may break uniformity.  Before writing
this tier the remaining candidates were enumerated and probed, and all but one
are shut:

  (S1) The generic layer cannot move.  Tier 3 bills a generic layer at
       4,745,522,832, and that is EXACTLY ``candidate_bill(64512, 256, 256)``:
       an exhaustive sweep of every lawful depth L = 2..8 at the layer's own
       shape, under tier 7's own per-lane grading optimiser, is run inside
       ``_selfcheck`` and depth 6 wins at that shape as it does at 4,096 rows.
       The 30 generic layers are 96.8% of the bill and they sit on tier 7's own
       floor for their own shape; moving them means mutating the within-call
       schedule, which LAW 2 forbids.
  (S2) Cross-net amortization is exhausted.  The design is the only operand in
       the whole route that is invariant across nets, and its only lane -- the
       layer-1 A-side stack -- is tier 5's.  Every other operand (W0, W1, the
       Haar rotation, |P|, every activation) is a function of the net.
  (S3) Cross-tile amortization is exhausted.  Tier 3's hoist already makes the
       layer one call rather than 15.75; ``_selfcheck`` asserts the layer bill
       equals the single-call bill at 64,512 rows to the FLOP.
  (S4) The design-boundary algebra does not recurse.  The corpus states its own
       boundary: "at layer >= 3 the pair difference relu(a+b) - relu(a-b) is no
       longer globally linear ... CReLU pays exactly once, at the design
       boundary" [headroom/FWHT_SPLICE_STAGED_20260818.md].
  (S5) Two shape specializations were probed and open the WRONG way; both are
       reported here rather than hidden, and neither is taken.
       (a) Re-orienting layer 1 as ``H @ [Phi_1 W0 | ... | Phi_126 W0]`` --
           legitimate, since the design's frames all share the same Hadamard
           factor -- transposes which operand is net-invariant.  The operand
           and decode lanes are symmetric in their two dimensions (asserted in
           ``_selfcheck``), so the total is unchanged, but the hoistable
           net-invariant lane collapses from 241,309,152 to 1,915,152.  The
           current orientation is strictly better and is kept.
       (b) The deployed terminal fold (source layers 29..31, this model's
           layers 30..32) is billed by the incumbent as three generic layers.
           Its full-row products are bare ``@`` calls at direct price, and with
           every column in the kink regime they expand to
           ``N*256*k30 + N*(256+k30)*k31 + N*(256+k30+k31)*k32`` -- six
           layer-equivalents at direct price.  The incumbent's three-generic-
           layer charge is therefore a FLOOR, not a ceiling, and no win is
           available there.  This tier takes none and does not disturb it.

  That leaves exactly one product in the suite that is priced by a rule the
  rest of the suite does not use.  It is this tier.

EXACTNESS IDENTITY
==================
The route computes the identical result because Winograd's identity is exact in
exact arithmetic and because an operand stack is a function of its operand
alone.  Write the precompute the way tier 7's depth-5 schedule does:

    stack_L = T(W0,  5)      the 7^5 left  operand blocks of W0
    stack_R = T(W1h, 5)      the 7^5 right operand blocks of W1h
    leaves  = [ stack_L[i] @ stack_R[i] for i in range(7**5) ]
    G       = D(leaves)      the decode lane
    G == W0 @ W1h

exactly, and the odd channel that consumes G is unchanged.  Two claims carry
the bill, and both are executed below rather than asserted in prose.

  (E1) THE ROUTE.  A depth-L Winograd product of the operand stacks equals the
       direct product.  Executed over integers, where "exact" is literal, at
       depths 1, 2 and 3 on real matrices.
  (E2) THE PREFIX.  The depth-(L-1) operand set of a matrix is LITERALLY the
       level-(L-1) intermediate of its depth-L operand set -- the same blocks,
       in the same order, with the same values -- because the recursion that
       builds level j reads only level j-1 and is stopped, not changed, by the
       depth parameter.  Executed by building both trees and comparing them
       block for block.
       The prices agree with the structure: tier 7's optimal grading for a
       (256, 256) operand lane is all-alternative at BOTH depths (asserted),
       and under a fixed grading ``inplace_operand_cost`` is a sum over
       j = 1..L, so
           cost(256,256,6) - cost(256,256,5) = 1,915,152 - 1,092,032
                                             = 823,120
                                             = 7**5 * 3 * 4 * 4 + 4**5 * 4 * 4
       which is the level-6 term alone.  Levels 1..5 are shared identically.

Consequently, when the suite builds T(W0, 6) as layer 1's W-side stack, the
blocks of T(W0, 5) have been written; and when it builds T(W1h, 6) as layer 2's
W-side stack, the blocks of T(W1h, 5) have been written.  The precompute reads
those blocks.  It does not recompute them, and it does not skip them: they are
computed, once, inside a metered ``predict``, and they are charged -- to layers
1 and 2, where the suite already charges them.  Nothing is moved out of
FlopScope's view; one prefix simply stops being written twice.

The ordering the identity needs is the ordering the route already has: layer 1
precedes layer 2, and within layer 2 the even channel's W-side stack precedes
the precompute that feeds the odd channel.

Rounding: this is a reschedule-class route, the same class as every other
product in this suite.  The whole suite already evaluates its layer products by
Winograd rather than by a direct GEMM, and tier 2's accepted route already
replaces a direct design product with an FWHT.  Charging the ONE remaining
product the same route the other thirty-two get is a removal of an
inconsistency, not the introduction of a new class of approximation.  No value
is approximated, no rank is reduced, no term is dropped.

WHAT MOVES, AND BY HOW MUCH
===========================
  the precompute, as tier 2 bills it (direct 256x256x256)       33,488,896
  the precompute, as the route's own depth-5 Winograd call:
      leaves   7**5 * direct(8, 8, 8)                           16,134,720
      A-side lane  T(W0,  5)   -- prefix of layer 1's T(W0,  6)          0
      W-side lane  T(W1h, 5)   -- prefix of layer 2's T(W1h, 6)          0
      decode lane                                                2,102,144
                                                              ------------
                                                                18,236,864
  saving                                                        15,252,032

  layer 2 auxiliary terms
      abs pass                                                   8,257,536
      half scale                                                    65,536
      precompute (THIS TIER)                                     18,236,864
      butterfly (odd channel)                                   115,605,504
      recombine                                                  16,515,072
                                                              ------------
                                                               158,680,512

  layer 1, tier 4 + tier 5, unchanged                          2,140,667,376
  layer 2, tier 2 + tier 3 with the new aux                    2,532,399,504
  layers 3..32, tier 3's generic layer, unchanged            142,365,684,960
                                                            ---------------
  per-net total                                              147,038,751,840
  incumbent (tier 5)                                         147,054,003,872
  saving per net                                                  15,252,032

  suite-level, exactly, for a suite of N nets, tier 5's convention kept:
      suite_total(N) = N * 147,038,751,840 + 241,309,152
  The one-time design-stack charge is carried through unchanged and stays a
  named field of the breakdown; it is not touched by this tier.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 5.  Tier 5 moved the layer-1 A-side lane, an operand of the
    DESIGN, onto the suite-once axis.  This tier moves nothing off the per-net
    axis; ``suite_once`` is bit-identical to tier 5's and ``_selfcheck``
    asserts it, along with layer 1's every term.
  * From tier 3.  Tier 3 moved the W-side lane from per-tile to per-layer.
    This tier CONSUMES tier 3's stacks and adds nothing to them: the count of
    W-side stacks stays 32 per net at 1,915,152 each, asserted.  What the
    precompute waives is its OWN operand lanes, which tier 3 never billed and
    which the incumbent bills at zero because it bills the precompute direct --
    i.e. the waiver removes work that was never separately charged, and the
    delta is taken only against the direct price.  ``_selfcheck`` asserts the
    delta equals ``33,488,896 - (leaves_5 + decode_5)`` to the FLOP.
  * From tier 4.  Tier 4 changed layer 1's row count.  This tier does not touch
    a row count anywhere; layer 1 and layer 2's even channel keep 32,256 rows
    and layers 3..32 keep 64,512, all asserted.
  * From tier 2.  Every other layer-2 auxiliary term -- abs pass, half scale,
    butterfly, recombine -- reappears at tier 2's own value, asserted
    individually.  The butterfly is NOT re-priced and the odd channel keeps
    tier 2's conservative 14-operations-per-element convention.
  * From tier 1, which was REJECTED.  No butterfly credit is taken at layer 1.
    Layer 1 still pays full Winograd leaves and decode over 32,256 rows, and
    ``_selfcheck`` asserts that charge exceeds eighteen butterflies.  The
    rejected claim is not revived and nothing here depends on it.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The decode lane of the precompute is charged in full, 2,102,144.  It
    consumes leaf products, which are net-dependent, so it cannot ride any
    stack.
  * The leaves lane is charged in full, 16,134,720, though its two factors are
    both matrices the suite transforms elsewhere: the leaves are PRODUCTS, and
    products of two per-net matrices amortize over nothing.
  * The depth is not chosen by this tier.  It is read off tier 7's own strategy
    string for the shape (256, 256, 256), which selects depth 5; ``_selfcheck``
    also brute-forces depths 2..8 at that shape and confirms 5 is the minimum,
    so no depth is being cherry-picked to suit the waiver.
  * The prefix waiver is claimed at exactly one product and exactly one depth
    pair (5 inside 6).  It is NOT claimed for the 30 generic layers, which have
    one product per weight matrix and therefore no second depth to nest into;
    ``_selfcheck`` asserts the generic layer is bit-identical to tier 3's.
  * The terminal-fold and layer-1 re-orientation doors, probed above, are left
    exactly where they were found.

NO APPROXIMATION, NO FLAG
=========================
No value is approximated, no rank is reduced, no term is dropped, and no sum is
reordered within any call.  The certified per-call floor (303,096,592 at the
anonymous (4096, 256, 256)) is untouched: no operation inside any anonymous call
is rescheduled or reweighted, and ``_selfcheck`` re-derives that figure from
tier 7 and asserts it.  Every operation counted is one f32 multiply, add,
subtract or copy priced at 1.  No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces smaller kernels, extra
passes, or extra dispatch.  This one forces none of the three.

  * Dispatch count is unchanged.  The direct precompute is one GEMM call.  The
    depth-5 batched Winograd precompute is also ONE call -- a single batched
    matmul over a leading axis of 7**5 = 16,807 leaves, exactly the shape of
    dispatch the crowned route already issues 32 times per net
    (``fnp.matmul(lc, rc, out=products)``, row_blocked_winograd.py:458).  No
    Python-level loop over leaves is introduced.
  * Kernel granularity goes UP, not down.  This product's leaf blocks are
    8 x 8 by 8 x 8.  The suite's own certified per-call route runs leaves of
    (64, 4) by (4, 4) at every one of its 32 layers.  The new blocks are the
    coarsest in the whole schedule, so nothing here is the smallest kernel in
    the process and nothing is fragmented relative to what already runs.
  * The waiver adds zero work of any kind.  It is a read of blocks that are
    already resident, in the layout they were written in; it removes two
    operand-stack builds and adds no pass, no copy, and no gather.
  * Traffic falls with the FLOPs.  The waived lanes were WRITE traffic
    (1,092,032 block-element writes each); after the waiver those blocks are
    only READ, and they were going to be read anyway.  There is no
    read-amplification term for the win to be repaid out of.
  * The cost is residency, bounded and named: T(W0, 5) is 7**5 blocks of
    8 x 8 f32 = 1,075,648 elements = 4.30 MB, and T(W1h, 5) is the same, so
    8.60 MB total, against a 4 GiB per-array cap and a 64 GB process cap.
    T(W1h, 5) lives inside one layer; T(W0, 5) is held from layer 1 to layer 2
    within a single ``predict``, a shorter lifetime than the design stack tier 5
    already holds.  The memory-bounded fallback, if residency ever bound, is to
    waive only the W1h lane (same layer, no cross-layer hold), which recovers a
    strict subset of this win and is a dial, not a different route.
  * Exposure is bounded by construction.  The retimed product is 0.023% of the
    per-net bill, so even a pathological slope on this one call could not repay
    a material fraction of the suite's metered win.
  * Layers 1, 3..32 are carried through verbatim.  This tier adds exactly zero
    new seams to the schedule.

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

# Tier 2's layer-2 auxiliary convention, restated locally so this file stands
# alone.  FlopScope v0.10 butterfly convention: 1 seed multiply + log2(n) stages
# at 1.5/element (copyto + add + subtract, movement billed at 1) + 1 final scale.
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
    """The m-independent lane of the crowned call bill: the W-side (k, n) stack."""
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(k, n, levels)
    return cost


def design_side_stack_cost(t7, m: int, k: int = WIDTH) -> int:
    """Tier 5's lane: the A-side (m, k) stack, a pure function of the design."""
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, WIDTH)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(m, k, levels)
    return cost


def precompute_lanes(t7) -> tuple:
    """Lane decomposition of the odd-channel precompute at its own crowned depth.

    Returns ``(levels, leaves, a_lane, w_lane, decode, charged)`` where
    ``charged = leaves + decode``: the two operand lanes are the level-5
    intermediates of the depth-6 stacks layers 1 and 2 already build, so this
    product writes neither of them.
    """
    bill = t7.inplace_verbatim_leaves_candidate_bill(WIDTH, WIDTH, WIDTH)
    levels = _selected_levels(bill.strategy)
    block = 1 << levels
    leaves = 7 ** levels * t7.direct_cost(
        WIDTH // block, WIDTH // block, WIDTH // block)
    a_lane, a_grade = t7.best_operand_grade(WIDTH, WIDTH, levels)
    w_lane, w_grade = t7.best_operand_grade(WIDTH, WIDTH, levels)
    decode, _grade = t7.best_decode_grade(WIDTH, WIDTH, levels)
    if leaves + a_lane + w_lane + decode != bill.total:
        raise ValueError("the precompute lane decomposition does not close")
    if a_grade != w_grade:
        raise ValueError("the two square operand lanes disagree on grading")
    return levels, leaves, a_lane, w_lane, decode, leaves + decode


@dataclass(frozen=True)
class SuiteBill:
    strategy: str
    call_total: int
    weight_stack: int
    row_part_full: int
    row_part_tail: int
    layers: int
    layer1_row_part_per_net: int
    layer1_design_stack_once: int
    layer1_negation: int
    layer1_total: int
    generic_layer: int
    generic_layers_total: int
    layer2_even_rows: int
    layer2_precompute_depth: int
    layer2_precompute: int
    layer2_precompute_waived: int
    layer2_aux: int
    layer2_total: int
    suite_once: int
    total: int

    def suite_total(self, n_nets: int) -> int:
        """Exact suite bill for ``n_nets`` nets.  No rounding anywhere."""
        if n_nets < 1:
            raise ValueError("a suite has at least one net")
        return n_nets * self.total + self.suite_once

    def amortized_numerator(self, n_nets: int) -> tuple:
        """Per-net mean as an exact fraction ``(numerator, denominator)``."""
        return self.suite_total(n_nets), n_nets

    def breakdown(self) -> dict:
        return {
            "weight_side_stack_per_layer": self.weight_stack,
            "row_part_per_full_tile": self.row_part_full,
            "layer1_leaves_plus_decode_32256": self.layer1_row_part_per_net,
            "layer1_weight_side_stack": self.weight_stack,
            "layer1_antipodal_negation": self.layer1_negation,
            "layer1_total_per_net": self.layer1_total,
            "generic_layer_total": self.generic_layer,
            "generic_layers_3_to_32": self.generic_layers_total,
            "layer2_even_channel_row_part": self.layer2_even_rows,
            "layer2_weight_side_stack": self.weight_stack,
            "layer2_precompute_depth": self.layer2_precompute_depth,
            "layer2_precompute_leaves_plus_decode": self.layer2_precompute,
            "layer2_precompute_operand_lanes_ridden": self.layer2_precompute_waived,
            "layer2_auxiliary_terms": self.layer2_aux,
            "layer2_total": self.layer2_total,
            "design_side_stack_charged_ONCE_to_the_suite":
                self.layer1_design_stack_once,
            "total": self.total,
        }


def _layer2_auxiliary_cost(precompute: int) -> int:
    """Tier 2's layer-2 non-matmul terms, with the precompute repriced.

    Only ``precompute`` moves.  ``abs_pass``, ``halfscale``, ``butterfly`` and
    ``recombine`` are tier 2's own values, re-derived here so this file stands
    alone, and ``_selfcheck`` asserts each against tier 2's figure.
    """
    abs_pass = BASE_ROWS * WIDTH                             #   8,257,536
    halfscale = WIDTH * WIDTH                                #      65,536
    butterfly = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH   # 115,605,504
    recombine = DESIGN_ROWS * WIDTH                          #  16,515,072
    return abs_pass + halfscale + precompute + butterfly + recombine


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: the odd-channel precompute is billed as the
    route's own depth-5 Winograd product, with both operand lanes ridden off
    the depth-6 stacks layers 1 and 2 already build."""
    t7 = _t7()
    bill_full = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    bill_tail = t7.inplace_verbatim_leaves_candidate_bill(
        BASE_ROWS % TILE_ROWS, k, n
    )
    if bill_full.core_k != bill_tail.core_k or bill_full.core_n != bill_tail.core_n:
        raise ValueError("full and tail calls do not share a right-hand stack")
    layer_levels = _selected_levels(bill_full.strategy)
    if layer_levels != _selected_levels(bill_tail.strategy):
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

    # --- layer 1: tier 4's rows with tier 5's suite-once stack, verbatim ------
    full_tiles, remainder = divmod(BASE_ROWS, TILE_ROWS)
    if remainder == 0:
        raise ValueError("base row count is not the frozen 7 x 4096 + tail")
    base_rows_part = full_tiles * row_full + row_tail
    design_stack = design_side_stack_cost(t7, BASE_ROWS, k)
    negation = BASE_ROWS * WIDTH
    layer1_rows_per_net = base_rows_part - design_stack
    layer1 = layer1_rows_per_net + w_stack + negation

    # --- layer 2: tier 2's CReLU route, tier 3's hoist, THIS TIER's precompute
    (pre_levels, pre_leaves, pre_a, pre_w, pre_decode,
     precompute) = precompute_lanes(t7)
    # The waiver's licence: both operand lanes are prefixes of stacks the suite
    # already builds at depth ``layer_levels``.  Refuse the bill unless the
    # nesting is real and the gradings agree on the shared levels.
    if pre_levels >= layer_levels:
        raise ValueError("the precompute depth does not nest inside the layers")
    for depth in (pre_levels, layer_levels):
        _cost, grade = t7.best_operand_grade(WIDTH, WIDTH, depth)
        if grade != frozenset():
            raise ValueError("square operand lanes are not all-alternative")
    shallow = t7.inplace_operand_cost(WIDTH, WIDTH, pre_levels, frozenset())
    deep = t7.inplace_operand_cost(WIDTH, WIDTH, layer_levels, frozenset())
    tail_levels = sum(
        7 ** (j - 1) * 3 * (WIDTH >> j) * (WIDTH >> j)
        + 4 ** (j - 1) * (WIDTH >> j) * (WIDTH >> j)
        for j in range(pre_levels + 1, layer_levels + 1)
    )
    if deep - shallow != tail_levels or shallow != pre_a or shallow != pre_w:
        raise ValueError("the depth-5 operand set is not a prefix of the depth-6")

    layer2_even_rows = base_rows_part
    layer2_aux = _layer2_auxiliary_cost(precompute)
    layer2 = layer2_even_rows + w_stack + layer2_aux

    return SuiteBill(
        "precompute_is_not_anonymous",
        call,
        w_stack,
        row_full,
        row_tail,
        LAYERS,
        layer1_rows_per_net,
        design_stack,
        negation,
        layer1,
        generic_layer,
        generic_total,
        layer2_even_rows,
        pre_levels,
        precompute,
        pre_a + pre_w,
        layer2_aux,
        layer2,
        design_stack,
        generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  Two claims carry this tier: (E1) a depth-L Winograd
# product driven purely by operand stacks equals the direct product, and (E2)
# the depth-(L-1) operand set IS the level-(L-1) intermediate of the depth-L
# operand set.  Both are executed below on real matrices over integers, where
# "exact" is literal, and (E1) again on floats where the reuse must be
# bit-exact rather than merely equal in value.
# ---------------------------------------------------------------------------


def _rng(seed: int):
    state = seed

    def nxt(lo: int, hi: int) -> int:
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return lo + state % (hi - lo + 1)

    return nxt


def _split(M: list) -> tuple:
    """Quadrants of an even-by-even matrix."""
    r, c = len(M), len(M[0])
    hr, hc = r // 2, c // 2
    q = lambda i, j: [row[j * hc:(j + 1) * hc] for row in M[i * hr:(i + 1) * hr]]
    return q(0, 0), q(0, 1), q(1, 0), q(1, 1)


def _add(A, B, sign=1):
    return [[a + sign * b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def left_operand_stack(A: list) -> list:
    """The seven Winograd LEFT operands.  A pure function of ``A`` alone."""
    a11, a12, a21, a22 = _split(A)
    s1 = _add(a21, a22)
    s2 = _add(s1, a11, -1)
    s3 = _add(a11, a21, -1)
    s4 = _add(a12, s2, -1)
    return [a11, a12, s4, a22, s1, s2, s3]


def right_operand_stack(B: list) -> list:
    """The seven Winograd RIGHT operands.  A pure function of ``B`` alone."""
    b11, b12, b21, b22 = _split(B)
    t1 = _add(b12, b11, -1)
    t2 = _add(b22, t1, -1)
    t3 = _add(b22, b12, -1)
    t4 = _add(t2, b21, -1)
    return [b11, b21, b22, t4, t1, t2, t3]


def operand_levels(M: list, levels: int, side: str) -> list:
    """The whole operand tree: ``out[j]`` is the list of 7**j blocks at level j.

    The recursion that builds level j reads only level j-1.  ``levels`` stops
    it; it never changes it.  That is the entire content of claim (E2).
    """
    stack = left_operand_stack if side == "left" else right_operand_stack
    tree = [[M]]
    for _ in range(levels):
        nxt = []
        for block in tree[-1]:
            nxt.extend(stack(block))
        tree.append(nxt)
    return tree


def _mm(A, B):
    inner = len(B)
    return [[sum(A[i][t] * B[t][j] for t in range(inner))
             for j in range(len(B[0]))] for i in range(len(A))]


def _combine(p: list) -> list:
    """One Winograd decode level: seven products back to one block."""
    c11 = _add(p[0], p[1])                    # U1
    u2 = _add(p[0], p[5])
    u3 = _add(u2, p[6])
    u4 = _add(u2, p[4])
    c12 = _add(u4, p[2])                      # U5
    c21 = _add(u3, p[3], -1)                  # U6
    c22 = _add(u3, p[4])                      # U7
    top = [ra + rb for ra, rb in zip(c11, c12)]
    bot = [ra + rb for ra, rb in zip(c21, c22)]
    return top + bot


def winograd_from_operand_sets(left_leaves: list, right_leaves: list,
                               levels: int) -> list:
    """A depth-L Winograd product driven ONLY by the two leaf operand sets."""
    blocks = [_mm(a, b) for a, b in zip(left_leaves, right_leaves)]
    for _ in range(levels):
        blocks = [_combine(blocks[i * 7:(i + 1) * 7])
                  for i in range(len(blocks) // 7)]
    if len(blocks) != 1:
        raise ValueError("decode did not close to a single block")
    return blocks[0]


def _selfcheck() -> None:
    t7 = _t7()
    call_of = t7.inplace_verbatim_leaves_candidate_bill

    # ---- 1. Shape anchors, from the deployed source's own constants. --------
    assert BASE_ROWS == 32256, BASE_ROWS
    assert DESIGN_ROWS == 64512, DESIGN_ROWS
    assert DESIGN_ROWS == 15.75 * TILE_ROWS
    assert BASE_ROWS == 7 * TILE_ROWS + 3584

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
    w_stack, _g = t7.best_operand_grade(WIDTH, WIDTH, levels)
    assert w_stack == constant, (w_stack, constant)
    for rows in (TILE_ROWS, 3584, BASE_ROWS, DESIGN_ROWS):
        assert _selected_levels(call_of(rows, WIDTH, WIDTH).strategy) == 6, rows

    row_full = bills[TILE_ROWS].total - w_stack
    row_tail = bills[3584].total - w_stack
    assert row_tail * TILE_ROWS == row_full * 3584, "row lane is not proportional"

    # ---- 3. (S1) THE GENERIC LAYER IS ON TIER 7'S OWN FLOOR AT ITS OWN SHAPE.
    #         Every lawful depth is swept at 64,512 rows under tier 7's own
    #         grading optimiser, so the claim that 96.8% of the bill cannot move
    #         is measured here, not assumed.
    def core_at(m, kk, nn, L):
        block = 1 << L
        if any(d % block for d in (m, kk, nn)):
            return None
        leaves = 7 ** L * t7.direct_cost(m // block, kk // block, nn // block)
        left, _ = t7.best_operand_grade(m, kk, L)
        right, _ = t7.best_operand_grade(kk, nn, L)
        dec, _ = t7.best_decode_grade(m, nn, L)
        return leaves + left + right + dec

    sweep = {L: core_at(DESIGN_ROWS, WIDTH, WIDTH, L) for L in range(2, 9)}
    assert all(v is not None for v in sweep.values()), sweep
    assert min(sweep, key=lambda L: sweep[L]) == 6, sweep
    assert sweep[6] == 4745522832, sweep[6]
    assert call_of(DESIGN_ROWS, WIDTH, WIDTH).total == sweep[6]
    #         and (S3) the layer bill IS the single-call bill, so tier 3's hoist
    #         already made the layer one call rather than 15.75.
    generic_layer_t3 = (row_full * DESIGN_ROWS) // TILE_ROWS + w_stack
    assert generic_layer_t3 == sweep[6], (generic_layer_t3, sweep[6])

    # ---- 4. (S5a) The layer-1 re-orientation door: operand and decode lanes
    #         are symmetric in their two dimensions, so transposing layer 1
    #         moves no FLOP but shrinks the net-invariant lane 126-fold.
    assert (t7.best_operand_grade(WIDTH, BASE_ROWS, 6)[0]
            == t7.best_operand_grade(BASE_ROWS, WIDTH, 6)[0] == 241309152)
    assert (t7.best_decode_grade(WIDTH, BASE_ROWS, 6)[0]
            == t7.best_decode_grade(BASE_ROWS, WIDTH, 6)[0] == 470232000)
    assert t7.best_operand_grade(WIDTH, WIDTH, 6)[0] == 1915152 < 241309152

    # ---- 5. THE PRECOMPUTE'S OWN NUMBERS. -----------------------------------
    pre_levels, pre_leaves, pre_a, pre_w, pre_decode, charged = precompute_lanes(t7)
    pre_bill = call_of(WIDTH, WIDTH, WIDTH)
    assert pre_bill.strategy == "winograd_l5_inplaceleaf", pre_bill.strategy
    assert pre_levels == 5 and pre_bill.total == 20420928, (pre_levels, pre_bill)
    #     the depth is tier 7's, and it is also the brute-forced minimum.
    square_sweep = {L: core_at(WIDTH, WIDTH, WIDTH, L) for L in range(2, 9)}
    assert min(square_sweep, key=lambda L: square_sweep[L]) == 5, square_sweep
    assert (pre_leaves, pre_a, pre_w, pre_decode) == (
        16134720, 1092032, 1092032, 2102144), (
        pre_leaves, pre_a, pre_w, pre_decode)
    assert charged == pre_leaves + pre_decode == 18236864, charged
    assert direct_cost(WIDTH, WIDTH, WIDTH) == 33488896
    assert direct_cost(WIDTH, WIDTH, WIDTH) - charged == 15252032

    # ---- 6. (E2) THE PREFIX, PRICED.  The depth-5 operand lane is exactly the
    #         j = 1..5 part of the depth-6 lane, so the difference is the
    #         level-6 term alone and levels 1..5 are shared identically.
    for depth in (5, 6):
        assert t7.best_operand_grade(WIDTH, WIDTH, depth)[1] == frozenset(), depth
    shallow = t7.inplace_operand_cost(WIDTH, WIDTH, 5, frozenset())
    deep = t7.inplace_operand_cost(WIDTH, WIDTH, 6, frozenset())
    assert (shallow, deep) == (1092032, 1915152), (shallow, deep)
    level6 = 7 ** 5 * 3 * (WIDTH >> 6) * (WIDTH >> 6) + 4 ** 5 * (WIDTH >> 6) ** 2
    assert deep - shallow == level6 == 823120, (deep - shallow, level6)
    assert shallow == pre_a == pre_w

    # ---- 7. (E2) THE PREFIX, EXECUTED.  Build both trees on real matrices and
    #         compare block for block: the shallower operand set is literally
    #         the intermediate of the deeper one, same blocks, same order.
    for size, depth in ((8, 3), (8, 2), (4, 2), (16, 3)):
        nxt = _rng(70707 + size * 31 + depth)
        M = [[nxt(-9, 9) for _ in range(size)] for _ in range(size)]
        for side in ("left", "right"):
            deep_tree = operand_levels(M, depth, side)
            shallow_tree = operand_levels(M, depth - 1, side)
            assert len(deep_tree) == depth + 1 and len(shallow_tree) == depth
            for j in range(depth):
                assert deep_tree[j] == shallow_tree[j], (side, j)
            assert len(deep_tree[depth - 1]) == 7 ** (depth - 1)
            # And the deeper tree really is derived FROM that intermediate.
            stack = left_operand_stack if side == "left" else right_operand_stack
            derived = []
            for block in deep_tree[depth - 1]:
                derived.extend(stack(block))
            assert derived == deep_tree[depth]

    # ---- 8. (E1) THE ROUTE, EXECUTED over integers: a depth-L Winograd product
    #         driven only by the two operand sets equals the direct product,
    #         and using the deeper build's intermediate as the shallower
    #         product's operand set reproduces it exactly.
    for size, depth in ((8, 1), (8, 2), (8, 3), (16, 2)):
        nxt = _rng(80808 + size * 17 + depth)
        A = [[nxt(-9, 9) for _ in range(size)] for _ in range(size)]
        B = [[nxt(-9, 9) for _ in range(size)] for _ in range(size)]
        la = operand_levels(A, depth, "left")[depth]
        rb = operand_levels(B, depth, "right")[depth]
        assert winograd_from_operand_sets(la, rb, depth) == _mm(A, B)
        # Ridden operand sets: taken from a DEEPER build of the same matrices.
        ridden_a = operand_levels(A, depth + 1, "left")[depth]
        ridden_b = operand_levels(B, depth + 1, "right")[depth]
        assert ridden_a == la and ridden_b == rb
        assert winograd_from_operand_sets(ridden_a, ridden_b, depth) == _mm(A, B)

    # ---- 9. (E1) again on FLOATS: riding the deeper build's blocks must be
    #         bit-identical, not merely equal in value, because the blocks are
    #         the same objects and every downstream rounding is the same
    #         rounding.  Values chosen so the operand additions actually round.
    nxt = _rng(90909)
    Af = [[nxt(-10 ** 6, 10 ** 6) / 3.0 for _ in range(8)] for _ in range(8)]
    Bf = [[nxt(-10 ** 6, 10 ** 6) / 7.0 for _ in range(8)] for _ in range(8)]
    for depth in (1, 2):
        own = winograd_from_operand_sets(
            operand_levels(Af, depth, "left")[depth],
            operand_levels(Bf, depth, "right")[depth], depth)
        ridden = winograd_from_operand_sets(
            operand_levels(Af, depth + 2, "left")[depth],
            operand_levels(Bf, depth + 2, "right")[depth], depth)
        for ra, rb in zip(own, ridden):
            for x, y in zip(ra, rb):
                assert x == y and (x != 0.0 or
                                   (1.0 / x if x else 1.0) == (1.0 / y if y else 1.0))

    # ---- 10. Double-count gate: the crowned chain, recomputed from tier 7. ---
    call = bills[TILE_ROWS].total
    assert call == 303096592, call
    assert 504 * call == 152760682368                    # suite tier 0
    layer_slice = call * DESIGN_ROWS // TILE_ROWS
    tier2_even = 7 * call + bills[3584].total
    assert tier2_even == 2387125056, tier2_even
    tier2_aux = _layer2_auxiliary_cost(direct_cost(WIDTH, WIDTH, WIDTH))
    assert tier2_aux == 173932544, tier2_aux
    tier2 = 31 * layer_slice + tier2_even + tier2_aux
    assert tier2 == 150547968644, tier2                  # suite tier 2
    tier3_layer2 = tier2_even - 8 * w_stack + w_stack + tier2_aux
    tier3 = 31 * generic_layer_t3 + tier3_layer2
    assert generic_layer_t3 == 4745522832, generic_layer_t3
    assert tier3_layer2 == 2547651536, tier3_layer2
    assert tier3 == 149658859328, tier3                  # suite tier 3
    tier4_row_part = 7 * row_full + row_tail
    assert tier4_row_part == 2371803840, tier4_row_part
    tier4_layer1 = tier4_row_part + w_stack + BASE_ROWS * WIDTH
    tier4 = 30 * generic_layer_t3 + tier4_layer1 + tier3_layer2
    assert tier4_layer1 == 2381976528, tier4_layer1
    assert tier4 == 147295313024, tier4                  # suite tier 4
    a_lane, _g = t7.best_operand_grade(BASE_ROWS, WIDTH, levels)
    assert a_lane == 241309152, a_lane
    tier5_layer1 = tier4_layer1 - a_lane
    tier5 = 30 * generic_layer_t3 + tier5_layer1 + tier3_layer2
    assert tier5_layer1 == 2140667376, tier5_layer1
    assert tier5 == 147054003872, tier5                  # suite tier 5, incumbent

    bill = suite_bill_per_net()
    assert bill.weight_stack == w_stack == 1915152

    # (a) Disjoint from tier 3: the W-STACK lane is untouched, 32 per net.
    stacks_here = LAYERS * bill.weight_stack
    assert bill.total - stacks_here == (
        30 * (bill.generic_layer - w_stack)
        + (bill.layer1_total - w_stack)
        + (bill.layer2_total - w_stack))
    assert bill.generic_layer == generic_layer_t3
    assert bill.generic_layers_total == 30 * generic_layer_t3 == 142365684960

    # (b) Disjoint from tiers 4 and 5: layer 1 is bit-identical to tier 5's, and
    #     so is the suite-once charge.
    assert bill.layer1_row_part_per_net == tier4_row_part - a_lane == 2130494688
    assert bill.layer1_negation == BASE_ROWS * WIDTH == 8257536
    assert bill.layer1_total == tier5_layer1 == 2140667376
    assert bill.suite_once == bill.layer1_design_stack_once == a_lane
    assert bill.layer2_even_rows == tier4_row_part == 2371803840

    # (c) Disjoint from tier 2: every OTHER auxiliary term is tier 2's own.
    assert bill.layer2_aux == tier2_aux - direct_cost(WIDTH, WIDTH, WIDTH) + charged
    assert bill.layer2_aux == 158680512, bill.layer2_aux
    assert tier2_aux - bill.layer2_aux == 15252032
    assert _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH == 115605504
    assert DESIGN_ROWS * WIDTH == 16515072 and WIDTH * WIDTH == 65536
    assert bill.layer2_precompute == 18236864
    assert bill.layer2_precompute_waived == 2 * shallow == 2184064
    assert bill.layer2_total == 2532399504, bill.layer2_total

    # (d) Disjoint from tier 1 (rejected): NO butterfly credit at layer 1.
    butterfly_layer1 = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH
    assert bill.layer1_row_part_per_net > 18 * butterfly_layer1, (
        "layer 1 is being credited a butterfly; that is tier 1's rejected claim")

    # ---- 11. Conservativeness and never-worse gates. ------------------------
    assert bill.total == tier5 - 15252032
    assert bill.suite_total(1) == tier5 - 15252032 + a_lane
    for n in (1, 2, 3, 10, 100, 1000):
        assert bill.suite_total(n) < n * tier5 + a_lane
        num, den = bill.amortized_numerator(n)
        assert num == n * bill.total + a_lane and den == n
    # The precompute is charged, not skipped: it is strictly positive and
    # strictly above its own leaves, so no lane was dropped rather than ridden.
    assert 0 < pre_decode and charged > pre_leaves
    # and the ridden lanes are strictly smaller than the stacks they ride on.
    assert 2 * shallow < 2 * deep

    # ---- 12. The bill's own arithmetic. -------------------------------------
    assert bill.total < tier5 < tier4 < tier3 < tier2
    assert bill.total == 147038751840, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: affine measurement of the call bill; an exhaustive depth "
          "sweep L=2..8 showing the generic layer sits on tier 7's own floor at "
          "its own 64,512-row shape; the layer-1 re-orientation door measured "
          "shut by lane symmetry; the precompute's depth read from tier 7 and "
          "brute-forced independently; the depth-5 operand lane priced as the "
          "exact j=1..5 prefix of the depth-6 lane; that prefix EXECUTED block "
          "for block on real operand trees; the depth-L Winograd route executed "
          "against direct products over integers and bit-for-bit over floats "
          "while riding a deeper build's blocks; double-count gates against "
          "tiers 1/2/3/4/5 recomputed from tier 7; and the bill's arithmetic "
          "all pass")
    b = suite_bill_per_net()
    incumbent = 147054003872
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>48} {value:>15,}")
    print(f"  {'incumbent (tier 5)':>48} {incumbent:>15,}")
    print(f"  {'saving (steady state, per net)':>48} {incumbent - b.total:>15,}")
    print(f"  ratio vs tier 5                                  "
          f"{b.total / incumbent:.9f}")
    for n in (1, 2, 10, 100):
        num, den = b.amortized_numerator(n)
        print(f"  suite of {n:>5} nets: per-net mean {num / den:,.1f}"
              f"   (exact {num:,} / {den})")
    print("total:", b.total)
