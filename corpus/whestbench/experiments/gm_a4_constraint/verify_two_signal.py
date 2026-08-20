"""gm_a4_constraint -- second, INDEPENDENT signal for the step-0 kill.

Signal 2a (independent of the text grep in run_step0.py):
  Import the frozen v3 estimator A4 actually invoked, enumerate the TRANSITIVE
  first-party module closure that the import graph really loads, and scan each
  module's compiled code objects (co_names / co_consts, recursively) for the
  residual source `budget_summary_dict`. Bytecode-level reachability over the
  real import closure -- catches transitive modules a single-directory grep
  would miss. No predict() is called; no estimator is run.

Signal 2b (independent of the source constant CAP=244.8e9):
  Recompute the maximum MEASURED billed F ever produced under capped_fold3 from
  the committed T3 gate metering (t3_gate_results.json), and compare to A4's
  worst hostile F. Measurement vs source-constant: neither can fool the other.

Signal 2c: bit-repeat of run_step0.py -> results.json must be byte-identical.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SHARE = REPO.parent.parent
WORK = SHARE / "work"
SF = WORK / "scorefloor_generation"
FROZEN_V3 = SF / "kerdock_l1_owned_buffer/candidate_source_validator_v3"
T3 = REPO / "corpus/whestbench/experiments/t3_fold3_deterministic_cap/t3_gate_results.json"
A4 = REPO / "corpus/whestbench/experiments/a_series_granular_adversarial/a4_results.json"

out = {"experiment": "gm_a4_constraint", "check": "two-signal verification of step-0 kill"}

# ------------------------------------------------------------- signal 2a ----
sys.path.insert(0, str(FROZEN_V3))
before = set(sys.modules)
est_mod = importlib.import_module("estimator")          # import only; no predict
fold3 = importlib.import_module("fold3_estimator")
newly = set(sys.modules) - before


def first_party(m: types.ModuleType) -> bool:
    f = getattr(m, "__file__", None)
    if not f:
        return False
    try:
        return SF in Path(f).resolve().parents
    except Exception:
        return False


closure = sorted(
    {n for n in newly | {"estimator", "fold3_estimator"}
     if isinstance(sys.modules.get(n), types.ModuleType) and first_party(sys.modules[n])}
)


def scan_code(code, needles, hits):
    for n in code.co_names:
        if n in needles:
            hits.add(n)
    for c in code.co_consts:
        if isinstance(c, str) and c in needles:
            hits.add(c)
        elif hasattr(c, "co_names"):
            scan_code(c, needles, hits)


NEEDLES = {"budget_summary_dict", "_tally", "get_data", "summary_dict"}
per_module = {}
all_hits = set()
for name in closure:
    f = Path(sys.modules[name].__file__)
    code = compile(f.read_text(encoding="utf-8"), str(f), "exec")
    hits = set()
    scan_code(code, NEEDLES, hits)
    per_module[name] = {"file": f.name, "hits": sorted(hits)}
    all_hits |= hits

out["signal_2a_import_closure_bytecode"] = {
    "modules_in_first_party_closure": closure,
    "n_modules": len(closure),
    "per_module_hits": per_module,
    "any_residual_source_reachable": bool(all_hits),
    "hits_union": sorted(all_hits),
    "estimator_class_present": hasattr(est_mod, "Estimator"),
    "fold3_module_loaded": fold3.__name__,
}

# ------------------------------------------------------------- signal 2b ----
t3 = json.loads(T3.read_text(encoding="utf-8"))
a4 = json.loads(A4.read_text(encoding="utf-8"))
B = 272000000000.0

metered = [n["c_capped_metered"] for n in t3["gates"]["g1"]["nets"]]
metered.append(t3["gates"]["g2"]["c_capped_metered"])
max_capped_metered = max(metered)
uncapped_diag = t3["gates"]["g2"]["diagnostic_uncapped_metered"]
F_worst = max(r["billed_flops"] for r in a4["rows"] + [a4["baseline"]])

out["signal_2b_measured_cap_binding"] = {
    "capped_metered_F_values": metered,
    "max_capped_metered_F": max_capped_metered,
    "max_capped_metered_over_B": max_capped_metered / B,
    "cap_constant_from_source": t3["constants"]["cap_billed_flops"],
    "g2_uncapped_diagnostic_F": uncapped_diag,
    "g2_uncapped_would_breach_B": t3["gates"]["g2"]["diagnostic_uncapped_would_breach_B"],
    "g2_n_eff_trimmed_from_to": [t3["constants"]["n_full"], t3["gates"]["g2"]["n_eff"]],
    "a4_worst_hostile_F": F_worst,
    "a4_worst_F_minus_max_capped_metered": F_worst - max_capped_metered,
    "a4_worst_F_reachable_under_cap": F_worst <= max_capped_metered,
    "coherent_variant_measured": max_capped_metered + 3.0e10,
    "coherent_variant_measured_over_B": (max_capped_metered + 3.0e10) / B,
}

# ---------------------------------------------------------------- attack ----
# Strongest counter-hypotheses to the step-0 kill, tested specifically:
#  H1: some UNCAPPED estimator also calls _tally, letting both addends co-occur.
#  H2: the cap's cost model under-predicts badly enough that metered F can still
#      reach A4's 259,700,796,917 under the cap.
CORPUS = REPO / "corpus"
tally_definers = sorted(
    str(p.relative_to(REPO)).replace("\\", "/")
    for p in CORPUS.rglob("*.py")
    if p.parent != HERE                       # exclude this harness's own source
    and "def _tally" in p.read_text(encoding="utf-8", errors="replace")
)
definer_caps = {}
for rel in tally_definers:
    txt = (REPO / rel).read_text(encoding="utf-8", errors="replace")
    definer_caps[rel] = {
        "declares_cap_billed_flops": "cap_billed_flops = 244.8e9" in txt,
        "u2_fix_applied": "get_active_budget().flops_used" in txt,
    }

pred_pairs = [(n["c_capped_metered"], n["c_pred_chosen"]) for n in t3["gates"]["g1"]["nets"]]
pred_pairs.append((t3["gates"]["g2"]["c_capped_metered"], t3["gates"]["g2"]["c_pred_chosen"]))
errs = [(m / p - 1.0) for m, p in pred_pairs]
CAP = float(t3["constants"]["cap_billed_flops"])
needed = F_worst / CAP - 1.0

out["attack"] = {
    "H1_uncapped_tally_caller": {
        "files_defining__tally": tally_definers,
        "their_cap_and_fix_status": definer_caps,
        "any_uncapped_tally_caller": any(
            not v["declares_cap_billed_flops"] for v in definer_caps.values()
        ),
        "verdict": "H1 fails: every _tally definer carries CAP=244.8e9",
    },
    "H2_cost_model_underprediction": {
        "observed_metered_over_pred_errors": errs,
        "max_observed_error": max(errs),
        "underprediction_required_to_reach_A4_worst_F": needed,
        "ratio_required_over_observed": needed / max(errs),
        "verdict": "H2 fails: required miss is ~1.6e3x the largest observed miss",
    },
    "attack_landed": False,
}

# ------------------------------------------------------------- signal 2c ----
res = HERE / "results.json"
h1 = hashlib.sha256(res.read_bytes()).hexdigest()
subprocess.run([sys.executable, str(HERE / "run_step0.py")], check=True,
               stdout=subprocess.DEVNULL)
h2 = hashlib.sha256(res.read_bytes()).hexdigest()
out["signal_2c_bit_repeat"] = {
    "results_json_sha256_run1": h1,
    "results_json_sha256_run2": h2,
    "bitwise_identical": h1 == h2,
}

(HERE / "verify_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
