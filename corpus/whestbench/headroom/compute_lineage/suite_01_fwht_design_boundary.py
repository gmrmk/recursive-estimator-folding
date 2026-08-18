"""Suite tier 1: layer 1 is priced at the design boundary, by fast Walsh-Hadamard.

ONE SUBSTANTIVE CHANGE
======================
The suite incumbent bills all 32 layers at one anonymous (4096, 256, 256) tile
price -- 32 x 15.75 x 303,096,592.  Its own docstring names the frozen
assumption: "the design billed as anonymous rows".  The design is not anonymous.
It is 126 phased-Hadamard frames of 256 rows, antipodally doubled, and
2 * 126 * 256 = 64,512 is exactly the row count the incumbent's 15.75 tiles
carry.  Layer 1 -- and only layer 1 -- consumes those rows directly, so layer 1
alone can be evaluated through the design's own algebra.  Layers 2..32 consume
post-ReLU activations, which carry no Hadamard structure, and are left at the
crowned tier-7 call price, unchanged, this tier does not touch them.

EXACTNESS IDENTITY
==================
Write H for the 256 x 256 Sylvester-Hadamard matrix (entries +-1, H symmetric)
and D_j = diag(d_j) for frame j's +-1 phase vector.  Frame j's design rows are
the vectors D_j h over the rows h of H, i.e. the frame's row block is

    U_j = H D_j                                    (256 x 256, entries +-1)

The layer-1 preactivation block of that frame, for the first-layer weight matrix
W1 (256 x 256), is Z_j = U_j W1^T, whose transpose is

    Z_j^T = W1 D_j H^T = (W1 D_j) H^T .

Both factorisations name the same real numbers: entry (r, o) of Z_j is
sum_i H[r][i] * d_j[i] * W1[o][i] read either way.  W1 D_j is a sign flip of W1
(D_j is a +-1 diagonal, so no multiplication is performed); right-multiplication
by H^T is a sum of +-1-weighted terms, which the fast Walsh-Hadamard transform
computes in log2(n) butterfly passes of n add/subtracts per row.  The antipodal
half of the design is the row set -U_j, whose preactivation block is exactly
-Z_j: one negation per entry, charged below rather than assumed free.

So layer 1's first-layer matmul contains no multiplications at all under this
route.  That is not a saving bought by dropping work; it is the arithmetic the
+-1 design was always asking for, which the anonymous tile price hid.

``_selfcheck`` proves the identity rather than arguing it: it builds H by the
Sylvester recursion, builds the frames, computes Z both ways over the integers
at n = 8, 16, 32 with several random phase vectors and random integer W1, and
asserts bit-equality including the antipodal half.  It also counts the adds the
butterfly really performs and asserts the count equals the billed n*log2(n).

REROUTE CLASS, NOT APPROXIMATION
================================
The FWHT is a reassociation of the same sums of the same products (here, of the
same +-1-signed weights).  Over the integers it is bit-identical, and
``_selfcheck`` checks that literally.  Over floating point the summation order
differs, exactly as it does for the adopted Winograd fringe route and every
reschedule-class tier of the call ladder; no value is approximated, no rank is
reduced, no term is dropped.  Compliance flag recorded, same class as the
precedent.  No f32 repricing: every op counted here is one f32 add, subtract or
sign flip, priced at 1, the same unit the incumbent's call bill uses.

WHAT IS CHARGED, CONSERVATIVELY
===============================
Per net, per frame (126 frames):
    sign mask   W1 D_j                        256 * 256 =  65,536
    FWHT        256 rows x 256 * log2(256)  = 256 * 2048 = 524,288
    antipodal   -Z_j materialised            256 * 256 =  65,536
                                                        --------
                                                          655,360
    x 126 frames                                       82,575,360

The staged judge note priced the antipodal half at zero.  It is charged here:
the antipodal rows' preactivations are real values layer 2 reads, and one sign
flip per entry is what producing them costs.  The charge is 10.0% of the layer-1
bill and 0.18% of the tier's saving, and paying it closes the gate rather than
arguing it.

Removed from the incumbent: the layer-1 slice, 15.75 * 303,096,592 =
4,773,771,324 per net.  Nothing else in the incumbent moves.

DOUBLE-COUNT GATE (checked, does not fire)
==========================================
``suite_00_incumbent.suite_bill_per_net`` computes ``layers * tiles * call`` with
``layers, tiles = 32, 64512 / m`` and ``call`` from the shape-anonymous tier-7
bill at (4096, 256, 256).  The layer index never enters the price and no design
structure appears anywhere in the tier-7 module, whose bill is a function of
(m, k, n) alone.  Layer 1 is therefore billed at the generic tile price and this
tier is not re-spending a saving already banked.  ``_selfcheck`` asserts the
incumbent total equals 504 * call exactly, which is the same statement in
arithmetic.

The certified per-call floor (303,096,592 at anonymous (4096, 256, 256)) is
untouched: this tier does not reschedule anything inside a call.  It removes a
call, because at the design boundary there was never an anonymous (4096, 256,
256) product to make -- there was a Hadamard transform wearing one.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
The metered win is only real if the route runs as few large kernels, not many
small ones.  The shape it runs in:

  * One dispatch per frame, 126 per net, not one per row.  The FWHT is the
    batched in-place butterfly over the whole 256 x 256 frame block: 8 passes,
    each a full-block strided add/subtract, all 256 rows transformed together in
    the pass.  There is no per-row call and no per-row Python.
  * The sign mask is fused into the first butterfly pass as a negate-on-load of
    W1, so ``W1 D_j`` is never materialised as a separate buffer or a separate
    pass; it costs the 65,536 sign ops charged above and no extra traffic.
  * The block is 256 x 256 f32 = 256 KiB and is loaded once per frame, so all 8
    passes run against a resident tile; the whole layer-1 pass over the net is a
    sequential sweep of 126 such blocks.
  * The antipodal half is emitted by a fused negate at the point layer 2 loads
    the row, adding no pass of its own; its 65,536 ops per frame are charged
    anyway, so the accounting does not depend on that fusion landing.
  * Layers 2..32 keep the incumbent's batched tile dispatch verbatim, so the
    residual schedule is unchanged and this tier adds no new seam to it.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass

_T7_PATH = "corpus/whestbench/headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py"

# Production design shape: 126 phased-Hadamard frames of 256 rows, antipodally
# doubled.  2 * 126 * 256 == 64512 == the incumbent's 15.75 x 4096 design rows.
FRAMES = 126
WIDTH = 256
DESIGN_ROWS = 2 * FRAMES * WIDTH

LAYERS = 32
TILE_ROWS = 4096


def _t7():
    spec = importlib.util.spec_from_file_location("t7base", _T7_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


@dataclass(frozen=True)
class SuiteBill:
    strategy: str
    call_total: int
    layers: int
    tiles_per_layer: float
    layer1_sign_mask: int
    layer1_fwht: int
    layer1_antipodal: int
    layer1_total: int
    layers_2_to_32: int
    total: int

    def breakdown(self) -> dict:
        return {
            "layer1_sign_mask": self.layer1_sign_mask,
            "layer1_fwht_adds": self.layer1_fwht,
            "layer1_antipodal_negations": self.layer1_antipodal,
            "layer1_total": self.layer1_total,
            "layers_2_to_32": self.layers_2_to_32,
            "total": self.total,
        }


def _log2_exact(n: int) -> int:
    if n < 1 or n & (n - 1):
        raise ValueError(f"{n} is not a power of two")
    return n.bit_length() - 1


def fwht_adds_per_row(n: int) -> int:
    """Add/subtracts one length-n fast Walsh-Hadamard transform performs."""
    return n * _log2_exact(n)


def fwht_design_layer1_bill(frames: int = FRAMES, width: int = WIDTH) -> tuple:
    """(sign mask, FWHT adds, antipodal negations) for one net's layer 1."""
    sign_mask = frames * width * width
    fwht = frames * width * fwht_adds_per_row(width)
    antipodal = frames * width * width
    return sign_mask, fwht, antipodal


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH, n: int = WIDTH) -> SuiteBill:
    """Layer 1 at the design-boundary FWHT price, layers 2..32 at tier 7's call."""
    call = _t7().inplace_verbatim_leaves_candidate_bill(m, k, n).total
    if DESIGN_ROWS % 1 or DESIGN_ROWS * 1 != 64512:
        raise ValueError("design row count does not match the frozen suite shape")
    # Integer tile arithmetic: 64512 rows / 4096 rows per tile == 63/4 tiles.
    layer_slice = call * DESIGN_ROWS // m
    if layer_slice * m != call * DESIGN_ROWS:
        raise ValueError("tile count is not exact; refusing a rounded bill")
    sign_mask, fwht, antipodal = fwht_design_layer1_bill()
    layer1 = sign_mask + fwht + antipodal
    rest = (LAYERS - 1) * layer_slice
    return SuiteBill(
        "fwht_design_boundary_layer1",
        call,
        LAYERS,
        DESIGN_ROWS / m,
        sign_mask,
        fwht,
        antipodal,
        layer1,
        rest,
        layer1 + rest,
    )


