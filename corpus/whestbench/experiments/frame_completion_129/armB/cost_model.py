"""Closed-form FlopScope billing for one preallocated Winograd level."""

from __future__ import annotations

from dataclasses import asdict, dataclass


def direct_cost(m: int, k: int, n: int) -> int:
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def winograd_core_cost(m: int, k: int, n: int) -> int:
    """Seven leaf products + 8 input adds + 7 output adds + one copy.

    Dimensions are the complete, even core.  The copy initializes C11 from
    P1 because all four output quadrants are strided views of a full-width
    preallocated output.
    """
    if min(m, k, n) <= 0 or any(value % 2 for value in (m, k, n)):
        raise ValueError("one Winograd level requires positive even dimensions")
    leaf = 7 * direct_cost(m // 2, k // 2, n // 2)
    input_adds = m * k + k * n
    output_adds = 7 * (m // 2) * (n // 2)
    initialization_copy = (m // 2) * (n // 2)
    return leaf + input_adds + output_adds + initialization_copy


def batched_winograd_core_cost(m: int, k: int, n: int) -> int:
    """One batched leaf call with explicit stack fills and reconstruction."""
    if min(m, k, n) <= 0 or any(value % 2 for value in (m, k, n)):
        raise ValueError("one Winograd level requires positive even dimensions")
    leaf = 7 * direct_cost(m // 2, k // 2, n // 2)
    # Each seven-way operand stack has three copied identity blocks and four
    # arithmetic blocks.  Both cost one write per destination element.
    stack_fills = 7 * (m // 2) * (k // 2) + 7 * (k // 2) * (n // 2)
    output_adds = 7 * (m // 2) * (n // 2)
    return leaf + stack_fills + output_adds


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
    core = winograd_core_cost(m, kc, nc)
    inner = k - kc
    output = n - nc
    inner_mm = direct_cost(m, inner, nc) if inner else 0
    inner_add = m * nc if inner else 0
    output_mm = direct_cost(m, k, output) if output else 0
    calls = 7 + int(bool(inner)) + int(bool(output))
    total = core + inner_mm + inner_add + output_mm
    # Preserve the original engineering limit.  Two simultaneous ragged
    # dimensions need nine matmul calls and therefore dispatch direct even if
    # their arithmetic bill is lower.
    if calls > 8 or total >= baseline:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    return Bill(
        "winograd_preallocated",
        m,
        k,
        n,
        kc,
        nc,
        core,
        inner_mm,
        inner_add,
        output_mm,
        total,
        baseline,
        calls,
    )


def batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Shape-only bill for the memory-bounded batched mutation.

    Odd contracted widths dispatch direct because Mutation B deliberately has
    no full-size correction buffer.  An odd output width appends one direct
    tail call.
    """
    baseline = direct_cost(m, k, n)
    if m % 2 or k % 2:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    nc = n - (n % 2)
    if nc == 0:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    core = batched_winograd_core_cost(m, k, nc)
    output = n - nc
    output_mm = direct_cost(m, k, output) if output else 0
    total = core + output_mm
    calls = 1 + int(bool(output))
    if total >= baseline:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    return Bill(
        "winograd_batched_preallocated", m, k, n, k, nc, core, 0, 0,
        output_mm, total, baseline, calls
    )


def packed_candidate_bill(m: int, k: int, n: int) -> Bill:
    item = batched_candidate_bill(m, k, n)
    if item.strategy == "direct":
        return item
    return Bill(
        "winograd_packed_sequential", item.m, item.k, item.n,
        item.core_k, item.core_n, item.core, item.inner_correction,
        item.inner_add, item.output_tail, item.total, item.direct,
        7 + int(bool(item.output_tail)),
    )

