"""v3.1 GUARDS gate runner: G1 (bitwise identity + billing on healthy nets),
G2 (guards fire on A4's two hostile nets), G3 (package + validate + member
listing).  Governed by the v3.1 GUARDS task predeclaration; governing
evidence a4_results.json + A3_A4_NOTES.md (M186/M187 guard candidates and
their cheapest falsifiers).

Arms run in separate subprocesses (module-name isolation: frozen v3 and the
v3.1 package both expose ``estimator.py`` etc.).  Invocation replicates
run_a4_hostile.py exactly: SetupContext(width=256, depth=32, flop_budget=
int(2.72e11), api_version='2.0', seed=0, submission_dir=<arm dir>); predict
inside flops.BudgetContext(int(2.72e11), quiet=True).

First failed gate stops the run; v31_results.json records the broken link.

Firewall: synthetic nets only; frozen v3 imported read-only (bytecode writes
disabled); byte-identity of the copied sources verified by sha256 against
both the frozen directory and v3_package_manifest.json before any gate; no
dataset/truth/scorer/submission access; writes confined to v31_guards.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
PKG_DIR = HERE / "package_source"
ROOT = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c"
)
V3_DIR = (
    ROOT / "work" / "scorefloor_generation" / "kerdock_l1_owned_buffer"
    / "candidate_source_validator_v3"
)
WHEST = ROOT / "work" / "whest-v014" / "Scripts" / "whest.exe"
A4_DIR = HERE.parent / "a_series_granular_adversarial"
TAR_PATH = HERE / "submission_kerdock_v31_guards_20260808.tar.gz"

WIDTH, DEPTH = 256, 32
BUDGET = int(2.72e11)
GAIN = math.sqrt(2.0 / WIDTH)
G1_NET_SEEDS = (101, 202, 303)
G1_BILL_TOLERANCE = 1.0e-3           # +0.1 percent ceiling (predeclared)

# A4 anchors (a4_results.json, 2026-08-08) for harness cross-checks.
A4_DET_BILLED = 179_197_201_680
A4_F_BILLED = 5_159_851_464
A4_B_BILLED = 154_722_710_745

# Byte-identity pairs: sha256 recomputed from disk on both sides at run
# time (frozen dir is the source of truth; v3_package_manifest.json was
# independently confirmed to carry the same hashes at build time).
FROZEN_PAIRS = [
    # (frozen-dir file, package_source file)
    ("base_estimator.py", "base_estimator.py"),
    ("cost_model.py", "cost_model.py"),
    ("fold3_estimator.py", "fold3_estimator.py"),
    ("fold_estimator.py", "fold_estimator.py"),
    ("row_blocked_winograd.py", "row_blocked_winograd.py"),
    ("estimator.py", "kerdock_v3_estimator.py"),
    ("kerdock_phases.npz", "kerdock_phases.npz"),
    ("sobol_owen_u32.npz", "sobol_owen_u32.npz"),
]
EXPECTED_TAR_MEMBERS = {
    "estimator.py",
    "kerdock_v3_estimator.py",
    "base_estimator.py",
    "cost_model.py",
    "fold3_estimator.py",
    "fold_estimator.py",
    "row_blocked_winograd.py",
    "kerdock_phases.npz",
    "sobol_owen_u32.npz",
    "manifest.json",
}

HOSTILE_SPECS = {
    # kind -> (rng seed per run_a4_hostile.build_net, mlp seed per A4 loop)
    "f_negshift": (4400 + "abcdefg".index("f"), 555_006),
    "b_gain_1e3": (4400 + "abcdefg".index("b"), 555_002),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hostile_gate_pass(*, v3_reproduced: bool, v3_billed_match: bool,
                      completes: bool, finite_all: bool,
                      within_budget: bool, fired_expected: bool) -> bool:
    """Pure fail-closed G2 predicate, kept separately regression-testable."""
    return all((v3_reproduced, v3_billed_match, completes, finite_all,
                within_budget, fired_expected))


def tar_members_gate_pass(*, returncode: int, missing: list[str],
                          unexpected: list[str], members: list[str]) -> bool:
    """Pure fail-closed G3 member predicate."""
    return (
        returncode == 0
        and not missing
        and not unexpected
        and not any("__pycache__" in member for member in members)
    )


# ----------------------------------------------------------- net builders
def he_weights(seed: int) -> list[np.ndarray]:
    """n8c / A4 'normal' He construction (identical bitwise)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(GAIN)
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


