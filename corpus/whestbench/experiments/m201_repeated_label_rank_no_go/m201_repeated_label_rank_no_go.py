"""Exact width-3 witness for the M201 repeated-label contraction no-go."""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence


WITNESS_WEIGHT = (
    (1, 2, 1),
    (2, 1, 3),
    (3, 4, 2),
)

EXPECTED_DECODER = (
    (72, 144, 216),
    (105, 156, 279),
    (75, 168, 207),
)


def determinant3(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    """Exact determinant of a 3-by-3 matrix."""

    a, b, c = matrix
    return Fraction(
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def _outer(left: Sequence[int], right: Sequence[int]) -> list[list[int]]:
    return [[x * y for y in right] for x in left]


def _add_scaled(
    target: list[list[Fraction]], scale: int | Fraction, value: Sequence[Sequence[int]]
) -> None:
    for row in range(3):
        for column in range(3):
            target[row][column] += Fraction(scale) * value[row][column]


def feature_aaab(
    weight: Sequence[Sequence[int]], i: int, j: int, k: int
) -> tuple[tuple[int, ...], ...]:
    """M151's exact coefficient-free ordered [2,1,1] aaab feature."""

    x, y, z = weight[i], weight[j], weight[k]
    xyz = [x[t] * y[t] * z[t] for t in range(3)]
    xxz = [x[t] * x[t] * z[t] for t in range(3)]
    xxy = [x[t] * x[t] * y[t] for t in range(3)]
    result = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    _add_scaled(result, 6, _outer(xyz, x))
    _add_scaled(result, 3, _outer(xxz, y))
    _add_scaled(result, 3, _outer(xxy, z))
    return tuple(tuple(int(value) for value in row) for row in result)


def repeated_label_decoder(
    weight: Sequence[Sequence[int]] = WITNESS_WEIGHT,
) -> tuple[tuple[int, ...], ...]:
    """Map the three symmetric repeated-label coefficients to S00/S01/S02."""

    columns: list[list[int]] = []
    for repeated in range(3):
        j, k = [label for label in range(3) if label != repeated]
        left = feature_aaab(weight, repeated, j, k)
        right = feature_aaab(weight, repeated, k, j)
        # M151 assigns one half to each singleton ordering.
        combined = [
            int(Fraction(left[0][column] + right[0][column], 2))
            for column in range(3)
        ]
        columns.append(combined)
    return tuple(tuple(columns[column][row] for column in range(3)) for row in range(3))


def exact_result() -> dict[str, object]:
    decoder = repeated_label_decoder()
    return {
        "candidate": "M201 repeated-label contraction no-go",
        "weight_determinant": int(determinant3(WITNESS_WEIGHT)),
        "decoder": [list(row) for row in decoder],
        "decoder_determinant": int(determinant3(decoder)),
        "status": "KILLED_EXACT_COMMUTE_THEN_COLLAPSE_REPEATED_LABEL_AXIS",
        "scope": "exact width-3 integer witness; no contest data or efficacy claim",
    }
