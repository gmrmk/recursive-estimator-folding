"""Tier 1: depth-swept grouped Winograd core (the incumbent's L=2 generalized to L).

ONE SUBSTANTIVE CHANGE
======================
The incumbent's grouped route is hard-wired to exactly two Winograd levels
(``batched_winograd_l2_core_cost``: 49 leaves at (m/4, k/4, n/4) plus a
``77 * (mk + kn + mn) // 16`` transform charge).  This tier replaces the frozen
constant 2 with a swept recursion depth L and selects the depth whose bill is
lowest for the requested shape.  Nothing else changes: the same leaf pricing,
the same per-level batched transform accounting, the same fringe policy, the
same ``Bill`` shape.

EXACTNESS IDENTITY
==================
The billed arithmetic is Winograd's seven-multiplication form of the 2x2 block
product, applied recursively.  For

    A = [[A11, A12],        B = [[B11, B12],
         [A21, A22]]             [B21, B22]]

with blocks over the (commutative) ring of matrix entries, define

    S1 = A21 + A22    T1 = B12 - B11
    S2 = S1  - A11    T2 = B22 - T1
    S3 = A11 - A21    T3 = B22 - B12
    S4 = A12 - S2     T4 = T2  - B21

    M1 = A11 * B11    M2 = A12 * B21    M3 = S4 * B22    M4 = A22 * T4
    M5 = S1  * T1     M6 = S2  * T2     M7 = S3 * T3

    U1 = M1 + M2                 C11 = U1
    U2 = M1 + M6                 C12 = U2 + M5 + M3
    U3 = U2 + M7                 C21 = U3 - M4
                                 C22 = U3 + M5

Expanding every M and U symbolically gives, term by term,

    C11 = A11 B11 + A12 B21
    C12 = A11 B12 + A12 B22
    C21 = A21 B11 + A22 B21
    C22 = A21 B12 + A22 B22

which is the definition of the block product.  The derivation uses only ring
addition, subtraction and multiplication -- no division, no reciprocal, no
truncation, no reordering that depends on the numeric values -- so the result
is the *same element of the ring* the direct route computes.  Applying the
identity again to each of M1..M7 (each of which is itself a matrix product of
half-sized blocks) composes exact identities and is therefore exact at every
depth.  Depth L is L nested applications; depth 2 is what the incumbent already
deploys and depth 5 is what this file selects at (4096, 256, 256).  The
exactness *class* is thus identical to the incumbent's -- this tier does not
introduce a new kind of algebra, it iterates the algebra the champion already
ships.

The depth-L core requires 2**L | m, k, n so that every recursion level splits
into equal halves and no level is ragged.  Residual columns/rows outside the
2**L-aligned core are billed with the incumbent's exact fringe rule (a direct
matmul on the fringe slab plus its accumulate), which is likewise exact.

WHY THE TRANSFORM MODEL IS THE INCUMBENT'S, NOT A NEW ONE
=========================================================
``batched_winograd_core_cost`` charges one level as
``7 * (mk + kn + mn) / 4`` (7 stacked A-blocks of m/2 x k/2, 7 stacked
B-blocks of k/2 x n/2, 7 reconstruction adds of m/2 x n/2).  Level j of the
recursion runs that same rule on 7**(j-1) parent blocks of half the parent's
dimensions, contributing ``7**j * (mk + kn + mn) / 4**j``.  Summing j = 1..L:

    L = 1 ->  7/4                     ->  matches batched_winograd_core_cost
    L = 2 ->  7/4 + 49/16 = 77/16     ->  matches batched_winograd_l2_core_cost
    L = 3 ->  77/16 + 343/64 = 651/64
    L      ->  sum_{j=1..L} 7**j * 4**(L-j) / 4**L

The L=1 and L=2 rows reproduce the incumbent's two frozen helpers exactly
(471,711,744 and 418,238,464 at (4096, 256, 256)), which is what licenses the
extrapolation: the closed form is fitted to the champion's own accounting, not
chosen to flatter the new depth.

RESULT AT (4096, 256, 256)
==========================
    L = 2 (incumbent)  418,238,464   = 407,830,528 leaves + 10,407,936 transforms
    L = 3              376,040,448
    L = 4              347,151,616
    L = 5              335,934,144   = 258,155,520 leaves + 77,778,624 transforms
    L = 6              350,724,304   (transform growth overtakes leaf savings)

Depth 5 is the interior minimum: leaves fall as (7/8)**L while transforms grow
as (7/4)**L, so the bill is convex in L and the sweep finds the turning point
rather than assuming it.  No approximation, no rank reduction, no f32
repricing -- pure schedule.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


# ---------------------------------------------------------------------------
# Helpers copied verbatim from tier_00_incumbent.py (self-contained by rule 7).
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


def candidate_bill(m: int, k: int, n: int) -> Bill:
    baseline = direct_cost(m, k, n)
    if m % 2:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    kc = k - (k % 2)
    nc = n - (n % 2)
    if kc == 0 or nc == 0:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    leaf = 7 * direct_cost(m // 2, kc // 2, nc // 2)
    core = leaf + m * kc + kc * nc + 7 * (m // 2) * (nc // 2) + (m // 2) * (nc // 2)
    inner = k - kc
    output = n - nc
    inner_mm = direct_cost(m, inner, nc) if inner else 0
    inner_add = m * nc if inner else 0
    output_mm = direct_cost(m, k, output) if output else 0
    calls = 7 + int(bool(inner)) + int(bool(output))
    total = core + inner_mm + inner_add + output_mm
    if calls > 8 or total >= baseline:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    return Bill(
        "winograd_preallocated", m, k, n, kc, nc, core,
        inner_mm, inner_add, output_mm, total, baseline, calls,
    )


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
# The one substantive change: depth L is swept instead of frozen at 2.
# ---------------------------------------------------------------------------


def winograd_transform_numerator(levels: int) -> int:
    """sum_{j=1..L} 7**j * 4**(L-j).  L=1 -> 7 (over 4); L=2 -> 77 (over 16)."""
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    return sum(7 ** j * 4 ** (levels - j) for j in range(1, levels + 1))


def batched_winograd_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
    """Depth-L batched Winograd core: 7**L leaves plus the nested transforms.

    Identical in form to the incumbent's L=1 and L=2 helpers -- it reproduces
    both of them exactly when called with levels=1 and levels=2.
    """
    block = 1 << levels
    if min(m, k, n) <= 0 or any(value % block for value in (m, k, n)):
        raise ValueError(f"{levels} Winograd levels require multiples of {block}")
    leaves = 7 ** levels * direct_cost(m // block, k // block, n // block)
    transforms = (
        winograd_transform_numerator(levels) * (m * k + k * n + m * n)
        // (4 ** levels)
    )
    return leaves + transforms


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
    core = batched_winograd_depth_core_cost(m, core_k, core_n, levels)
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
        else f"winograd_l{levels}_grouped"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total, direct_total,
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def depth_swept_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Select the cheapest exact owned route over all lawful Winograd depths.

    Supersedes ``grouped_l2_candidate_bill``: same routes, same fringe policy,
    same dual-odd branch, but the grouped core's depth is searched rather than
    frozen at two levels.
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

    # The swept depths.  Bounded by the 2-adic valuation of m (the core needs
    # 2**L | m) and by leaves staying at least one element wide.
    levels = 2
    while (1 << levels) <= m and (1 << levels) <= min(k, n):
        route = _depth_route(m, k, n, levels, baseline.direct)
        if route is not None and route.total < best.total:
            best = route
        levels += 1
    return best


# Campaign-facing name.
grouped_depth_candidate_bill = depth_swept_candidate_bill


def _selfcheck() -> None:
    """Fails loudly if the depth model drifts from the incumbent's L=1/L=2."""
    m, k, n = 4096, 256, 256
    assert batched_winograd_depth_core_cost(m, k, n, 1) == \
        batched_winograd_core_cost(m, k, n), "L=1 must equal the incumbent L=1"
    assert batched_winograd_depth_core_cost(m, k, n, 2) == \
        batched_winograd_l2_core_cost(m, k, n), "L=2 must equal the incumbent L=2"
    assert winograd_transform_numerator(1) == 7
    assert winograd_transform_numerator(2) == 77


if __name__ == "__main__":
    _selfcheck()
    bill = depth_swept_candidate_bill(4096, 256, 256)
    print(bill.to_dict())
    print("total:", bill.total)
    for level in range(1, 9):
        try:
            print(
                f"  L={level}",
                batched_winograd_depth_core_cost(4096, 256, 256, level),
            )
        except ValueError as exc:
            print(f"  L={level} unavailable: {exc}")
