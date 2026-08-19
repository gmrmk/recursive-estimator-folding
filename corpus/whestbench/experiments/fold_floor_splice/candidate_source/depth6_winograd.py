"""Depth-swept alternative-basis Winograd with leaf-layout operand scatter.

This module realizes ``tier_07_inplace_verbatim_leaves.winograd_l6_inplaceleaf``
as executable ``flopscope.numpy`` code: a depth sweep, the Karstadt-Schwartz
alternative basis, a level grading, the nested ``Psi`` transform, and operand
trees whose four view children per node are strided views rather than copies.

WHAT IS REALIZED AND WHAT IS NOT
================================
The tier-7 model prices ``3**L`` root-descended leaves at zero by handing the
leaf call one operand *descriptor* per leaf -- a base pointer and a leading
dimension.  ``numpy.matmul`` takes one strided ndarray per side, not a pointer
list, so those leaves have to live inside the batch buffer and the schedule
below pays one whole-matrix load per operand instead.  That is the tier-4 copy
lane (``4**L * A_L == m*k``), which is why the executed bill lands near the
tier-4 rung rather than on the tier-7 floor.  Everything else in the tier-7
model is realized exactly: the depth sweep, the basis, the grading, ``Psi``,
the three-arithmetic-blocks-per-node operand lanes, and the six-write decode.

The measured gap is small and is reported, not hidden:

    (4096, 256, 256)   direct                        535,822,336
                       frozen fallback (owned_batched) 471,711,744
                       tier-7 analytical floor        303,096,592
                       tier-4 rung                    304,210,704
                       THIS SCHEDULE, billed          307,749,648

LEAF LAYOUT
===========
Operands live in one contiguous buffer of shape ``(7,)*L + (rows, cols)``.  Leaf
``(v_1..v_L)`` is ``buf[v_1, ..., v_L]``.  A node at level ``j`` on path
``(v_1..v_j)`` owns ``buf[v_1..v_j][VIEW, ..., VIEW]`` -- its four view children
at every level below are its four quadrants, so under the all-alternative
grading the node's matrix *is* that strided sub-lattice, exactly tiled.
Reading a quadrant is one integer index; writing an arithmetic block writes its
whole free-view descendant set in one strided store.  Every level of every lane
is therefore one ``fnp`` call for all ``7**j`` nodes at once, which is the
slope discipline this operator exists to keep: ``4L`` calls per operand lane,
``6L`` for the decode, one ``matmul``, whatever the depth.

DIGIT ASSIGNMENT (the only nontrivial combinatorial choice)
===========================================================
The seven Winograd children in canonical order are

    left  [A11(q0), A12(q1), S4, A22(q3), S1(q2), S2, S3]
    right [B11(q0), B21(q2), B22(q3), T4, T1(q1), T2, T3]

so the left's four view children sit at positions {0,1,3,4} and the right's at
{0,1,2,4}: different sets.  A single permutation of the seven positions has to
send both sets to basic slices (so each side's owner regions are strided views)
and should send at least one side's digit->quadrant map into the group a NumPy
view can express (axis transpose and axis reversal, order 8), so that the load
from the caller's matrix is one ``copyto``.  Exhaustive search over all 5,040
permutations and all length-4 basic slices shows no permutation puts *both*
maps in that group; ``_selfcheck`` re-runs that search.  The permutation used
here is

    position 0 1 2 3 4 5 6  ->  digit 1 2 0 4 3 5 6

giving left views at digits 1..4 with the identity quadrant map (its load is one
``copyto``), right views at digits 0..3 with map (3,0,2,1) (its load pays one
gather, 7*k*n instead of k*n -- 0.13% of the call at (4096,256,256)), and the
decode's four outputs at digits 1..4 with map (1,0,3,2), which is in the group.

EXACTNESS CLASS
===============
Reassociation, not bit-identity.  Every value is a Winograd reassociation of the
direct product, exact over any ring and checked over the integers in
``_selfcheck``; in float32 it differs from ``a @ b`` at reassociation level.
"""

from __future__ import annotations

from itertools import permutations

import numpy as _np
import flopscope.numpy as fnp

from cost_model import (
    Bill,
    direct_cost,
    floor_candidate_bill,
    inplace_depth_core_cost,
    node_area_sum,
    owned_batched_candidate_bill,
)
from row_blocked_winograd import BLOCK_ROWS, RowBlockedBatchedWinograd


# --- the digit assignment, and the two facts that pin it -------------------

#: canonical position -> digit
PI = (1, 2, 0, 4, 3, 5, 6)

LEFT_VIEW_LO = 1                 # left view children occupy digits 1..4
RIGHT_VIEW_LO = 0                # right view children occupy digits 0..3
DECODE_VIEW_LO = 1               # decode outputs occupy digits 1..4

