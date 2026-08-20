"""Self-tests for Fable's independent M243 oracle.

Every fixture is synthetic and constructed HERE; the real frozen manifest
is touched only for format validation, and the real G0B seeds are never
used.  Test precision is deliberately low (dps 20/28) to keep runtime
small; production runs use the frozen (80, 100).
"""

from __future__ import annotations

import json
import math
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_g0a_oracle as oracle
import run_shard

TEST_DPS = (16, 22)       # production stays frozen at (80, 100)
TEST_DPS_COARSE = (12, 16)
TEST_SELF_TOL = 1e-8      # two-precision agreement at test dps
TEST_COARSE_TOL = 1e-6
TEST_FORMULA_TOL = 5e-8   # closed forms (float64) vs direct at test dps
TEST_EXPECT_TOL = 5e-7

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"test": name, "pass": bool(ok), "detail": str(detail)})
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    if not ok:
        raise SystemExit(f"self-test failed: {name}: {detail}")


def fixture_cell():
    """Tiny synthetic width-3 cell (mild correlations, non-unit scales)."""
    mu = np.array([-0.30, 0.20, 0.45])
    C = np.array([[1.21, 0.28, -0.22],
                  [0.28, 0.81, 0.10],
                  [-0.22, 0.10, 1.44]])
    # exact symmetry + comfortable PD by construction
    assert np.array_equal(C, C.T)
    assert float(np.min(np.linalg.eigvalsh(C))) > 0.3
    return mu, C