def hostile_weights(kind: str) -> list[np.ndarray]:
    """Verbatim run_a4_hostile.build_net for the two G2 kinds."""
    rng = np.random.default_rng(4400 + "abcdefg".index(kind[0]))
    ws = []
    for _ in range(DEPTH):
        if kind == "b_gain_1e3":
            w = rng.standard_normal((WIDTH, WIDTH)) * (GAIN * 1e3)
        elif kind == "f_negshift":
            w = rng.standard_normal((WIDTH, WIDTH)) * GAIN - 3.0 / 16.0
        else:
            raise ValueError(kind)
        ws.append(w.astype(np.float32))
    return ws


def build_net(net: str) -> tuple[list[np.ndarray], int, str]:
    """Return (weights, mlp_seed, mlp_name) for a net token."""
    if net.startswith("he"):
        seed = int(net[2:])
        return he_weights(seed), 900_000 + seed * 1_000, f"v31-g1-{seed}"
    if net == "a4det":
        # A4 determinism anchor: normal net (rng seed 101), mlp.seed 901101.
        return he_weights(101), 901_101, "a4-det"
    if net in HOSTILE_SPECS:
        return hostile_weights(net), HOSTILE_SPECS[net][1], f"a4-{net}"
    raise ValueError(net)


# ---------------------------------------------------------------- worker
def worker(arm: str, net: str, out_path: str) -> None:
    import traceback

    arm_dir = {"v3": V3_DIR, "v31": PKG_DIR}[arm]
    sys.path.insert(0, str(arm_dir))

    import flopscope as flops            # noqa: PLC0415
    import flopscope.numpy as fnp        # noqa: PLC0415
    from whestbench import SetupContext  # noqa: PLC0415
    from whestbench.domain import MLP    # noqa: PLC0415

    flops.configure(symmetry_warnings=False)
    from estimator import Estimator      # noqa: PLC0415  (arm-resolved)

    weights_np, mlp_seed, name = build_net(net)
    weights_f = [fnp.asarray(w) for w in weights_np]
    est = Estimator()
    est.setup(SetupContext(
        width=WIDTH, depth=DEPTH, flop_budget=BUDGET,
        api_version="2.0", seed=0, submission_dir=str(arm_dir),
    ))
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights_f,
              seed=mlp_seed, name=name)
    mlp.validate()

    out = None
    exc = ""
    ctx = flops.BudgetContext(BUDGET, quiet=True)
    t0 = time.perf_counter()
    try:
        with ctx:
            out = est.predict(mlp, BUDGET)
    except BaseException:
        exc = traceback.format_exc(limit=8)
    wall = time.perf_counter() - t0

    payload = {
        "billed": np.int64(ctx.flops_used),
        "wall_s": np.float64(wall),
        "exception": np.str_(exc),
        "guard_report": np.str_(
            json.dumps(getattr(est, "last_guard_report", None))
        ),
    }
    if out is not None:
        payload["stack"] = np.asarray(out).copy()
    np.savez(out_path, **payload)


def run_worker(arm: str, net: str) -> dict:
    out_path = HERE / f"_worker_{arm}_{net}.npz"
    if out_path.exists():
        out_path.unlink()
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "worker", arm, net,
         str(out_path)],
        capture_output=True, text=True, timeout=900,
    )
    if proc.returncode != 0 or not out_path.exists():
        raise RuntimeError(
            f"worker {arm}/{net} rc={proc.returncode}\n"
            f"stderr tail: {proc.stderr[-3000:]}"
        )
    with np.load(out_path, allow_pickle=False) as data:
        result = {
            "billed": int(data["billed"]),
            "wall_s": float(data["wall_s"]),
            "exception": str(data["exception"][()]),
            "guard_report": json.loads(str(data["guard_report"][()])),
            "stack": data["stack"].copy() if "stack" in data else None,
        }
    out_path.unlink()
    return result


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    import os
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(args, capture_output=True, text=True, timeout=900,
                          env=env, cwd=str(HERE))


