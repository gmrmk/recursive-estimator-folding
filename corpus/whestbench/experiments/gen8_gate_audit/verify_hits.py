"""Empirical verification of the top M183-class hits.

Each check runs the SUSPECT detector logic verbatim against a fixture where the
ground truth is POSITIVE, and reports whether the detector fires.  A detector
that cannot fire on a positive fixture is structurally void: its published
negative carries no information.

Read-only with respect to every audited file; the suspect logic is copied here,
never edited in place.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import flopscope as flops
import flopscope.numpy as fnp

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SHARE = REPO.parent.parent
SF = SHARE / "work" / "scorefloor_generation"

results = {}


# --------------------------------------------------------------------------
# HIT 1 -- M183 f64 detector (the reference defect; reproduced independently)
# --------------------------------------------------------------------------
def m183_detector(ops):
    """Verbatim copy of run_m183_falsifier.py lines 52-65."""
    total = 0.0
    f64 = 0.0
    by_op_f64 = {}
    for op in ops:
        cost = float(getattr(op, "flop_cost", 0) or 0)
        total += cost
        dts = getattr(op, "dtypes", None) or ()
        names = [str(getattr(d, "name", d))
                 for d in (dts if isinstance(dts, (list, tuple)) else [dts])]
        if any(("float64" in n) or ("complex" in n) for n in names):
            f64 += cost
            key = f"{getattr(op, 'name', '?')}|{','.join(sorted(set(names)))}"
            by_op_f64[key] = by_op_f64.get(key, 0.0) + cost
    return (f64 / total if total else 0.0), total, f64, by_op_f64


def m183_detector_corrected(ops):
    """Same measurement against the field the installed OpRecord actually has."""
    total = 0.0
    f64 = 0.0
    for op in ops:
        cost = float(getattr(op, "flop_cost", 0) or 0)
        total += cost
        dt = str(getattr(op, "resolved_dtype", "") or "")
        if ("float64" in dt) or ("complex" in dt):
            f64 += cost
    return (f64 / total if total else 0.0), total, f64


def check_m183():
    # POSITIVE FIXTURE: every array float64, every op billed in the f64 lane.
    rng = np.random.default_rng(0)
    with flops.BudgetContext(int(1e13), quiet=True) as budget:
        a = fnp.asarray(rng.standard_normal((256, 256)).astype(np.float64))
        b = fnp.asarray(rng.standard_normal((256, 256)).astype(np.float64))
        c = a @ b
        d = c @ a
        _ = fnp.asarray(np.asarray(d))
        ops = list(budget.op_log)

    dtypes_seen = sorted({str(getattr(o, "resolved_dtype", None)) for o in ops})
    share_bad, total, f64_bad, top = m183_detector(ops)
    share_ok, total2, f64_ok = m183_detector_corrected(ops)
    return {
        "hit": "M183 run_m183_falsifier.py:58 getattr(op,'dtypes',None) or ()",
        "fixture": "100% float64 program, 2 chained 256x256 matmuls inside BudgetContext",
        "n_ops": len(ops),
        "resolved_dtypes_present_in_fixture": dtypes_seen,
        "oprecord_has_dtypes_attr": any(hasattr(o, "dtypes") for o in ops),
        "oprecord_has_name_attr": any(hasattr(o, "name") for o in ops),
        "total_billed": total,
        "SUSPECT_f64_billed": f64_bad,
        "SUSPECT_f64_share": share_bad,
        "SUSPECT_top_ops": top,
        "CORRECTED_f64_billed": f64_ok,
        "CORRECTED_f64_share": share_ok,
        "detector_fires_on_positive_fixture": share_bad > 0.0,
        "verdict": ("STRUCTURALLY VOID: returns 0.00% on a program that is "
                    "100% float64 by construction"
                    if share_bad == 0.0 and share_ok > 0.0 else "fires"),
    }


# --------------------------------------------------------------------------
# HIT 2 -- gm_a4_constraint signal 2a bytecode needle scan
# --------------------------------------------------------------------------
def scan_code(code, needles, hits):
    """Verbatim copy of gm_a4_constraint/verify_two_signal.py:64-72."""
    for n in code.co_names:
        if n in needles:
            hits.add(n)
    for c in code.co_consts:
        if isinstance(c, str) and c in needles:
            hits.add(c)
        elif hasattr(c, "co_names"):
            scan_code(c, needles, hits)


def check_gm_a4():
    NEEDLES = {"budget_summary_dict", "_tally", "get_data", "summary_dict"}
    # POSITIVE FIXTURE: the file the same script's own attack section names as a
    # definer of _tally + the cap constant.
    pos = (REPO / "corpus/whestbench/experiments/t3_fold3_deterministic_cap"
                  "/capped_fold3.py")
    text = pos.read_text(encoding="utf-8")
    code = compile(text, str(pos), "exec")
    hits = set()
    scan_code(code, NEEDLES, hits)
    return {
        "hit": "gm_a4_constraint/verify_two_signal.py:64 scan_code needle scan",
        "fixture": str(pos.relative_to(REPO)),
        "needles": sorted(NEEDLES),
        "needles_present_in_fixture_text": sorted(n for n in NEEDLES if n in text),
        "detector_hits_on_positive_fixture": sorted(hits),
        "detector_fires_on_positive_fixture": bool(hits),
        "verdict": ("fires -- published [] is a genuine negative"
                    if hits else "STRUCTURALLY VOID"),
    }


# --------------------------------------------------------------------------
# HIT 3 -- gm_m179_m199 audit_event_ledger legacy-tag scan
# --------------------------------------------------------------------------
def legacy_named_scan(op_names):
    """Verbatim copy of gm_m179_m199/run_depth32_identity_trace.py:134-138."""
    ops = {n: 1 for n in op_names}
    return sorted(
        op for op in ops
        if any(tag in op for tag in ("legacy", "rebuild",
                                     "build_extended_background", "full_archive"))
    )


def check_gm_m179_legacy_tags():
    res = json.loads((REPO / "corpus/whestbench/experiments/gm_m179_m199"
                             "/results.json").read_text(encoding="utf-8"))
    cell = res["ARM_B_identity_trace_depth32"]["cells"][0]
    real = sorted(cell["ledger_audit"]["operation_histogram"])
    # POSITIVE FIXTURE: inject an operation name that a legacy rebuild would emit.
    positive = real + ["m200.legacy_rebuild.full_archive"]
    return {
        "hit": "gm_m179_m199/run_depth32_identity_trace.py:134 legacy tag scan",
        "fixture": "real observed operation histogram + one injected legacy op",
        "n_real_operations_observed": len(real),
        "scan_on_real_ops": legacy_named_scan(real),
        "scan_on_positive_fixture": legacy_named_scan(positive),
        "detector_fires_on_positive_fixture": bool(legacy_named_scan(positive)),
        "independent_positive_capable_instrument": "LegacyCallCounter (monkeypatch counter)",
        "verdict": ("fires -- published [] is a genuine negative"
                    if legacy_named_scan(positive) else "STRUCTURALLY VOID"),
    }


# --------------------------------------------------------------------------
# HIT 4 -- m184 certain-on detector (does its zero have a positive control?)
# --------------------------------------------------------------------------
def check_m184():
    p = (REPO / "corpus/whestbench/experiments/m184_trichotomy_upward"
                "/m184_g0_results.json")
    res = json.loads(p.read_text(encoding="utf-8"))
    on_counts, dead_counts = [], []
    for n in res["nets"]:
        for lay in n.get("per_layer", []):
            on_counts.append(lay["on"])
            dead_counts.append(lay["certain_dead_all256"])
    fires = max(on_counts) > 0 or max(dead_counts) > 0
    return {
        "hit": "m184_trichotomy_upward/run_m184_g0.py certain-on detector",
        "reported_statistic": res["aggregate"],
        "max_certain_on_count_observed": max(on_counts),
        "max_certain_dead_count_observed": max(dead_counts),
        "n_layer_cells": len(on_counts),
        "detector_fires_somewhere": fires,
        "verdict": ("NOT the M183 class -- the same detector produces nonzero "
                    "certain-on (39) and certain-dead (37) counts at other "
                    "layers, so its 0.00% reduction is a measured negative, "
                    "not a structural one"
                    if fires else "needs manual read"),
    }


def main():
    results["m183_f64_detector"] = check_m183()
    results["gm_a4_bytecode_needle_scan"] = check_gm_a4()
    results["gm_m179_legacy_tag_scan"] = check_gm_m179_legacy_tags()
    results["m184_certain_on_detector"] = check_m184()
    (HERE / "verify_hits_results.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8")
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    sys.exit(main())
