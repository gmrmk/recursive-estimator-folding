"""Phased Walsh-Hadamard first product, on the crowned butterfly schedule.

Ported from ``experiments/v31_guards/package_source/kerdock_v3_estimator.py``
lines 103-132 (the deployed transcription) and then moved onto the schedule
suites 10..15 crowned for the identical transform:

  suite_10  the design scalar rides the 256 x 256 matrix, not the 32,256 x 256
            output block, so the closing whole-block pass disappears;
  suite_11  each radix-2 stage writes into the alternate buffer, so the
            ``copyto`` that existed only to save a soon-to-be-overwritten
            operand disappears (ping-pong);
  suite_12  the seed pass and stage 1 do not depend on the frame -- with signs
            in {+1, -1} the ordered pair stage 1 writes is one of four arrays
            that mention no phase -- so both are built once per net as a
            level-1 alphabet and the 126 seeded frames are never written;
  suite_13  stage 2's group of four rows likewise takes one of thirty-two
            values, and stage 3 would need 1,024 arrays costing 8,388,608
            against the 8,257,536 of the pass it replaces, so the ladder ends
            at stage 2.

A NumPy detail that changes the schedule, not the algebra: ``fnp.reshape`` is
billed at the array's element count even when it returns a view, while
transposes and basic slices are free.  The deployed hook reshapes the whole
32,256 x 256 block once per stage, which would be eight extra whole-block
passes.  This port therefore holds the two ping-pong buffers already split
into one axis per butterfly stage, so every stage is basic slicing and the only
reshape is the single one that hands the result back as a matrix.

WHAT IT IS WORTH HERE, AND WHY IT SHIPS OFF
===========================================
On the Kerdock lineage this replaces a real 32,256 x 256 x 256 product.  On
*this* lineage the design is 126 Haar-QR frames, not 126 phased Hadamard
frames: the butterfly computes ``mean_chi * H diag(phase_s) M / 16``, so
adopting it substitutes the sample design, which changes the estimator's
variance and therefore its MSE.  That is a class-B move against the parity law
(per-net ``|MSE_new/MSE_old - 1| <= 5e-4``), not a reassociation, and it is the
reason ``PHASED_DESIGN_IS_PARITY_PRESERVING`` is ``False`` and nothing in
``estimator.py`` calls this module.  It ships as the verified port plus its own
price, so the campaign can price the substitution without pricing it again.

WHAT IS REALIZED AND WHAT IS ONLY PRICED
========================================
``shared_stages`` 0 and 1 are realized and checked against an explicit
``H diag(phase) M``.  Level 2 (suite_13) is priced by ``butterfly_ops`` and is
NOT realized: its thirty-two-array alphabet is worth 7,733,248 per net against
a 144B suite bill (0.0054%), which does not buy the gather-index machinery it
needs.  ``_selfcheck`` refuses to let the unrealized rung be requested rather
than quietly mispricing it.

A MEASURED REVERSAL, RECORDED BECAUSE IT CONTRADICTS THE MODEL
==============================================================
suite_12's level-1 alphabet is a LOSS under this meter, and the realized bills
say so at 126 x 256 x 256:

    shared_stages=0   suite price 74,317,824   realized  74,383,360
    shared_stages=1   suite price 57,966,592   realized  99,319,808

The alphabet saves the seed pass and stage 1 -- two whole-block passes -- but
its four phase-free arrays still have to become 126 frames, and FlopScope
charges an advanced-index gather at four times its output plus one copy: five
blocks in, two blocks out.  The rung is real in the suite's model, where the
frames are addressed rather than materialized, and negative in NumPy.  The
realized default is therefore ``shared_stages=0``, and both remain available so
the contradiction can be re-measured rather than taken on trust.
"""

from __future__ import annotations

import numpy as _np
import flopscope.numpy as fnp


#: E[chi_256], the design's radius normalization.
MEAN_CHI_256 = 15.98438266660852747

#: Adopting the phased design substitutes the sample design on this lineage.
PHASED_DESIGN_IS_PARITY_PRESERVING = False

#: stage 1 writes the ordered pair (alphabet[i], alphabet[j]) for sign code c.
_PAIR_INDEX = _np.array([[0, 1], [1, 0], [2, 3], [3, 2]], dtype=_np.intp)


def normalized_walsh(width: int):
    """The unnormalized Walsh matrix the deployed hook builds."""
    stage = _np.eye(width, dtype=_np.float64)
    half = 1
    while half < width:
        blocks = stage.reshape(-1, 2, half, width)
        left = blocks[:, 0, :, :]
        right = blocks[:, 1, :, :]
        stage = _np.stack((left + right, left - right), axis=1).reshape(
            width, width
        )
        half *= 2
    return stage


