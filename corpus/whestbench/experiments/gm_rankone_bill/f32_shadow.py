"""float32-working-dtype shadow of the FROZEN M205 / M203 algebra.

The frozen modules
  experiments/m205_rankone_complete_physical_owner/m205_rankone_complete_physical_owner.py
  experiments/m203_terminal_contraction_circuit_no_go/m203_terminal_contraction_circuit_no_go.py
are imported read-only and NEVER edited.  Every closed form below is a literal
transcription of theirs with the working dtype lifted to a parameter.

DELIBERATELY INVERTED GUARDS (named, not bypassed): the frozen constructors
enforce float64-scale tolerances (symmetry allclose atol=2e-13, weight-sum
abs_tol=3e-13, singleton-pair isclose abs_tol=2e-13).  Those guards are
fail-closed against implicit float32 casts by design.  A float32 parity
demonstration cannot run behind them, so the shadow drops exactly those three
tolerance checks and nothing else.  Structural checks (shape, finiteness,
non-negative diagonal) are retained.

Transcription fidelity is verified in the harness: shadow(dtype=float64) must
agree with the frozen module to <=1e-12 absolute on every slot.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

B1_NODE_COUNT = 49


@dataclass(frozen=True)
class S3:
    aaaa: np.ndarray
    aaab: np.ndarray
    aabb: np.ndarray


def build_state(mean, covariance, D):
    mu = np.asarray(mean, dtype=D)
    v = np.asarray(covariance, dtype=D)
    diagonal = np.diag(v).copy()
    active = diagonal > D(0.0)
    count = int(np.count_nonzero(active))
    factor = np.zeros(mu.size, dtype=D)
    if count:
        factor[active] = np.sqrt(diagonal[active]) / D(math.sqrt(count))
    residual = diagonal - factor * factor
    residual = np.maximum(residual, D(0.0))
    omega = np.zeros(B1_NODE_COUNT, dtype=D)
    omega[:2] = D(0.5)
    cm = np.broadcast_to(mu, (B1_NODE_COUNT, mu.size)).copy()
    cm[0] += factor
    cm[1] -= factor
    cv = np.broadcast_to(residual, cm.shape).copy()
    return omega, cm, cv, factor, residual


def canonical_covariance(omega, mean, variance, D):
    mu = omega @ mean
    centered = mean - mu[None, :]
    return centered.T @ (omega[:, None] * centered) + np.diag(omega @ variance)


def canonical_delta_tilde_distinct(omega, mean, variance, D):
    mu = omega @ mean
    centered = mean - mu[None, :]
    covariance = canonical_covariance(omega, mean, variance, D)
    n = mean.shape[1]
    answer = np.zeros((n, n, n), dtype=D)
    raw_scale = D(0.0)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) != 3:
                    continue
                raw = np.sum(
                    omega
                    * (centered[:, i] * centered[:, i] + variance[:, i])
                    * centered[:, j]
                    * centered[:, k]
                )
                raw_scale = max(raw_scale, abs(float(raw)))
                answer[i, j, k] = (
                    raw
                    - covariance[i, i] * covariance[j, k]
                    - D(2.0) * covariance[i, j] * covariance[i, k]
                )
    return answer, float(raw_scale)


def rank_one_control_table(u, D):
    u = np.asarray(u, dtype=D)
    return D(-2.0) * np.einsum("i,j,k->ijk", u * u, u, u).astype(D)


def complete_physical_owner_table(distinct, k4, k31, k22, D):
    distinct = np.asarray(distinct, dtype=D)
    n = distinct.shape[0]
    k22 = D(0.5) * (k22 + k22.T)
    answer = np.zeros_like(distinct)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    answer[i, j, k] = distinct[i, j, k]
    for i in range(n):
        answer[i, i, i] = k4[i] / D(6.0)
        for j in range(n):
            if i == j:
                continue
            answer[i, i, j] = k31[i, j] / D(3.0)
            answer[i, j, i] = k31[i, j] / D(3.0)
            answer[i, j, j] = k22[i, j] / D(2.0)
    return answer


def zero_source(m, D):
    return S3(np.zeros(m, dtype=D), np.zeros((m, m), dtype=D), np.zeros((m, m), dtype=D))


def source_add(a, b):
    return S3(a.aaaa + b.aaaa, a.aaab + b.aaab, a.aabb + b.aabb)


def half_owned_feature(w, i, j, k, D):
    x, y, z = w[i], w[j], w[k]
    aaab = D(3.0) * (np.outer(x * y * z, x) + np.outer(x * x * z, y))
    first = np.outer(x * x, y * z)
    split = D(2.0) * np.outer(x * y, x * z)
    aabb = first + first.T + split + split.T
    return S3(np.diag(aaab).copy(), aaab, aabb)


def brute_complete_source(w, coefficient, D):
    w = np.asarray(w, dtype=D)
    coefficient = np.asarray(coefficient, dtype=D)
    n = w.shape[0]
    ans = zero_source(w.shape[1], D)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                scale = coefficient[i, j, k]
                if scale:
                    f = half_owned_feature(w, i, j, k, D)
                    ans = source_add(ans, S3(scale * f.aaaa, scale * f.aaab, scale * f.aabb))
    return ans


def compile_lifted_rank_one_control(w, u, D):
    w = np.asarray(w, dtype=D)
    u = np.asarray(u, dtype=D)
    p = w.T @ u
    rho = (w * w).T @ (u * u)
    b = w.T @ ((u * u)[:, None] * w)
    aaab = D(-6.0) * ((p * p)[:, None] * b + np.outer(rho * p, p))
    aabb = D(-2.0) * (
        np.outer(rho, p * p) + np.outer(p * p, rho) + D(4.0) * ((p[:, None] * b) * p[None, :])
    )
    return S3(np.diag(aaab).copy(), aaab, aabb)


def compile_lifted_rank_one_control_alt(w, u, D):
    """Algebraically identical, different reduction/association order (einsum)."""
    w = np.asarray(w, dtype=D)
    u = np.asarray(u, dtype=D)
    uu = u * u
    p = np.einsum("i,ia->a", u, w, optimize=False)
    rho = np.einsum("i,ia,ia->a", uu, w, w, optimize=False)
    b = np.einsum("ia,i,ib->ab", w, uu, w, optimize=False)
    aaab = D(-6.0) * (np.einsum("a,ab->ab", p * p, b) + np.einsum("a,b->ab", rho * p, p))
    aabb = D(-2.0) * (
        np.einsum("a,b->ab", rho, p * p)
        + np.einsum("a,b->ab", p * p, rho)
        + D(4.0) * np.einsum("a,ab,b->ab", p, b, p)
    )
    return S3(np.diag(aaab).copy(), aaab, aabb)


def independent_physical_collision_source(w, k4, k31, k22, D):
    """Transcription of the frozen TEST's independent [4]/[3,1]/[2,2] source."""
    w = np.asarray(w, dtype=D)
    width, outputs = w.shape
    aaab = np.zeros((outputs, outputs), dtype=D)
    aabb = np.zeros_like(aaab)
    for i in range(width):
        x = w[i]
        aaab += k4[i] * np.outer(x**3, x)
        aabb += k4[i] * np.outer(x * x, x * x)
        for j in range(width):
            if i == j:
                continue
            y = w[j]
            aaab += k31[i, j] * (D(3.0) * np.outer(x * x * y, x) + np.outer(x**3, y))
            mixed = np.outer(x * x, x * y)
            aabb += D(2.0) * k31[i, j] * (mixed + mixed.T)
    for i in range(width):
        for j in range(i + 1, width):
            x, y = w[i], w[j]
            aaab += D(3.0) * k22[i, j] * (np.outer(x * y * y, x) + np.outer(x * x * y, y))
            aabb += k22[i, j] * (
                np.outer(x * x, y * y) + np.outer(y * y, x * x) + D(4.0) * np.outer(x * y, x * y)
            )
    return S3(np.diag(aaab).copy(), aaab, aabb)