# ------------------------------------------------------------------ main
def main() -> None:
    if len(sys.argv) == 5 and sys.argv[1] == "worker":
        worker(sys.argv[2], sys.argv[3], sys.argv[4])
        return

    results: dict = {
        "date": "2026-08-08",
        "candidate": "Kerdock v3.1 GUARDS (frozen v3 + M186 empty-regime "
                     "+ M187 finite-output)",
        "governing_evidence": "a_series_granular_adversarial/a4_results.json"
                              " + A3_A4_NOTES.md",
        "firewall": (
            "synthetic nets only; frozen v3 invoked read-only in an isolated "
            "subprocess; package sources are sha256-verified byte-identical "
            "copies; no dataset/truth/scorer/submission; no git; writes "
            "confined to v31_guards"
        ),
        "invocation": {
            "setup": "SetupContext(width=256, depth=32, flop_budget="
                     "int(2.72e11), api_version='2.0', seed=0, "
                     "submission_dir=<arm dir>)",
            "predict": "BudgetContext(int(2.72e11), quiet=True)",
            "rotation_seed_formula_g1": "900000 + net_seed*1000 + 0 "
                                        "(canonical n8c/n9/wc1/pb1 formula)",
        },
        "gates": {},
        "verdict": None,
    }
    out_path = HERE / "v31_results.json"

    def finish(verdict: str) -> None:
        results["verdict"] = verdict
        out_path.write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"\nVERDICT: {verdict}")
        print(f"results written to {out_path}")

    # ------------------------------------------------- G0: byte identity
    print("G0 (precondition): package_source byte-identity vs frozen v3")
    g0 = {"files": [], "pass": True}
    for src_name, dst_name in FROZEN_PAIRS:
        src_sha = sha256_file(V3_DIR / src_name)
        dst_sha = sha256_file(PKG_DIR / dst_name)
        ok = src_sha == dst_sha
        g0["files"].append({
            "frozen": src_name, "package": dst_name,
            "sha256": dst_sha, "identical": ok,
        })
        g0["pass"] = g0["pass"] and ok
        print(f"  {dst_name}: {'identical' if ok else 'MISMATCH'} "
              f"({dst_sha[:16]}...)")
    g0["new_estimator_sha256"] = sha256_file(PKG_DIR / "estimator.py")
    results["gates"]["g0_byte_identity"] = g0
    if not g0["pass"]:
        finish("KILL at G0: package_source is not a byte-identical copy of "
               "the frozen v3 sources (first broken link)")
        return

    # -------------------------------------------------------------- G1
    print("\nG1: bitwise identity + billing on 3 healthy He nets")
    g1 = {"nets": [], "pass": True}

    # Harness anchor: reproduce the A4 determinism artifact exactly.
    anchor = run_worker("v3", "a4det")
    a4_run1 = np.load(A4_DIR / "a4_det_run1.npz")
    anchor_stack64 = anchor["stack"].astype(np.float64)
    anchor_bitwise = bool(np.array_equal(anchor_stack64, a4_run1["stack"]))
    anchor_billed_ok = anchor["billed"] == A4_DET_BILLED
    g1["a4_anchor_crosscheck"] = {
        "mlp_seed": 901_101,
        "bitwise_equal_to_a4_det_run1": anchor_bitwise,
        "billed": anchor["billed"],
        "billed_matches_a4": bool(anchor_billed_ok),
    }
    print(f"  A4 anchor (v3, mlp.seed 901101): bitwise vs a4_det_run1.npz="
          f"{anchor_bitwise}, billed={anchor['billed']} "
          f"(A4: {A4_DET_BILLED}, match={anchor_billed_ok})")
    if not (anchor_bitwise and anchor_billed_ok):
        g1["pass"] = False
        results["gates"]["g1"] = g1
        finish("KILL at G1: harness fails to reproduce the A4 determinism "
               "anchor -- the comparison rig itself is broken "
               "(first broken link)")
        return

    for net_seed in G1_NET_SEEDS:
        net = f"he{net_seed}"
        r3 = run_worker("v3", net)
        r31 = run_worker("v31", net)
        if r3["exception"] or r31["exception"]:
            g1["pass"] = False
            g1["nets"].append({
                "net_seed": net_seed,
                "v3_exception": r3["exception"][-500:],
                "v31_exception": r31["exception"][-500:],
            })
            print(f"  net {net_seed}: RUN FAILURE")
            break
        bitwise = bool(
            r3["stack"].dtype == r31["stack"].dtype
            and r3["stack"].shape == r31["stack"].shape
            and np.array_equal(r3["stack"], r31["stack"])
        )
        delta = (r31["billed"] - r3["billed"]) / r3["billed"]
        bill_ok = 0.0 <= delta <= G1_BILL_TOLERANCE
        guards_quiet = (
            r31["guard_report"] is not None
            and not r31["guard_report"]["m186_empty_regime_fired"]
            and not r31["guard_report"]["m187_finite_output_fired"]
        )
        net_pass = bitwise and bill_ok and guards_quiet
        g1["nets"].append({
            "net_seed": net_seed,
            "mlp_seed": 900_000 + net_seed * 1_000,
            "bitwise_equal": bitwise,
            "v3_billed": r3["billed"],
            "v31_billed": r31["billed"],
            "billed_delta_flops": r31["billed"] - r3["billed"],
            "billed_delta_fraction": delta,
            "within_plus_0.1pct": bill_ok,
            "guards_quiet": guards_quiet,
            "v31_guard_report": r31["guard_report"],
            "v3_wall_s": round(r3["wall_s"], 2),
            "v31_wall_s": round(r31["wall_s"], 2),
            "pass": net_pass,
        })
        g1["pass"] = g1["pass"] and net_pass
        print(f"  net {net_seed}: bitwise={bitwise} "
              f"billed v3={r3['billed']} v3.1={r31['billed']} "
              f"delta={r31['billed'] - r3['billed']} ({delta:.3e}) "
              f"guards_quiet={guards_quiet} "
              f"[{'PASS' if net_pass else 'KILL'}]")
    results["gates"]["g1"] = g1
    if not g1["pass"]:
        finish("KILL at G1: v3.1 is not a bitwise no-op on healthy nets "
               "(or billing exceeded +0.1%) (first broken link)")
        return
    print("G1: PASS")

    # -------------------------------------------------------------- G2
    print("\nG2: guards fire on A4's two hostile nets")
    g2 = {"nets": [], "pass": True}
    expectations = {
        "f_negshift": {"a4_billed": A4_F_BILLED, "guard": "m186"},
        "b_gain_1e3": {"a4_billed": A4_B_BILLED, "guard": "m187"},
    }
    for kind, exp in expectations.items():
        r3 = run_worker("v3", kind)
        r31 = run_worker("v31", kind)

        # Cross-check: frozen v3 reproduces the A4 failure exactly.
        if kind == "f_negshift":
            v3_reproduced = (
                "matrix dimensions must be positive" in r3["exception"]
                and r3["stack"] is None
            )
        else:
            v3_reproduced = (
                not r3["exception"]
                and r3["stack"] is not None
                and not bool(np.isfinite(r3["stack"]).all())
            )
        v3_billed_match = r3["billed"] == exp["a4_billed"]

        completes = not r31["exception"]
        finite_all = (
            bool(np.isfinite(r31["stack"]).all())
            if r31["stack"] is not None else False
        )
        guard = r31["guard_report"] or {}
        fired_expected = bool(guard.get(
            {"m186": "m186_empty_regime_fired",
             "m187": "m187_finite_output_fired"}[exp["guard"]]
        ))
        within_budget = r31["billed"] <= BUDGET
        # Fail closed on the frozen hostile anchor as well as the child.  If
        # v3 no longer reproduces the exact A4 failure/bill, this comparison
        # rig is stale and cannot validate either guard.
        net_pass = hostile_gate_pass(
            v3_reproduced=v3_reproduced,
            v3_billed_match=v3_billed_match,
            completes=completes,
            finite_all=finite_all,
            within_budget=within_budget,
            fired_expected=fired_expected,
        )
        g2["nets"].append({
            "net": kind,
            "mlp_seed": HOSTILE_SPECS[kind][1],
            "v3_reproduces_a4_failure": v3_reproduced,
            "v3_billed": r3["billed"],
            "v3_billed_matches_a4": bool(v3_billed_match),
            "v31_completes": completes,
            "v31_prediction_finite_all": finite_all,
            "v31_billed": r31["billed"],
            "v31_wall_s": round(r31["wall_s"], 2),
            "v31_within_budget": within_budget,
            "expected_guard": exp["guard"],
            "expected_guard_fired": fired_expected,
            "v31_guard_report": guard,
            "v31_exception": r31["exception"][-500:] if r31["exception"]
            else None,
            "pass": net_pass,
        })
        g2["pass"] = g2["pass"] and net_pass
        print(f"  {kind}: v3 reproduces A4 failure={v3_reproduced} "
              f"(billed match={v3_billed_match}); "
              f"v3.1 completes={completes} finite={finite_all} "
              f"within_budget={within_budget} "
              f"{exp['guard']}_fired={fired_expected} "
              f"billed={r31['billed']} "
              f"[{'PASS' if net_pass else 'KILL'}]")
        if guard:
            print(f"    guard report: {guard}")
    results["gates"]["g2"] = g2
    if not g2["pass"]:
        finish("KILL at G2: hostile v3 anchor is stale, or v3.1 does not "
               "complete finite within budget with the expected guard "
               "firing (first broken link)")
        return
    print("G2: PASS")

    # -------------------------------------------------------------- G3
    print("\nG3: package (folder mode) + validate-package + validate + tar")
    g3 = {"pass": True}

    pyc = list(PKG_DIR.rglob("__pycache__"))
    g3["pycache_in_source_before_packaging"] = [str(p) for p in pyc]
    if pyc:
        g3["pass"] = False
        results["gates"]["g3"] = g3
        finish("KILL at G3: __pycache__ present in package_source before "
               "packaging (first broken link)")
        return

    if TAR_PATH.exists():
        TAR_PATH.unlink()
    pkg = run_cli([str(WHEST), "package", "--estimator", str(PKG_DIR),
                   "--output", str(TAR_PATH), "--yes", "--format", "json"])
    g3["package"] = {
        "rc": pkg.returncode,
        "stdout_tail": pkg.stdout[-1500:],
        "stderr_tail": pkg.stderr[-800:],
        "tar_exists": TAR_PATH.exists(),
    }
    print(f"  package: rc={pkg.returncode} tar_exists={TAR_PATH.exists()}")
    if pkg.returncode != 0 or not TAR_PATH.exists():
        g3["pass"] = False
        results["gates"]["g3"] = g3
        finish("KILL at G3: whest package failed (first broken link)")
        return

    vp = run_cli([str(WHEST), "validate-package", str(TAR_PATH),
                  "--format", "json"])
    try:
        vp_json = json.loads(vp.stdout)
    except json.JSONDecodeError:
        vp_json = None
    vp_ok = vp.returncode == 0 and vp_json is not None and (
        vp_json.get("ok", False) if isinstance(vp_json, dict) else False
    )
    g3["validate_package"] = {
        "rc": vp.returncode, "json": vp_json,
        "stdout_tail": None if vp_json else vp.stdout[-1500:],
        "ok": vp_ok,
    }
    print(f"  validate-package: rc={vp.returncode} ok={vp_ok}")
    if not vp_ok:
        g3["pass"] = False
        results["gates"]["g3"] = g3
        finish("KILL at G3: whest validate-package failed "
               "(first broken link)")
        return

    vc = run_cli([str(WHEST), "validate", "--estimator",
                  str(PKG_DIR / "estimator.py"), "--format", "json"])
    try:
        vc_json = json.loads(vc.stdout)
    except json.JSONDecodeError:
        vc_json = None
    vc_ok = vc.returncode == 0 and vc_json is not None and (
        vc_json.get("ok", False) if isinstance(vc_json, dict) else False
    )
    g3["validate_contract"] = {
        "rc": vc.returncode, "json": vc_json,
        "stdout_tail": None if vc_json else vc.stdout[-1500:],
        "ok": vc_ok,
    }
    print(f"  validate: rc={vc.returncode} ok={vc_ok}")
    if not vc_ok:
        g3["pass"] = False
        results["gates"]["g3"] = g3
        finish("KILL at G3: whest validate (contract) failed "
               "(first broken link)")
        return

    tar_list = run_cli(["tar", "-tzf", str(TAR_PATH)])
    members = [line.strip() for line in tar_list.stdout.splitlines()
               if line.strip()]
    member_set = set(members)
    missing = sorted(EXPECTED_TAR_MEMBERS - member_set)
    unexpected = sorted(member_set - EXPECTED_TAR_MEMBERS)
    members_ok = tar_members_gate_pass(
        returncode=tar_list.returncode,
        missing=missing,
        unexpected=unexpected,
        members=members,
    )
    g3["tar_members"] = {
        "rc": tar_list.returncode,
        "members": members,
        "missing": missing,
        "unexpected": unexpected,
        "ok": members_ok,
    }
    print(f"  tar members ({len(members)}): missing={missing} "
          f"unexpected={unexpected} ok={members_ok}")
    if not members_ok:
        g3["pass"] = False
        results["gates"]["g3"] = g3
        finish("KILL at G3: tar member listing is incomplete or contains "
               "unexpected members -- the T3 near-miss rule "
               "(first broken link)")
        return

    g3["tar_sha256"] = sha256_file(TAR_PATH)
    g3["tar_size_bytes"] = TAR_PATH.stat().st_size
    (HERE / (TAR_PATH.name + ".sha256")).write_text(
        f"{g3['tar_sha256']}  {TAR_PATH.name}\n", encoding="utf-8",
    )
    results["gates"]["g3"] = g3
    print(f"  tar sha256: {g3['tar_sha256']}")
    print("G3: PASS")

    finish("PASS: G1 (bitwise + billing), G2 (both guards fire, finite), "
           "G3 (package validated, all members present) -- v3.1 GUARDS "
           "candidate holds")


if __name__ == "__main__":
    main()