def butterfly_ops(frames: int, width: int, columns: int, *,
                  pingpong: bool, shared_stages: int = 0,
                  final_scale: bool = False) -> int:
    """Element writes, by the suites' own accounting.

    ``pingpong=False, final_scale=True, shared_stages=0`` is the deployed
    transcription (14 passes per output element).  Each further argument moves
    one crowned rung: suite_10 drops ``final_scale``, suite_11 sets
    ``pingpong``, suite_12 sets ``shared_stages=1``, suite_13 sets 2.
    """
    block = frames * width * columns
    stages = int(width).bit_length() - 1
    if not 0 <= shared_stages <= 2:
        raise ValueError("only the seed pass, stage 1 and stage 2 are shared")
    per_stage = block if pingpong else (3 * block) // 2
    seed = 0 if shared_stages >= 1 else block
    shared = 0
    if shared_stages >= 1:
        shared += 5 * (width // 2) * columns          # one negate + four sums
    if shared_stages >= 2:
        shared += 32 * (width // 4) * columns         # thirty-two arrays
    return (
        seed
        + shared
        + max(stages - shared_stages, 0) * per_stage
        + (block if final_scale else 0)
    )


#: measured multiplier FlopScope charges for an advanced-index gather.
GATHER_RATE = 4


def realized_transform_bill(frames: int, width: int, columns: int,
                            shared_stages: int) -> int:
    """What ``PhasedWHT.transform`` actually spends under FlopScope.

    The suites' price plus the weight-side scale, and -- at
    ``shared_stages=1`` -- the alphabet gather NumPy needs to turn the four
    phase-free arrays into 126 seeded frames.  There is no reshape term: both
    ping-pong buffers are held pre-split into one axis per stage, and their
    matrix-shaped aliases are built once in ``_ensure``.
    """
    block = frames * width * columns
    ops = butterfly_ops(frames, width, columns, pingpong=True,
                        shared_stages=shared_stages)
    ops += width * columns                             # weight-side scale
    if shared_stages >= 1:
        ops += GATHER_RATE * block + block             # gather, then one copy
    return ops


class PhasedWHT:
    """``frame s -> scale * H diag(phase_s) M`` for every frame, ping-ponged."""

    def __init__(self, phases, width: int):
        phases = _np.asarray(phases)
        if phases.ndim != 2 or phases.shape[1] != width:
            raise ValueError("phase table must be (frames, width)")
        if width & (width - 1) or width < 2:
            raise ValueError("width must be a power of two")
        if not _np.isin(phases, (-1.0, 1.0)).all():
            raise ValueError("phases must be signs")
        self.width = int(width)
        self.frames = int(phases.shape[0])
        self.stages = self.width.bit_length() - 1
        self._signs = fnp.array(phases.astype(_np.float32))
        pairs = phases.reshape(self.frames, self.width // 2, 2)
        code = ((pairs[:, :, 0] < 0).astype(_np.intp) * 2
                + (pairs[:, :, 1] < 0).astype(_np.intp))
        self._pair_take = _PAIR_INDEX[code]                       # (F, W/2, 2)
        self._pair_rows = _np.arange(self.width // 2)[None, :, None]
        self._buffers = None
        self._index = None
        self._alphabet = None
        self._negated = None

    def _ensure(self, columns: int):
        shape = (self.frames,) + (2,) * self.stages + (columns,)
        if self._buffers is None or self._buffers[0].shape != shape:
            ping = fnp.empty(shape, dtype=fnp.float32)
            pong = fnp.empty(shape, dtype=fnp.float32)
            flat = (self.frames * self.width, columns)
            seed = (self.frames, self.width, columns)
            # Matrix-shaped aliases, built once: reshape is billed per call,
            # and the butterfly must not pay it eight times.
            self._buffers = (
                ping, pong,
                fnp.reshape(ping, flat), fnp.reshape(pong, flat),
                fnp.reshape(ping, seed),
            )
            take = self._pair_take.reshape(
                (self.frames,) + (2,) * (self.stages - 1) + (2,))
            rows = _np.arange(self.width // 2).reshape(
                (1,) + (2,) * (self.stages - 1) + (1,))
            self._index = (take, rows)
        return self._buffers

    def _level_one_alphabet(self, matrix):
        """[E+O, E-O, -(E-O), -(E+O)] over the width/2 row pairs: five writes.

        Written into one preallocated block instead of stacked, so the five
        writes suite_12 charges are the five writes performed.
        """
        columns = int(matrix.shape[1])
        shape = (4, self.width // 2, columns)
        if self._alphabet is None or self._alphabet.shape != shape:
            self._alphabet = fnp.empty(shape, dtype=fnp.float32)
            self._negated = fnp.empty(shape[1:], dtype=fnp.float32)
        alpha, negated = self._alphabet, self._negated
        even = matrix[0::2]
        odd = matrix[1::2]
        fnp.negative(even, out=negated)
        fnp.add(even, odd, out=alpha[0])
        fnp.subtract(even, odd, out=alpha[1])
        fnp.add(negated, odd, out=alpha[2])
        fnp.subtract(negated, odd, out=alpha[3])
        return alpha

    def transform(self, matrix, *, scale: float = MEAN_CHI_256 / 16.0,
                  shared_stages: int = 0):
        """Return ``scale * H diag(phase_s) matrix`` stacked over the frames."""
        if shared_stages not in (0, 1):
            raise NotImplementedError(
                "the level-2 alphabet is priced by butterfly_ops but not "
                "realized here; see this module's docstring")
        width, frames, stages = self.width, self.frames, self.stages
        columns = int(matrix.shape[1])
        if int(matrix.shape[0]) != width:
            raise ValueError("operand rows must match the design width")
        # suite_10 / suite_19: the design scalar rides the small matrix.
        scaled = fnp.multiply(matrix, scale)
        ping, pong, ping_flat, pong_flat, ping_seed = self._ensure(columns)

        if shared_stages == 1:
            alphabet = self._level_one_alphabet(scaled)
            take, rows = self._index
            fnp.copyto(ping, alphabet[take, rows])
            done = 1
        else:
            fnp.multiply(self._signs[:, :, None], scaled[None, :, :],
                         out=ping_seed)
            done = 0

        source, target = ping, pong
        flat = {id(ping): ping_flat, id(pong): pong_flat}
        for step in range(done, stages):
            axis = stages - step                   # bit axis this stage pairs
            head = (slice(None),) * axis
            left = source[head + (0,)]
            right = source[head + (1,)]
            fnp.add(left, right, out=target[head + (0,)])
            fnp.subtract(left, right, out=target[head + (1,)])
            source, target = target, source
        return flat[id(source)]


def _selfcheck() -> None:
    import flopscope as flops

    width, frames, columns = 16, 6, 5
    rng = _np.random.default_rng(20260818)
    phases = rng.choice((-1.0, 1.0), size=(frames, width))
    matrix = rng.integers(-4, 5, size=(width, columns)).astype(_np.float32)

    walsh = normalized_walsh(width)
    want = _np.stack(
        [walsh @ (phases[s][:, None] * matrix) for s in range(frames)], axis=0
    ).reshape(frames * width, columns).astype(_np.float32)

    # (1) both realized schedules are the transform, exactly (integer entries,
    #     integer transform, so "exactly" is literal).
    for shared in (0, 1):
        engine = PhasedWHT(phases, width)
        got = _np.asarray(engine.transform(fnp.array(matrix), scale=1.0,
                                           shared_stages=shared))
        assert _np.array_equal(got, want), (
            f"phased WHT with shared_stages={shared} is not the transform")

    # (2) the design scalar commutes with H and with diag(phase).
    engine = PhasedWHT(phases, width)
    scaled = _np.asarray(engine.transform(fnp.array(matrix), scale=0.25,
                                          shared_stages=1))
    assert _np.array_equal(scaled, (0.25 * want).astype(_np.float32)), (
        "moving the design scalar onto the operand changed the map")

    # (3) the unrealized rung is refused rather than silently mispriced.
    try:
        engine.transform(fnp.array(matrix), shared_stages=2)
    except NotImplementedError:
        pass
    else:
        raise AssertionError("shared_stages=2 must refuse")

    # (4) the four published constants of the ladder, at 126 x 256 x 256.
    assert butterfly_ops(126, 256, 256, pingpong=False,
                         final_scale=True) == 115_605_504
    assert butterfly_ops(126, 256, 256, pingpong=True) == 74_317_824
    assert butterfly_ops(126, 256, 256, pingpong=True,
                         shared_stages=1) == 57_966_592
    assert butterfly_ops(126, 256, 256, pingpong=True,
                         shared_stages=2) == 50_233_344
    assert 5 * (256 // 2) * 256 == 163_840
    assert 32 * (256 // 4) * 256 == 524_288
    # suite_13's shut proof: stage 3's alphabet costs more than the pass.
    assert 1024 * (256 // 8) * 256 == 8_388_608 > 126 * 256 * 256 == 8_257_536

    # (5) the executed bill equals the realized closed form, measured.
    with flops.BudgetContext(flop_budget=10 ** 13) as budget:
        engine = PhasedWHT(phases, width)
        operand = fnp.zeros((width, columns), dtype=fnp.float32)
        for shared in (0, 1):
            engine.transform(operand, shared_stages=shared)      # warm
            start = budget.flops_used
            engine.transform(operand, shared_stages=shared)
            spent = budget.flops_used - start
            predicted = realized_transform_bill(frames, width, columns, shared)
            assert spent == predicted, (
                f"shared_stages={shared}: measured {spent}, "
                f"closed form {predicted}")


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: the ping-pong butterfly equals H diag(phase) M at "
          "shared_stages 0 and 1, the design scalar commutes, the four "
          "published ladder constants reproduce, and measured equals billed")
    for shared in (0, 1, 2):
        print(f"  suite price shared_stages={shared}: "
              f"{butterfly_ops(126, 256, 256, pingpong=True, shared_stages=shared):,}")
    for shared in (0, 1):
        print(f"  realized here, shared_stages={shared}: "
              f"{realized_transform_bill(126, 256, 256, shared):,}")
    print(f"  the product it would replace: "
          f"{32256 * 256 * (2 * 256 - 1):,}")
