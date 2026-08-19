"""Exact re-pricing of the WHestBench designation tables (policy v2, 2026-08-19).

Why this file exists: DESIGNATION_POLICY_20260819.md v1 priced the fold from a
hand-carried curve, C_post(m) = (126.7 + 18.815m)e9 over 222.405357e9.  That
expression divides a LOCAL-scale analytical absolute by a RECORD-scale total, and
the resulting 0.739 headline is contradicted by the measured paired ratio of
0.8388/0.8447.  v2 therefore prices by RATIO against the incumbent's own recorded
public-100 score and never forms an absolute from two scales.

Run it instead of re-deriving by hand the hour the Phase-2 rules post:

    python -B designation_repricing.py --lambda-mode survives --floor 0.1
    python -B designation_repricing.py --lambda-mode dies --floor 0.5
    python -B designation_repricing.py --lambda-mode capped
    python -B designation_repricing.py --selfcheck

Every load-bearing number is fractions.Fraction.  The single float in the file is
the suite-size CV line, which is reportorial and enters no designation.

Evidence tags on the constants: [O] observed in a committed artifact this session,
[D] derived by shown arithmetic, [R] reported, [A] assumed.

CAVEAT THAT TRAVELS WITH EVERY NUMBER DERIVED FROM full.json: pending round-4 bill
repair re-run.  The committed full.json was produced under a static bill known
wrong in both directions (unpriced m*n copy-out on the fallback branch; an m*k
operand copy charged to the direct branch it never performs), and that bill drives
route selection, so the measured ratios below can move in either direction.
"""

from __future__ import annotations

import argparse
import math
from fractions import Fraction as F

# --------------------------------------------------------------------------
# Constants of the scoring law.
# S = MSE * max(FLOOR, C/B),  C = analytical_FLOPs + RESIDUAL_CONSTANT * residual_s
# [O: verified in source and receipts; reconfirmed here against full.json, where
#  flops + 1e11*residual reproduces effective_C to 1e-12 relative on floor_L4.]
# --------------------------------------------------------------------------
B_DEFAULT = F("2.72e11")
RESIDUAL_CONSTANT_DEFAULT = F("1e11")

# 129-frame completion over the 126-frame carrier: the billed point count rises by
# exactly 129/126.  [O: CODEX_HANDOFF_20260810.md:131; S11_VERDICT.md:48]
POINT_COUNT_FACTOR = F(129, 126)

# The 129 cell's AMENDED pre-registered band and its falsifier.
# [O: channel 2026-08-19 ~02:1x UTC, commit 0486668 "band widened honestly".
#  Supersedes the 0.78-0.86 band that v1 quoted and that spec.json still carries.]
BAND_129 = (F("0.78"), F("0.86"), F("0.93"))
FALSIFIER_129 = F("0.95")

# --------------------------------------------------------------------------
# Hosts.  Every field read from a committed report this session [O].
# --------------------------------------------------------------------------
HOSTS = {
    # experiments/ROW_BLOCKED_WINOGRAD_PRODUCTION_REPORT.md, child column, and
    # core/SUBMISSION_DOSSIER_20260808.md row 3.
    "row_blocked": {
        "score": F("2.121762464e-7"),
        "raw_mse": F("3.089460087e-7"),
        "mean_C": F("189.852556e9"),
        "mean_analytical": F("173.794058e9"),
        "mean_residual_s": F("0.160585"),
        "max_C": F("222.405357e9"),
        "label": "row_blocked_winograd_production (Haar-QR carrier)",
    },
    # experiments/t4_kerdock_descriptive_rescore/T4_REPORT.md.  mean_analytical is
    # [D] = mean_C - RESIDUAL_CONSTANT * 0.080, and the 0.080 s/net residual is
    # [R] from the T4 wall decomposition rather than a field of the report.
    "kerdock_v3": {
        "score": F("1.6190837992231567e-7"),
        "raw_mse": F("2.493887556909158e-7"),
        "mean_C": F("178.462975e9"),
        "mean_analytical": F("178.462975e9") - F("1e11") * F("0.080"),
        "mean_residual_s": F("0.080"),
        "max_C": F("209.575026e9"),
        "label": "t4_kerdock_v3 (126 phased-Hadamard frames)",
    },
}

