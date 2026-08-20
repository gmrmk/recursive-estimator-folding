"""M170: exact tensor-rank audit for M166's oriented collision-null control.

This is generated-array, response-free algebra only.  It studies the M166
coefficient

    c[i,j,k] = -(A[i,j] B[i,k] + B[i,j] A[i,k]),  B=A.T,

on the tie-to-zero orientation cell.  The audited compiler model is the one
actually relevant to M166: dense node-axis products, followed by rowwise
pointwise maps and output-axis Gram products.  A block or rectangular product
is charged by its scalar-product volume, not merely by its dispatch count.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
import random
from typing import Iterable, Sequence


Matrix = list[list[float]]
IntMatrix = list[list[int]]

WIDTH = 256
SOURCE_LAYERS = 31
PROTECTION = 1.25
TARGET_COMPILER_CAP = 14_019_121_200


@dataclass(frozen=True)
class Source211:
    """The only fourth-source coordinates required by the inherited ABI."""

    aaaa: Matrix
    aaab: Matrix
    aabb: Matrix


def zeros(rows: int, columns: int) -> Matrix:
    return [[0.0 for _ in range(columns)] for _ in range(rows)]


def transpose(value: Sequence[Sequence[float]]) -> Matrix:
    return [list(column) for column in zip(*value)]


def matmul(left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]) -> Matrix:
    """Small, dependency-free dense reference product (never a target claim)."""

    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix product")
    rows, middle, columns = len(left), len(right), len(right[0])
    return [
        [sum(left[i][k] * right[k][j] for k in range(middle)) for j in range(columns)]
        for i in range(rows)
    ]


def hadamard(*values: Sequence[Sequence[float]]) -> Matrix:
    if not values:
        raise ValueError("at least one matrix is required")
    rows, columns = len(values[0]), len(values[0][0])
    if any(len(value) != rows or any(len(row) != columns for row in value) for value in values):
        raise ValueError("Hadamard shapes differ")
    return [
        [math.prod(value[i][j] for value in values) for j in range(columns)]
        for i in range(rows)
    ]


def matrix_add(*values: Sequence[Sequence[float]]) -> Matrix:
    if not values:
        raise ValueError("at least one matrix is required")
    rows, columns = len(values[0]), len(values[0][0])
    if any(len(value) != rows or any(len(row) != columns for row in value) for value in values):
        raise ValueError("matrix shapes differ")
    return [
        [sum(value[i][j] for value in values) for j in range(columns)]
        for i in range(rows)
    ]


def scale(value: Sequence[Sequence[float]], factor: float) -> Matrix:
    return [[factor * item for item in row] for row in value]


def outer(left: Sequence[float], right: Sequence[float]) -> Matrix:
    return [[x * y for y in right] for x in left]


def _add_scaled(destination: Matrix, source: Sequence[Sequence[float]], factor: float) -> None:
    for i, row in enumerate(destination):
        for j in range(len(row)):
            row[j] += factor * source[i][j]


def positive_covariance(seed: int, width: int) -> Matrix:
    """Generated SPD covariance; no data, response, or scorer is consulted."""

    rng = random.Random(seed)
    factor = [[rng.uniform(-1.0, 1.0) for _ in range(width)] for _ in range(width)]
    covariance = matmul(factor, transpose(factor))
    for i in range(width):
        covariance[i][i] += float(width)
    return covariance


def generated_weight(seed: int, width: int, outputs: int) -> Matrix:
    rng = random.Random(seed)
    return [[rng.uniform(-1.0, 1.0) for _ in range(outputs)] for _ in range(width)]


def orient_covariance_edges(covariance: Sequence[Sequence[float]]) -> tuple[Matrix, Matrix, list[float]]:
    """The exact M166 max-correlation, tie-to-zero orientation rule.

    Width two is admitted here solely for the requested exhaustive algebra
    sweep.  Its two node scores necessarily tie, so the returned control is
    identically zero, exactly as M166's rule requires.
    """

    width = len(covariance)
    if width < 2 or any(len(row) != width for row in covariance):
        raise ValueError("covariance must be square with width at least two")
    if any(covariance[i][i] <= 0.0 for i in range(width)):
        raise ValueError("covariance diagonal must be positive")
    sigma = [math.sqrt(covariance[i][i]) for i in range(width)]
    correlation = [
        [covariance[i][j] / (sigma[i] * sigma[j]) for j in range(width)]
        for i in range(width)
    ]
    score = [
        max(correlation[i][j] * correlation[i][j] for j in range(width) if j != i)
        for i in range(width)
    ]
    a = zeros(width, width)
    for i in range(width):
        for j in range(width):
            if i != j and score[i] > score[j]:
                a[i][j] = float(covariance[i][j])
    return a, transpose(a), score


def coefficient_table(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> list[list[list[float]]]:
    width = len(a)
    return [
        [
            [-(a[i][j] * b[i][k] + b[i][j] * a[i][k]) for k in range(width)]
            for j in range(width)
        ]
        for i in range(width)
    ]


def compile_seven_products(weight: Sequence[Sequence[float]], a: Sequence[Sequence[float]]) -> Source211:
    """M166's exact seven-product compiler, expressed without NumPy.

    This is a small-width parity oracle.  Its seven billed product families
    are AW, A.TW, P, QAB, QBA, R, and S; it is not a deployment replacement.
    """

    b = transpose(a)
    za, zb = matmul(a, weight), matmul(b, weight)
    w2, product = hadamard(weight, weight), hadamard(za, zb)
    p = matmul(transpose(hadamard(weight, product)), weight)
    qab = matmul(transpose(hadamard(w2, za)), zb)
    qba = matmul(transpose(hadamard(w2, zb)), za)
    r = matmul(transpose(w2), product)
    s = matmul(transpose(hadamard(weight, za)), hadamard(weight, zb))
    aaab = scale(matrix_add(scale(p, 2.0), qab, qba), -3.0)
    aabb = scale(matrix_add(r, transpose(r), scale(matrix_add(s, transpose(s)), 2.0)), -2.0)
    return Source211([[aaab[i][i]] for i in range(len(aaab))], aaab, aabb)


def exhaustive_source(weight: Sequence[Sequence[float]], coefficient: Sequence[Sequence[Sequence[float]]]) -> Source211:
    """Independent ordered-triple source expansion, including width two."""

    width, outputs = len(weight), len(weight[0])
    aaaa, aaab, aabb = zeros(outputs, 1), zeros(outputs, outputs), zeros(outputs, outputs)
    for i in range(width):
        x = weight[i]
        for j in range(width):
            y = weight[j]
            for k in range(width):
                value = coefficient[i][j][k]
                if value == 0.0:
                    continue
                z = weight[k]
                xyz = [x[t] * y[t] * z[t] for t in range(outputs)]
                xxz = [x[t] * x[t] * z[t] for t in range(outputs)]
                xx = [x[t] * x[t] for t in range(outputs)]
                yz = [y[t] * z[t] for t in range(outputs)]
                xy = [x[t] * y[t] for t in range(outputs)]
                xz = [x[t] * z[t] for t in range(outputs)]
                _add_scaled(aaab, matrix_add(outer(xyz, x), outer(xxz, y)), 3.0 * value)
                first, split = outer(xx, yz), scale(outer(xy, xz), 2.0)
                _add_scaled(aabb, matrix_add(first, transpose(first), split, transpose(split)), value)
    for output in range(outputs):
        aaaa[output][0] = aaab[output][output]
    return Source211(aaaa, aaab, aabb)


def source_max_abs_difference(left: Source211, right: Source211) -> float:
    maximum = 0.0
    for name in ("aaaa", "aaab", "aabb"):
        first, second = getattr(left, name), getattr(right, name)
        if len(first) != len(second) or len(first[0]) != len(second[0]):
            raise ValueError("source shapes differ")
        for i in range(len(first)):
            for j in range(len(first[0])):
                maximum = max(maximum, abs(first[i][j] - second[i][j]))
    return maximum


def generated_parity_sweep() -> dict[int, float]:
    """Exhaustive source parity for generated widths 2 through 7."""

    result: dict[int, float] = {}
    for width in range(2, 8):
        covariance = positive_covariance(170_100 + width, width)
        a, b, _ = orient_covariance_edges(covariance)
        if any(abs(a[i][j] * b[i][j]) > 0.0 for i in range(width) for j in range(width)):
            raise AssertionError("tie-to-zero orientation lost disjoint support")
        weight = generated_weight(170_200 + width, width, width + 2)
        direct = exhaustive_source(weight, coefficient_table(a, b))
        compiled = compile_seven_products(weight, a)
        result[width] = source_max_abs_difference(direct, compiled)
    return result


def _rank_exact(value: Sequence[Sequence[int]]) -> int:
    """Exact rational rank for the symbolic coefficient and witness matrices."""

    work = [[Fraction(item) for item in row] for row in value]
    rows, columns, pivot_row = len(work), len(work[0]), 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [item / divisor for item in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [item - factor * basis for item, basis in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def _determinant_exact(value: Sequence[Sequence[int]]) -> int:
    """Fraction-free determinant for the fixed integer specialization."""

    size = len(value)
    if size == 0 or any(len(row) != size for row in value):
        raise ValueError("determinant input must be nonempty and square")
    work = [list(row) for row in value]
    sign, previous = 1, 1
    for pivot_column in range(size - 1):
        if work[pivot_column][pivot_column] == 0:
            replacement = next((row for row in range(pivot_column + 1, size) if work[row][pivot_column]), None)
            if replacement is None:
                return 0
            work[pivot_column], work[replacement] = work[replacement], work[pivot_column]
            sign *= -1
        pivot = work[pivot_column][pivot_column]
        for row in range(pivot_column + 1, size):
            for column in range(pivot_column + 1, size):
                work[row][column] = (work[row][column] * pivot - work[row][pivot_column] * work[pivot_column][column]) // previous
        previous = pivot
        for row in range(pivot_column + 1, size):
            work[row][pivot_column] = 0
    return sign * work[-1][-1]


def _matrix_vector_int(matrix: IntMatrix, vector_matrix: IntMatrix) -> IntMatrix:
    return [
        [sum(matrix[i][k] * vector_matrix[k][j] for k in range(len(matrix))) for j in range(len(vector_matrix[0]))]
        for i in range(len(matrix))
    ]


def admissible_specialization_certificate() -> dict[str, object]:
    """An exact, SPD, tied-score orientation-cell rank certificate.

    C=N/100 has diagonal one, is strictly diagonally dominant, and has score
    tiers {0,1}>{2,3}>{4,5}.  Its max edges 45, 30, and 15 create tied pairs;
    every cross-tier entry is smaller than the lower tier's max.  Hence the
    displayed A is precisely M166's lawful tie-to-zero orientation, rather
    than an unrestricted A/A.T toy specialization.
    """

    covariance_numerator: IntMatrix = [
        [100, 45, 7, 6, 4, 3],
        [45, 100, 8, 5, 5, 4],
        [7, 8, 100, 30, 6, 5],
        [6, 5, 30, 100, 7, 6],
        [4, 5, 6, 7, 100, 15],
        [3, 4, 5, 6, 15, 100],
    ]
    a_numerator: IntMatrix = [
        [0, 0, 7, 6, 4, 3],
        [0, 0, 8, 5, 5, 4],
        [0, 0, 0, 0, 6, 5],
        [0, 0, 0, 0, 7, 6],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]
    weight: IntMatrix = [
        [-3, -4, -4, -3, 2, -1, -3],
        [-2, 1, -3, 2, 4, -2, -1],
        [3, 1, 2, -1, -3, -3, 2],
        [1, -2, 1, 1, 2, 1, -3],
        [2, 3, -3, -1, -1, -2, 4],
        [-2, -4, -4, 3, -1, -2, -2],
    ]
    p_all = _matrix_vector_int(a_numerator, weight)
    q_all = _matrix_vector_int(transpose(a_numerator), weight)  # numerator forms; both actual rows divide by 100
    row = 2
    x, p, q = weight[row], p_all[row], q_all[row]
    left_31 = [
        [x[t] * p[t] * q[t] for t in range(7)],
        [x[t] * x[t] * p[t] for t in range(7)],
        [x[t] * x[t] * q[t] for t in range(7)],
    ]
    right_31 = [x, q, p]
    left_22 = [
        [x[t] * x[t] for t in range(7)],
        [p[t] * q[t] for t in range(7)],
        [x[t] * p[t] for t in range(7)],
        [x[t] * q[t] for t in range(7)],
    ]
    columns_3, columns_4 = (0, 1, 2), (0, 1, 2, 3)
    projection_minor = _determinant_exact([[p[0], p[1]], [q[0], q[1]]])
    left_31_minor = _determinant_exact([[feature[column] for column in columns_3] for feature in left_31])
    right_31_minor = _determinant_exact([[feature[column] for column in columns_3] for feature in right_31])
    left_22_minor = _determinant_exact([[feature[column] for column in columns_4] for feature in left_22])
    return {
        "covariance_numerator": covariance_numerator,
        "a_numerator": a_numerator,
        "weight": weight,
        "row": row,
        "score_tiers": [2025, 2025, 900, 900, 225, 225],
        "strict_diagonal_dominance": True,
        "projection_minor_numerator": projection_minor,
        "left_31_minor_numerator": left_31_minor,
        "right_31_minor_numerator": right_31_minor,
        "left_22_minor_numerator": left_22_minor,
        "projection_rank": _rank_exact([p, q]),
        "left_31_rank": _rank_exact(left_31),
        "right_31_rank": _rank_exact(right_31),
        "left_22_rank": _rank_exact(left_22),
    }


def symbolic_tensor_rank_ledger() -> dict[str, object]:
    """The formal monomial flattenings behind the lower-bound certificate.

    Put x=W[i,:], p=(AW)[i,:], q=(A.TW)[i,:].  After the two independent
    node-axis maps, the exact source has:

      aaab: 2(xpq)^T x + (x^2p)^T q + (x^2q)^T p,
      aabb: (x^2)^T(pq)+(pq)^T(x^2)
             +2[(xp)^T(xq)+(xq)^T(xp)].

    The aaab ordered flattening is diagonal rank three.  The aabb output is
    symmetric, so a product plus its free transpose is one billed family; its
    symmetric-pair quotient has rank two.  The output tags and their distinct
    output multidegrees prevent a terminal family from serving both blocks.
    """

    projection = [[1, 0], [0, 1]]
    aaab = [[2, 0, 0], [0, 1, 0], [0, 0, 1]]
    aabb_symmetric_pair = [[1, 0], [0, 2]]
    certificate = admissible_specialization_certificate()
    return {
        "model": "row-separable dense node-axis maps + rowwise pointwise maps + output Gram products; transpose reuse only for symmetric aabb",
        "projection_channels": ["p=AW", "q=A.TW"],
        "projection_flattening": projection,
        "projection_rank": _rank_exact(projection),
        "aaab_left_monomials": ["xpq", "x^2p", "x^2q"],
        "aaab_right_monomials": ["x", "q", "p"],
        "aaab_flattening": aaab,
        "aaab_ordered_rank": _rank_exact(aaab),
        "aabb_symmetric_pairs": [["x^2", "pq"], ["xp", "xq"]],
        "aabb_symmetric_pair_flattening": aabb_symmetric_pair,
        "aabb_symmetric_pair_rank": _rank_exact(aabb_symmetric_pair),
        "terminal_product_lower_bound": 5,
        "dense_product_lower_bound": 7,
        "certificate": certificate,
    }


def static_cost_ledger(width: int = WIDTH, layers: int = SOURCE_LAYERS) -> dict[str, int | float | str]:
    """Bill scalar products and pointwise/copy material, never dispatch count."""

    one_f32 = int(math.ceil(PROTECTION * int(layers) * (2 * int(width) ** 3 - int(width) ** 2)))
    one_f64 = 2 * one_f32
    pointwise_copy_f32 = int(math.ceil(PROTECTION * int(layers) * 64 * int(width) ** 2))
    return {
        "width": int(width),
        "layers": int(layers),
        "protection": PROTECTION,
        "f64_one_square_product_family": one_f64,
        "five_f64_dense_product_bill": 5 * one_f64,
        "six_f64_dense_product_bill": 6 * one_f64,
        "seven_f64_dense_product_bill": 7 * one_f64,
        "pointwise_copy_f32_allowance": pointwise_copy_f32,
        "pointwise_copy_f64_allowance": 2 * pointwise_copy_f32,
        "seven_f64_total_including_pointwise_copy": 7 * one_f64 + 2 * pointwise_copy_f32,
        "cap": TARGET_COMPILER_CAP,
        "six_product_margin_before_any_pointwise_or_copy": TARGET_COMPILER_CAP - 6 * one_f64,
        "seven_product_margin_including_pointwise_copy": TARGET_COMPILER_CAP - (7 * one_f64 + 2 * pointwise_copy_f32),
        "rectangular_or_block_rule": "charge 2*m*k*n-m*n f32 scalar-product work (twice for f64); concatenating channels does not reduce the sum of their widths",
    }


def static_results() -> dict[str, object]:
    parity = generated_parity_sweep()
    return {
        "prediction": "If a lawful <=5-family exact compiler exists, its symbolic terminal flattening must beat ranks 3+2 after two independent AW/A.TW channels.",
        "kill_condition": "A lawful tied-score SPD specialization has nonzero minors for both projection channels, the aaab rank-3 flattening, and the aabb symmetric-pair rank-2 flattening.",
        "generated_widths": list(parity),
        "generated_parity_max_abs": parity,
        "symbolic_tensor_rank": symbolic_tensor_rank_ledger(),
        "cost": static_cost_ledger(),
        "nonmerged_salvage": {
            "observation": "Sorting by the scalar score makes A strictly triangular and B=A.T the opposite strict triangle; their combined nonzero scalar multiply count is n*(n-1)*m, the count of one dense off-diagonal action.",
            "status": "UNTESTED_SEPARATE_STRUCTURED_KERNEL_DESCENDANT",
            "not_a_rank_claim": "This does not reduce the two independent projection channels or the seven-family tensor-rank lower bound.  Dispatches, triangular-kernel implementation, gathers/permutations, copies, dtype exactness, and actual billed scalar work remain unproved.",
            "composition_rule": "Only after an exact triangular-kernel cost proof may it be factorial-tested with independently validated L2 Strassen or cross-layer batching; no credit is inherited here.",
        },
        "disposition": "KILLED_STATIC: no <=5 dense-product-family exact compiler in the audited M166 normal form; the certified lower bound is seven and six f64 families already exceed the cap before pointwise/copy work.",
    }
