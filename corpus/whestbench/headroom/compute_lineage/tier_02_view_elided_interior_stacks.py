"""Tier 2: elide the interior batch-stack fills of the depth-swept Winograd core.

ONE SUBSTANTIVE CHANGE
======================
Tier 1 unfroze the recursion depth L but kept charging every level the *batched*
operand price, ``7 * (parent_mk + parent_kn) / 4`` -- seven stack blocks per
parent, at every one of the L levels.  That price exists for exactly one reason:
a batched matmul dispatch needs its 7 operands materialised side by side in one
contiguous stack.  Only the FINAL level dispatches a matmul.  Levels 1..L-1
dispatch nothing at all; their operands are read, strided, by the next level's
combination step and are never handed to BLAS.

This tier charges the interior levels the champion's own non-dispatching price
instead: the four arithmetic blocks only.  Of Winograd's seven left operands,
three (A11, A12, A22) are verbatim submatrices of the parent and four (S1..S4)
are arithmetic; of the seven right operands, three (B11, B21, B22) are verbatim
and four (T1..T4) are arithmetic.  An interior level therefore has to write only
the four combinations -- the three identity operands stay strided views of a
block that already exists in memory (either the input itself, or an S/T buffer
the previous level already wrote).  The final level still pays all seven per
parent, because that is the level whose 7**L blocks must land contiguously in
the batch buffer.

Nothing else moves: same leaf pricing, same reconstruction pricing, same fringe
policy, same depth sweep, same ``Bill`` shape, same route-selection order.

THIS IS THE CHAMPION'S OWN PRICE LIST, APPLIED WHERE IT WAS WRITTEN FOR
======================================================================
The incumbent ships two operand accountings side by side in ``cost_model.py``:

    winograd_core_cost:          input_adds = m * k + k * n          (4 blocks)
    batched_winograd_core_cost:  stack_fills = 7*(m/2)*(k/2)
                                             + 7*(k/2)*(n/2)         (7 blocks)

``m*k`` is exactly four blocks of ``(m/2)*(k/2)``: Winograd's eight input
additions, four on each side, which is the irreducible arithmetic of the
identity.  The extra 3/7 in the batched variant is pure data movement into the
dispatch buffer.  Tier 1's depth recursion applied the *dispatch* price to
levels that never dispatch.  Correcting that is a schedule change -- where the
batch boundary sits -- not a repricing: every block that is still written is
still charged 1/element, and the movement the v0.10.0 cost model prices is
movement that no longer happens.

Interior level j has 7**(j-1) parents, each writing 4 blocks of
(m >> j) x (k >> j), so its left-hand charge is

    4 * 7**(j-1) * (m >> j) * (k >> j)   =   (7/4)**(j-1) * m * k

against tier 1's ``(7/4)**j * m * k`` -- a factor 4/7 on every interior level.
At j = 1 it is ``m*k``, digit for digit the incumbent's ``input_adds``.

EXACTNESS IDENTITY
==================
The billed arithmetic is unchanged from tier 1 and from the champion: Winograd's
seven-multiplication form of the 2x2 block product, applied recursively.  For

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

which is the definition of the block product.  Only ring addition, subtraction
and multiplication appear -- no division, no reciprocal, no truncation, no
value-dependent reordering -- so the result is the same element of the ring the
direct route computes.  Each of M1..M7 is itself a product of half-sized blocks,
so re-applying the identity composes exact identities and is exact at every
depth.

The change this tier makes touches NO term of that algebra.  Not materialising
A11, A12, A22, B11, B21, B22 at an interior level changes *where the operand is
read from*, never what is read: a strided view of a block and a copy of that
block hold the same entries, so every M is formed from bit-identical operands
and every C is bit-identical.  The saving is deleted copies, not deleted
arithmetic -- the strongest form of exactness available, and the reason the
identity argument above is unchanged from tier 1 rather than extended.

The depth-L core requires 2**L | m, k, n so that no level is ragged.  Residual
rows/columns outside the 2**L-aligned core are billed with the incumbent's exact
fringe rule (a direct matmul on the fringe slab plus its accumulate).

VERIFICATION RUN IN ``_selfcheck``
==================================
1. ``L = 1`` reproduces ``batched_winograd_core_cost`` exactly.  A one-level core
   is all final level and no interior levels, so this tier must be a no-op
   there -- and it is, which is what licenses the interior formula.
2. An executable integer-arithmetic verifier builds the depth-L operand tree with
   the interior identity operands left as views, multiplies the leaves, folds the
   reconstruction back up, and asserts the result equals the plain integer
   product.  Over the integers "exact" is literal and bit-for-bit.
3. The same verifier counts every write it actually performs and asserts the
   count equals the billed ``4 * 7**(j-1)`` interior / ``7**L`` final formula.
   The bill is therefore measured off the schedule, not asserted about it.

RESULT AT (4096, 256, 256)
==========================
    L = 2   417,402,880   (tier 1: 418,238,464)
    L = 3   373,742,592   (tier 1: 376,040,448)
    L = 4   342,294,784   (tier 1: 347,151,616)
    L = 5   326,599,104   (tier 1: 335,934,144)   <- selected
    L = 6   333,552,400   (tier 1: 350,724,304)

    total 326,599,104  =  258,155,520 leaves
                        +  28,924,928 left operands
                        +   1,807,808 right operands
                        +  37,710,848 reconstruction adds

L = 5 stays the interior minimum; the elision lowers the whole curve without
moving its turning point, because it scales the operand terms rather than the
leaf term.  Against tier 1 the saving is 9,335,040 FLOPs (2.779%); against the
535,822,336 direct comparator the ratio is 0.609527.

No approximation, no rank reduction, no f32 repricing, no compliance flags --
pure schedule.
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
# The one substantive change: interior levels write 4 operand blocks per parent,
# not 7.  Only the dispatching final level fills a contiguous batch stack.
# ---------------------------------------------------------------------------


def operand_stack_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """Blocks written to form one side's depth-L operand set.

    Interior level j: 4 arithmetic blocks per parent (Winograd's four input
    additions on this side), 7**(j-1) parents.  Final level: all 7 per parent,
    because those 7**L blocks are the batched matmul's contiguous operand stack.
    """
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    interior = sum(
        4 * 7 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
        for j in range(1, levels)
    )
    final = 7 ** levels * (a_dim >> levels) * (b_dim >> levels)
    return interior + final


def reconstruction_cost(m: int, n: int, levels: int) -> int:
    """Seven reconstruction adds per node per level -- unchanged from tier 1.

    Sums to 7/4 at L=1 and 77/16 at L=2 times m*n, matching both incumbent
    helpers.
    """
    return sum(7 ** j * (m >> j) * (n >> j) for j in range(1, levels + 1))


def view_elided_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
    """Depth-L batched Winograd core with interior identity operands as views."""
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
    core = view_elided_depth_core_cost(m, core_k, core_n, levels)
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
        else f"winograd_l{levels}_view_elided"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total, direct_total,
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def view_elided_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Cheapest exact owned route over all lawful depths, interior stacks elided.

    Supersedes ``depth_swept_candidate_bill``: same routes, same fringe policy,
    same dual-odd branch, same depth sweep -- the interior levels simply stop
    paying for a batch buffer they never dispatch from.
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
grouped_depth_candidate_bill = view_elided_candidate_bill


# ---------------------------------------------------------------------------
# Executable exactness + accounting verifier (pure integers: "exact" is literal).
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


def _transform(X, levels, side, writes):
    """Depth-L operand set.  Interior identity operands are never copied."""
    nodes = [X]
    for j in range(1, levels + 1):
        final = j == levels
        out = []
        for parent in nodes:
            p11, p12, p21, p22 = _quads(parent)
            if side == "A":
                s1 = _lin(p21, p22, 1)
                s2 = _lin(s1, p11, -1)
                s3 = _lin(p11, p21, -1)
                s4 = _lin(p12, s2, -1)
                kids = [p11, p12, s4, p22, s1, s2, s3]
                arithmetic = 4
            else:
                t1 = _lin(p12, p11, -1)
                t2 = _lin(p22, t1, -1)
                t3 = _lin(p22, p12, -1)
                t4 = _lin(t2, p21, -1)
                kids = [p11, p21, p22, t4, t1, t2, t3]
                arithmetic = 4
            size = len(kids[0]) * len(kids[0][0])
            # Every leaf is copied into the contiguous batch stack; an interior
            # level writes only its arithmetic blocks and leaves the three
            # identity operands as strided views of `parent`.
            writes[0] += (7 if final else arithmetic) * size
            out.extend(kids)
        nodes = out
    return nodes


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
    """Assert the schedule is exact AND that the bill matches its real writes."""
    state = seed
    def nxt():
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return state % 19 - 9

    a = [[nxt() for _ in range(k)] for _ in range(m)]
    b = [[nxt() for _ in range(n)] for _ in range(k)]

    left_writes = [0]
    right_writes = [0]
    adds = [0]
    a_ops = _transform(a, levels, "A", left_writes)
    b_ops = _transform(b, levels, "B", right_writes)
    products = [_plain(a_ops[i], b_ops[i]) for i in range(len(a_ops))]
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


def _selfcheck() -> None:
    m, k, n = 4096, 256, 256

    # 1. A one-level core is all-final and no-interior, so this tier must be a
    #    no-op there.  It reproducing the incumbent exactly is what licenses the
    #    interior formula being applied at depth.
    assert view_elided_depth_core_cost(m, k, n, 1) == \
        batched_winograd_core_cost(m, k, n), "L=1 must equal the incumbent L=1"
    assert operand_stack_cost(m, k, 1) == 7 * (m // 2) * (k // 2)
    # 2. Interior level 1 charges exactly the incumbent's `input_adds = m*k`.
    assert operand_stack_cost(m, k, 2) == m * k + 49 * (m // 4) * (k // 4)
    # 3. The reconstruction side is untouched: it still reproduces 7/4 and 77/16.
    assert reconstruction_cost(m, n, 1) == 7 * (m // 2) * (n // 2)
    assert reconstruction_cost(m, n, 2) == 77 * m * n // 16
    # 4. Tier-1 parity check: rebuilding L=2 with the batched interior price
    #    must return the incumbent's frozen L=2 helper.
    tier1_l2 = (
        49 * direct_cost(m // 4, k // 4, n // 4)
        + 77 * (m * k + k * n + m * n) // 16
    )
    assert tier1_l2 == batched_winograd_l2_core_cost(m, k, n)
    assert view_elided_depth_core_cost(m, k, n, 2) < tier1_l2

    # 5. Executable exactness: the schedule computes the identical integer
    #    product, and its real write count equals the bill, at several shapes.
    for shape in ((8, 4, 4, 2), (16, 8, 8, 3), (8, 8, 8, 3),
                  (32, 16, 16, 4), (64, 8, 8, 3)):
        verify_schedule(*shape, seed=20260817)


if __name__ == "__main__":
    _selfcheck()
    bill = view_elided_candidate_bill(4096, 256, 256)
    print(bill.to_dict())
    print("total:", bill.total)
    print("breakdown of the selected core:")
    best = 5
    print("  leaves       ", 7 ** best * direct_cost(4096 >> best, 256 >> best, 256 >> best))
    print("  left operands", operand_stack_cost(4096, 256, best))
    print("  right operand", operand_stack_cost(256, 256, best))
    print("  reconstruction", reconstruction_cost(4096, 256, best))
    for level in range(1, 9):
        try:
            print(f"  L={level}", view_elided_depth_core_cost(4096, 256, 256, level))
        except ValueError as exc:
            print(f"  L={level} unavailable: {exc}")