# --------------------------------------------------------------------------
# The measurement v2 prices from: experiments/fold_floor_splice/full.json,
# end_to_end.routes.floor_L4, paired against end_to_end.incumbent in the same run.
# Read verbatim this session [O].  PENDING ROUND-4 BILL REPAIR RE-RUN.
# --------------------------------------------------------------------------
MEASURED = {
    "floor_L4_net0": {
        "child_flops": F(132729573911),
        "child_C": F("169836253875.92703"),
        "child_residual_s": F("0.37106679964927"),  # = (child_C - child_flops)/1e11
        "parent_flops": F(186406005979),
        "parent_C": F("202478836002.76788"),
        "parent_residual_s": F("0.16072830023767892"),
        "effective_C_ratio": F("0.8387852144389322"),
        "flops_ratio": F("0.712045586803426"),
        "residual_ratio": F("2.3086587682477244"),
    },
    "floor_L4_net1": {
        "child_flops": F(135136725535),
        "child_C": F("170697585372.27826"),
        "child_residual_s": F("0.35560859837278"),
        "parent_flops": F(186224805407),
        "parent_C": F("202070095477.8653"),
        "parent_residual_s": F("0.15845290070865303"),
        "effective_C_ratio": F("0.8447444188542803"),
        "flops_ratio": F("0.7256644743950977"),
        "residual_ratio": F("2.244254265983046"),
    },
}

# S1's measured coefficient of variation on a 50-net suite [O: S1_VERDICT.md].
CV_50 = {"R1": F("0.08541"), "R6": F("0.03507")}
CV_BASE_SUITE = 50


def fmt(x: F, digits: int = 6) -> str:
    """Round-half-even decimal rendering of an exact Fraction."""
    if x == 0:
        return "0"
    scale = 10 ** digits
    n = x * scale
    lo = n.numerator // n.denominator
    frac = n - lo
    if frac > F(1, 2) or (frac == F(1, 2) and lo % 2 == 1):
        lo += 1
    sign = "-" if lo < 0 else ""
    lo = abs(lo)
    s = str(lo).rjust(digits + 1, "0")
    return f"{sign}{s[:-digits]}.{s[-digits:]}"


def sci(x: F, digits: int = 4) -> str:
    """Scientific notation for a score, exact input, rounded output."""
    if x == 0:
        return "0"
    e = 0
    y = abs(x)
    while y >= 10:
        y /= 10
        e += 1
    while y < 1:
        y *= 10
        e -= 1
    return f"{fmt(y, digits)}e{e}"


def suite_scale_C_ratio(host: dict, m: dict, residual_constant: F) -> F:
    """Project the paired half-ratios onto the deployed suite's own C split.

    The directly measured effective_C_ratio is a two-probe-net quantity whose
    parent carries a 7.94% residual share; the deployed suite's parent carries
    8.46%.  Because the residual half moved UP (ratio ~2.3) while the analytical
    half moved DOWN (ratio ~0.71), that share difference matters.  This applies
    each measured half-ratio to the suite's own measured half.  [D]
    """
    a = host["mean_analytical"] * m["flops_ratio"]
    r = residual_constant * host["mean_residual_s"] * m["residual_ratio"]
    return (a + r) / host["mean_C"]


def score_from_ratio(host: dict, c_cand: F, c_parent: F, floor: F, B: F,
                     mse_factor: F = F(1)) -> tuple[F, F, bool]:
    """Score a candidate as a RATIO off the incumbent's recorded score.

    Returns (score, C/B, floor_binds).  Staying in ratio space is the whole point
    of v2: the incumbent's recorded 2.121762464e-7 already contains its own suite
    MSE and its own per-network multipliers, so no MSE has to be backed out of a
    single network's C.  Forming the product MSE x mean(C)/B instead over-states
    the recorded score by a measured +1.63% on this very suite (selfcheck 3).
    """
    mult_cand_raw = c_cand / B
    mult_cand = max(floor, mult_cand_raw)
    mult_parent = max(floor, c_parent / B)
    return host["score"] * mse_factor * mult_cand / mult_parent, mult_cand_raw, mult_cand_raw < floor


def price(lambda_mode: str, floor: F, B: F, residual_constant: F, suite_size: int,
          host: str, C_ratio: F, basis: str = "floor_L4_net0") -> dict:
    """The seven-parameter re-pricing.  Everything else is read off the record."""
    h = HOSTS[host]
    m = MEASURED[basis]
    rows = []

    if lambda_mode in ("survives", "capped"):
        c_parent = h["mean_C"]
        c_fold = c_parent * C_ratio
    elif lambda_mode == "dies":
        # BOTH sides collapse to their analytical part.  v1 collapsed ours only.
        c_parent = h["mean_analytical"]
        c_fold = c_parent * m["flops_ratio"]
    else:
        raise ValueError(f"lambda_mode must be survives|dies|capped, got {lambda_mode!r}")

    s, cb, binds = score_from_ratio(h, c_parent, c_parent, floor, B)
    rows.append(("incumbent " + host, c_parent, cb, s, binds, ""))

    s, cb, binds = score_from_ratio(h, c_fold, c_parent, floor, B)
    rows.append(("fold", c_fold, cb, s, binds, "MSE parity to 7 digits"))

    for r in BAND_129:
        c129 = c_fold * POINT_COUNT_FACTOR
        s, cb, binds = score_from_ratio(h, c129, c_parent, floor, B, mse_factor=r)
        rows.append((f"fold + 129 @ raw-MSE {fmt(r, 2)}", c129, cb, s, binds,
                     "C carries 129/126"))

    # Break-even raw-MSE ratio at which fold+129 matches the candidate we already
    # hold unfolded.  This is the decision number the whole 129 cell turns on.
    rival = HOSTS["kerdock_v3"]["score"]
    s_fold_129_at_1, _, _ = score_from_ratio(h, c_fold * POINT_COUNT_FACTOR, c_parent, floor, B)
    r_star = rival / s_fold_129_at_1

    return {
        "rows": rows,
        "c_parent": c_parent,
        "c_fold": c_fold,
        "r_star": r_star,
        "rival": rival,
        "cv": {k: math.sqrt(float(v) ** 2 * CV_BASE_SUITE / suite_size)
               for k, v in CV_50.items()},
        "floor": floor,
        "B": B,
        "basis": basis,
        "lambda_mode": lambda_mode,
        "host": host,
    }