#: left  local index t (digit LEFT_VIEW_LO+t) -> quadrant
LEFT_QMAP = (0, 1, 2, 3)
#: right local index t (digit RIGHT_VIEW_LO+t) -> quadrant
RIGHT_QMAP = (3, 0, 2, 1)
#: decode local index t (digit DECODE_VIEW_LO+t) -> quadrant
DECODE_QMAP = (1, 0, 3, 2)

# arithmetic children, by digit
L_S2, L_S4, L_S3 = PI[5], PI[2], PI[6]        # 5, 0, 6
R_T2, R_T3, R_T4 = PI[5], PI[6], PI[3]        # 5, 6, 4

#: product digits, named by the Winograd product they hold (M1..M7 -> p0..p6)
D_M3, D_M1, D_M2, D_M5, D_M4, D_M6, D_M7 = (
    PI[2], PI[0], PI[1], PI[4], PI[3], PI[5], PI[6]
)

MAX_LEVELS = 8


def _hyperoctahedral() -> frozenset:
    """Permutations of the four quadrants a NumPy view can express."""
    out = set()
    for swap in (0, 1):
        for flip_row in (0, 1):
            for flip_col in (0, 1):
                image = []
                for value in range(4):
                    row, col = divmod(value, 2)
                    if swap:
                        row, col = col, row
                    image.append(2 * (row ^ flip_row) + (col ^ flip_col))
                out.add(tuple(image))
    return frozenset(out)


# --- billing ---------------------------------------------------------------


