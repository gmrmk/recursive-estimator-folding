"""Tier 3: write interior operand blocks straight into the leaf batch stack.

ONE SUBSTANTIVE CHANGE
======================
Tier 2 freed the *interior* levels from the batched-dispatch operand price and
then stopped, with an explicit reason in its own docstring:

    "The final level still pays all seven per parent, because that is the level
     whose 7**L blocks must land contiguously in the batch buffer."

That sentence is right about the requirement and wrong about the price.  The
7**L leaf operands do have to land in the batch buffer.  What tier 2 assumed --
without needing to, and this tier is the one change -- is that each of them
lands there by a *second* write, on top of the write that already produced the
bytes.  Three of every seven leaf operands (A11, A12, A22 on the left; B11,
B21, B22 on the right) are verbatim quadrants of their parent, and their parent
is, four times out of seven, an interior arithmetic block that we ourselves
write.  Route that interior write to scattered destinations -- its
identity-descendant quadrants straight into the leaf stack slots they will
occupy, the remainder into scratch -- and the leaf slot is filled by the write
that was going to happen anyway.  A write is one write per destination element
whatever its address, so the interior block still costs its own area and the
copy disappears.

The leaf stack still ends up contiguous and complete.  Nothing about the
dispatch is relaxed; the bytes simply arrive by the short route.

WHAT STILL PAYS, AND WHY THE RESIDUE IS NOT ZERO
================================================
A leaf operand is free only if some ancestor's write can carry it.  Walk each
leaf up the tree to the first ancestor that is an arithmetic block:

  * ARITHMETIC LEAF (4 of every 7).  It is a fresh linear combination; it is
    computed directly into its own stack slot.  Charged its area, exactly as
    every interior arithmetic block is charged.  Unchanged.
  * IDENTITY LEAF WITH AN ARITHMETIC ANCESTOR.  Its bytes are a quadrant-path
    sub-block of that ancestor.  The ancestor's scattered write places it.
    Charged nothing.
  * IDENTITY LEAF WHOSE WHOLE PATH IS IDENTITY, up to the root.  Its bytes live
    in the caller's input matrix, which we do not write and may not scatter.
    It costs a real copy.  There are exactly 3**L of these per side -- one for
    each all-identity path of length L.

So the leaf-level charge falls from 7**L blocks to 4*7**(L-1) + 3**L blocks,
and the whole operand bill collapses into one line that treats every level the
same way plus one boundary term:

    operand_stack_cost(a, b, L)
        = sum_{j=1..L} 4 * 7**(j-1) * (a >> j) * (b >> j)     (materialised)
        + 3**L * (a >> L) * (b >> L)                          (root copies)

DISJOINTNESS, THE ONE GEOMETRIC CLAIM
=====================================
The scatter is only free if an arithmetic block's identity-descendant leaves fit
inside it without collision.  They do, and the count is tight rather than
lucky.  From a block at level j, an identity step selects one of three quadrants
(11, 12, 22 on the left; 11, 21, 22 on the right), so an identity path of length
L-j names a distinct quadrant address; distinct addresses are disjoint regions.
There are 3**(L-j) such leaves, each of area (M_j/2**(L-j)) * (K_j/2**(L-j)),
so they occupy

    (3/4)**(L-j) * M_j * K_j   <=   M_j * K_j

of the block -- always a strict subset for L > j, never an overflow.  The
remainder goes to scratch, and the block's own arithmetic children read its
quadrants as strided views, which costs nothing in this cost model and is the
same licence tier 2 already spent.  ``verify_schedule`` asserts the disjointness
and the containment on real rectangles rather than asserting the argument.

L = 1 IS A NO-OP, WHICH IS WHAT LICENSES THE FORMULA
====================================================
At L = 1 every leaf hangs directly off the root, so no leaf has an arithmetic
ancestor and every identity leaf is a root copy:

    4 * (a/2)(b/2)  +  3 * (a/2)(b/2)  =  7 * (a/2)(b/2)

which is ``batched_winograd_core_cost``'s ``stack_fills``, digit for digit.  The
tier prices the champion's own L = 1 core unchanged and only diverges where the
tree is deep enough to have interior writes to ride on -- the same shape of
self-check that licensed tier 2.

EXACTNESS IDENTITY
==================
The billed arithmetic is Winograd's seven-multiplication form of the 2x2 block
product, applied recursively -- unchanged from tier 2, tier 1 and the champion.
For

    A = [[A11, A12],        B = [[B11, B12],
         [A21, A22]]             [B21, B22]]

    S1 = A21 + A22    T1 = B12 - B11
    S2 = S1  - A11    T2 = B22 - T1
    S3 = A11 - A21    T3 = B22 - B12
    S4 = A12 - S2     T4 = T2  - B21

    M1 = A11 * B11    M2 = A12 * B21    M3 = S4 * B22    M4 = A22 * T4
    M5 = S1  * T1     M6 = S2  * T2     M7 = S3  * T3

    U2 = M1 + M6      U3 = U2 + M7

    C11 = M1 + M2     C12 = U2 + M5 + M3
    C21 = U3 - M4     C22 = U3 + M5

Expanding every M and U symbolically gives, term by term,

    C11 = A11 B11 + A12 B21        C12 = A11 B12 + A12 B22
    C21 = A21 B11 + A22 B21        C22 = A21 B12 + A22 B22

the definition of the block product.  Only ring addition, subtraction and
multiplication occur -- no division, no reciprocal, no truncation, no
value-dependent reordering -- so the result is the same ring element the direct
route computes, and re-applying the identity to each M composes exact identities
at every depth.

The change this tier makes touches no term of that algebra.  It changes only
the ADDRESS an already-billed write is sent to.  A block written scattered and
the same block written contiguously hold the same entries in the same order
along each axis, so every M is formed from bit-identical operands and every C
is bit-identical.  What is deleted is a copy, never an arithmetic operation --
the strongest form of exactness available, which is why the identity argument
above is inherited verbatim rather than extended.

The depth-L core requires 2**L | m, k, n so that no level is ragged.  Residual
rows/columns outside the 2**L-aligned core are billed with the incumbent's exact
fringe rule (a direct matmul on the fringe slab plus its accumulate).

VERIFICATION RUN IN ``_selfcheck``
==================================
1. ``L = 1`` reproduces ``batched_winograd_core_cost`` exactly (no interior
   write exists to ride on, so the tier must be a no-op there -- and is).
2. An executable integer verifier builds the depth-L operand trees carrying a
   provenance tag per node (root / arithmetic / identity view) and the node's
   offset inside the block that owns its storage.  It multiplies the leaves,
   folds the reconstruction back up, and asserts the result equals the plain
   integer product.  Over the integers "exact" is literal and bit-for-bit.
3. The same verifier counts every write the scatter schedule really performs --
   one per element of every arithmetic block at every level, plus one per
   element of every root-descended identity leaf -- and asserts the count equals
   the billed closed form.  The bill is measured off the schedule, not asserted
   about it.
4. It asserts the geometry: for every owner block, the leaf rectangles it hosts
   are pairwise disjoint and lie inside its bounds.  This is the check that
   fails if the scatter were not actually free.

RESULT AT (4096, 256, 256)
==========================
    L = 1   471,711,744   (tier 2: 471,711,744)   <- no-op, as required
    L = 2   416,567,296   (tier 2: 417,402,880)
    L = 3   371,653,632   (tier 2: 373,742,592)
    L = 4   338,169,088   (tier 2: 342,294,784)
    L = 5   319,026,624   (tier 2: 326,599,104)   <- selected
    L = 6   320,036,176   (tier 2: 333,552,400)
    L = 7   351,987,132   (tier 2: 375,838,812)

    total 319,026,624  =  258,155,520 leaves
                        +  21,797,888 left operands
                        +   1,362,368 right operands
                        +  37,710,848 reconstruction adds

L = 5 stays the interior minimum, though L = 6 closes to within 1,009,552 --
the elision scales the deepest operand term hardest, which is where the depth
curve was being held back.  Against tier 2 the saving is 7,572,480 FLOPs
(2.319%); against the 535,822,336 direct comparator the ratio is 0.595397.

No approximation, no rank reduction, no f32 repricing, no compliance flags --
pure schedule.

LEAD LEFT FOR A LATER TIER (not taken here; one change per tier)
================================================================
The reconstruction lane, 37,710,848 and untouched since tier 1, is now the
largest overhead term.  Its 7 adds per node are minimal in the standard basis
(Probert 1976), so the only lawful door there is an alternative-basis
<2,2,2;7> in the Karstadt-Schwartz sense, trading the 15 standard-basis
additions for 12 plus an O(n^2 log n) basis change.  Netting that honestly
against 5 or 6 levels of basis change is a whole tier's work.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


# ---------------------------------------------------------------------------
# Helpers copied verbatim from the lineage (self-contained by rule 7).
# ---------------------------------------------------------------------------


def direct_cost(m: int, k: int, n: int) -> int:
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def batched_winograd_core_cost(m: int, k: int, n: int) -> int:
    """One batched leaf call with explicit stack fills and reconstruction."""
    if min(m, k, n) <= 0 or any(value % 2 for value in (m, k, n)):
        raise ValueError("one Winograd level requires positive even dimensions")
    leaf = 7 * direct_cost(m // 2, k // 2, n // 2)
    stack_fills = 7 * (m // 2) * (k // 2) + 7 * (k // 2) * (n // 2)
    output_adds = 7 * (m // 2) * (n // 2)
    return leaf + stack_fills + output_adds


def batched_winograd_l2_core_cost(m: int, k: int, n: int) -> int:
    """Two Winograd levels with all 49 leaves in one batched product."""
    if min(m, k, n) <= 0 or any(value % 4 for value in (m, k, n)):
        raise ValueError("two Winograd levels require multiples of four")
    leaves = 49 * direct_cost(m // 4, k // 4, n // 4)
    transforms = 77 * (m * k + k * n + m * n) // 16
    return leaves + transforms


@dataclass(frozen=True)
class Bill:
    strategy: str
    m: int
    k: int
    n: int
    core_k: int
    core_n: int
    core: int
    inner_correction: int
    inner_add: int
    output_tail: int
    total: int
    direct: int
    call_count: int

    def to_dict(self) -> dict:
        return asdict(self)


def batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Shape-only bill for the memory-bounded batched mutation."""
    baseline = direct_cost(m, k, n)
    if m % 2:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    kc = k - (k % 2)
    nc = n - (n % 2)
    inner = k - kc
    output = n - nc
    if kc == 0 or nc == 0 or (inner and output):
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    core = batched_winograd_core_cost(m, kc, nc)
    inner_mm = direct_cost(m, inner, nc) if inner else 0
    inner_add = (m * nc + m) if inner else 0
    output_mm = direct_cost(m, k, output) if output else 0
    total = core + inner_mm + inner_add + output_mm
    calls = 1 + int(bool(inner)) + int(bool(output))
    if total >= baseline:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    strategy = (
        "winograd_batched_preallocated_odd_k"
        if inner
        else "winograd_batched_preallocated"
    )
    return Bill(
        strategy, m, k, n, kc, nc, core, inner_mm, inner_add,
        output_mm, total, baseline, calls,
    )


