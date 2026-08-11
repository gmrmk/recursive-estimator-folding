"""Assemble audit_results.json from the four sub-audits."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def load(n):
    return json.loads((HERE / n).read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


corpses = load("corpse_verdicts.json")
widths = load("width_exposure.json")
verify = load("verify_hits_results.json")

M183_HITS = [
    {
        "rank": 1,
        "site": "corpus/whestbench/experiments/m183_f32_hotpath/run_m183_falsifier.py:58",
        "code": 'dts = getattr(op, "dtypes", None) or ()',
        "subpattern": "(a) getattr with falsy default + (b) any() over the empty result + (c) name absent from installed API",
        "installed_api_truth": "flopscope 0.10.0 OpRecord exposes resolved_dtype; it has no 'dtypes'. hasattr(op,'dtypes') is False on a live record.",
        "can_return_null_regardless_of_ground_truth": True,
        "empirical_check": "100%-float64 fixture (2 chained 256x256 matmuls, 1.34e8 billed): suspect detector returns f64_share 0.0; corrected resolved_dtype detector returns 1.0",
        "cited_in_fold_ledger": ["m183_f32_hotpath_falsifier (result: 'f64-lane billed = 0.0000e0 of 1.5803e11 total (0.00%)')",
                                  "gen8_m183_detector_void (today's retraction)"],
        "cited_in_phase1_writeup": ["line 129 table row: 'M183 | float32 hot-path recast (the \"free 2x\") | 0.00% f64-lane billing - already clean | killed'",
                                     "line 422: 'the fidelity family formally retired the dtype-repricing escape (M183 measured the f64 SHARE at 0.00%, which is invariant to how f64 is priced)'"],
        "verdict": "STRUCTURALLY VOID - confirmed",
    },
    {
        "rank": "1b",
        "site": "corpus/whestbench/experiments/m183_f32_hotpath/run_m183_falsifier.py:62",
        "code": "getattr(op, 'name', '?')",
        "subpattern": "(c) name absent from installed API (OpRecord field is op_name)",
        "installed_api_truth": "hasattr(op,'name') is False on a live OpRecord",
        "can_return_null_regardless_of_ground_truth": True,
        "empirical_check": "same fixture; the branch containing this read is unreachable because hit 1 makes the guard always False, so the defect is masked by the larger one",
        "cited_in_fold_ledger": [],
        "cited_in_phase1_writeup": [],
        "verdict": "DEAD NAME - confirmed, currently unreachable",
    },
    {
        "rank": 2,
        "site": "corpus/whestbench/experiments/gm_a4_constraint/verify_two_signal.py:64-72 (scan_code)",
        "code": 'NEEDLES = {"budget_summary_dict","_tally","get_data","summary_dict"}; scan co_names/co_consts',
        "subpattern": "(b) reducer over a possibly-empty needle set feeding any_residual_source_reachable=False",
        "can_return_null_regardless_of_ground_truth": False,
        "empirical_check": "positive fixture = t3_fold3_deterministic_cap/capped_fold3.py (the file this script's own attack section names as a _tally definer): scan_code returns ['_tally'] -> the detector FIRES",
        "note": "2 of the 4 needles occur in that fixture only inside a comment, which bytecode cannot see; that is the intended behaviour of a bytecode scan and not a defect",
        "cited_in_fold_ledger": ["a4_hostile_inputs_battery (screened) is the audited parent; gm_a4_constraint's own step-0 kill"],
        "cited_in_phase1_writeup": [],
        "verdict": "SHAPE MATCH, NOT VOID - published [] is a genuine negative",
    },
    {
        "rank": 3,
        "site": "corpus/whestbench/experiments/gm_m179_m199/run_depth32_identity_trace.py:134-138",
        "code": 'legacy_named = sorted(op for op in ops if any(tag in op for tag in ("legacy","rebuild","build_extended_background","full_archive")))',
        "subpattern": "(b) any() over a tag list; empty result is the clean bill",
        "can_return_null_regardless_of_ground_truth": False,
        "empirical_check": "real 21-operation histogram + one injected op 'm200.legacy_rebuild.full_archive' -> detector FIRES; and the same run carries an independent monkeypatch LegacyCallCounter",
        "cited_in_fold_ledger": ["gm_m179_m199 (KILL_CONFIRMED) - the record that licenses the whole width-gate proposal"],
        "cited_in_phase1_writeup": [],
        "verdict": "SHAPE MATCH, NOT VOID - instrument is positive-capable and double-covered",
    },
    {
        "rank": 4,
        "site": "corpus/whestbench/experiments/v31_guards/run_v31_gates.py:202",
        "code": 'json.dumps(getattr(est, "last_guard_report", None))',
        "subpattern": "(a) getattr with None default on an estimator resolved dynamically from an arm directory",
        "can_return_null_regardless_of_ground_truth": False,
        "empirical_check": "read from the committed v31_results.json: gate G2 is an explicit positive control - m186_empty_regime_fired=true on net f_negshift and m187_finite_output_fired=true with 164 nonfinite entries replaced on net b_gain_1e3",
        "cited_in_fold_ledger": ["v31_guards_m186_m187 (status 'validated' - the only validated record in the ledger)"],
        "cited_in_phase1_writeup": [],
        "verdict": "SHAPE MATCH, NOT VOID - G1's zeros are backed by G2's firing control. This is the correct pattern.",
    },
    {
        "rank": 5,
        "site": "corpus/whestbench/experiments/m184_trichotomy_upward/run_m184_g0.py (certain-on / certain-dead detector)",
        "code": "per-layer certain-on counts feeding 'projected billed reduction 0.00%'",
        "subpattern": "reported statistic is exactly 0.00% on all three nets - the M183 signature",
        "can_return_null_regardless_of_ground_truth": False,
        "empirical_check": "the same detector reports max per-layer certain-on = 39 and max certain-dead = 37 inside the same artifact, so it demonstrably fires; the 0.00% reduction is a measured negative (the counts never reach composition break-even)",
        "cited_in_fold_ledger": ["m184_trichotomy_upward_g0"],
        "cited_in_phase1_writeup": ["line 130: 'M184 | mid-layer exact on-composition + sparsity | 0.00% billed reduction'"],
        "verdict": "SHAPE MATCH, NOT VOID",
    },
    {
        "rank": 6,
        "site": "corpus/whestbench/experiments/m177_bivariate_relu_primitive/m177_bivariate_relu_primitive.py:167-168",
        "code": 'hasattr(fnp,"owens_t") or hasattr(getattr(flops,"stats",None),"owens_t"); hasattr(getattr(flops,"stats",None),"multivariate_normal_cdf")',
        "subpattern": "(a)+(c) capability probe by literal name; a rename would report the primitive absent",
        "can_return_null_regardless_of_ground_truth": False,
        "empirical_check": "full enumeration of the installed surface: flopscope.stats = [cauchy, expon, laplace, logistic, lognorm, norm, truncnorm, uniform]; norm = [cdf, name, pdf, ppf]; no member of flopscope.stats or flopscope.numpy matches owen/multivar/bivar under any spelling",
        "cited_in_fold_ledger": ["m177_bivariate_relu_value_jacobian_primitive (formal_runtime_no_go_phi2_owent_certificate_absent)"],
        "cited_in_phase1_writeup": [],
        "verdict": "SHAPE MATCH, NOT VOID - the no-go conclusion is confirmed by enumeration, but the instrument would not have detected a rename",
    },
    {
        "rank": 7,
        "site": "corpus/whestbench/experiments/t3_fold3_deterministic_cap/run_t3_gates.py:204,265",
        "code": 'report = getattr(capped, "last_cap_report", None)',
        "subpattern": "(a) getattr with None default on the capped estimator",
        "can_return_null_regardless_of_ground_truth": False,
        "empirical_check": "static read: `report is None` is folded into the failure branch (`g1['pass'] = False`) and into `completed` for G2, so an absent attribute FAILS the gate rather than silently passing it",
        "cited_in_fold_ledger": ["t3_fold3_deterministic_cap (screened)"],
        "cited_in_phase1_writeup": [],
        "verdict": "SHAPE MATCH, FAIL-CLOSED - safe",
    },
    {
        "rank": 8,
        "site": "corpus/whestbench/experiments/terra_m153_pilot_reuse/run_m153_pilot_prefix_reuse_structural.py:97",
        "code": 'list(getattr(estimator, "pilot_reuse_trace", []))',
        "subpattern": "(a) getattr with empty-list default feeding removed_formal_dispatches and removed_shape_bill",
        "can_return_null_regardless_of_ground_truth": False,
        "empirical_check": "committed trace has pilot_reuse_trace = ['formal:first:pilot','formal:layer2:pilot','formal:layer3:pilot'], removed_formal_dispatches n=3, removed_shape_bill=589,840,384; and the blocking assertion only_three_formal_dispatches_removed is computed from matmul dispatch-call deltas, independent of this attribute",
        "cited_in_fold_ledger": ["m153_exact_formal_prefix_reuse"],
        "cited_in_phase1_writeup": [],
        "verdict": "SHAPE MATCH, NOT VOID - independent blocking assertion",
    },
]

CLEARED = {
    "gm_m116_streams/probe_cheap.py op.*": "op is a local GroupedInplaceL3, not a flopscope OpRecord; differing_words=0 is a bitwise equality with a max_abs cross-check",
    "gm_s17_reuse/step0_results.json rel_err_ratio_costfloor=0": "bitwise reproduction check; the underlying ratios are 1.63/2.37/1.37, non-zero",
    "pb1_premise_battery m191 odd-degree design_rms=0": "antipodal design cancels odd moments exactly; even degrees are non-zero (2.18e-6 / 0.107 / 0.348)",
    "gm_flatworm_response_ladder permutation_relative_error=0 on 14/24 states": "max over states is 6.90e-14, non-zero; the instrument fires",
    "gm_latent_cubature/step0_arithmetic.py": "hard-indexes ops['take']['flop_cost'] (loud KeyError on absence) and reads weights from flopscope._weights - exemplary",
    "m217_balanced_three_color/run_m217_native_trace.py": "uses -1 as the absent-key sentinel, not 0: int(matmul.get('calls', -1)) - this is the recommended antidote idiom",
    "u2_fold3cap_bound/calib_summary_cost.py": "constructs OpRecord with the correct installed field names including resolved_dtype - the right name was already known in this corpus",
    "wc1_winner_ablation/wc1_ablation.py 'A_frames' in arms": "keys match ARMS exactly; derived_isolated_ratios is populated",
}

result = {
    "audit": "gen8_gate_audit - verification of the proposed WIDTH-TRANSFER GATE",
    "date": "2026-08-10",
    "governed_by": "commits 9e7ecda + ad04e4a on origin/claude/repos-agentic-frontier-e8ixlk",
    "scope": "read-only over the repo; writes confined to corpus/whestbench/experiments/gen8_gate_audit/",
    "pinned_inputs": {
        "fold_ledger.json": {
            "sha256": widths["ledger_snapshot"]["sha256"],
            "n_candidates": widths["ledger_snapshot"]["n_candidates"],
        },
        "GEN6_FAILURE_SALVAGE_ATLAS_20260809.json": {
            "sha256": sha(REPO / "corpus/whestbench/headroom/GEN6_FAILURE_SALVAGE_ATLAS_20260809.json"),
            "n_records": 223,
        },
        "flopscope": "0.10.0+np2.4.6",
        "python": "work/whest-v014/Scripts/python.exe",
    },
    "deviations": [
        "The fold ledger grew from 261 candidates (task statement) to 263 during the audit; a parallel session is appending gen8_* records. All Task-2 counts are pinned to sha256 "
        + widths["ledger_snapshot"]["sha256"] + " at 263 candidates. The two new records are both status 'killed' and do not change any promotion-eligible count.",
        "The graveyard's six-corpse table names corpses in prose, not by ledger id. The id mapping was made by matching the quoted numbers (0.997502, 8.8716, 0.04738, 2.475%, 3.01e-15) against the ledger text and is recorded per corpse.",
        "Width auto-extraction has one confirmed false positive: gm_u3_grid's '48' is the size of the empirical rotation pool (build_pool_spec('empirical48')), not a network width. gm_u3_grid has no width parameter. It is left in the machine output and corrected in prose.",
        "Task 3 was scoped as instructed to corpus/whestbench/experiments/**/*.py (522 files). m245_*/m243_*/m244_* were scanned but excluded from the finding set per the no-touch instruction; their hits are OS-portability getattrs (st_file_attributes, O_BINARY, orig_argv), not measurement defects.",
    ],
    "task1_six_corpses": corpses,
    "task2_width_exposure": widths,
    "task3_m183_defect_class": {
        "installed_api_ground_truth": {
            "flopscope.OpRecord fields": ["op_name", "subscripts", "shapes", "flop_cost",
                                           "cumulative", "namespace",
                                           "flopscope_context_start_offset_s",
                                           "flopscope_backend_duration_s",
                                           "flopscope_overhead_duration_s",
                                           "resolved_dtype"],
            "live_probe": "hasattr(op,'dtypes') == False, hasattr(op,'name') == False",
        },
        "files_scanned": 522,
        "static_pattern_counts": {
            "a_getattr_falsy_default": 62,
            "b_reducer_over_comprehension": 991,
            "c_attr_not_in_installed_api_raw": 176,
            "token_in_source_detectors": 55,
            "dead_name_reads_with_falsy_default": 2,
            "cross_artifact_get_with_unknown_key": 0,
        },
        "empirical_filter": "109 artifacts carry a zero-valued measured statistic; each was traced back to its producing detector",
        "hits": M183_HITS,
        "confirmed_structurally_void": 1,
        "shape_matched_but_positive_capable": 7,
        "cleared_with_reason": CLEARED,
        "empirical_verification": verify,
    },
}

(HERE / "audit_results.json").write_text(json.dumps(result, indent=1),
                                         encoding="utf-8")
print("wrote audit_results.json")
print("corpse tally:", json.dumps(corpses["tally"]))
print("width exposure:", widths["n_promotion_eligible_records"], "eligible /",
      widths["n_exposed_measured_below_256"], "exposed /",
      widths["n_would_fail_two_width_clause"], "fail 2-width clause")
