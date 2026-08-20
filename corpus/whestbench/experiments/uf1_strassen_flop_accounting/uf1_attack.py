"""U-F1 adversarial pass: two attacks on the verdict.

ATTACK 1 -- "the -m*n accumulator discount is a pricing exploit, so r(d)<1
measures the biller, not Strassen." Test: price a CLASSICAL 2x2 block
decomposition (8 sub-multiplies + 4 accumulation adds). If blocking alone is
cheaper than the direct call, the whole r(d) result is an artifact.

ATTACK 2 -- "depth 5 wins on FLOPs but cannot survive the frozen numerical
gate." Test: a fresh synthetic width-256 depth-32 ReLU chain, float32
Strassen-Winograd at depth 0..5 against a float64 classical reference, scored
against the frozen gates used by INTEGRATED_BATCHED_WINOGRAD_REPORT
(relative final error <= 2e-5, ReLU gate mismatch fraction <= 2e-4).
Numpy-only twin of the metered recursion (identical schedule) so the chain is
tractable; the FLOP claim is unaffected.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

import flopscope as fl
import flopscope.numpy as fnp

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from uf1_derive_and_verify import matmul_charge  # noqa: E402

BUDGET = 10**18


# --------------------------------------------------------------------------
# ATTACK 1
# --------------------------------------------------------------------------
def attack_no_free_lunch() -> dict:
    rows = []
    for (M, K, N) in [(256, 64, 64), (1024, 128, 128), (2048, 256, 256)]:
        rng = np.random.default_rng(7)
        a = np.asarray(rng.standard_normal((M, K)), dtype="float32")
        b = np.asarray(rng.standard_normal((K, N)), dtype="float32")
        fa, fb = fnp.asarray(a), fnp.asarray(b)
        with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
            fnp.matmul(fa, fb)
            direct = int(bud.summary_dict()["flops_used"])
        hm, hk, hn = M // 2, K // 2, N // 2
        with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
            C = fnp.empty((M, N), dtype=fnp.float32)
            A11, A12 = fa[:hm, :hk], fa[:hm, hk:]
            A21, A22 = fa[hm:, :hk], fa[hm:, hk:]
            B11, B12 = fb[:hk, :hn], fb[:hk, hn:]
            B21, B22 = fb[hk:, :hn], fb[hk:, hn:]
            tmp = fnp.empty((hm, hn), dtype=fnp.float32)
            for (X1, Y1, X2, Y2, dst) in (
                (A11, B11, A12, B21, C[:hm, :hn]),
                (A11, B12, A12, B22, C[:hm, hn:]),
                (A21, B11, A22, B21, C[hm:, :hn]),
                (A21, B12, A22, B22, C[hm:, hn:]),
            ):
                fnp.matmul(X1, Y1, out=dst)
                fnp.matmul(X2, Y2, out=tmp)
                fnp.add(dst, tmp, out=dst)
            blocked = int(bud.summary_dict()["flops_used"])
        rows.append({
            "shape": f"({M}x{K})@({K}x{N})",
            "direct_charged": direct,
            "classical_2x2_blocked_charged": blocked,
            "ratio": blocked / direct,
            "formula_direct": matmul_charge(M, K, N),
            "exploit_present": blocked < direct,
        })
    return {"rows": rows,
            "verdict": ("no free lunch: classical 2x2 blocking prices EXACTLY "
                        "equal to the direct call, so r(d)<1 is attributable to "
                        "Strassen's 7-vs-8, not to the -m*n discount")
            if all(r["ratio"] == 1.0 for r in rows) else
            "EXPLOIT PRESENT -- r(d) is contaminated by the accumulator discount"}


# --------------------------------------------------------------------------
# ATTACK 2 -- numpy twin of the metered Winograd schedule
# --------------------------------------------------------------------------
def sw_np(A, B, depth):
    m, k = A.shape[-2], A.shape[-1]
    n = B.shape[-1]
    if depth <= 0 or m % 2 or k % 2 or n % 2:
        return A @ B
    hm, hk, hn = m // 2, k // 2, n // 2
    A11, A12 = A[:hm, :hk], A[:hm, hk:]
    A21, A22 = A[hm:, :hk], A[hm:, hk:]
    B11, B12 = B[:hk, :hn], B[:hk, hn:]
    B21, B22 = B[hk:, :hn], B[hk:, hn:]
    S1 = A21 + A22
    S2 = S1 - A11
    S3 = A11 - A21
    S4 = A12 - S2
    T1 = B12 - B11
    T2 = B22 - T1
    T3 = B22 - B12
    T4 = T2 - B21
    M1 = sw_np(A11, B11, depth - 1)
    M2 = sw_np(A12, B21, depth - 1)
    M3 = sw_np(S4, B22, depth - 1)
    M4 = sw_np(A22, T4, depth - 1)
    M5 = sw_np(S1, T1, depth - 1)
    M6 = sw_np(S2, T2, depth - 1)
    M7 = sw_np(S3, T3, depth - 1)
    U2 = M1 + M6
    U3 = U2 + M7
    U4 = U2 + M5
    C = np.empty((m, n), dtype=A.dtype)
    C[:hm, :hn] = M1 + M2
    C[:hm, hn:] = U4 + M3
    C[hm:, :hn] = U3 - M4
    C[hm:, hn:] = U3 + M5
    return C


def attack_depth32_chain(rows_n=512, width=256, layers=32) -> dict:
    rng = np.random.default_rng(20260810)
    X0 = np.asarray(rng.standard_normal((rows_n, width)), dtype="float32")
    Ws = [np.asarray(rng.standard_normal((width, width)) * np.sqrt(2.0 / width),
                     dtype="float32") for _ in range(layers)]
    # float64 classical reference
    Xr = X0.astype(np.float64)
    ref_gates = []
    for W in Ws:
        Xr = Xr @ W.astype(np.float64)
        ref_gates.append(Xr > 0)
        Xr = np.maximum(Xr, 0.0)
    out = {}
    for d in range(0, 6):
        t0 = time.time()
        X = X0.copy()
        mism = 0
        for i, W in enumerate(Ws):
            X = sw_np(X, W, d)
            mism += int(np.count_nonzero((X > 0) != ref_gates[i]))
            X = np.maximum(X, np.float32(0.0))
        rel = float(np.linalg.norm(X.astype(np.float64) - Xr)
                    / np.linalg.norm(Xr))
        total_gates = rows_n * width * layers
        out[f"d{d}"] = {
            "relative_final_error": rel,
            "gate_mismatches": mism,
            "gate_total": total_gates,
            "gate_mismatch_fraction": mism / total_gates,
            "passes_rel_gate_2e-5": rel <= 2e-5,
            "passes_gate_fraction_2e-4": mism / total_gates <= 2e-4,
            "seconds": round(time.time() - t0, 2),
        }
        print(f"chain d={d} rel={rel:.4e} mism={mism}/{total_gates} "
              f"({mism / total_gates:.3e}) {out[f'd{d}']['seconds']}s", flush=True)
    return {"rows": rows_n, "width": width, "layers": layers,
            "reference": "float64 classical", "results": out}


def main() -> None:
    res = {"attack1_no_free_lunch": attack_no_free_lunch()}
    print(json.dumps(res, indent=2), flush=True)
    res["attack2_depth32_chain"] = attack_depth32_chain()
    (HERE / "uf1_attack.json").write_text(json.dumps(res, indent=2),
                                          encoding="utf-8")
    print(json.dumps(res["attack2_depth32_chain"]["results"], indent=2))


if __name__ == "__main__":
    main()