def owned_batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Exact bill for the caller-owned, blockwise in-place operator."""
    base = batched_candidate_bill(m, k, n)
    direct_total = direct_cost(m, k, n) + m * k
    if base.strategy == "direct":
        return Bill("direct_owned", m, k, n, 0, 0, 0, 0, 0, 0,
                    direct_total, direct_cost(m, k, n), 1)
    tail_copy = m if base.output_tail else 0
    total = base.total + tail_copy
    if total >= direct_total:
        return Bill("direct_owned", m, k, n, 0, 0, 0, 0, 0, 0,
                    direct_total, direct_cost(m, k, n), 1)
    strategy = (
        "winograd_batched_owned_odd_k"
        if base.inner_correction
        else "winograd_batched_owned"
    )
    return Bill(
        strategy, m, k, n, base.core_k, base.core_n,
        base.core, base.inner_correction, base.inner_add,
        base.output_tail + tail_copy, total, direct_cost(m, k, n),
        base.call_count,
    )


# ---------------------------------------------------------------------------
# The one substantive change: an interior arithmetic block is written straight
# into the leaf-stack slots its identity descendants occupy, so only arithmetic
# leaves and root-descended identity leaves pay a leaf-stack write.
# ---------------------------------------------------------------------------


def operand_stack_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """Blocks written to form one side's depth-L operand set.

    Every level, interior or final, materialises exactly its four arithmetic
    blocks per parent -- Winograd's four input additions on this side.  The
    only leaf-stack copies left are the 3**L operands whose entire ancestry is
    identity, because those live in the caller's input matrix, which we do not
    write and therefore cannot scatter.
    """
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    materialised = sum(
        4 * 7 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
        for j in range(1, levels + 1)
    )
    root_copies = 3 ** levels * (a_dim >> levels) * (b_dim >> levels)
    return materialised + root_copies


def reconstruction_cost(m: int, n: int, levels: int) -> int:
    """Seven reconstruction adds per node per level -- unchanged from tier 1.

    Sums to 7/4 at L=1 and 77/16 at L=2 times m*n, matching both incumbent
    helpers.
    """
    return sum(7 ** j * (m >> j) * (n >> j) for j in range(1, levels + 1))


def ancestor_scattered_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
    """Depth-L batched Winograd core with ancestor-scattered leaf stacks."""
    block = 1 << levels
    if min(m, k, n) <= 0 or any(value % block for value in (m, k, n)):
        raise ValueError(f"{levels} Winograd levels require multiples of {block}")
    leaves = 7 ** levels * direct_cost(m // block, k // block, n // block)
    left = operand_stack_cost(m, k, levels)
    right = operand_stack_cost(k, n, levels)
    output = reconstruction_cost(m, n, levels)
    return leaves + left + right + output


def _depth_route(m: int, k: int, n: int, levels: int, direct_total: int):
    """Bill the depth-L grouped route with the incumbent's mod-block fringe rule."""
    block = 1 << levels
    if m % block:
        return None
    core_k = k - k % block
    core_n = n - n % block
    if core_k == 0 or core_n == 0:
        return None
    inner_width = k - core_k
    output_width = n - core_n
    core = ancestor_scattered_depth_core_cost(m, core_k, core_n, levels)
    inner_correction = direct_cost(m, inner_width, core_n) if inner_width else 0
    inner_add = m * core_n if inner_width else 0
    output_tail = (
        direct_cost(m, k, output_width) + m * output_width
        if output_width
        else 0
    )
    total = core + inner_correction + inner_add + output_tail
    fringed = bool(inner_width or output_width)
    strategy = (
        f"winograd_l{levels}_mod{block}_fringe"
        if fringed
        else f"winograd_l{levels}_ancestor_scattered"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total, direct_total,
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def ancestor_scattered_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Cheapest exact owned route over all lawful depths, leaf stacks scattered.

    Supersedes ``view_elided_candidate_bill``: same routes, same fringe policy,
    same dual-odd branch, same depth sweep -- the leaf stack simply stops paying
    for copies of bytes an interior write can deposit directly.
    """
    baseline = owned_batched_candidate_bill(m, k, n)
    best = baseline

    # Incumbent's dual-odd branch, preserved unchanged.
    if m % 2 == 0 and k > 1 and n > 1 and k % 2 and n % 2:
        core_k = k - 1
        core_n = n - 1
        core = batched_winograd_core_cost(m, core_k, core_n)
        inner_correction = direct_cost(m, 1, core_n)
        inner_add = m * core_n + m
        output_tail = direct_cost(m, k, 1) + m
        total = core + inner_correction + inner_add + output_tail
        if total < best.total:
            best = Bill(
                "winograd_batched_owned_dual_odd", m, k, n, core_k, core_n,
                core, inner_correction, inner_add, output_tail, total,
                baseline.direct, 3,
            )

    levels = 2
    while (1 << levels) <= m and (1 << levels) <= min(k, n):
        route = _depth_route(m, k, n, levels, baseline.direct)
        if route is not None and route.total < best.total:
            best = route
        levels += 1
    return best


# Campaign-facing name.
grouped_depth_candidate_bill = ancestor_scattered_candidate_bill


# ---------------------------------------------------------------------------
# Executable exactness + accounting + geometry verifier.
# Pure integers, so "exact" is literal and bit-for-bit.
# ---------------------------------------------------------------------------


def _quads(X):
    h = len(X) // 2
    w = len(X[0]) // 2
    return [
        [row[b * w:(b + 1) * w] for row in X[a * h:(a + 1) * h]]
        for a in (0, 1) for b in (0, 1)
    ]


def _lin(X, Y, sign):
    return [[X[i][j] + sign * Y[i][j] for j in range(len(X[0]))]
            for i in range(len(X))]


def _plain(A, B):
    return [[sum(A[i][t] * B[t][j] for t in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


class _Node:
    """One operand-tree node plus the provenance the scatter schedule needs."""

    __slots__ = ("mat", "tag", "owner", "off")

    def __init__(self, mat, tag, owner, off):
        self.mat = mat            # values (layout-independent)
        self.tag = tag            # "root" | "arith" | "view"
        self.owner = owner        # node whose write owns these bytes
        self.off = off            # (row, col) offset inside owner.mat

    @property
    def rows(self):
        return len(self.mat)

    @property
    def cols(self):
        return len(self.mat[0])


def _build_operands(root_mat, levels, side, writes, hosted):
    """Build the depth-L operand set under the scatter schedule.

    ``writes`` accumulates real destination-element writes.  ``hosted`` maps an
    owner node to the leaf rectangles its single write must place, which is the
    geometry the disjointness assertion checks.
    """
    root = _Node(root_mat, "root", None, (0, 0))
    root.owner = root
    nodes = [root]

    for _ in range(1, levels + 1):
        out = []
        for parent in nodes:
            p11, p12, p21, p22 = _quads(parent.mat)
            h = parent.rows // 2
            w = parent.cols // 2
            if side == "A":
                s1 = _lin(p21, p22, 1)
                s2 = _lin(s1, p11, -1)
                s3 = _lin(p11, p21, -1)
                s4 = _lin(p12, s2, -1)
                kids = [
                    (p11, "view", (0, 0)), (p12, "view", (0, w)),
                    (s4, "arith", None), (p22, "view", (h, w)),
                    (s1, "arith", None), (s2, "arith", None),
                    (s3, "arith", None),
                ]
            else:
                t1 = _lin(p12, p11, -1)
                t2 = _lin(p22, t1, -1)
                t3 = _lin(p22, p12, -1)
                t4 = _lin(t2, p21, -1)
                kids = [
                    (p11, "view", (0, 0)), (p21, "view", (h, 0)),
                    (p22, "view", (h, w)), (t4, "arith", None),
                    (t1, "arith", None), (t2, "arith", None),
                    (t3, "arith", None),
                ]
            for mat, tag, qoff in kids:
                if tag == "arith":
                    node = _Node(mat, "arith", None, (0, 0))
                    node.owner = node
                    # One write per element, wherever the scatter sends it.
                    writes[0] += node.rows * node.cols
                else:
                    node = _Node(
                        mat, "view", parent.owner,
                        (parent.off[0] + qoff[0], parent.off[1] + qoff[1]),
                    )
                out.append(node)
        nodes = out

    # Complete the leaf stack.  Arithmetic leaves were written into their slots
    # above.  Identity leaves ride an owner's write -- unless the owner is the
    # caller's input, which we cannot scatter, so those cost a real copy.
    for leaf in nodes:
        if leaf.tag != "view":
            continue
        if leaf.owner.tag == "root":
            writes[0] += leaf.rows * leaf.cols
        else:
            hosted.setdefault(id(leaf.owner), (leaf.owner, []))[1].append(
                (leaf.off[0], leaf.off[1], leaf.rows, leaf.cols)
            )
    return nodes


def _assert_scatter_is_free(hosted):
    """The load-bearing geometry: an owner's write can place all its leaves."""
    for owner, rects in hosted.values():
        covered = set()
        area = 0
        for r0, c0, hh, ww in rects:
            assert r0 >= 0 and c0 >= 0, "leaf rectangle starts outside its owner"
            assert r0 + hh <= owner.rows and c0 + ww <= owner.cols, (
                f"leaf rectangle {(r0, c0, hh, ww)} escapes owner "
                f"{(owner.rows, owner.cols)}"
            )
            for i in range(r0, r0 + hh):
                for j in range(c0, c0 + ww):
                    assert (i, j) not in covered, (
                        f"two leaves claim owner cell {(i, j)}"
                    )
                    covered.add((i, j))
            area += hh * ww
        assert area <= owner.rows * owner.cols, (
            "hosted leaves exceed the owner's own write"
        )


def _reconstruct(products, levels, m, n, adds):
    nodes = products
    for j in range(levels, 0, -1):
        h = m >> j
        w = n >> j
        nxt = []
        for i in range(0, len(nodes), 7):
            m1, m2, m3, m4, m5, m6, m7 = nodes[i:i + 7]
            c11 = _lin(m1, m2, 1)
            u2 = _lin(m1, m6, 1)
            c12 = _lin(_lin(u2, m5, 1), m3, 1)
            u3 = _lin(u2, m7, 1)
            c21 = _lin(u3, m4, -1)
            c22 = _lin(u3, m5, 1)
            adds[0] += 7 * h * w
            block = [[0] * (2 * w) for _ in range(2 * h)]
            for a in range(h):
                for b in range(w):
                    block[a][b] = c11[a][b]
                    block[a][b + w] = c12[a][b]
                    block[a + h][b] = c21[a][b]
                    block[a + h][b + w] = c22[a][b]
            nxt.append(block)
        nodes = nxt
    return nodes[0]


def verify_schedule(m: int, k: int, n: int, levels: int, seed: int) -> None:
    """Assert the schedule is exact, that the bill matches its real writes, and
    that every ancestor-scattered placement is disjoint and in bounds."""
    state = seed

    def nxt():
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return state % 19 - 9

    a = [[nxt() for _ in range(k)] for _ in range(m)]
    b = [[nxt() for _ in range(n)] for _ in range(k)]

    left_writes = [0]
    right_writes = [0]
    left_hosted: dict = {}
    right_hosted: dict = {}
    adds = [0]

    a_ops = _build_operands(a, levels, "A", left_writes, left_hosted)
    b_ops = _build_operands(b, levels, "B", right_writes, right_hosted)
    _assert_scatter_is_free(left_hosted)
    _assert_scatter_is_free(right_hosted)

    products = [_plain(a_ops[i].mat, b_ops[i].mat) for i in range(len(a_ops))]
    result = _reconstruct(products, levels, m, n, adds)

    assert result == _plain(a, b), f"schedule is not exact at {(m, k, n, levels)}"
    assert left_writes[0] == operand_stack_cost(m, k, levels), (
        f"left bill {operand_stack_cost(m, k, levels)} != writes {left_writes[0]}"
    )
    assert right_writes[0] == operand_stack_cost(k, n, levels), (
        f"right bill {operand_stack_cost(k, n, levels)} != writes {right_writes[0]}"
    )
    assert adds[0] == reconstruction_cost(m, n, levels), (
        f"output bill {reconstruction_cost(m, n, levels)} != adds {adds[0]}"
    )
    # The 3**L root-descended identity leaves are the whole residue; anything
    # else riding the root would mean an interior write was silently skipped.
    root_leaves = sum(
        1 for leaf in a_ops if leaf.tag == "view" and leaf.owner.tag == "root"
    )
    assert root_leaves == 3 ** levels, (
        f"expected {3 ** levels} root-descended identity leaves, got {root_leaves}"
    )


def _tier2_operand_stack_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """Tier 2's price, reproduced here only so the delta can be asserted."""
    interior = sum(
        4 * 7 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
        for j in range(1, levels)
    )
    return interior + 7 ** levels * (a_dim >> levels) * (b_dim >> levels)


def _selfcheck() -> None:
    m, k, n = 4096, 256, 256

    # 1. L=1 has no interior write to ride on, so this tier must be a no-op and
    #    must reproduce the champion's own stack_fills exactly.
    assert operand_stack_cost(m, k, 1) == 7 * (m // 2) * (k // 2)
    assert ancestor_scattered_depth_core_cost(m, k, n, 1) == \
        batched_winograd_core_cost(m, k, n), "L=1 must equal the incumbent L=1"

    # 2. The saving is exactly the identity leaves that gained an arithmetic
    #    ancestor: 3*7**(L-1) of them exist, 3**L still hit the root.
    for levels in range(1, 8):
        gained = 3 * 7 ** (levels - 1) - 3 ** levels
        block_area = (m >> levels) * (k >> levels)
        assert _tier2_operand_stack_cost(m, k, levels) \
            - operand_stack_cost(m, k, levels) == gained * block_area

    # 3. The reconstruction side is untouched: still 7/4 and 77/16.
    assert reconstruction_cost(m, n, 1) == 7 * (m // 2) * (n // 2)
    assert reconstruction_cost(m, n, 2) == 77 * m * n // 16

    # 4. Lineage parity: the frozen L=2 helper is still the tier-1 number, and
    #    this tier is strictly below it.
    tier1_l2 = (
        49 * direct_cost(m // 4, k // 4, n // 4)
        + 77 * (m * k + k * n + m * n) // 16
    )
    assert tier1_l2 == batched_winograd_l2_core_cost(m, k, n)
    assert ancestor_scattered_depth_core_cost(m, k, n, 2) < tier1_l2

    # 5. Executable exactness, accounting and geometry at several shapes.
    for shape in ((8, 4, 4, 2), (16, 8, 8, 3), (8, 8, 8, 3),
                  (32, 16, 16, 4), (64, 8, 8, 3)):
        verify_schedule(*shape, seed=20260817)


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: exactness, write-accounting and scatter geometry all pass")
    bill = ancestor_scattered_candidate_bill(4096, 256, 256)
    print(bill.to_dict())
    print("total:", bill.total)
    print("breakdown of the selected core:")
    best = 5
    print("  leaves        ",
          7 ** best * direct_cost(4096 >> best, 256 >> best, 256 >> best))
    print("  left operands ", operand_stack_cost(4096, 256, best))
    print("  right operands", operand_stack_cost(256, 256, best))
    print("  reconstruction", reconstruction_cost(4096, 256, best))
    for level in range(1, 9):
        try:
            print(f"  L={level}",
                  ancestor_scattered_depth_core_cost(4096, 256, 256, level))
        except ValueError as exc:
            print(f"  L={level} unavailable: {exc}")