def admissibility(host: str, basis: str, taus: list[F]) -> list[tuple]:
    """B8 repair: one residual base, and it is the MEASURED one.

    v1 ran two incompatible bases at once - 0.18815 s/net implied by the 18.815e9
    coefficient in the section-1a C-law, and 0.1606 s/net in the section-1c
    admissibility table, 17.2% apart.  Neither is a measurement of the fold.  The
    fold's residual was measured directly, in the same run as its parent.
    """
    m = MEASURED[basis]
    # The host's own deployed residual base, scaled by the MEASURED residual ratio.
    # On row_blocked this reproduces the directly measured child residual to 0.1%,
    # which is the cross-check that licenses using it for the other host.
    parent = HOSTS[host]["mean_residual_s"]
    child = parent * m["residual_ratio"]
    out = []
    for tau in taus:
        out.append((tau, child, child <= tau, child / parent))
    return out, child, parent


def table_lambda(res: dict) -> str:
    lines = [
        f"| candidate | C (this scale) | C/B | score | vs incumbent | vs unfolded kerdock_v3 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    base = res["rows"][0][3]
    for name, c, cb, s, binds, note in res["rows"]:
        floor_mark = " (floored)" if binds else ""
        lines.append(
            f"| {name} | {fmt(c / F('1e9'), 3)}B | {fmt(cb, 4)}{floor_mark} | {sci(s)} "
            f"| {fmt(s / base, 4)}x | {fmt(s / res['rival'], 4)}x |"
        )
    return "\n".join(lines)


def selfcheck() -> int:
    """Four discriminating checks.  Each one fails if the model is wrong."""
    ok = True

    # 1. The score law's decomposition reproduces full.json's own effective_C.
    for k, m in MEASURED.items():
        lhs = m["child_flops"] + RESIDUAL_CONSTANT_DEFAULT * m["child_residual_s"]
        rel = abs(lhs - m["child_C"]) / m["child_C"]
        good = rel < F(1, 10 ** 9)
        ok &= good
        print(f"[{'ok' if good else 'FAIL'}] 1/{k}: flops + 1e11*residual == effective_C, rel={float(rel):.2e}")

    # 2. The v1 headline reproduces from v1's own inputs.  If this fails, this
    #    script is not modelling the thing it claims to replace.
    v1_C = (F("126.7e9") + 2 * F("18.815e9"))
    v1_ratio = v1_C / F("222.405357e9")
    v1_score = HOSTS["row_blocked"]["score"] * v1_ratio
    good = abs(v1_score - F("1.5677e-7")) / F("1.5677e-7") < F(1, 1000)
    ok &= good
    print(f"[{'ok' if good else 'FAIL'}] 2: v1 curve reproduces its 1.5677e-7 headline "
          f"-> {sci(v1_score)} at C/B ratio {fmt(v1_ratio, 6)}")

    # 3. The product form MSE x mean(C)/B over-states the incumbent's OWN recorded
    #    score - the reason v2 prices by ratio and never by product.
    h = HOSTS["row_blocked"]
    product = h["raw_mse"] * h["mean_C"] / B_DEFAULT
    bias = product / h["score"] - 1
    good = F("0.010") < bias < F("0.025")
    ok &= good
    print(f"[{'ok' if good else 'FAIL'}] 3: product form {sci(product)} vs recorded "
          f"{sci(h['score'])}, bias +{fmt(bias * 100, 3)}%")

    # 4. NOT A LICENCE (corrected 2026-08-19 by hostile verify).  T4's "mean ratio"
    #    column is itself the ratio of two aggregate scores, not a mean of per-network
    #    ratios: its other row reproduces the same way (kerdock/L2 = 0.770267409), and
    #    its bootstrap is 200k resamples, not a million.  Both sides of this comparison
    #    are the same quantity, so it passes by construction.  Retained only as a
    #    transcription check on the two recorded scores.
    agg = HOSTS["kerdock_v3"]["score"] / HOSTS["row_blocked"]["score"]
    good = abs(agg - F("0.763084382")) < F(1, 10 ** 4)
    ok &= good
    print(f"[{'ok' if good else 'FAIL'}] 4: aggregate score ratio {fmt(agg, 9)} vs T4 "
          f"printed mean-ratio column 0.763084382 (IDENTITY, transcription check only)")

    print("SELFCHECK", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--lambda-mode", default="survives", choices=["survives", "dies", "capped"])
    p.add_argument("--floor", default="0.1")
    p.add_argument("--B", default=str(B_DEFAULT))
    p.add_argument("--residual-constant", default=str(RESIDUAL_CONSTANT_DEFAULT))
    p.add_argument("--suite-size", type=int, default=50)
    p.add_argument("--host", default="row_blocked", choices=sorted(HOSTS))
    p.add_argument("--c-ratio", default=None,
                   help="paired effective-C ratio; default = the basis's measured value")
    p.add_argument("--basis", default="floor_L4_net0", choices=sorted(MEASURED))
    p.add_argument("--suite-scale", action="store_true",
                   help="project the measured half-ratios onto the suite's own C split")
    p.add_argument("--selfcheck", action="store_true")
    a = p.parse_args()

    if a.selfcheck:
        return selfcheck()

    floor = F(a.floor)
    B = F(a.B)
    rc = F(a.residual_constant)
    m = MEASURED[a.basis]
    if a.c_ratio is not None:
        c_ratio = F(a.c_ratio)
        src = "supplied"
    elif a.suite_scale:
        c_ratio = suite_scale_C_ratio(HOSTS[a.host], m, rc)
        src = "suite-scale projection of the measured half-ratios [D]"
    else:
        c_ratio = m["effective_C_ratio"]
        src = f"measured paired {a.basis} [O]"

    res = price(a.lambda_mode, floor, B, rc, a.suite_size, a.host, c_ratio, a.basis)

    print(f"lambda_mode={a.lambda_mode}  floor={fmt(floor,2)}  B={sci(B,5)}  "
          f"residual_constant={sci(rc,5)}  suite_size={a.suite_size}  host={a.host}")
    print(f"C_ratio={fmt(c_ratio, 7)}  ({src})")
    print(f"scale: {'analytical only, BOTH sides' if a.lambda_mode == 'dies' else 'effective C'}"
          f", suite-mean basis, parent C = {fmt(res['c_parent']/F('1e9'), 3)}B")
    print()
    print(table_lambda(res))
    print()
    print(f"break-even raw-MSE ratio at which fold+129 matches unfolded kerdock_v3 "
          f"({sci(res['rival'])}): r* = {fmt(res['r_star'], 5)}")
    lo, hi = BAND_129[0], BAND_129[2]
    print(f"  amended pre-registered band [{fmt(lo,2)}, {fmt(hi,2)}]; "
          f"falsifier > {fmt(FALSIFIER_129,2)}")
    if res["r_star"] >= hi:
        print("  -> r* is above the band's upper edge: the stack wins across the whole band")
    elif res["r_star"] <= lo:
        print("  -> r* is below the band's lower edge: the stack loses across the whole band")
    else:
        print(f"  -> the stack beats the candidate we already hold only on the band's "
              f"lower {fmt((res['r_star'] - lo) / (hi - lo) * 100, 1)}% "
              f"(r in [{fmt(lo,2)}, {fmt(res['r_star'],4)}])")
    print()
    print(f"suite-draw CV at n={a.suite_size} (S1 model, 1/sqrt(n) law) [float, reportorial]: "
          f"R=1 {res['cv']['R1']:.5f}, R=6 {res['cv']['R6']:.5f}")

    if a.lambda_mode == "capped":
        taus = [F("0.1606"), F("0.20"), F("0.25"), F("0.3212"), F("0.3556"),
                F("0.3711"), F("0.50")]
        rowsad, child, parent = admissibility(a.host, a.basis, taus)
        print()
        print(f"ADMISSIBILITY on the measured residual base ({a.basis}): "
              f"fold {fmt(child,6)} s/net against parent {fmt(parent,6)} s/net, "
              f"m = {fmt(child/parent, 4)} [O]")
        print("| tau (s/net) | fold as built (measured) | verdict | implied m |")
        print("|---|---:|---|---:|")
        for tau, ch, fits, mm in rowsad:
            print(f"| {fmt(tau,4)} | {fmt(ch,6)} | {'fits' if fits else 'BREACH'} | {fmt(mm,4)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