def main():
    mu, C = fixture_cell()
    i, j, k = 0, 1, 2

    # T0 -- hash-verification hooks fire correctly
    tr = oracle.verify_frozen_inputs()
    check("T0a_frozen_input_hashes", len(tr) == 2, tr)
    try:
        oracle.verify_frozen_inputs(tempfile.gettempdir())
        check("T0b_hash_hard_fail", False, "no hard fail on wrong dir")
    except oracle.OracleHardFail:
        check("T0b_hash_hard_fail", True, "OracleHardFail raised")
    for name in oracle.PARENT_SHA256:
        oracle.import_frozen(name)
    check("T0c_shared_module_hashes", True, sorted(oracle.PARENT_SHA256))

    # T1 -- reference internals: Phi2 factorizes at rho=0; positive-part
    # product moment matches the independent 1-D reduction at rho=0
    import mpmath as mp
    with mp.workdps(30):
        v = oracle._Phi2(mp.mpf("0.3"), mp.mpf("-0.7"), mp.mpf(0))
        w = oracle._Phi(mp.mpf("0.3")) * oracle._Phi(mp.mpf("-0.7"))
        check("T1a_phi2_rho0", abs(v - w) < 1e-25, float(abs(v - w)))
        pp = oracle.pospart_product_mp("0.4", "-0.2", "1.3", "0.8", 0)
        ind = (oracle.relu_mean_mp(mp.mpf("0.4"), mp.mpf("1.3"))
               * oracle.relu_mean_mp(mp.mpf("-0.2"), mp.mpf("0.8")))
        check("T1b_pospart_rho0", abs(pp - ind) < 1e-25, float(abs(pp - ind)))

    # T2 -- full per-event oracle on the fixture; bias contract and the
    # frozen-M122 Hermite-series second derivation of Delta
    rec = oracle.oracle_event(mu, C, i, j, k, dps_pair=TEST_DPS,
                              tol=TEST_SELF_TOL)
    delta = rec["delta_reference"]
    gh = oracle.delta_series_cross_check(mu, C, i, j, k)
    check("T2a_delta_two_signals",
          abs(gh - delta) <= TEST_EXPECT_TOL * (1 + abs(delta)),
          f"quad={delta:.12e} series={gh:.12e}")
    for arm in ("ANTI", "Q2_actual", "Q4_actual", "Q2_ideal", "Q4_ideal"):
        resid = rec["arms"][arm]["bias_contract_residual"]
        # actual arms carry closed-form R error; ideal arms are exact
        tol = TEST_EXPECT_TOL if arm.endswith("ideal") else 1e-5
        check(f"T2b_bias_contract_{arm}",
              abs(resid) <= tol * (1 + abs(delta)), f"resid={resid:.3e}")
    check("T2c_variances_finite",
          all(math.isfinite(rec["arms"][a]["var"]) and
              rec["arms"][a]["var"] >= 0
              for a in ("RAW1", "RAW2", "ANTI", "Q2_actual", "Q4_actual")),
          {a: rec["arms"][a]["var"] for a in
           ("RAW1", "ANTI", "Q2_actual", "Q4_actual")})
    check("T2d_gh2_reported",
          math.isfinite(rec["arms"]["GH2"]["bias"]),
          f"gh2_bias={rec['arms']['GH2']['bias']:.3e}")

    # T3 -- gate-1 style: proposed section-5 R closed forms vs direct
    # integration (independent reference)
    close = [abs(a - b) <= TEST_FORMULA_TOL * (1 + abs(b))
             for a, b in zip(rec["R_actual"], rec["R_ideal"])]
    check("T3_R_closed_vs_direct", all(close),
          [f"{a:.10e}/{float(b):.10e}" for a, b in
           zip(rec["R_actual"], rec["R_ideal"])])

    # T4 -- gate-2 style: proposed section-4 betas through the certified
    # M178 provider vs direct E[b He_r]/r!
    close = [abs(a - b) <= TEST_FORMULA_TOL * (1 + abs(b))
             for a, b in zip(rec["beta_actual_m178"], rec["beta_ideal"])]
    check("T4_beta_m178_vs_direct", all(close),
          [f"{a:.10e}/{float(b):.10e}" for a, b in
           zip(rec["beta_actual_m178"], rec["beta_ideal"])])

    # T4g -- G0A gate checker wiring on this record (loose test tolerances)
    gates = oracle.g0a_gate_check(rec, formula_tol=TEST_FORMULA_TOL,
                                  expectation_tol=1e-5)
    check("T4g_gate_checker", gates["all"], gates)

    # T5 -- tree convention: local single-entry (i,i,j,k) evaluation vs the
    # frozen M122 continuation tensor
    m122 = oracle.import_frozen("m122_nonzero_bridge.py")
    state = m122.build_state(mu, C)
    tensor = m122.tree_tensor_continuation(state, 4)
    mine = oracle.tree_iijk(mu, C, i, j, k)
    check("T5_tree_vs_frozen_tensor",
          abs(mine - tensor[i, i, j, k]) <= 1e-9 * (1 + abs(mine)),
          f"local={mine:.12e} frozen={tensor[i, i, j, k]:.12e}")

    # T6 -- ownership: typed refusal on collisions and forbidden strata
    r1 = oracle.oracle_event(mu, C, 0, 1, 1, dps_pair=TEST_DPS)
    check("T6a_collision_refusal", "refusal" in r1, r1.get("refusal"))
    r2 = oracle.refuse_stratum("[2,2]")
    check("T6b_stratum_refusal",
          isinstance(r2, oracle.TypedRefusal), r2)

    # T6c -- symmetry under j<->k (gate-4 style, swap only; coarse dps)
    rec_sw = oracle.oracle_event(mu, C, i, k, j, dps_pair=TEST_DPS_COARSE,
                                 tol=TEST_COARSE_TOL, tail_check=False)
    check("T6c_jk_swap_symmetry",
          abs(rec_sw["delta_reference"] - delta) <= 1e-8 * (1 + abs(delta))
          and all(abs(a - b) <= 1e-9 * (1 + abs(b)) for a, b in
                  zip(rec_sw["beta_actual_m178"], rec["beta_actual_m178"])),
          f"delta_swap={rec_sw['delta_reference']:.12e}")

    # T6d -- positive diagonal gauge: physical degree lambda_i^2 l_j l_k
    lam = np.array([1.7, 0.6, 1.2])
    Cg = C * np.outer(lam, lam)
    Cg = 0.5 * (Cg + Cg.T)
    rec_g = oracle.oracle_event(lam * mu, Cg, i, j, k,
                                dps_pair=TEST_DPS_COARSE,
                                tol=TEST_COARSE_TOL, tail_check=False)
    want = delta * lam[i] ** 2 * lam[j] * lam[k]
    check("T6d_gauge_degree",
          abs(rec_g["delta_reference"] - want) <= 1e-6 * (1 + abs(want)),
          f"scaled={rec_g['delta_reference']:.10e} want={want:.10e}")

    # T7 -- manifest: real file passes format validation; corrupted copy
    # hard-fails (copy lives in THIS experiment dir, never the frozen one)
    m = oracle.validate_manifest()
    check("T7a_manifest_format_ok", m["candidate"] == "M243", "")
    bad_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "selftest_artifacts")
    os.makedirs(bad_dir, exist_ok=True)
    bad_path = os.path.join(bad_dir, "corrupted_manifest.json")
    m_bad = json.loads(json.dumps(m))
    m_bad["g0b"]["bootstrap_seed"] = 999
    with open(bad_path, "w", encoding="utf-8") as f:
        json.dump(m_bad, f)
    try:
        oracle.validate_manifest(bad_path)
        check("T7b_manifest_hard_fail", False, "no hard fail")
    except oracle.OracleHardFail:
        check("T7b_manifest_hard_fail", True, "OracleHardFail raised")

    # T8 -- regeneration determinism + q_e hook on a SYNTHETIC cell (seed
    # 999000111 is not a frozen seed; the recipe is exercised, the real
    # G0B cells are not generated here)
    a = oracle.regenerate_g0a_cell(5, 999000111)
    b = oracle.regenerate_g0a_cell(5, 999000111)
    check("T8a_regen_deterministic",
          np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]), "")
    mu5, C5 = a
    C5 = C5 + np.eye(5) * 0.05
    W5 = np.random.Generator(np.random.Philox(999000112)).normal(
        0, 1 / math.sqrt(13), size=(5, 13))
    prop = oracle.build_proposal(mu5, C5, W5)
    rng = np.random.Generator(np.random.Philox(999000113))
    draws = prop.sample(rng, 16)
    qs = [oracle.q_e_check(prop, *map(int, d)) for d in draws]
    check("T8b_qe_positive", all(q > 0 for q in qs),
          f"min q_e = {min(qs):.3e}")
    try:
        oracle.q_e_check(prop, 0, 1, 1)
        check("T8c_qe_collision_hard_fail", False, "no hard fail")
    except oracle.OracleHardFail:
        check("T8c_qe_collision_hard_fail", True, "OracleHardFail raised")
    wsq = oracle.feature_weight_sq(W5, 0, 1, 2, qs[0])
    check("T8d_feature_weight",
          math.isfinite(wsq) and wsq > 0, f"||F/(2q)||^2 = {wsq:.6e}")

    # T9 -- shard plumbing: mapping, caps, checkpoint/resume with a stub
    check("T9a_shard_map",
          oracle.SHARDS == {0: ("P0", 0, 64), 1: ("P0", 64, 128),
                            2: ("P1", 0, 64), 3: ("P1", 64, 128)}, "")
    ck = os.path.join(bad_dir, "stub_checkpoint.jsonl")
    if os.path.exists(ck):
        os.remove(ck)
    calls = []

    def stub(i, j, k):
        calls.append((i, j, k))
        return {"event": [i, j, k], "q_e": 1.0, "weight_sq": 1.0,
                "delta_reference": 0.1,
                "arms": {a: {"var": v} for a, v in
                         (("ANTI", 3.0), ("Q2_actual", 2.0),
                          ("Q4_actual", 1.0))}}

    work = [(t, (0, 1, 2)) for t in range(6)]
    s1 = run_shard.run_shard_core(work[:3], stub, ck, log=lambda *_: None)
    s2 = run_shard.run_shard_core(work, stub, ck, log=lambda *_: None)
    with open(ck, encoding="utf-8") as f:
        lines = [json.loads(x) for x in f if x.strip()]
    check("T9b_checkpoint_resume",
          s1 == "DONE" and s2 == "DONE" and len(lines) == 6
          and len(calls) == 6, f"calls={len(calls)} lines={len(lines)}")
    s3 = run_shard.run_shard_core([(9, (0, 1, 2))], stub, ck,
                                  wall_cap_s=-1.0, log=lambda *_: None)
    check("T9c_wall_cap", s3 == "WALL", s3)
    rss = oracle.rss_mib()
    check("T9d_rss_probe", math.isfinite(rss) and rss > 0,
          f"rss={rss:.1f} MiB")

    # T10 -- aggregation + paired bootstrap on synthetic records (tiny
    # replicate count for speed; frozen 20000/2430002 used in real runs)
    rng = np.random.Generator(np.random.Philox(999000114))
    recs = []
    for t in range(24):
        d = tuple(int(x) for x in draws[t % len(draws)])
        recs.append({"event": list(d), "q_e": qs[t % len(qs)],
                     "weight_sq": float(rng.uniform(0.5, 2.0)),
                     "delta_reference": float(rng.normal(0, 0.1)),
                     "arms": {"ANTI": {"var": float(rng.uniform(2, 3))},
                              "Q2_actual": {"var": float(rng.uniform(1, 2))},
                              "Q4_actual": {"var": float(rng.uniform(.2, .9))}}})
    agg = oracle.aggregate_records(recs, W5, replicates=200, seed=1)
    check("T10_aggregator",
          math.isfinite(agg["upper90_nq4_nanti"])
          and math.isfinite(agg["upper90_nq4_vdelta"])
          and agg["point"]["N"]["Q4_actual"] < agg["point"]["N"]["ANTI"],
          {k: agg[k] for k in ("upper90_nq4_nanti", "upper90_nq4_vdelta")})

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "selftest_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"dps_pair": TEST_DPS, "results": RESULTS,
                   "fixture_record_excerpt": {
                       "delta_reference": rec["delta_reference"],
                       "delta_gh_cross_check": gh,
                       "beta_actual_m178": rec["beta_actual_m178"],
                       "beta_ideal": [float(x) for x in rec["beta_ideal"]],
                       "R_actual": rec["R_actual"],
                       "R_ideal": [float(x) for x in rec["R_ideal"]],
                       "arm_vars": {a: rec["arms"][a].get("var")
                                    for a in rec["arms"]}}},
                  f, indent=2)
    print(f"ALL SELF-TESTS PASSED -> {out}")


if __name__ == "__main__":
    main()