# ---------------- M203 two-rectangle circuit ----------------
def packed_terminal(x, a, D):
    x = np.asarray(x, dtype=D)
    a = np.asarray(a, dtype=D)
    p = a @ x
    q = a.T @ x
    u3 = np.vstack((D(2.0) * x * p * q, x * x * p, x * x * q))
    v3 = np.vstack((x, q, p))
    aaab = D(-3.0) * (u3.T @ v3)
    u2 = np.vstack((x * x, D(2.0) * x * p))
    v2 = np.vstack((p * q, x * q))
    raw = u2.T @ v2
    aabb = D(-2.0) * (raw + raw.T)
    return S3(np.diag(aaab).copy(), aaab, aabb)


def expanded_terminal(x, a, D):
    x = np.asarray(x, dtype=D)
    a = np.asarray(a, dtype=D)
    p = a @ x
    q = a.T @ x
    aaab = D(-3.0) * ((D(2.0) * x * p * q).T @ x + (x * x * p).T @ q + (x * x * q).T @ p)
    raw = (x * x).T @ (p * q) + (D(2.0) * x * p).T @ (x * q)
    aabb = D(-2.0) * (raw + raw.T)
    return S3(np.diag(aaab).copy(), aaab, aabb)


# ---------------- metrics ----------------
def slot_rel(left: S3, right: S3) -> dict:
    """Result-normalised relative error per slot: max|L-R| / max|R|."""
    out = {}
    worst = 0.0
    for name in ("aaaa", "aaab", "aabb"):
        L = np.asarray(getattr(left, name), dtype=np.float64)
        R = np.asarray(getattr(right, name), dtype=np.float64)
        num = float(np.max(np.abs(L - R)))
        den = float(np.max(np.abs(R)))
        rel = num / den if den > 0.0 else (0.0 if num == 0.0 else float("inf"))
        out[name] = {"max_abs_diff": num, "ref_max_abs": den, "rel": rel}
        worst = max(worst, rel)
    out["rel"] = worst
    return out


def scale_max(s: S3) -> float:
    return float(
        max(
            np.max(np.abs(s.aaaa)),
            np.max(np.abs(s.aaab)),
            np.max(np.abs(s.aabb)),
        )
    )
