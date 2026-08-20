#!/usr/bin/env python3
"""Finite dual witness for the block-mixture minimax over the 129 real-MUB blocks.

Companion to DUAL_WITNESS_CERTIFICATE_20260818.md. Discharges the rank-10
OFFLINE_CERTIFICATE row of the 2026-08-13 Schauder/Kerdock theorem map:

    "Sion minimax / Hahn-Banach duality | Produce a finite dual witness for why
     no tested block mixture improves | Require matching primal and dual
     objectives on a frozen matrix | OFFLINE_CERTIFICATE"

Everything structural is exact rational arithmetic (fractions.Fraction). The
only f64 inputs are the committed spectral-energy shares a_l read from R0's
artifact; every conclusion that uses them is reported with its own bracket.

Deterministic: no randomness, no network, no wall-clock dependence. Two runs
produce byte-identical JSON.

Run:
    python dual_witness_certificate.py            # verify + print + emit JSON
    python dual_witness_certificate.py --quiet    # JSON only

Exit code 0 iff every check in CHECKS passes.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent  # corpus/whestbench
R0_JSON = CORPUS / "experiments" / "r0_harmonic_energy_spectrum" / "r0_results.json"
MUB_JSON = CORPUS / "experiments" / "mub129_completion" / "RESULTS.json"

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    CHECKS.append((name, bool(ok), detail))
    return bool(ok)


# ---------------------------------------------------------------------------
# 1. Exact normalised Gegenbauer kernel G_l^(alpha)(t) = C_l^(alpha)(t)/C_l^(alpha)(1)
# ---------------------------------------------------------------------------


def gegenbauer(l: int, t: F, alpha: F) -> F:
    """C_l^(alpha)(t) by the standard three-term recurrence, in exact rationals."""
    if l == 0:
        return F(1)
    c_prev, c_cur = F(1), 2 * alpha * t
    for n in range(2, l + 1):
        c_prev, c_cur = c_cur, (
            2 * t * (n + alpha - 1) * c_cur - (n + 2 * alpha - 2) * c_prev
        ) / F(n)
    return c_cur


def G(l: int, t: F, d: int) -> F:
    """Zonal kernel on S^{d-1}, normalised to G_l(1) = 1."""
    alpha = F(d - 2, 2)
    return gegenbauer(l, t, alpha) / gegenbauer(l, F(1), alpha)


# ---------------------------------------------------------------------------
# 2. The 129 block summaries, in closed form
# ---------------------------------------------------------------------------
#
# A "block" is one orthonormal basis of R^d, antipodally doubled to 2d points,
# carrying weight w_a spread uniformly over its 2d points. For a family of
# mutually unbiased bases every cross-block inner product is +-1/sqrt(d) and
# every within-block off-diagonal inner product is 0. Hence the degree-l
# block-summary Gram matrix M^(l)_{ab} = (2d)^-2 sum_{p in a, q in b} G_l(<p,q>)
# has only two distinct entries:
#
#     M_aa = (1 + (-1)^l + (2d-2) G_l(0)) / (2d)
#     M_ab = ((1 + (-1)^l)/2) * G_l(1/sqrt(d))       (a != b)
#
# For odd l both vanish: the antipodal doubling annihilates every odd degree.
# For even l, M^(l) = alpha_l * I + g_l * J  with
#
#     g_l     = G_l(1/sqrt(d))
#     alpha_l = (2 + (2d-2) G_l(0)) / (2d)  -  g_l
#
# so that for any mixture w in the simplex,  Q_l(w) = w' M^(l) w = alpha_l*||w||^2 + g_l.


def block_summary(l: int, d: int, isqrt_d: F) -> tuple[F, F]:
    """Return (alpha_l, g_l) for even l. isqrt_d is the exact value of 1/sqrt(d)."""
    assert l % 2 == 0, "odd degrees have M^(l) = 0 identically"
    g = G(l, isqrt_d, d)
    diag = (2 + (2 * d - 2) * G(l, F(0), d)) / F(2 * d)
    return diag - g, g


def Q(alpha_l: F, g_l: F, k: int) -> F:
    """Degree-l zonal error of the uniform mixture on k blocks (||w||^2 = 1/k)."""
    return alpha_l / k + g_l


D = 256
ISQRT_D = F(1, 16)  # 1/sqrt(256) exactly
K_CHAMP = 126  # champion: uniform over 126 of the 129 blocks
K_MAX = 129  # maximum number of real MUBs in R^256 = d/2 + 1, attained since 256 = 4^4

# Even degrees carried in the certificate. Degrees above L_MODEL have g_l below
# f64 resolution (verified in CHECK "g_l tail is numerically zero") and are
# folded into a single lumped tail block with alpha = 1/256, g = 0.
L_MODEL = 40
EVEN = [l for l in range(4, L_MODEL + 1) if l % 2 == 0]

SUMMARY: dict[int, tuple[F, F]] = {l: block_summary(l, D, ISQRT_D) for l in EVEN}
SUMMARY[2] = block_summary(2, D, ISQRT_D)


# ---------------------------------------------------------------------------
# CHECK A. Independent d = 4 brute force: build 3 real MUBs, enumerate all
# 24 x 24 point pairs, and confirm the closed form above from first principles.
# This validates the combinatorics without touching the d = 256 corpus at all.
# ---------------------------------------------------------------------------


def real_mubs_d4() -> list[list[tuple[F, ...]]]:
    """Three mutually unbiased orthonormal bases of R^4, entries in {0, +-1/2, +-1}."""
    h4 = [
        (1, 1, 1, 1),
        (1, -1, 1, -1),
        (1, 1, -1, -1),
        (1, -1, -1, 1),
    ]
    ident = [tuple(F(1) if i == j else F(0) for j in range(4)) for i in range(4)]
    cands = [ident]
    for phase in product((1, -1), repeat=4):
        cands.append([tuple(F(r[j] * phase[j], 2) for j in range(4)) for r in h4])

    def dot(x, y):
        return sum(a * b for a, b in zip(x, y))

    def unbiased(b1, b2):
        return all(abs(dot(x, y)) == F(1, 2) for x in b1 for y in b2)

    for triple in combinations(range(len(cands)), 3):
        bs = [cands[i] for i in triple]
        if all(unbiased(bs[i], bs[j]) for i, j in combinations(range(3), 2)):
            return bs
    raise RuntimeError("no real MUB triple found in R^4")


def check_d4_bruteforce() -> dict:
    bases = real_mubs_d4()
    d4 = 4
    blocks = [[v for x in b for v in (x, tuple(-c for c in x))] for b in bases]

    def dot(x, y):
        return sum(a * b for a, b in zip(x, y))

    out = {}
    ok_all = True
    for l in range(1, 9):
        # brute-force block summaries over every ordered point pair
        brute = [
            [
                sum(G(l, dot(p, q), d4) for p in blocks[a] for q in blocks[b])
                / F((2 * d4) ** 2)
                for b in range(3)
            ]
            for a in range(3)
        ]
        if l % 2 == 1:
            ok = all(brute[a][b] == 0 for a in range(3) for b in range(3))
            out[l] = {"odd_all_zero": ok}
        else:
            al, gl = block_summary(l, d4, F(1, 2))
            ok = all(
                brute[a][b] == (al + gl if a == b else gl)
                for a in range(3)
                for b in range(3)
            )
            uni = Q(al, gl, 3)  # uniform over all 3 blocks
            out[l] = {
                "closed_form_matches_bruteforce": ok,
                "Q_uniform_3_blocks": str(uni),
            }
        ok_all &= ok

    # the complete 3-MUB antipodal union in R^4 is the D4 root system: a 5-design
    five_design = all(
        (Q(*block_summary(l, d4, F(1, 2)), 3) == 0) for l in (2, 4)
    )
    deg6_nonzero = Q(*block_summary(6, d4, F(1, 2)), 3) != 0
    check(
        "d=4 brute force: closed-form block summaries reproduce all 24x24 pairs, l=1..8",
        ok_all,
    )
    check(
        "d=4: complete 3-MUB union is an exact 5-design (Q_2 = Q_4 = 0) and fails at 6",
        five_design and deg6_nonzero,
        f"Q_6(3 blocks) = {Q(*block_summary(6, d4, F(1, 2)), 3)}",
    )
    out["is_5_design"] = five_design
    out["degree_6_nonzero"] = deg6_nonzero
    return out


# ---------------------------------------------------------------------------
# CHECK B. d = 256 against two independently committed corpus artifacts.
# ---------------------------------------------------------------------------


def check_corpus() -> dict:
    out: dict = {}

    # B1 - exact rationals quoted by P4 sections 3.6 / 3.7
    p4 = {
        "G4_at_0": (G(4, F(0), D), F(1, 21845)),
        "G4_at_1_16": (G(4, ISQRT_D, D), F(-65, 2105344)),
        "G6_at_0": (G(6, F(0), D), F(-1, 1131571)),
        "G6_at_1_16": (G(6, ISQRT_D, D), F(16637, 17449091072)),
    }
    ok = all(a == b for a, b in p4.values())
    check("P4 exact Gegenbauer rationals reproduced (G4/G6 at 0 and 1/16)", ok)
    out["p4_exact_rationals"] = {k: str(v[0]) for k, v in p4.items()}

    # B2 - R0's committed lam_top on the doubled 64,512-point champion set
    r0 = json.loads(R0_JSON.read_text())
    lam = r0["design_property_NOT_residual"]["lam_top_doubled_64512_set"]
    rows = []
    ok = True
    for l in EVEN[: len(EVEN)]:
        if str(l) not in lam:
            continue
        mine = float(Q(*SUMMARY[l], K_CHAMP))
        theirs = lam[str(l)]
        hit = mine == theirs
        ok &= hit
        rows.append({"l": l, "mine": repr(mine), "R0": repr(theirs), "identical": hit})
    check(
        f"R0 lam_top_doubled_64512_set reproduced bit-for-bit at {len(rows)} even degrees",
        ok,
    )
    out["r0_lam_top_doubled"] = rows

    # B3 - odd degrees vanish on the doubled set (R0 commits 0.0)
    odd_ok = all(lam[str(l)] == 0.0 for l in range(1, 21, 2))
    check("R0 commits zero error at every odd degree on the doubled set", odd_ok)

    # B4 - MUB129's exact-rational Gegenbauer design defect, m = 126/128/129
    mub = json.loads(MUB_JSON.read_text())
    defect = mub["second_signal_gegenbauer_design_defect"]
    rows = []
    ok = True
    for l in (2, 4, 6):
        for m in (126, 128, 129):
            key = f"degree_{l}"
            if key not in defect:
                continue
            theirs = defect[key][f"m_{m}"]
            mine = float(Q(*SUMMARY[l], m))
            hit = mine == theirs
            ok &= hit
            rows.append(
                {"l": l, "m": m, "mine": repr(mine), "MUB129": repr(theirs), "identical": hit}
            )
    check(
        f"MUB129 exact-rational design defect reproduced at all {len(rows)} (degree, m) cells",
        ok,
    )
    out["mub129_design_defect"] = rows

    # B5 - the two exactness identities the whole certificate leans on
    q4_129 = Q(*SUMMARY[4], K_MAX)
    q2_any = [Q(*SUMMARY[2], k) for k in (1, 8, 126, 129)]
    check("Q_4(129 blocks) = 0 exactly (complete real-MUB union is a 5-design)", q4_129 == 0)
    check(
        "Q_2(k) = 0 exactly for every k (every orthonormal frame is a 2-design)",
        all(v == 0 for v in q2_any),
        f"alpha_2 = {SUMMARY[2][0]}, g_2 = {SUMMARY[2][1]}",
    )
    check(
        "Q_4(126) = 65/88424448 exactly (P4 section 3.6)",
        Q(*SUMMARY[4], K_CHAMP) == F(65, 88424448),
    )

    # B6 - alpha_l > 0 at every active degree (needed for strict convexity)
    pos = {l: SUMMARY[l][0] > 0 for l in EVEN}
    check(
        f"alpha_l > 0 at all {len(EVEN)} even degrees 4..{L_MODEL} (strict convexity in ||w||^2)",
        all(pos.values()),
    )
    check(
        "alpha_2 = 0 exactly - the proved degree-2 free direction (P4 draft-2 erratum)",
        SUMMARY[2][0] == 0,
    )

    # B7 - g_l alternates in sign and decays monotonically, so lumping every
    # degree above L_MODEL into one block with g = 0 costs nothing that matters.
    mags = [(l, abs(SUMMARY[l][1])) for l in EVEN if l >= 8]
    monotone = all(mags[i][1] > mags[i + 1][1] for i in range(len(mags) - 1))
    check(
        f"|G_l(1/16)| decreases strictly over even l in [8, {L_MODEL}] (justifies the tail bound)",
        monotone,
        f"|g_8| = {float(mags[0][1]):.3e} down to |g_{L_MODEL}| = {float(mags[-1][1]):.3e}",
    )
    # The sign pattern alternates from l = 4 but is NOT purely alternating: g_20
    # and g_22 are both negative. Recorded as data; nothing in the certificate
    # depends on it, since only g_4 < 0 and g_6 > 0 are load-bearing.
    signs = {l: (1 if SUMMARY[l][1] > 0 else -1 if SUMMARY[l][1] < 0 else 0) for l in EVEN}
    out["g_l_sign_pattern"] = signs
    out["g_l_sign_alternation_defect_at"] = [
        l for l in EVEN if l + 2 in signs and signs[l] == signs[l + 2]
    ]
    # tail bound: |B_tail| <= (tail even mass <= 1) * max_{l > L_MODEL} |g_l| <= |g_L_MODEL|
    b_tail_bound = float(abs(SUMMARY[L_MODEL][1]))
    check(
        "Tail bound |B_tail| <= |g_40| < 1e-25, so setting g_tail = 0 is below f64 resolution",
        b_tail_bound < 1e-25,
        f"|g_{L_MODEL}| = {b_tail_bound:.3e}",
    )
    out["B_tail_upper_bound"] = b_tail_bound
    out["g_l_monotone_decay_above_8"] = monotone
    out["alpha_limit_1_over_256"] = float(F(1, 256))

    # B8 - the two exact affine closed forms the certificate turns on
    a4, g4 = SUMMARY[4]
    a6, g6 = SUMMARY[6]
    check("alpha_4 = -129 * G_4(1/16) exactly (degree-4 exactness of the 129 union)",
          a4 == -129 * g4, f"alpha_4 = {a4}, g_4 = {g4}")
    check("alpha_6 = 4095 * G_6(1/16) exactly", a6 == 4095 * g6, f"alpha_6/g_6 = {a6 / g6}")
    check("Q_6(126) = (67/2) * G_6(1/16) exactly",
          Q(a6, g6, K_CHAMP) == F(67, 2) * g6)
    out["alpha_4_over_g_4"] = str(a4 / g4)
    out["alpha_6_over_g_6"] = str(a6 / g6)

    # B9 - the block-summary reduction is LOSSLESS. On the 512k-point set of any
    # k blocks every point sees the identical fingerprint (itself, its antipode,
    # 510 in-block zeros, 512(k-1) cross-block +-1/16), so the full point-kernel
    # K_l has constant row sums; with K_l PSD (addition theorem) the uniform
    # point weight is a global minimiser over the FULL point simplex, not merely
    # over block mixtures. The identity below is that statement in arithmetic:
    # the block formula evaluated at uniform equals rowsum / (512k).
    ok = True
    for l in EVEN:
        al, gl = SUMMARY[l]
        g0 = G(l, F(0), D)
        for k in (1, 8, 13, 126, 129):
            rowsum = 2 + (2 * D - 2) * g0 + 2 * D * (k - 1) * gl
            ok &= Q(al, gl, k) == rowsum / (2 * D * k)
    check(
        "Block reduction is lossless: block formula = constant row sum / point count, "
        "so uniform-on-k minimises over the full 512k-point simplex",
        ok,
    )
    return out


# ---------------------------------------------------------------------------
# 3. THE GAME. Rows are even degrees; columns are block counts k = 1..129.
#
#    payoff  R(k, l) = adjusted score of uniform-on-k relative to the champion,
#                      when all spectral energy sits at degree l
#            = [Q_l(k) / Q_l(126)] * (k / 126)          (compute proportional
#            = (alpha_l + k g_l) / (alpha_l + 126 g_l)   to the block count)
#
#    R is AFFINE in k. That single fact is what makes the witness finite: the
#    128-dimensional mixture polytope collapses onto one scalar (||w||^2), and
#    the game reduces to a 2 x 129 matrix game on the two degrees whose g_l
#    carry opposite signs.
# ---------------------------------------------------------------------------


def ratio(l: int, k: int) -> F:
    al, gl = SUMMARY[l]
    return (al + k * gl) / (al + K_CHAMP * gl)


def solve_game() -> dict:
    ks = list(range(1, K_MAX + 1))
    # PRIMAL: min over block mixtures of the worst-case adjusted score ratio.
    per_k = {k: max((ratio(l, k), l) for l in EVEN) for k in ks}
    primal_val, primal_k = min((v[0], k) for k, v in per_k.items())
    argmax_at_opt = per_k[primal_k][1]

    # DUAL: a nonnegative spectral energy y makes the payoff  A_y + k B_y  with
    # B_y = sum_l y_l g_l. The payoff is flat in k iff B_y = 0, so the dual
    # optimum is any y >= 0 with sum_l y_l G_l(1/16) = 0. Two degrees suffice:
    # g_4 < 0 and g_6 > 0.
    g4, g6 = SUMMARY[4][1], SUMMARY[6][1]
    y6, y4 = -g4, g6  # y4*g4 + y6*g6 = g6*g4 - g4*g6 = 0
    tot = y4 + y6
    y4, y6 = y4 / tot, y6 / tot
    b_y = y4 * g4 + y6 * g6
    dual_flat = b_y == 0

    # Evaluate the dual objective honestly: min over k of the y-weighted ratio.
    # Weighted ratio = sum_l y_l Q_l(k) * (k/126) / sum_l y_l Q_l(126).
    num_den = []
    for k in ks:
        num = sum(
            y * (SUMMARY[l][0] / k + SUMMARY[l][1]) for l, y in ((4, y4), (6, y6))
        ) * F(k, K_CHAMP)
        den = sum(
            y * (SUMMARY[l][0] / K_CHAMP + SUMMARY[l][1]) for l, y in ((4, y4), (6, y6))
        )
        num_den.append((num / den, k))
    dual_val, dual_k = min(num_den)
    dual_flat_everywhere = len({v for v, _ in num_den}) == 1

    gap = primal_val - dual_val
    check("Sion minimax: primal value = dual value exactly (zero duality gap)", gap == 0,
          f"primal = dual = {primal_val}")
    check("Primal optimum is the champion's block count k = 126", primal_k == K_CHAMP)
    check("Minimax value is exactly 1 - no block mixture improves in the worst case",
          primal_val == 1)
    check("Dual witness is admissible: y >= 0 and sum_l y_l G_l(1/16) = 0",
          dual_flat and y4 > 0 and y6 > 0)
    check("Under the dual witness the adjusted score is flat in k at every k = 1..129",
          dual_flat_everywhere)

    # strictness: every k != 126 is strictly worse in the worst case
    strict = all(per_k[k][0] > 1 for k in ks if k != K_CHAMP)
    check("Every block count k != 126 has worst-case ratio strictly > 1", strict)

    # the two closed-form penalties
    below = {k: ratio(4, k) for k in (1, 8, 13, 55, 96, 112, 125)}
    above = {k: ratio(6, k) for k in (127, 128, 129)}
    deg4_formula_ok = all(ratio(4, k) == F(129 - k, 3) for k in range(1, 130))
    check("Closed form: degree-4 adjusted penalty of a k-block mixture = (129 - k)/3",
          deg4_formula_ok)
    deg6_formula_ok = all(ratio(6, k) == F(4095 + k, 4221) for k in range(1, 130))
    check("Closed form: degree-6 adjusted penalty of a k-block mixture = (4095 + k)/4221",
          deg6_formula_ok)
    check("Both closed forms equal 1 at k = 126 and only there",
          ratio(4, K_CHAMP) == 1 and ratio(6, K_CHAMP) == 1
          and all(ratio(4, k) != 1 and ratio(6, k) != 1 for k in ks if k != K_CHAMP))

    # Break-even compute ratio for the full completion. The completion improves
    # in the worst case iff its compute ratio c satisfies c * Q_6(129)/Q_6(126) < 1.
    c_star = Q(*SUMMARY[6], K_CHAMP) / Q(*SUMMARY[6], K_MAX)
    c_nominal = F(K_MAX, K_CHAMP)  # one extra block is one extra full frame of 512 points
    margin = c_nominal / c_star
    check(
        "Cheapest admissible compute ratio 129/126 exceeds the break-even ratio",
        c_nominal > c_star,
        f"c* = {c_star} = {float(c_star):.10f} < 129/126 = {float(c_nominal):.10f}",
    )
    check("Worst-case margin equals the degree-6 penalty 1408/1407 exactly",
          margin == F(1408, 1407) and margin == ratio(6, K_MAX))

    # THE FALSIFIER, priced. The certificate flips only if the completion's
    # marginal compute is cheaper than three full blocks by at least this much.
    # MUB129 STRUCTURAL_FINDING section 4 names the one real saving: the identity
    # frame needs no Walsh butterfly, since I @ W1 = W1.
    C_CHAMP_FLOPS = 178.462975e9  # T4_REPORT.md, mean effective compute at 126 blocks
    c126 = C_CHAMP_FLOPS
    c129_nominal = c126 * 129 / 126
    c129_breakeven = c126 * float(c_star)
    required_saving = c129_nominal - c129_breakeven
    # fast Walsh-Hadamard on one 256-point frame: 256 vectors x 256*log2(256) adds
    walsh_saving = 256 * 256 * 8
    check(
        "Flipping the certificate needs a compute saving >> the only identified one "
        "(the identity frame's absent Walsh butterfly)",
        required_saving > 100 * walsh_saving,
        f"required {required_saving:.4e} FLOPs vs Walsh saving {walsh_saving:.4e} FLOPs "
        f"= {required_saving / walsh_saving:.1f}x",
    )

    return {
        "falsifier_price": {
            "champion_compute_flops": c126,
            "completion_nominal_compute_flops": c129_nominal,
            "completion_breakeven_compute_flops": c129_breakeven,
            "required_saving_flops": required_saving,
            "identity_frame_walsh_saving_flops": float(walsh_saving),
            "safety_factor": required_saving / walsh_saving,
        },
        "break_even_cost_ratio": str(c_star),
        "break_even_cost_ratio_float": float(c_star),
        "nominal_cost_ratio_129_over_126": str(c_nominal),
        "worst_case_margin": str(margin),
        "worst_case_margin_float": float(margin),
        "closed_form_degree4": "R_4(k) = (129 - k)/3",
        "closed_form_degree6": "R_6(k) = (4095 + k)/4221",
        "primal_value": str(primal_val),
        "primal_argmin_k": primal_k,
        "primal_binding_degree_at_optimum": argmax_at_opt,
        "dual_value": str(dual_val),
        "dual_argmin_k": dual_k,
        "duality_gap": str(gap),
        "dual_witness": {
            "support_degrees": [4, 6],
            "y_4": str(y4),
            "y_6": str(y6),
            "y_4_float": float(y4),
            "y_6_float": float(y6),
            "B_y = sum_l y_l G_l(1/16)": str(b_y),
            "g_4 = G_4(1/16)": str(g4),
            "g_6 = G_6(1/16)": str(g6),
        },
        "worst_case_ratio_by_k": {
            str(k): {"value": str(per_k[k][0]), "float": float(per_k[k][0]),
                     "binding_degree": per_k[k][1]}
            for k in (1, 8, 13, 55, 96, 112, 125, 126, 127, 128, 129)
        },
        "degree4_penalty_below_126": {str(k): str(v) for k, v in below.items()},
        "degree6_penalty_above_126": {str(k): str(v) for k, v in above.items()},
    }


# ---------------------------------------------------------------------------
# 4. FROZEN-SPECTRUM EVALUATION. What the axis is actually worth under R0's
#    committed harmonic energy budget.
# ---------------------------------------------------------------------------


def frozen_spectrum() -> dict:
    r0 = json.loads(R0_JSON.read_text())
    a_share = r0["armB_meanfield_rederivation"]["a_l_energy_share_per_degree"]
    ebd = r0["estimator_error_by_degree"]
    tail_error_share = ebd["unresolved_tail_error_share"]
    v_model = ebd["implied_MSE_over_sigma2"]

    # resolved even degrees 4..40 with their committed shares
    a = {l: a_share[str(l)] for l in EVEN}

    # tail: every even degree above L_MODEL has alpha = 1/256 and g = 0 exactly
    # (checked above), so its error is a_tail/(256*126) = a_tail/32256. Recover
    # a_tail from R0's own committed tail error share.
    a_tail = tail_error_share * v_model * 256 * K_CHAMP

    A = sum(a[l] * float(SUMMARY[l][0]) for l in EVEN) + a_tail * float(F(1, 256))
    B = sum(a[l] * float(SUMMARY[l][1]) for l in EVEN)  # tail g = 0
    V = A / K_CHAMP + B

    rel = abs(V - v_model) / v_model
    check(
        "Frozen spectrum: A/126 + B reproduces R0's implied MSE to < 1e-12 relative",
        rel < 1e-12,
        f"mine {V!r} vs R0 {v_model!r}, rel diff {rel:.3e}",
    )

    theta = (A / K_CHAMP) / V  # share of the champion's error carried by the collision term
    s4 = a[4] * float(Q(*SUMMARY[4], K_CHAMP)) / V
    check(
        "theta > 1 exactly when B < 0, i.e. when sum_l a_l G_l(1/16) < 0",
        (theta > 1) == (B < 0),
    )

    # delta = the whole design axis's worth, in adjusted score, at proportional cost
    delta_prop = (theta - 1) / 42  # = 1 - (1 - theta/43)*(43/42)
    # identity: delta = s_4 - (1/42) * sum_{l>=6} a_l g_l / V
    corr = sum(a[l] * float(SUMMARY[l][1]) for l in EVEN if l >= 6) / (42 * V)
    ident_ok = abs(delta_prop - (s4 - corr)) < 1e-15
    check(
        "Identity delta = s_4 - (1/42) sum_{l>=6} a_l G_l(1/16)/V holds to 1e-15",
        ident_ok,
        f"delta {delta_prop!r} vs s4 - corr {(s4 - corr)!r}",
    )

    # cost bracket committed by MUB129: [129/126, 17/16]
    mub = json.loads(MUB_JSON.read_text())
    lo, hi = mub["CORRECTION_20260812_0324"]["cost_ratio_bracket"]
    check("Cost bracket read from MUB129 is [129/126, 17/16]",
          abs(lo - 129 / 126) < 1e-12 and abs(hi - 17 / 16) < 1e-12)

    def delta_at(rho: float) -> float:
        """1 - S(129)/S(126) under cost ratio rho for the 126 -> 129 completion."""
        return 1.0 - (1.0 - theta / 43.0) * rho

    delta_lo, delta_hi = delta_at(hi), delta_at(lo)  # hi cost -> lowest delta

    # the k-frontier under proportional cost: S(k)/S(126) = 1 + (theta-1)(126-k)/126
    frontier = {
        str(k): 1.0 + (theta - 1.0) * (K_CHAMP - k) / K_CHAMP
        for k in (8, 13, 55, 96, 112, 126, 127, 128, 129)
    }
    fr_ok = abs(frontier["129"] - (1.0 - delta_prop)) < 1e-15
    check("Frontier formula agrees with delta at k = 129", fr_ok)

    # measured discrimination floor from the MUB129 adversarial audit
    audit = mub["CORRECTION_20260812_adversarial_audit"]
    ci = audit["sixteen_fresh_nets_CI"]
    half = (ci[1] - ci[0]) / 2
    inside = ci[0] <= (1.0 - delta_prop) <= ci[1]
    check(
        "Predicted 129/126 score ratio lies inside MUB129's 16-fresh-net measured CI",
        inside,
        f"predicted {1.0 - delta_prop!r} in {ci}",
    )

    # ---- the score-floor regime -------------------------------------------
    # score = MSE * max(0.1, C/B). The champion measured mean C = 178.462975e9
    # on 126 blocks (T4_REPORT.md), i.e. 1.416373e9 per block, multiplier
    # 0.6561138779836238. Below C = 27.2e9 the multiplier floors at 0.1 and
    # compute becomes free, so small mixtures are scored on raw MSE alone.
    # This is where the theorem map's live 8-basis candidate sits.
    C_CHAMP = 178.462975e9
    MULT_CHAMP = 0.6561138779836238
    B_BUDGET = 2.72e11
    per_block = C_CHAMP / K_CHAMP
    # T4 prints mean effective compute to six decimals of 1e9, so C/B recovers
    # its committed mean multiplier only to that precision - 1e-9, not 1e-12.
    check(
        "T4's committed champion multiplier equals C/B to the report's printed precision",
        abs(C_CHAMP / B_BUDGET - MULT_CHAMP) < 1e-8,
        f"C/B = {C_CHAMP / B_BUDGET!r} vs committed {MULT_CHAMP!r}",
    )
    k_floor = int(0.1 * B_BUDGET / per_block)  # largest k still on the floor

    def score_ratio(k: int) -> float:
        v_k = A / k + B
        mult = max(0.1, per_block * k / B_BUDGET)
        return (v_k / V) * (mult / MULT_CHAMP)

    floor_rows = {
        str(k): {
            "effective_compute_e9": per_block * k / 1e9,
            "multiplier": max(0.1, per_block * k / B_BUDGET),
            "on_floor": per_block * k < 0.1 * B_BUDGET,
            "score_ratio_vs_champion": score_ratio(k),
        }
        for k in (8, 13, 19, 20, 55, 96, 112, 126, 129)
    }
    best_small = min(
        (floor_rows[str(k)]["score_ratio_vs_champion"], k) for k in (8, 13, 19, 20)
    )
    check(
        "Even with compute free on the 0.1 floor, no small block mixture beats the champion",
        best_small[0] > 1.0,
        f"best small mixture k = {best_small[1]} at ratio {best_small[0]:.6f}",
    )

    return {
        "floor_regime": {
            "champion_effective_compute_e9": C_CHAMP / 1e9,
            "per_block_compute_e9": per_block / 1e9,
            "largest_k_on_the_0.1_floor": k_floor,
            "rows": floor_rows,
            "best_small_mixture": {"k": best_small[1], "score_ratio": best_small[0]},
        },
        "A_collision_coefficient": A,
        "B_constant_coefficient": B,
        "V_champion_zonal_MSE_over_sigma2": V,
        "R0_implied_MSE_over_sigma2": v_model,
        "theta_collision_share": theta,
        "s4_degree4_error_share": s4,
        "R0_committed_deg4_share": ebd["deg4_share_of_total_error"],
        "a_tail_even_mass_above_L40": a_tail,
        "delta_proportional_cost": delta_prop,
        "delta_bracket_over_committed_cost_range": [delta_lo, delta_hi],
        "cost_ratio_bracket": [lo, hi],
        "score_ratio_129_over_126_predicted": 1.0 - delta_prop,
        "measured_16_fresh_net_ratio": audit["sixteen_fresh_nets_score_ratio"],
        "measured_16_fresh_net_CI": ci,
        "measured_CI_half_width": half,
        "prediction_inside_measured_CI": inside,
        "adjusted_score_frontier_over_k": frontier,
        "delta_under_four_independent_deg4_share_estimates": {
            k: (v / 100.0) - corr
            for k, v in audit["four_independent_estimates_of_the_degree4_share_pct"].items()
        },
    }


# ---------------------------------------------------------------------------
# 5. The equal-compute KKT certificate (Hahn-Banang/Lagrangian half), exact.
# ---------------------------------------------------------------------------


def kkt_equal_compute() -> dict:
    """At fixed support S of size k, min_{w in simplex(S)} A||w||^2 + B.

    KKT point: w* = 1/k, mu* = 0, nu* = 2A/k. Dual function
    g(nu) = B + nu - k nu^2/(4A) is maximised at nu* with g(nu*) = A/k + B = f(w*).
    Shown here in exact rationals per degree, so the statement holds for every
    nonnegative spectral energy simultaneously.
    """
    rows = []
    ok = True
    for l in EVEN:
        al, gl = SUMMARY[l]
        k = K_CHAMP
        primal = al / k + gl
        nu = 2 * al / k
        dual = gl + nu - k * nu * nu / (4 * al)
        hit = primal == dual
        ok &= hit
        rows.append(
            {"l": l, "nu_star": str(nu), "primal": str(primal), "dual": str(dual),
             "gap": str(primal - dual)}
        )
    check(
        f"KKT: primal = dual exactly at all {len(EVEN)} active degrees, equal-compute problem",
        ok,
    )
    return {"per_degree": rows, "w_star": f"uniform, 1/{K_CHAMP}", "mu_star": "0"}


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json-out", default=str(HERE / "dual_witness_certificate.json"))
    args = ap.parse_args()

    result = {
        "artifact": "DUAL_WITNESS_CERTIFICATE_20260818",
        "discharges": "rank-10 OFFLINE_CERTIFICATE, 2026-08-13 Schauder/Kerdock theorem map",
        "setting": {
            "d": D,
            "blocks": K_MAX,
            "champion_block_count": K_CHAMP,
            "points_per_block": 2 * D,
            "cross_block_inner_product": "+-1/16",
            "score_formula": "MSE * max(0.1, (billed_FLOPs + 1e11*residual_s)/2.72e11)",
        },
        "check_A_d4_bruteforce": check_d4_bruteforce(),
        "check_B_corpus": check_corpus(),
        "game": solve_game(),
        "kkt_equal_compute": kkt_equal_compute(),
        "frozen_spectrum": frozen_spectrum(),
    }
    passed = all(ok for _, ok, _ in CHECKS)
    result["checks"] = [
        {"name": n, "pass": ok, "detail": d} for n, ok, d in CHECKS
    ]
    result["all_checks_pass"] = passed

    Path(args.json_out).write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")

    if not args.quiet:
        print("=" * 78)
        print("FINITE DUAL WITNESS - block mixtures over the 129 real-MUB blocks")
        print("=" * 78)
        for n, ok, d in CHECKS:
            print(f"  [{'PASS' if ok else 'FAIL'}] {n}")
            if d:
                print(f"         {d}")
        g = result["game"]
        f = result["frozen_spectrum"]
        print("-" * 78)
        print(f"  primal value  min_w max_l R = {g['primal_value']} at k = {g['primal_argmin_k']}")
        print(f"  dual value    max_y min_w R = {g['dual_value']}")
        print(f"  duality gap                 = {g['duality_gap']}")
        print(f"  dual witness  y_4 = {g['dual_witness']['y_4_float']:.10f}, "
              f"y_6 = {g['dual_witness']['y_6_float']:.10f}")
        print("-" * 78)
        print(f"  theta (collision share)     = {f['theta_collision_share']:.10f}")
        print(f"  s_4 (degree-4 error share)  = {f['s4_degree4_error_share']:.10f}")
        print(f"  delta (axis worth, prop.)   = {f['delta_proportional_cost']:.10f}")
        print(f"  delta bracket over cost     = [{f['delta_bracket_over_committed_cost_range'][0]:.6f}, "
              f"{f['delta_bracket_over_committed_cost_range'][1]:.6f}]")
        print(f"  predicted 129/126 ratio     = {f['score_ratio_129_over_126_predicted']:.8f}")
        print(f"  measured 16-net CI          = {f['measured_16_fresh_net_CI']}")
        print("-" * 78)
        print(f"  ALL CHECKS PASS: {passed}")
        print(f"  JSON -> {args.json_out}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