def realized_core_bill(m: int, k: int, n: int, levels: int) -> int:
    """Exactly what ``_core`` spends, lane by lane, at a complete core shape."""
    block = 1 << levels
    if min(m, k, n) <= 0 or any(value % block for value in (m, k, n)):
        raise ValueError(f"{levels} levels require multiples of {block}")
    leaves = 7 ** levels * direct_cost(m >> levels, k >> levels, n >> levels)
    # left: one reshape of the caller's block + one load + Psi + 3 blocks/node
    left = 2 * m * k + levels * (m * k // 4) + 3 * node_area_sum(m, k, levels)
    # right: two reshapes, one gather (billed 4x), one load, Psi, 3 blocks/node
    right = 7 * k * n + levels * (k * n // 4) + 3 * node_area_sum(k, n, levels)
    # decode: six writes/node, inverse Psi, one reshape of out, one unload
    decode = (
        6 * node_area_sum(m, n, levels)
        + levels * (m * n // 4)
        + 2 * m * n
    )
    return leaves + left + right + decode


def realized_right_lane_bill(k: int, n: int, levels: int) -> int:
    """The weight-side lane alone: what suite_03's hoist stops re-paying."""
    return 7 * k * n + levels * (k * n // 4) + 3 * node_area_sum(k, n, levels)


def realized_depth_bill(m: int, k: int, n: int, levels: int):
    """Bill for one depth including the fringe policy, or ``None`` if unlawful."""
    block = 1 << levels
    if levels < 1 or m % block:
        return None
    core_k = k - k % block
    core_n = n - n % block
    if core_k == 0 or core_n == 0:
        return None
    inner_width = k - core_k
    output_width = n - core_n
    core = realized_core_bill(m, core_k, core_n, levels)
    inner_correction = direct_cost(m, inner_width, core_n) if inner_width else 0
    inner_add = m * core_n if inner_width else 0
    output_tail = direct_cost(m, k, output_width) if output_width else 0
    total = core + inner_correction + inner_add + output_tail
    fringed = bool(inner_width or output_width)
    strategy = (
        f"realized_l{levels}_altbasis_mod{block}_fringe"
        if fringed
        else f"realized_l{levels}_altbasis"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total,
        direct_cost(m, k, n),
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def realized_candidate_bill(m: int, k: int, n: int, max_levels: int = MAX_LEVELS):
    """Cheapest executable route: depth sweep against the frozen fallback."""
    best = owned_batched_candidate_bill(m, k, n)
    levels = 2
    while levels <= max_levels and (1 << levels) <= min(m, k, n):
        route = realized_depth_bill(m, k, n, levels)
        if route is not None and route.total < best.total:
            best = route
        levels += 1
    return best


# --- the operator ----------------------------------------------------------


def _full(count: int):
    return (slice(None),) * count


class DepthWinograd:
    """Depth-swept alternative-basis Winograd over a bounded row window.

    ``multiply`` reproduces ``a @ b`` up to Winograd reassociation.  Shapes it
    cannot beat -- odd or small contracted widths, fringes that cost more than
    they save -- fall through to the frozen ``RowBlockedBatchedWinograd``
    incumbent, which this class never modifies.

    ``multiply`` returns a freshly allocated result on *both* routes, so a
    caller may hold several products live at once and add them.  That is the
    contract the terminal fold needs and the frozen fallback does not offer;
    see ``multiply`` and ``_selfcheck`` item (8).

    That fallback owns a 91.4375 MiB workspace at production geometry, and it
    used to be built in ``__init__`` underneath this operator's own pools, so
    the declared 192 MiB envelope was really 283.4 MiB and every shipped
    predict carried the larger of the two operators it did not use.  It is now
    built on first fallback dispatch, so a run that never leaves the depth
    route never pays for it.
    """

    def __init__(self, max_m: int, width: int,
                 block_rows: int = 2048,
                 workspace_mib: float = 192.0,
                 max_levels: int = 6,
                 dtype=fnp.float32):
        if min(max_m, width, block_rows) <= 0:
            raise ValueError("workspace dimensions must be positive")
        self.max_m = int(max_m)
        self.width = int(width)
        self.max_levels = int(max_levels)
        self.block_rows = int(block_rows)
        self.workspace_mib = float(workspace_mib)
        self.dtype = dtype
        self._fallback = None
        self._row_plans: dict = {}
        self._right_plans: dict = {}
        # suite_03: the right-hand operand stack is a pure function of the
        # weight matrix, so consecutive products against the *same* array
        # object reuse the tree instead of rebuilding it.  The reference is
        # held, which is what makes the identity test sound.
        self._hoisted = None
        # Every plan buffer is scratch that its own call overwrites, so all
        # plans of one side share one pool.  Caching plans without pooling is
        # how a 333 MiB predict became 1,211 MiB; capping the cache instead
        # traded that back for 200 MiB of reallocation per shape change, which
        # landed in residual.  Pooling gets both.
        self._pools: dict = {}
        self.last_strategy = "unused"
        self.last_native_calls = 0
        self.last_right_hoisted = False

    @property
    def fallback(self):
        """The frozen incumbent operator, built on the first dispatch to it.

        Its workspace is 91.4375 MiB at production geometry and is dead weight
        on any run the depth sweep never leaves, so it is not allocated until a
        shape actually needs it.  The frozen operator requires even workspace
        dimensions; rounding up only widens its scratch, so it is used exactly
        as shipped while odd construction dimensions stop being a constructor
        crash (found by the hostile shape battery at (255,256,256)).
        """
        if self._fallback is None:
            self._fallback = RowBlockedBatchedWinograd(
                self.max_m + self.max_m % 2,
                self.width + self.width % 2,
                BLOCK_ROWS,
            )
        return self._fallback

    @property
    def workspace_bytes(self) -> int:
        """Resident operator workspace: pooled scratch plus any built fallback."""
        pooled = sum(int(pool.nbytes) for pool in self._pools.values())
        inner = 0 if self._fallback is None else int(self._fallback.buffer_bytes)
        return pooled + inner

    # -- geometry -----------------------------------------------------------

    @staticmethod
    def _load_perm(levels: int):
        perm = []
        for lvl in range(levels):
            perm += [lvl, levels + 1 + lvl]
        return tuple(perm + [levels, 2 * levels + 1])

    @staticmethod
    def _right_inverse():
        inv = [0] * 4
        for local, quad in enumerate(RIGHT_QMAP):
            inv[quad] = local
        return inv

    def _rows_per_block(self, levels: int) -> int:
        """Largest multiple of 2**L whose row-side buffers fit the workspace.

        Sized from the widest operand this workspace can be asked for, so the
        row block is a function of the depth alone and the pools never have to
        grow once the first product of a depth has run.
        """
        block = 1 << levels
        leaves = 7 ** levels
        wide = max(self.width >> levels, 1)
        per_unit = 4.0 * leaves * 2 * wide            # bytes per leaf row
        budget = self.workspace_mib * 1024.0 * 1024.0 - 4.0 * leaves * wide * wide
        if per_unit <= 0.0 or budget <= 0.0:
            return block
        rows = int(budget // per_unit) * block
        rows = min(rows, self.max_m)
        return max(block, rows - rows % block)

    def _carve(self, name: str, shape, reserve: int = 0) -> object:
        """A view of the named pool with the given shape, resized if needed.

        The pool grows when the request does not fit and shrinks when the
        request fits in less than half of it.  Growth alone was the original
        rule, and it made the pools a high-water mark: the estimator's first
        products are full width, the terminal fold's are roughly half of it,
        and the pools held the difference -- about 106 MiB at production
        geometry -- through exactly the phase where three folded legs are live
        at once and the process peak is set.  The factor-of-two hysteresis is
        what keeps an alternating shape sequence from reallocating on every
        call, which is the trade this pool exists to avoid.

        ``reserve`` is the size the *widest* block of the current product needs.
        Without it the short remainder block at the end of every row sweep
        would look like a shrink and hand the next product a pool it has to
        grow again -- two reallocations and a replanned lane per call, which is
        the same trade under a different name.
        """
        count = 1
        for extent in shape:
            count *= extent
        need = max(count, int(reserve))
        pool = self._pools.get(name)
        size = 0 if pool is None else int(pool.shape[0])
        if pool is None or size < need or 2 * need <= size:
            # Views into the discarded pool are stale, so drop exactly the
            # plans that hold them -- clearing both sides here would make the
            # three pools of the first product evict each other's plans.  The
            # drop happens before the replacement is allocated, so the old and
            # new pools are never resident at the same time.
            if name == "right":
                self._right_plans.clear()
                self._hoisted = None
            else:
                self._row_plans.clear()
            pool = None
            self._pools[name] = None
            self._pools[name] = fnp.empty((need,), dtype=self.dtype)
            pool = self._pools[name]
        return fnp.reshape(pool[:count], tuple(shape))

    def _plan_right(self, levels: int, k: int, n: int):
        """Right-hand tree: shape-only, so it is built once per (L, k, n)."""
        key = (levels, k, n)
        plan = self._right_plans.get(key)
        if plan is not None:
            return plan
        if len(self._right_plans) > 8:
            self._right_plans.clear()
        kl, nl = k >> levels, n >> levels
        buf = self._carve("right", (7,) * levels + (kl, nl))
        lo = RIGHT_VIEW_LO
        root = buf[tuple(slice(lo, lo + 4) for _ in range(levels))]
        inv = self._right_inverse()

        # Every operand of every lane is a view of a buffer that outlives the
        # call, so the whole schedule is resolved to array objects once, here.
        # The hot loop then contains nothing but the fnp calls themselves --
        # this is the operator's entire slope story.
        psi = [(root[_full(lvl) + (inv[1],)], root[_full(lvl) + (inv[0],)])
               for lvl in range(levels)]
        encode = []
        for lvl in range(levels):
            quad = [self._at(buf, lvl, lo + inv[q], lo, levels) for q in range(4)]
            t2 = self._at(buf, lvl, R_T2, lo, levels)
            t3 = self._at(buf, lvl, R_T3, lo, levels)
            t4 = self._at(buf, lvl, R_T4, lo, levels)
            encode += [(quad[3], quad[1], t2), (t2, quad[0], t3),
                       (t2, quad[2], t4)]
        plan = {
            "levels": levels, "k": k, "n": n, "kl": kl, "nl": nl,
            "right": buf, "right_root": root,
            "load_perm": self._load_perm(levels),
            "gather": _np.array(RIGHT_QMAP, dtype=_np.intp),
            "shape_b": (2,) * levels + (kl,) + (2,) * levels + (nl,),
            "flat_b": (4,) * levels + (kl, nl),
            "psi_ops": psi, "encode_ops": encode,
        }
        self._right_plans[key] = plan
        return plan

    def _plan_rows(self, levels: int, rows: int, k: int, n: int,
                   block_rows: int = 0):
        """Row-side buffers and the two split views the loads write through.

        ``block_rows`` is the sweep's full row block; the last block of a sweep
        is shorter, and sizing the pools from it alone would make every product
        reallocate.
        """
        key = (levels, rows, k, n)
        plan = self._row_plans.get(key)
        if plan is not None:
            return plan
        if len(self._row_plans) > 8:
            self._row_plans.clear()
        ml, kl, nl = rows >> levels, k >> levels, n >> levels
        widest = max(int(block_rows), rows) >> levels
        left = self._carve("left", (7,) * levels + (ml, kl),
                           7 ** levels * widest * kl)
        prod = self._carve("prod", (7,) * levels + (ml, nl),
                           7 ** levels * widest * nl)

        def root(buf, lo):
            return buf[tuple(slice(lo, lo + 4) for _ in range(levels))]

        # Splitting each length-4 digit axis into (2, 2) is a pure view; it is
        # billed once here rather than on every call.
        left_root = fnp.reshape(root(left, LEFT_VIEW_LO),
                                (2, 2) * levels + (ml, kl))
        prod_root = fnp.reshape(root(prod, DECODE_VIEW_LO),
                                (2, 2) * levels + (ml, nl))
        # The left map is the identity, so (beta, gamma) are already the
        # quadrant bits.  The decode map is (1, 0, 3, 2); reversing the column
        # axis of every level turns it into the quadrant bits too.
        flip = [slice(None)] * (2 * levels + 2)
        for lvl in range(levels):
            flip[2 * lvl + 1] = slice(None, None, -1)
        prod_root = prod_root[tuple(flip)]

        lo = LEFT_VIEW_LO
        psi_left = [(left_root[_full(2 * lvl) + (1, 0)],
                     left_root[_full(2 * lvl) + (1, 1)])
                    for lvl in range(levels)]
        encode_left = []
        for lvl in range(levels):
            quad = [self._at(left, lvl, lo + t, lo, levels) for t in range(4)]
            s2 = self._at(left, lvl, L_S2, lo, levels)
            s4 = self._at(left, lvl, L_S4, lo, levels)
            s3 = self._at(left, lvl, L_S3, lo, levels)
            encode_left += [(quad[2], quad[0], s2), (quad[1], s2, s4),
                            (quad[3], s2, s3)]
        dlo = DECODE_VIEW_LO
        decode = []
        for lvl in range(levels - 1, -1, -1):
            m1 = self._at(prod, lvl, D_M1, dlo, levels)
            m2 = self._at(prod, lvl, D_M2, dlo, levels)
            m3 = self._at(prod, lvl, D_M3, dlo, levels)
            m4 = self._at(prod, lvl, D_M4, dlo, levels)
            m5 = self._at(prod, lvl, D_M5, dlo, levels)
            m6 = self._at(prod, lvl, D_M6, dlo, levels)
            m7 = self._at(prod, lvl, D_M7, dlo, levels)
            decode += [
                (fnp.add, m1, m6, m6),        # u2 = M1 + M6
                (fnp.add, m6, m7, m6),        # u3 = u2 + M7
                (fnp.add, m1, m2, m2),        # C11        -> digit of M2
                (fnp.subtract, m3, m7, m1),   # C12 - C22  -> digit of M1
                (fnp.subtract, m6, m4, m4),   # C21        -> digit of M4
                (fnp.add, m6, m5, m5),        # C22        -> digit of M5
            ]
        psi_c = [(prod_root[_full(2 * lvl) + (0, 1)],
                  prod_root[_full(2 * lvl) + (1, 1)])
                 for lvl in range(levels)]

        plan = {
            "levels": levels, "rows": rows, "k": k, "n": n,
            "ml": ml, "kl": kl, "nl": nl,
            "left": left, "prod": prod,
            "left_root": left_root, "prod_root": prod_root,
            "load_perm": self._load_perm(levels),
            "shape_a": (2,) * levels + (ml,) + (2,) * levels + (kl,),
            "shape_c": (2,) * levels + (ml,) + (2,) * levels + (nl,),
            "psi_left_ops": psi_left, "encode_left_ops": encode_left,
            "decode_ops": decode, "psi_c_ops": psi_c,
        }
        self._row_plans[key] = plan
        return plan

    # -- lanes --------------------------------------------------------------

    @staticmethod
    def _at(buf, prefix: int, digit: int, lo: int, levels: int):
        """``buf`` sliced to one digit at ``prefix`` with views below."""
        index = _full(prefix) + (digit,)
        index += tuple(slice(lo, lo + 4) for _ in range(levels - prefix - 1))
        return buf[index]

    # -- one complete core --------------------------------------------------

    def _core(self, a, b_ready, out, plan):
        """Load, transform, encode, one batched product, decode, unload.

        Every operand below is a precomputed view; the only per-call Python is
        the two reshapes of the caller's own arrays.
        """
        perm = plan["load_perm"]
        fnp.copyto(plan["left_root"],
                   fnp.reshape(a, plan["shape_a"]).transpose(perm))
        for dst, src in plan["psi_left_ops"]:          # A21 += A22, nested
            fnp.add(dst, src, out=dst)
        for lhs, rhs, dst in plan["encode_left_ops"]:  # S2, S4, S3 per level
            fnp.subtract(lhs, rhs, out=dst)
        fnp.matmul(plan["left"], b_ready, out=plan["prod"])
        for call, lhs, rhs, dst in plan["decode_ops"]:
            call(lhs, rhs, out=dst)
        for dst, src in plan["psi_c_ops"]:             # C12 += C22, nested
            fnp.add(dst, src, out=dst)
        fnp.copyto(fnp.reshape(out, plan["shape_c"]).transpose(perm),
                   plan["prod_root"])
        return 4 + 10 * plan["levels"]

    def _prepare_right(self, b, plan):
        levels = plan["levels"]
        b_nd = fnp.reshape(b, plan["shape_b"]).transpose(plan["load_perm"])
        flat = fnp.reshape(b_nd, plan["flat_b"])
        picked = flat[_np.ix_(*([plan["gather"]] * levels))]
        fnp.copyto(plan["right_root"], picked)
        for dst, src in plan["psi_ops"]:               # B12 -= B11, nested
            fnp.subtract(dst, src, out=dst)
        for lhs, rhs, dst in plan["encode_ops"]:       # T2, T3, T4 per level
            fnp.subtract(lhs, rhs, out=dst)
        return 4 + 4 * levels

    # -- public -------------------------------------------------------------

    def multiply(self, left, right):
        if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
            raise ValueError("incompatible 2-D matrix product")
        m, k = (int(value) for value in left.shape)
        n = int(right.shape[1])
        if m > self.max_m or max(k, n) > self.width:
            raise ValueError("product exceeds preallocated workspace")

        bill = realized_candidate_bill(m, k, n, self.max_levels)
        self.last_strategy = bill.strategy
        if not bill.strategy.startswith("realized_l"):
            # The frozen fallback hands back a view of its one preallocated
            # output, so two consecutive dispatches to it alias.  The terminal
            # fold holds two and three products live at once and adds them
            # (``fold3_estimator`` pre31, pre32), which turned such a sum into a
            # multiple of its last term.  ``multiply_at_depth`` already returns
            # a freshly allocated result per product; copying out here makes the
            # contract the same on both routes, for one write per output
            # element.  The frozen module is not touched.
            shared = self.fallback.multiply(left, right)
            self.last_native_calls = self.fallback.last_total_matmul_calls
            out = fnp.empty(shared.shape, dtype=shared.dtype)
            fnp.copyto(out, shared)
            return out
        return self.multiply_at_depth(left, right,
                                      int(bill.strategy.split("_")[1][1:]))

    def multiply_at_depth(self, left, right, levels: int):
        """The depth-``levels`` route, bypassing the sweep.  Exactness of one
        depth is a separate claim from the sweep's choice, so it gets its own
        entry point and ``_selfcheck`` drives every depth through it."""
        m, k = (int(value) for value in left.shape)
        n = int(right.shape[1])
        bill = realized_depth_bill(m, k, n, levels)
        if bill is None:
            raise ValueError(f"depth {levels} is unlawful at {(m, k, n)}")
        self.last_strategy = bill.strategy
        core_k, core_n = bill.core_k, bill.core_n
        rows = min(m, self._rows_per_block(levels))
        out = fnp.empty((m, n), dtype=self.dtype)

        right_plan = self._plan_right(levels, core_k, core_n)
        signature = (right, levels, core_k, core_n)
        hoisted = (
            self._hoisted is not None
            and self._hoisted[0] is right
            and self._hoisted[1:] == signature[1:]
        )
        if hoisted:
            calls = 0
        else:
            calls = self._prepare_right(right[:core_k, :core_n], right_plan)
            self._hoisted = signature
        self.last_right_hoisted = hoisted
        b_ready = right_plan["right"]

        for start in range(0, m, rows):
            stop = min(start + rows, m)
            plan = self._plan_rows(levels, stop - start, core_k, core_n, rows)
            calls += self._core(left[start:stop, :core_k], b_ready,
                                out[start:stop, :core_n], plan)

        if core_k < k:
            # The odd-k correction is streamed on the same row window as the
            # core.  Written whole it materializes an m x core_n float32
            # temporary -- 59 MiB at production geometry, and the single
            # largest transient in a traced predict, larger than the pooled
            # workspace it sits beside.  Both terms are exactly linear in rows
            # (`direct_cost` is m*n*(2k-1) and the add is one write per
            # element), so blocking reproduces the unsplit bill term for term
            # and no output element's dot product changes.
            tail = right[core_k:, :core_n]
            for start in range(0, m, rows):
                stop = min(start + rows, m)
                head = out[start:stop, :core_n]
                fnp.add(head, fnp.matmul(left[start:stop, core_k:], tail),
                        out=head)
                calls += 2
        if core_n < n:
            fnp.matmul(left, right[:, core_n:], out=out[:, core_n:])
            calls += 1
        self.last_native_calls = calls
        return out


# --- selfcheck --------------------------------------------------------------


def _integer_reference(a, b):
    return [[sum(a[i][t] * b[t][j] for t in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def _selfcheck() -> None:
    import flopscope as flops

    # (1) The digit assignment is forced, and the obstruction is real: no
    #     permutation of the seven children sends both sides' view sets to a
    #     basic slice with a view-expressible quadrant map.  Re-derived here.
    group = _hyperoctahedral()
    assert len(group) == 8
    left_q = {0: 0, 1: 1, 3: 3, 4: 2}
    right_q = {0: 0, 1: 2, 2: 3, 4: 1}
    windows = []
    for step in (1, 2, 3, -1, -2, -3):
        for start in range(7):
            seq = tuple(start + step * i for i in range(4))
            if all(0 <= x <= 6 for x in seq):
                windows.append(seq)
    both = 0
    for perm in permutations(range(7)):
        for seq in windows:
            if set(seq) != {perm[p] for p in (0, 1, 3, 4)}:
                continue
            fl = tuple(left_q[[p for p in (0, 1, 3, 4) if perm[p] == d][0]]
                       for d in seq)
            if fl not in group:
                continue
            for seq2 in windows:
                if set(seq2) != {perm[p] for p in (0, 1, 2, 4)}:
                    continue
                fr = tuple(right_q[[p for p in (0, 1, 2, 4) if perm[p] == d][0]]
                           for d in seq2)
                if fr in group:
                    both += 1
    assert both == 0, "a both-sides-view-expressible permutation exists"
    assert LEFT_QMAP in group and DECODE_QMAP in group
    assert RIGHT_QMAP not in group
    assert tuple(sorted(PI)) == (0, 1, 2, 3, 4, 5, 6)
    assert sorted(PI[p] for p in (0, 1, 3, 4)) == [1, 2, 3, 4]
    assert sorted(PI[p] for p in (0, 1, 2, 4)) == [0, 1, 2, 3]

    # (2) The tier-7 published depth table, digit for digit, from the ported
    #     closed forms; and the crowned call bill.
    tier7 = {
        1: 470876160, 2: 415535104, 3: 369662976, 4: 333938944,
        5: 310354368, 6: 303096592, 7: 320108124, 8: 375826177,
    }
    for lvl, value in tier7.items():
        got = inplace_depth_core_cost(4096, 256, 256, lvl)
        assert got == value, f"tier-7 L={lvl} reconstructs to {got}"
    assert min(tier7, key=tier7.get) == 6
    assert floor_candidate_bill(4096, 256, 256).total == 303_096_592
    assert owned_batched_candidate_bill(4096, 256, 256).total == 471_711_744
    assert direct_cost(4096, 256, 256) == 535_822_336

    # (3) The realized schedule's own closed form, and the fact that it is
    #     between the tier-4 rung and the fallback, never below the floor.
    assert realized_core_bill(4096, 256, 256, 6) == 307_749_648
    assert realized_core_bill(4096, 256, 256, 6) > 303_096_592
    assert realized_core_bill(4096, 256, 256, 6) < 471_711_744
    best = realized_candidate_bill(4096, 256, 256)
    assert best.strategy == "realized_l6_altbasis", best.strategy
    assert best.total == 307_749_648

    # (4) Executable exactness over the integers, at every depth the sweep can
    #     reach on a small shape.  Integers make "exact" literal: the schedule
    #     has to reproduce the triple loop entry for entry.
    for levels in (1, 2, 3):
        block = 1 << levels
        m, k, n = 4 * block, 2 * block, 2 * block
        rng = _np.random.default_rng(20260818 + levels)
        a = rng.integers(-9, 10, size=(m, k)).astype(_np.float64)
        b = rng.integers(-9, 10, size=(k, n)).astype(_np.float64)
        want = _np.asarray(_integer_reference(a.tolist(), b.tolist()),
                           dtype=_np.float64)
        op = DepthWinograd(m, max(k, n), workspace_mib=64.0,
                           max_levels=levels, dtype=fnp.float64)
        got = _np.asarray(op.multiply_at_depth(fnp.array(a), fnp.array(b),
                                               levels))
        assert op.last_strategy == f"realized_l{levels}_altbasis", (
            op.last_strategy)
        assert _np.array_equal(got, want), (
            f"depth {levels} is not exact over the integers")
        # ... and once more with both fringes live, so the fringe policy is
        # covered by the same literal-exactness standard.
        kk, nn = k + 1, n + 3
        a2 = rng.integers(-9, 10, size=(m, kk)).astype(_np.float64)
        b2 = rng.integers(-9, 10, size=(kk, nn)).astype(_np.float64)
        want2 = _np.asarray(_integer_reference(a2.tolist(), b2.tolist()),
                            dtype=_np.float64)
        op2 = DepthWinograd(m, max(kk, nn) + 1, workspace_mib=64.0,
                            max_levels=levels, dtype=fnp.float64)
        got2 = _np.asarray(op2.multiply_at_depth(fnp.array(a2), fnp.array(b2),
                                                 levels))
        assert _np.array_equal(got2, want2), (
            f"depth {levels} fringe route is not exact over the integers")

    # (5) The executed FLOP bill equals the closed form, measured, and the
    #     three terms that are not steady state are each pinned separately:
    #     the one-time plan reshapes, and suite_03's weight-side hoist.
    with flops.BudgetContext(flop_budget=10 ** 14) as budget:
        m, k, n = 512, 64, 64
        op = DepthWinograd(m, max(k, n), workspace_mib=64.0, max_levels=3)
        a = fnp.zeros((m, k), dtype=fnp.float32)
        b = fnp.zeros((k, n), dtype=fnp.float32)
        other = fnp.zeros((k, n), dtype=fnp.float32)
        start = budget.flops_used
        op.multiply(a, b)
        cold = budget.flops_used - start
        start = budget.flops_used
        op.multiply(a, other)              # fresh weight: the full bill
        warm = budget.flops_used - start
        assert not op.last_right_hoisted
        start = budget.flops_used
        op.multiply(a, other)              # same weight object: hoisted
        hoisted = budget.flops_used - start
        assert op.last_right_hoisted
    predicted = realized_candidate_bill(m, k, n, 3).total
    assert warm == predicted, (
        f"measured {warm} FLOPs, closed form says {predicted}")
    # The cold call additionally pays, once per shape: three pool reshapes and
    # the two root split views.  Everything after it is steady state.
    ml, kl, nl = m >> 3, k >> 3, n >> 3
    one_time = 7 ** 3 * (ml * kl + ml * nl + kl * nl) + m * k + m * n
    assert cold - warm == one_time, (
        f"one-time plan cost is {cold - warm}, expected {one_time}")
    assert warm - hoisted == realized_right_lane_bill(k, n, 3), (
        f"the hoist saved {warm - hoisted}, the weight lane is "
        f"{realized_right_lane_bill(k, n, 3)}")

    # (6) The same measured-equals-billed equality on a doubly fringed shape
    #     spread over more than one row block.  This is the route whose odd-k
    #     correction is streamed on the core's row window instead of being
    #     materialized whole, and both of its terms are linear in rows only if
    #     the split is exact -- so a wrong split shows up here as a bill
    #     mismatch rather than as a silent memory-for-arithmetic trade.
    with flops.BudgetContext(flop_budget=10 ** 14) as budget:
        m, k, n = 512, 67, 70
        op = DepthWinograd(m, max(k, n), workspace_mib=0.77, max_levels=3)
        assert 2 * op._rows_per_block(3) <= m, (
            f"fringe check needs several row blocks, got "
            f"{op._rows_per_block(3)} rows of {m}")
        a = fnp.zeros((m, k), dtype=fnp.float32)
        b = fnp.zeros((k, n), dtype=fnp.float32)
        other = fnp.zeros((k, n), dtype=fnp.float32)
        op.multiply_at_depth(a, b, 3)          # pay the one-time plan cost
        start = budget.flops_used
        op.multiply_at_depth(a, other, 3)      # fresh weight: the full bill
        fringed = budget.flops_used - start
    expected = realized_depth_bill(m, k, n, 3)
    assert expected is not None and "fringe" in expected.strategy, expected
    assert fringed == expected.total, (
        f"fringed route measured {fringed} FLOPs, closed form says "
        f"{expected.total}")

    # (7) The frozen fallback's 91.4375 MiB workspace is dead weight on a run
    #     that never leaves the depth route, so it must not exist until a shape
    #     actually dispatches to it.
    with flops.BudgetContext(flop_budget=10 ** 14):
        op = DepthWinograd(512, 64, workspace_mib=64.0, max_levels=3)
        assert op._fallback is None
        op.multiply(fnp.zeros((512, 64), dtype=fnp.float32),
                    fnp.zeros((64, 64), dtype=fnp.float32))
        assert op.last_strategy.startswith("realized_l")
        assert op._fallback is None, "the depth route built the fallback"
        assert op.workspace_bytes == sum(
            int(pool.nbytes) for pool in op._pools.values())
        op.multiply(fnp.zeros((511, 64), dtype=fnp.float32),   # odd m: direct
                    fnp.zeros((64, 64), dtype=fnp.float32))
        assert not op.last_strategy.startswith("realized_l")
        assert op._fallback is not None, "the fallback route never built it"

    # (8) Two products of one sum, both dispatching to the frozen fallback.
    #     The fallback returns a view of its single preallocated output, so the
    #     second dispatch overwrites the first and a caller that holds both --
    #     which is exactly what ``fold3_estimator`` pre31 (`product + second`)
    #     and pre32 (three legs) do -- summed the last term with itself.  The
    #     operands are integers and the arbiter is the triple loop, so the
    #     check is literal equality rather than a tolerance; it fails on the
    #     aliased build by a relative error of order 1, not of order eps.
    with flops.BudgetContext(flop_budget=10 ** 14):
        m, n, contracted = 24, 20, (20, 16)    # two widths, as pre31 has
        op = DepthWinograd(m, max(n, *contracted), workspace_mib=8.0,
                           max_levels=4)
        rng = _np.random.default_rng(20260819)
        pairs = []
        for k in contracted:
            a = rng.integers(-9, 10, size=(m, k)).astype(_np.float32)
            b = rng.integers(-9, 10, size=(k, n)).astype(_np.float32)
            pairs.append((a, b))
        held = []
        for a, b in pairs:
            held.append(op.multiply(fnp.array(a), fnp.array(b)))
            assert not op.last_strategy.startswith("realized_l"), (
                f"the regression needs the fallback route, got "
                f"{op.last_strategy}")
            # ... and the *view-returning* branch of it, not its direct escape.
            assert op.fallback.last_core_calls > 0, (
                "the fallback took its direct branch, which allocates and so "
                "cannot alias -- this shape does not exercise the defect")
        got = _np.asarray(held[0]) + _np.asarray(held[1])
    want = sum(
        _np.asarray(_integer_reference(a.tolist(), b.tolist()),
                    dtype=_np.float32)
        for a, b in pairs
    )
    assert _np.array_equal(got, want), (
        "two fallback dispatches aliased: the folded sum is a multiple of its "
        "last term")


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: digit-assignment obstruction, tier-7 depth table, "
          "realized closed form, integer exactness at depths 1-3, "
          "measured-equals-billed, lazy fallback construction and "
          "two-fallback-operand sum exactness all pass")
    for shape in ((4096, 256, 256), (64512, 256, 256), (4096, 256, 200)):
        floor = floor_candidate_bill(*shape)
        real = realized_candidate_bill(*shape)
        base = owned_batched_candidate_bill(*shape)
        print(f"  {shape}: direct {direct_cost(*shape):>14,}  "
              f"fallback {base.total:>14,}  floor {floor.total:>14,}  "
              f"realized {real.total:>14,}  [{real.strategy}]")
