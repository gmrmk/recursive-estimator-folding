"""Suite tier 7: the layer-1 antipodal negation pass has no consumer once tier 2's
CReLU route is in the suite, so it is billed at its one surviving reader instead
of at the full design half.

ONE SUBSTANTIVE CHANGE
======================
Exactly one term of the incumbent moves, and it moves because two already-crowned
tiers, composed, left it with nothing to feed:

    layer1_negation = BASE_ROWS * WIDTH = 8,257,536     (tier 4, incumbent)
    layer1_negation = PILOT_BASE * WIDTH =    65,536    (this tier)

Nothing else changes.  Layer 1 keeps tier 4's 32,256 base rows, its leaves and
decode lanes and its W-side stack; tier 5's suite-once design stack is carried
at its own value; layer 2 keeps tier 2's CReLU route with tier 3's hoist,
verbatim; layers 3..32 keep tier 3's generic layer, verbatim.  ``_selfcheck``
asserts every one of those terms is bit-identical to the incumbent's and that
the whole delta is the negation term alone.

THE FROZEN CONSTANT
===================
P1: enumerate what the suite model hard-codes, and take the one that a licence
already granted has quietly emptied.  Tier 4 introduced the negation term as the
conservative price of the half of layer 1 it stopped billing at row price: the
design is ``[D; -D]``, tier 4 bills the product only for ``D``'s 32,256 rows,
and it charges one elementwise pass over a 32,256 x 256 block to produce the
antipodal preactivations ``-P`` from ``P``.  That was the right price for tier
4 in isolation.

It is no longer the right price, because tier 2 replaced the only consumer those
rows ever had.  The frozen constant is therefore not a modelling choice anyone
made; it is a residue of billing two tiers separately that were adopted
together.  This tier bills the composition.

  (F1) ``-P``'s rows exist only as layer-1 preactivations.  The design's
       antipodal half enters the route at exactly one place, the first product:
           first_pre = self._first_sample_matmul(
               z, mlp.weights[0], out=activation[: self.n_base]
           )                                             [fold3_estimator.py:87]
           x = fnp.concatenate(
               (fnp.maximum(first_pre, 0.0), fnp.maximum(-first_pre, 0.0)),
               axis=0,
           )                                             [fold3_estimator.py:79-81]
       ``x``'s lower half IS ``relu(-P)``; there is no other occurrence of the
       antipodal rows anywhere in ``predict``.

  (F2) ``x`` is consumed by exactly three things before it is overwritten, and
       the loop overwrites it on its first iteration:
           x = fnp.maximum(self._sample_matmul(x, ...), 0.0)
                                                         [fold3_estimator.py:124]
       so nothing after layer 2 can see layer 1's ``x``.  The three consumers:
         (i)   the layer-2 product ``x @ W2``;
         (ii)  the layer-2 cold-column pilot, which reads
                   x[: self.pilot_base],
                   x[self.n_base : self.n_base + self.pilot_base]
                                                     [fold3_estimator.py:110-113]
               -- ``pilot_base = 256`` [base_estimator.py:62, and the champion
               restates it, kerdock_v3_estimator.py:51];
         (iii) the moment/variance residual reductions
                   first_moment_residual = fnp.mean(x, axis=0) - ...
                                                         [fold3_estimator.py:84]
               which the suite model does not bill on either route (see below).
       ``_additional_tangent`` receives ``x`` but the champion does not override
       fold3's stub, which ignores every argument and returns ``None``
       [fold3_estimator.py:28-41]; the champion overrides ``setup``,
       ``_initial_sample_state``, ``_release_initial_sample_state``,
       ``_first_sample_matmul``, ``_sample_matmul``, ``_haar_rotation`` and
       ``predict``, and nothing else [kerdock_v3_estimator.py:54-159].

  (F3) Consumer (i) -- the whole 64,512-row product -- is what tier 2 removed.
       Tier 2's route never multiplies the antipodal rows.  It forms
           even channel  B = |P| @ W2       (32,256 rows, paid at row price)
           odd  channel  A =  P  @ W2       (the design algebra, paid as the
                                             precompute + butterfly aux terms)
       and writes both halves of the layer-2 preactivation by recombination,
           pre2_top = (B + A) / 2 ,   pre2_bottom = (B - A) / 2 ,
       which is tier 2's ``recombine`` term at ``DESIGN_ROWS * WIDTH``, already
       in the incumbent's bill and carried here untouched.  ``|P|`` comes from
       ``P`` by tier 2's ``abs_pass``.  Neither ``B``, nor ``A``, nor ``|P|``,
       nor either half of ``pre2`` reads ``-P`` or ``relu(-P)``.

  (F4) Consumer (ii) survives, and is what this tier still charges.  The layer-2
       pilot reads 256 rows of ``relu(-P)``.  So the negation pass is not
       deleted; it is charged at the 256 rows that are actually read:
           PILOT_BASE * WIDTH = 256 * 256 = 65,536.

  (F5) Consumer (iii) is outside the model on BOTH routes and gets strictly
       cheaper on this one, so it cannot repay the win.  The incumbent's bill
       contains no reduction term at all -- no ``mean``, no row sum, anywhere in
       tiers 0..5.  Under the incumbent the two residual reductions run over
       64,512 rows; under this route they run over the 32,256 ``P`` rows plus
       two 256-wide fixups, because
           mean(relu(-P))    = mean(relu(P)) - mean(P)
           mean(relu(-P)^2)  = mean(P^2) - mean(relu(P)^2)
       (the second because ``relu(P) * P = relu(P)^2`` elementwise).  Both
       identities are executed in ``_selfcheck``.  Unbilled before, unbilled
       after, and smaller after: no repayment term exists.

EXACTNESS IDENTITY
==================
The route computes bit-identical results because it performs, in the same order,
every operation the incumbent route performs EXCEPT a block of 32,256 x 256
negations whose outputs no surviving operation reads -- and it performs 256 x 256
of those negations, the ones that are read.

Formally.  Let ``P = D @ W1`` be the layer-1 preactivation of the design's base
half.  The incumbent route materializes ``N = -P`` and then
``X = [relu(P); relu(N)]``, and every downstream value is a function of
``X``, ``W2..W32`` and the analytic pass.  Factor the downstream dependence:

    downstream = f( pre2 , pilot , residuals , W3..W32 , analytic )

  * ``pre2`` is produced by tier 2's recombination from ``B = |P| @ W2`` and
    ``A = P @ W2``.  Both are functions of ``P`` alone.  The identity that makes
    this exact is tier 2's, adopted at tier 2 and re-executed below:
        relu(P) + relu(-P) = |P| ,  relu(P) - relu(-P) = P ,
    hence   relu(P) @ W2 = (|P| @ W2 + P @ W2) / 2 = pre2_top
            relu(-P) @ W2 = (|P| @ W2 - P @ W2) / 2 = pre2_bottom .
    So ``pre2`` -- all 64,512 rows, in the design's row order -- is unchanged.
  * ``pilot`` reads ``relu(P)[:256]`` and ``relu(-P)[:256]``.  The second is
    produced here, from the first, by ``relu(-P) = relu(P) - P`` elementwise on a
    256 x 256 block: one op per element, the same op count a negation of that
    block would cost, and it is charged.  So ``pilot`` is unchanged.
  * ``residuals`` are the two reductions of (F5); their values are unchanged by
    the identities executed in ``_selfcheck``, and their price is zero in this
    model on both routes.

Every input to every subsequent operation is therefore the same value, produced
by the same operations in the same order, and no summation anywhere is
reordered.  The only difference between the two routes is that one of them
writes 8,257,536 negated floats that nothing subsequently reads, and the other
writes 65,536 of them -- the ones that are read.  Removing writes nothing reads
cannot change a result; that is not an approximation of the incumbent's output,
it is the incumbent's output.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 2.  Tier 2 moved layer 2's ROW COUNT and added five auxiliary
    terms.  Every one of them -- ``abs_pass``, ``halfscale``, ``precompute``,
    ``butterfly``, ``recombine`` -- reappears here at its own value, and
    ``_selfcheck`` asserts each and asserts their sum.  In particular
    ``recombine`` is still charged over all 64,512 rows: this tier does not
    claim the antipodal half of ``pre2`` is free, only that the antipodal half
    of ``pre1`` is unread.
  * From tier 3.  The W-side stack lane is untouched: 32 stacks per net, one per
    layer, at 1,915,152 each.  Asserted.
  * From tier 4.  Tier 4's row count at layer 1 is untouched at 32,256 and its
    leaves and decode lanes are untouched.  Only the elementwise term tier 4
    attached beside them moves, and it is a separate summand of tier 4's layer-1
    total, not a re-pricing of the rows.  Asserted to the FLOP.
  * From tier 5.  The suite-once design-side operand lane is unchanged at
    241,309,152 and is still published as a named one-time field.  Asserted.
  * From tier 1 and tier 6, both REJECTED.  Tier 1 claimed layer 1 is a
    butterfly; this tier takes no butterfly credit at layer 1, charging leaves
    and decode over 32,256 rows in full -- still more than eighteen times the
    butterfly the deployed hook runs, asserted.  Tier 6 repriced tier 2's
    odd-channel precompute; this tier charges that precompute at the same
    ``direct_cost(256, 256, 256) = 33,488,896`` the incumbent charges, asserted.
    Neither rejected claim is revived and nothing here depends on either.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The negation is charged, not deleted.  The 256 pilot rows are billed at one
    op per element even though the deployed pilot branch runs only when a layer
    has cold columns (``if cold.shape[0] > 0``); this tier charges them
    unconditionally, at every net, rather than making the bill depend on a
    net-dependent branch.
  * The reductions of (F5) get strictly cheaper and are still charged nothing --
    the win is not enlarged by starting to bill a lane that gets smaller.
  * Layer 2's ``recombine`` stays at 64,512 rows and ``abs_pass`` stays at
    32,256 rows.  No elementwise term other than the orphaned one moves.
  * The antipodal half of every layer from 2 on is carried at full price.  The
    licence taken here is explicitly the narrow one: it applies to the layer-1
    PREACTIVATION half only, because that is the only half whose consumer tier 2
    removed.  ``_selfcheck`` asserts layer 2 and layers 3..32 are bit-identical
    to the incumbent's.
  * ``.total`` remains the marginal per-net bill with tier 5's one-time charge
    published beside it; ``suite_total(1)`` is still exactly tier 4's figure
    minus this tier's saving, so no suite size is assumed anywhere.

A DOOR CLOSED IN PASSING, SO THE NEXT TIER DOES NOT PAY FOR IT TWICE
====================================================================
The two remaining constants the suite model names -- "pruned shapes at full
width" and "the terminal fold not modeled" -- were searched before this tier was
written, and neither is a win under worst-case-safe accounting:

  * Pruning.  ``active`` is ``flatnonzero(analytic_alphas[layer] >= dead_alpha)``
    plus pilot-rescued columns [fold3_estimator.py:104-121].  Its width is a
    function of the net's own weights; its worst case is the full 256, so no
    net-independent bill below 256 exists.  The corpus's own width audit records
    the task as fixed at "d=256, L=32" with no certified narrower deployed
    shape [experiments/gen8_gate_audit/audit_widths.py:3-4].
  * The terminal fold.  Layers 30, 31 and 32 are not generic layers; they are
    ``pre31`` and ``pre32``, which are sums of two and three row-products
    [fold3_estimator.py:175-181, 208-218].  With
    ``a = |active|, b = |kink30|, c = |kink31|, d = |kink32|``, their row work is
    proportional to ``a*b + (a+b)*c + (a+b+c)*d``, maximized at 393,216 against
    the incumbent's 3 * 256 * 256 = 196,608.  Modelling the terminal fold
    honestly RAISES the bill by up to a factor of two in the worst case; the
    incumbent's silence about it is not slack, it is the cheaper of the two
    accountings.  ``_selfcheck`` executes both bounds.

NO APPROXIMATION, NO FLAG
=========================
No value is approximated, no rank is reduced, no summation is reordered, and no
term is dropped that any operation reads.  The certified per-call floor
(303,096,592 at anonymous (4096, 256, 256)) is untouched: no op inside any call
is rescheduled or reweighted, the depth-6 selection is the tier-7 sweep's own at
every shape used, and the per-call price is used verbatim at 4,096 and 3,584
rows exactly as tiers 2, 3, 4 and 5 use it.  The term that moves is not inside
any call -- it is an elementwise pass between calls.  Every op counted here is
one f32 multiply, add, subtract, negate, abs or copy priced at 1.  No f32
repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
or new dispatch.  This one removes a pass and adds none:

  * Strictly fewer passes.  The route deletes one full-array elementwise kernel
    (a 32,256 x 256 negate-and-store) and replaces it with a single contiguous
    256 x 256 slice of the same kernel.  Pass count goes down by zero-or-one and
    never up; no pass is split.
  * No new kernel, no new route, no new dispatch, no new branch on net data.
    The 256-row slice is the same ``relu(P) - P`` the pilot already needs to read
    and is contiguous in the activation buffer, so it is one call on one slice.
  * Traffic falls with the FLOPs, hard.  The deleted pass wrote 8,257,536 f32
    (33.0 MB) into the activation buffer's lower half and read them back once at
    layer 2; the surviving slice writes 65,536 f32 (0.26 MB).  Roughly 66 MB of
    round-trip DRAM traffic per net disappears alongside 8.19 M ops, on a lane
    that is purely memory-bound -- so the wall-time win is larger than the
    metered win, not smaller.  There is no read-amplification term anywhere for
    the win to be repaid out of.
  * No new residency, and less.  The layer-1 activation buffer's lower half is
    written by tier 2's ``recombine`` at layer 2 regardless, so the allocation is
    unchanged in size and lifetime; only one earlier write into it disappears.
    No object lifetime class is created and nothing is cached.
  * Kernel sizes do not shrink anywhere else.  Every matmul in the suite keeps
    its shape: 32,256 rows at layer 1, 32,256 at layer 2's even channel, 64,512
    at layers 3..32, all still tiled at BLOCK_ROWS = 4,096 with the depth-6
    schedule.  This tier adds exactly zero seams to the schedule.
  * The win is flat in the suite size -- one net or a thousand, each pays
    8,192,000 less -- so nothing about it degrades as the suite grows.

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
PILOT_BASE = 256                  # base_estimator.py:62, kerdock_v3_estimator.py:51

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
    """The m-independent lane of the crowned call bill: the W-side (k, n) stack."""
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(k, n, levels)
    return cost


def design_side_stack_cost(t7, m: int, k: int = WIDTH) -> int:
    """The A-side (m, k) operand lane: a pure function of the LEFT operand.

    Tier 5's object, carried verbatim: at layer 1 the left operand is the
    design, invariant across the nets of the suite, so this is charged once to
    the suite rather than once per net.
    """
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, WIDTH)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(m, k, levels)
    return cost


def antipodal_negation_cost(read_rows: int = PILOT_BASE,
                            width: int = WIDTH) -> int:
    """Price of materializing the layer-1 antipodal activations that are READ.

    Tier 4 charged this over all ``BASE_ROWS``.  Under tier 2's CReLU layer-2
    route the only surviving reader is the layer-2 cold-column pilot, which
    reads ``x[n_base : n_base + pilot_base]`` -- 256 rows.  One op per element,
    the same unit price tier 4 used.
    """
    if read_rows < 0 or width <= 0:
        raise ValueError("row and width counts must be non-negative and positive")
    return read_rows * width


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
    layer1_negation_rows: int
    layer1_total: int
    generic_layer: int
    generic_layers_total: int
    layer2_even_rows: int
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
            "layer1_antipodal_negation_read_rows": self.layer1_negation_rows,
            "layer1_antipodal_negation": self.layer1_negation,
            "layer1_total_per_net": self.layer1_total,
            "generic_layer_total": self.generic_layer,
            "generic_layers_3_to_32": self.generic_layers_total,
            "layer2_even_channel_row_part": self.layer2_even_rows,
            "layer2_weight_side_stack": self.weight_stack,
            "layer2_auxiliary_terms": self.layer2_aux,
            "layer2_total": self.layer2_total,
            "design_side_stack_charged_ONCE_to_the_suite":
                self.layer1_design_stack_once,
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
    """Steady-state per-net bill: the layer-1 antipodal negation pass is charged
    at its one surviving reader, the 256-row layer-2 pilot, instead of at the
    design's whole 32,256-row base half."""
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

    # --- layer 1: tier 4's rows, tier 5's suite-once stack, THIS TIER's pass --
    full_tiles, remainder = divmod(BASE_ROWS, TILE_ROWS)
    if remainder == 0:
        raise ValueError("base row count is not the frozen 7 x 4096 + tail")
    base_rows_part = full_tiles * row_full + row_tail        # tier 4's row part
    design_stack = (full_tiles * design_side_stack_cost(t7, TILE_ROWS, k)
                    + design_side_stack_cost(t7, remainder, k))
    if design_stack != design_side_stack_cost(t7, BASE_ROWS, k):
        raise ValueError("the design-side lane is not additive over the tiling")
    if design_stack >= base_rows_part:
        raise ValueError("the design-side lane cannot exceed the row part")
    if PILOT_BASE > BASE_ROWS:
        raise ValueError("the pilot cannot read more rows than the half has")
    negation = antipodal_negation_cost(PILOT_BASE, WIDTH)
    layer1_rows_per_net = base_rows_part - design_stack
    layer1 = layer1_rows_per_net + w_stack + negation

    # --- layer 2: tier 2's CReLU route with tier 3's hoist, carried verbatim --
    layer2_even_rows = base_rows_part
    layer2_aux = _layer2_auxiliary_cost()
    layer2 = layer2_even_rows + w_stack + layer2_aux

    return SuiteBill(
        "orphaned_antipodal_negation",
        call,
        w_stack,
        row_full,
        row_tail,
        LAYERS,
        layer1_rows_per_net,
        design_stack,
        negation,
        PILOT_BASE,
        layer1,
        generic_layer,
        generic_total,
        layer2_even_rows,
        layer2_aux,
        layer2,
        design_stack,
        generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  The claim is that the layer-1 antipodal preactivations
# have exactly one surviving reader, so the pass that makes the other 32,000
# rows of them can be dropped without changing any downstream value.  That is
# executed below: the CReLU recombination is driven from ``P`` alone and its
# output is compared, element by element, against the reference route that does
# materialize ``-P``.
# ---------------------------------------------------------------------------


def _rng(seed: int):
    state = seed

    def nxt(lo: int, hi: int) -> int:
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return lo + state % (hi - lo + 1)

    return nxt


def _mm(A, B):
    inner = len(B)
    return [[sum(A[i][t] * B[t][j] for t in range(inner))
             for j in range(len(B[0]))] for i in range(len(A))]


def _relu(M):
    return [[v if v > 0 else 0 for v in row] for row in M]


def _neg(M):
    return [[-v for v in row] for row in M]


def _abs(M):
    return [[v if v >= 0 else -v for v in row] for row in M]


def reference_layer2_preactivation(design_base, w1, w2):
    """The incumbent route: materialize ``-P``, ReLU both halves, multiply all
    64,512 rows.  ``-D`` is formed explicitly, exactly as tier 4 charges for."""
    antipodal = _neg(design_base)
    full_design = design_base + antipodal          # [D; -D], row order preserved
    pre1 = _mm(full_design, w1)
    x = _relu(pre1)
    return _mm(x, w2), x


def crelu_layer2_preactivation(design_base, w1, w2):
    """Tier 2's route, driven from ``P`` alone.

    ``-P`` is never formed: the function's only matrix products are ``D @ W1``,
    ``|P| @ W2`` and ``P @ W2``, and its only elementwise passes are ``abs`` and
    the recombination.  The 256 pilot rows of ``relu(-P)`` are produced by
    ``relu(P) - P``, which is what this tier charges 65,536 ops for.
    """
    p = _mm(design_base, w1)
    even = _mm(_abs(p), w2)                        # B = |P| @ W2
    odd = _mm(p, w2)                               # A =  P  @ W2
    top, bottom = [], []
    for be, bo in zip(even, odd):
        top.append([(e + o) // 2 for e, o in zip(be, bo)])
        bottom.append([(e - o) // 2 for e, o in zip(be, bo)])
    pilot_rows = min(PILOT_BASE, len(p))
    relu_p = _relu(p)
    antipodal_pilot = [[a - b for a, b in zip(relu_p[i], p[i])]
                       for i in range(pilot_rows)]
    return top + bottom, relu_p, antipodal_pilot


def terminal_fold_row_units(a: int, b: int, c: int, d: int) -> int:
    """Row-proportional work of layers 30..32 in units of one (rows x 1 x 1).

    ``pre31`` is a sum of two row-products and ``pre32`` a sum of three
    [fold3_estimator.py:175-181, 208-218], so the terminal fold's row work is
    ``a*b + (a+b)*c + (a+b+c)*d`` where ``a = |active|``, ``b = |kink30|``,
    ``c = |kink31|``, ``d = |kink32|``.
    """
    return a * b + (a + b) * c + (a + b + c) * d


def _selfcheck() -> None:
    t7 = _t7()
    call_of = t7.inplace_verbatim_leaves_candidate_bill

    # ---- 1. Shape anchors, from the deployed source's own constants. --------
    assert BASE_ROWS == 32256, BASE_ROWS
    assert DESIGN_ROWS == 64512, DESIGN_ROWS
    assert DESIGN_ROWS == 15.75 * TILE_ROWS
    assert BASE_ROWS == 7 * TILE_ROWS + 3584
    assert PILOT_BASE == 256 and PILOT_BASE < BASE_ROWS

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

    # The depth-6 selection is the tier-7 sweep's own at every shape used here.
    for rows in (TILE_ROWS, 3584, BASE_ROWS, DESIGN_ROWS):
        assert _selected_levels(call_of(rows, WIDTH, WIDTH).strategy) == 6, rows

    row_full = bills[TILE_ROWS].total - w_stack
    row_tail = bills[3584].total - w_stack
    assert row_tail * TILE_ROWS == row_full * 3584, "row lane is not proportional"

    # ---- 3. Tier 5's lane decomposition, re-derived, still closing exactly. --
    leaves = 7 ** levels * t7.direct_cost(
        BASE_ROWS >> levels, WIDTH >> levels, WIDTH >> levels)
    a_lane, _g = t7.best_operand_grade(BASE_ROWS, WIDTH, levels)
    decode, _g = t7.best_decode_grade(BASE_ROWS, WIDTH, levels)
    tier4_row_part = 7 * row_full + row_tail
    assert leaves + a_lane + decode + w_stack == call_of(
        BASE_ROWS, WIDTH, WIDTH).total, "lane decomposition does not close"
    assert leaves + a_lane + decode == tier4_row_part, (
        leaves + a_lane + decode, tier4_row_part)
    assert (leaves, a_lane, decode) == (1660262688, 241309152, 470232000), (
        leaves, a_lane, decode)
    a_full, _g = t7.best_operand_grade(TILE_ROWS, WIDTH, levels)
    a_tail, _g = t7.best_operand_grade(3584, WIDTH, levels)
    assert 7 * a_full + a_tail == a_lane, (7 * a_full + a_tail, a_lane)

    # ---- 4. THE IDENTITY, executed.  The CReLU route reproduces BOTH halves
    #         of the layer-2 preactivation without ever forming ``-P``, and the
    #         256 pilot rows of ``relu(-P)`` are recovered by one subtract per
    #         element -- exactly the op count this tier still charges.
    for rows, width in ((6, 4), (8, 6), (5, 8), (11, 5)):
        nxt = _rng(70707 + rows * 31 + width)
        design = [[nxt(-9, 9) for _ in range(width)] for _ in range(rows)]
        w1 = [[nxt(-9, 9) for _ in range(width)] for _ in range(width)]
        w2 = [[nxt(-9, 9) for _ in range(width)] for _ in range(width)]

        ref_pre2, ref_x = reference_layer2_preactivation(design, w1, w2)
        route_pre2, relu_p, antipodal_pilot = crelu_layer2_preactivation(
            design, w1, w2)

        # Both halves, all rows, in the design's row order: identical.
        assert route_pre2 == ref_pre2, "CReLU route changed the layer-2 input"
        # The reference's own halves, for the record.
        assert ref_x[:rows] == relu_p, "the base half is not relu(P)"
        # The pilot rows the route still materializes match the reference's.
        pilot_rows = min(PILOT_BASE, rows)
        assert antipodal_pilot == ref_x[rows:rows + pilot_rows], (
            "relu(-P) = relu(P) - P failed on the pilot rows")

        # (F5): the two residual reductions are unchanged by the identities that
        # let them be taken over the base half alone.
        p = _mm(design, w1)
        n_rows = len(p)
        for j in range(width):
            sum_relu_neg = sum(max(-p[i][j], 0) for i in range(n_rows))
            assert sum_relu_neg == (sum(max(p[i][j], 0) for i in range(n_rows))
                                    - sum(p[i][j] for i in range(n_rows)))
            sq_relu_neg = sum(max(-p[i][j], 0) ** 2 for i in range(n_rows))
            assert sq_relu_neg == (sum(p[i][j] ** 2 for i in range(n_rows))
                                   - sum(max(p[i][j], 0) ** 2
                                         for i in range(n_rows)))

    # ---- 5. Bit-exactness over floats, not merely equality of value.  The
    #         recombination is tier 2's, adopted; what is executed here is that
    #         dropping the ``-P`` pass leaves every downstream operand the SAME
    #         object it already was, so every rounding is the same rounding.
    nxt = _rng(80808)
    for _trial in range(40):
        p_row = [nxt(-10 ** 6, 10 ** 6) / 3.0 for _ in range(8)]
        with_pass = [-v for v in p_row]                       # incumbent: -P
        relu_pos = [v if v > 0.0 else 0.0 for v in p_row]
        relu_neg_ref = [v if v > 0.0 else 0.0 for v in with_pass]
        relu_neg_route = [a - b for a, b in zip(relu_pos, p_row)]
        for x, y in zip(relu_neg_ref, relu_neg_route):
            assert x == y and (x != 0.0 or
                               (1.0 / x if x else 1.0) == (1.0 / y if y else 1.0))

    # ---- 6. Double-count gate: the crowned chain, recomputed from tier 7. ----
    call = bills[TILE_ROWS].total
    assert call == 303096592, call
    assert 504 * call == 152760682368                    # suite tier 0
    layer_slice = call * DESIGN_ROWS // TILE_ROWS
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
    assert tier3 == 149658859328, tier3                  # suite tier 3
    tier4_layer1 = tier4_row_part + w_stack + BASE_ROWS * WIDTH
    tier4 = 30 * generic_layer_t3 + tier4_layer1 + tier3_layer2
    assert tier4_layer1 == 2381976528, tier4_layer1
    assert tier4 == 147295313024, tier4                  # suite tier 4
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

    # (b) Disjoint from tier 4: the ROW COUNT and the leaves/decode lanes at
    #     layer 1 are untouched; only the elementwise pass beside them moves.
    assert bill.layer1_row_part_per_net + bill.layer1_design_stack_once == tier4_row_part
    assert bill.layer1_row_part_per_net == leaves + decode == 2130494688

    # (c) Disjoint from tier 5: the suite-once design lane is unchanged.
    assert bill.layer1_design_stack_once == a_lane == 241309152
    assert bill.suite_once == a_lane

    # (d) Disjoint from tier 2: every layer-2 term reappears at its own value.
    assert bill.layer2_even_rows == tier2_even - 8 * w_stack == 2371803840
    assert bill.layer2_aux == _layer2_auxiliary_cost() == 173932544
    assert bill.layer2_total == tier3_layer2 == 2547651536
    #     and in particular tier 2's recombination is still charged over all
    #     64,512 rows: this tier makes no claim about the antipodal half of the
    #     layer-2 preactivation, only about the layer-1 one.
    assert DESIGN_ROWS * WIDTH == 16515072
    assert bill.layer2_aux - (BASE_ROWS * WIDTH + WIDTH * WIDTH
                              + direct_cost(WIDTH, WIDTH, WIDTH)
                              + _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH) == 16515072

    # (e) Disjoint from tier 1 (rejected): NO butterfly credit at layer 1.
    butterfly_layer1 = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH
    assert butterfly_layer1 == 115605504
    assert bill.layer1_row_part_per_net > 18 * butterfly_layer1, (
        "layer 1 is being credited a butterfly; that is tier 1's rejected claim")

    # (f) Disjoint from tier 6 (rejected): the odd-channel precompute is still
    #     charged at the direct price, not repriced as a Winograd call.
    assert direct_cost(WIDTH, WIDTH, WIDTH) == 33488896

    # ---- 7. THE DELTA IS THE NEGATION TERM, AND NOTHING ELSE. ---------------
    assert bill.layer1_negation == PILOT_BASE * WIDTH == 65536
    assert bill.layer1_negation_rows == PILOT_BASE
    assert tier5_layer1 - bill.layer1_total == BASE_ROWS * WIDTH - PILOT_BASE * WIDTH
    assert tier5 - bill.total == 8257536 - 65536 == 8192000, tier5 - bill.total
    #     Layers 3..32 and layer 2 are bit-identical to the incumbent's.
    assert bill.generic_layer == generic_layer_t3
    assert bill.generic_layers_total == 30 * generic_layer_t3 == 142365684960
    assert bill.layer2_total == tier3_layer2

    # ---- 8. Conservativeness gates. -----------------------------------------
    #     The pass is charged, not deleted, and charged unconditionally.
    assert bill.layer1_negation > 0
    assert antipodal_negation_cost(0, WIDTH) == 0
    assert antipodal_negation_cost(BASE_ROWS, WIDTH) == 8257536   # tier 4's value
    #     Never worse than the incumbent at any suite size, strictly better at
    #     every size, and the one-time charge is still published exactly.
    for n in (1, 2, 3, 10, 100, 1000):
        assert bill.suite_total(n) == n * bill.total + a_lane
        assert bill.suite_total(n) < n * tier5 + a_lane
        num, den = bill.amortized_numerator(n)
        assert (num, den) == (n * bill.total + a_lane, n)
    assert bill.suite_total(1) == tier4 - 8192000

    # ---- 9. The two doors this tier closed rather than walked through. ------
    #     Pruning: worst case is the full width, so no net-independent bill
    #     below 256 exists and the incumbent's 256 is already the safe one.
    assert max(a for a in range(1, WIDTH + 1)) == WIDTH
    #     Terminal fold: modelling it honestly can DOUBLE its charge.
    incumbent_terminal = 3 * WIDTH * WIDTH
    assert incumbent_terminal == 196608
    worst = max(terminal_fold_row_units(a, b, c, d)
                for a in (0, WIDTH) for b in (0, WIDTH)
                for c in (0, WIDTH) for d in (0, WIDTH))
    assert worst == terminal_fold_row_units(WIDTH, WIDTH, WIDTH, WIDTH)
    assert worst == 393216 == 2 * incumbent_terminal, worst
    #     and it is not uniformly cheaper either: the all-kink corner alone
    #     already exceeds the incumbent's charge.
    assert terminal_fold_row_units(WIDTH, WIDTH, WIDTH, WIDTH) > incumbent_terminal

    # ---- 10. The bill's own arithmetic. -------------------------------------
    assert bill.layer1_total == 2132475376, bill.layer1_total
    assert bill.total < tier5 < tier4 < tier3 < tier2
    assert bill.total == 147045811872, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: affine measurement of the call bill, the tier-7 lane "
          "decomposition closing on tier 4's layer-1 row part, an executed "
          "CReLU route that reproduces BOTH halves of the layer-2 "
          "preactivation without ever forming -P, an executed recovery of the "
          "256 pilot rows by relu(P) - P (integers exactly, floats "
          "bit-for-bit), the two residual-reduction identities, double-count "
          "gates against tiers 1/2/3/4/5/6, the delta-is-the-negation-term "
          "gate, and the closed-door bounds on pruning and the terminal fold "
          "all pass")
    b = suite_bill_per_net()
    incumbent = 147054003872
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>44} {value:>15,}")
    print(f"  {'incumbent (tier 5)':>44} {incumbent:>15,}")
    print(f"  {'saving (per net, every net)':>44} {incumbent - b.total:>15,}")
    print(f"  ratio vs tier 5                              {b.total / incumbent:.9f}")
    for n in (1, 2, 10, 100):
        num, den = b.amortized_numerator(n)
        print(f"  suite of {n:>5} nets: per-net mean {num / den:,.1f}"
              f"   (exact {num:,} / {den})")
    print("total:", b.total)