# ---------------------------------------------------------------------------
# Executable exactness: integers, so "identical results" is literal.
# ---------------------------------------------------------------------------


def _hadamard(n: int) -> list:
    """Sylvester construction; H is symmetric with entries +-1."""
    H = [[1]]
    while len(H) < n:
        H = [row + row for row in H] + [row + [-x for x in row] for row in H]
    return H


def _fwht_in_place(vec: list, counter: list) -> list:
    """In-place butterfly.  Returns H @ vec and counts every add/subtract."""
    v = list(vec)
    n = len(v)
    step = 1
    while step < n:
        for base in range(0, n, step * 2):
            for i in range(base, base + step):
                a, b = v[i], v[i + step]
                v[i] = a + b
                v[i + step] = a - b
                counter[0] += 2
        step *= 2
    return v


def _rng(seed: int):
    state = seed

    def nxt(lo: int, hi: int) -> int:
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return lo + state % (hi - lo + 1)

    return nxt


def _selfcheck() -> None:
    # 1. The design shape is the shape the incumbent's tile count carries.
    assert DESIGN_ROWS == 64512, DESIGN_ROWS
    assert DESIGN_ROWS == 15.75 * TILE_ROWS

    # 2. The FWHT really computes H @ g, bit-for-bit, and really costs
    #    n*log2(n) adds -- both measured, not asserted from the formula.
    for n in (8, 16, 32, 64, 256):
        H = _hadamard(n)
        nxt = _rng(20260818 + n)
        g = [nxt(-9, 9) for _ in range(n)]
        counter = [0]
        fast = _fwht_in_place(g, counter)
        slow = [sum(H[r][i] * g[i] for i in range(n)) for r in range(n)]
        assert fast == slow, f"FWHT is not H @ g at n={n}"
        assert counter[0] == fwht_adds_per_row(n), (
            f"n={n}: butterfly performed {counter[0]} adds, billed "
            f"{fwht_adds_per_row(n)}")

    # 3. The full frame identity, including the antipodal half:
    #    Z_j = (H D_j) W1^T  ==  transpose of (W1 D_j) H^T, and the antipodal
    #    rows' block is exactly -Z_j.
    for n, frames in ((8, 3), (16, 4), (32, 2)):
        H = _hadamard(n)
        nxt = _rng(77000 + n)
        W1 = [[nxt(-9, 9) for _ in range(n)] for _ in range(n)]
        for _ in range(frames):
            d = [1 if nxt(0, 1) else -1 for _ in range(n)]
            # Direct route, as the incumbent bills it: design rows times W1^T.
            U = [[H[r][i] * d[i] for i in range(n)] for r in range(n)]
            direct = [[sum(U[r][i] * W1[o][i] for i in range(n))
                       for o in range(n)] for r in range(n)]
            anti_direct = [[sum(-U[r][i] * W1[o][i] for i in range(n))
                            for o in range(n)] for r in range(n)]
            # FWHT route: sign-mask W1 by d, then one FWHT per row of W1 D_j.
            counter = [0]
            G = [[W1[o][i] * d[i] for i in range(n)] for o in range(n)]
            ZT = [_fwht_in_place(G[o], counter) for o in range(n)]
            fast = [[ZT[o][r] for o in range(n)] for r in range(n)]
            anti_fast = [[-x for x in row] for row in fast]
            assert fast == direct, f"FWHT route differs at n={n}"
            assert anti_fast == anti_direct, f"antipodal half differs at n={n}"
            # The billed price for one frame must equal the ops the route just
            # performed: n*n sign flips forming G, the measured butterfly count,
            # and n*n negations forming the antipodal block.
            measured = (n * n) + counter[0] + (n * n)
            billed = sum(fwht_design_layer1_bill(frames=1, width=n))
            assert measured == billed, (
                f"n={n}: route performed {measured} ops, bill charges {billed}")

    # 3b. The same equality at the production width, where it is load-bearing.
    counter = [0]
    H = _hadamard(WIDTH)
    nxt = _rng(4242)
    d = [1 if nxt(0, 1) else -1 for _ in range(WIDTH)]
    W1row = [nxt(-9, 9) for _ in range(WIDTH)]
    fast = _fwht_in_place([W1row[i] * d[i] for i in range(WIDTH)], counter)
    slow = [sum(H[r][i] * d[i] * W1row[i] for i in range(WIDTH))
            for r in range(WIDTH)]
    assert fast == slow, "FWHT route differs from the direct route at n=256"
    assert sum(fwht_design_layer1_bill()) == FRAMES * (
        WIDTH * WIDTH + WIDTH * counter[0] + WIDTH * WIDTH)

    # 4. Double-count gate: the incumbent bills every layer, layer 1 included,
    #    at the same shape-anonymous call price.
    bill = suite_bill_per_net()
    incumbent = 504 * bill.call_total
    assert incumbent == 152760682368, incumbent
    assert bill.call_total == 303096592, bill.call_total
    layer_slice = bill.call_total * DESIGN_ROWS // TILE_ROWS
    assert layer_slice == 4773771324, layer_slice
    assert incumbent == LAYERS * layer_slice

    # 5. The tier changes layer 1 and nothing else.
    assert bill.layers_2_to_32 == incumbent - layer_slice
    assert bill.total == incumbent - layer_slice + bill.layer1_total
    assert bill.layer1_total == 82575360, bill.layer1_total
    assert bill.total < incumbent
    assert bill.layer1_total < layer_slice


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: FWHT exactness (bit-for-bit over the integers), measured "
          "butterfly op count, frame identity with antipodal half, "
          "double-count gate and single-change containment all pass")
    b = suite_bill_per_net()
    incumbent = 504 * b.call_total
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>28} {value:>15,}")
    print(f"  {'incumbent':>28} {incumbent:>15,}")
    print(f"  {'saving':>28} {incumbent - b.total:>15,}")
    print(f"  ratio vs incumbent            {b.total / incumbent:.9f}")
    print("total:", b.total)
