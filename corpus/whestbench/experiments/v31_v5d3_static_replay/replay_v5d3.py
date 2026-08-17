"""Deterministic static replay for the V31 V5-d3 arithmetic proposal.

This module reads only already-committed width tapes and the frozen GUARDS cost
model.  It does not import WhestBench or FlopScope, construct an MLP, execute a
matrix product, read truth, or make an efficacy claim.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from dataclasses import asdict, dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
M_PRODUCTION = 64_512
WIDTH_PRODUCTION = 256
N_DEEP_HOOKS = 28

INPUTS = {
    "stage3": (
        "corpus/whestbench/experiments/uf1_attack_eligibility/attack_stage3.json",
        "39275EAFE5FFF2587BDAEC81AB16545C588EBB40243B55B30580AB08BB6C5FE6",
    ),
    "raw_11_15": (
        "corpus/whestbench/experiments/uf1_attack_eligibility/attack_eligibility_raw.json",
        "6D6869253E0126920BC955D2C9BD19F7CD3B8CB3B875F943170C3D6A91DB8BD9",
    ),
    "judge_21_25": (
        "corpus/whestbench/experiments/uf1_attack_judge/j2_eligibility.json",
        "6192B23D61F25CCD4AB95FCBBB83D6E8E379C1F3AAC06A8047DCF5F07A1E2AD6",
    ),
    "judge_generator": (
        "corpus/whestbench/experiments/uf1_attack_judge/j2_eligibility.py",
        "8FB2A0D99FEC13250EA3B5AE7374D22A30D9B4A353929DB1E2445C92FCDAD710",
    ),
    "cost_model": (
        "corpus/whestbench/experiments/v31_guards/package_source/cost_model.py",
        "2A42E0D9CA3A80ECB4FF2BE302CCFAAACFA34BF6FE920B1EEA27FEB7AE798D68",
    ),
    "proposal": (
        "corpus/whestbench/core/CODEX_V31_V5D3_G4B1152_U1_PROPOSAL_20260811.md",
        "8E21F282F939C2BFD9ED1EFE59E881DC88F075B16A0BC8E200CF367060A2BA42",
    ),
    "erratum": (
        "corpus/whestbench/core/CODEX_V31_V5D3_G4B1152_ERRATUM1_20260811.md",
        "90DB78A80DA11C4DD302186E6DD54298AC289749F3E615AA98C3DCDA612FCB44",
    ),
}

EXPECTED_CURRENT = {
    11: 154_720_254_241,
    12: 151_088_919_681,
    13: 163_753_789_297,
    14: 148_253_240_205,
    15: 145_498_000_151,
    21: 155_038_228_331,
    22: 141_204_825_804,
    23: 148_305_556_567,
    24: 175_017_313_723,
    25: 148_006_959_800,
}

EXPECTED_V5 = {
    11: 116_618_302_059,
    12: 117_699_592_290,
    13: 127_773_730_077,
    14: 112_592_670_771,
    15: 111_528_316_074,
    21: 118_430_384_268,
    22: 110_703_752_775,
    23: 115_209_486_861,
    24: 131_038_699_176,
    25: 112_624_126_083,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_bound_inputs(repo: Path = REPO) -> dict[str, dict[str, Any]]:
    verified: dict[str, dict[str, Any]] = {}
    for role, (relative, expected) in INPUTS.items():
        path = repo / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing bound input {role}: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(
                f"SHA-256 mismatch for {role}: expected {expected}, got {actual}"
            )
        verified[role] = {
            "path": relative,
            "sha256": actual,
            "bytes": path.stat().st_size,
        }
    return verified


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_frozen_cost_model(repo: Path = REPO) -> ModuleType:
    relative, _expected = INPUTS["cost_model"]
    path = repo / relative
    spec = importlib.util.spec_from_file_location("v5_replay_frozen_cost_model", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load frozen cost model: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def direct_cost(m: int, k: int, n: int) -> int:
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


@dataclass(frozen=True)
class V5Components:
    m: int
    k: int
    n: int
    kc: int
    kt: int
    nc: int
    nt: int
    depth_three_core: int
    ragged_k_direct: int
    ragged_k_add: int
    ragged_n_direct: int
    ragged_n_copy: int
    total: int


def v5_components(m: int, k: int, n: int) -> V5Components:
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    if m % 8:
        raise ValueError("V5 depth-three core requires row count divisible by eight")
    kc = k - (k % 8)
    nc = n - (n % 8)
    kt = k - kc
    nt = n - nc
    if kc < 8 or nc < 8:
        raise ValueError("V5 depth-three core requires kc>=8 and nc>=8")

    movement_numerator = 651 * (m * kc + kc * nc + m * nc)
    if movement_numerator % 64:
        raise AssertionError("V5 movement term is not integral")
    core = (
        343 * direct_cost(m // 8, kc // 8, nc // 8)
        + movement_numerator // 64
    )
    ragged_k_direct = direct_cost(m, kt, nc) if kt else 0
    ragged_k_add = m * nc if kt else 0
    ragged_n_direct = direct_cost(m, k, nt) if nt else 0
    ragged_n_copy = m * nt if nt else 0
    total = (
        core
        + ragged_k_direct
        + ragged_k_add
        + ragged_n_direct
        + ragged_n_copy
    )
    return V5Components(
        m=m,
        k=k,
        n=n,
        kc=kc,
        kt=kt,
        nc=nc,
        nt=nt,
        depth_three_core=core,
        ragged_k_direct=ragged_k_direct,
        ragged_k_add=ragged_k_add,
        ragged_n_direct=ragged_n_direct,
        ragged_n_copy=ragged_n_copy,
        total=total,
    )


def ragged_class(components: V5Components) -> str:
    if components.kt and components.nt:
        return "both_ragged"
    if components.kt:
        return "ragged_k_only"
    if components.nt:
        return "ragged_n_only"
    return "core_only"


def parent_runtime_calls(strategy: str, n: int) -> int:
    if strategy == "direct_owned":
        return 16
    if strategy == "winograd_batched_owned":
        return 32 if n % 2 else 16
    raise ValueError(f"unexpected frozen parent strategy: {strategy}")


def v5_group_calls(components: V5Components, groups_per_product: int) -> int:
    if groups_per_product <= 0:
        raise ValueError("groups_per_product must be positive")
    products = 1 + int(bool(components.kt)) + int(bool(components.nt))
    return groups_per_product * products


@dataclass(frozen=True)
class Tape:
    seed: int
    k_sequence: tuple[int, ...]
    n_sequence: tuple[int, ...]
    recorded_current: int
    source_role: str


def _require_width_sequence(values: Iterable[Any], label: str) -> tuple[int, ...]:
    result = tuple(int(value) for value in values)
    if len(result) != N_DEEP_HOOKS:
        raise ValueError(f"{label} has {len(result)} hooks, expected {N_DEEP_HOOKS}")
    if any(value < 1 or value > WIDTH_PRODUCTION for value in result):
        raise ValueError(f"{label} contains width outside 1..{WIDTH_PRODUCTION}")
    return result


def load_tapes(repo: Path = REPO) -> list[Tape]:
    stage3 = _load_json(repo / INPUTS["stage3"][0])
    raw = _load_json(repo / INPUTS["raw_11_15"][0])
    judge = _load_json(repo / INPUTS["judge_21_25"][0])

    raw_current = {int(row["seed"]): int(row["deep_hook_charged"]) for row in raw["runs"]}
    tapes: list[Tape] = []
    for row in stage3["E_headline_shape_frequency"]["per_seed"]:
        seed = int(row["seed"])
        tapes.append(
            Tape(
                seed=seed,
                k_sequence=_require_width_sequence(row["k_widths"], f"seed {seed} k"),
                n_sequence=_require_width_sequence(row["n_widths"], f"seed {seed} n"),
                recorded_current=raw_current[seed],
                source_role="stage3+raw_11_15",
            )
        )

    for row in judge["rows"]:
        seed = int(row["seed"])
        if int(row["n_deep_hooks"]) != N_DEEP_HOOKS:
            raise ValueError(f"seed {seed} declares wrong hook count")
        tapes.append(
            Tape(
                seed=seed,
                k_sequence=_require_width_sequence(row["k_sequence"], f"seed {seed} k"),
                n_sequence=_require_width_sequence(row["n_sequence"], f"seed {seed} n"),
                recorded_current=int(row["deep_hook_shipped_bill"]),
                source_role="judge_21_25",
            )
        )

    tapes.sort(key=lambda tape: tape.seed)
    expected_seeds = sorted(EXPECTED_CURRENT)
    actual_seeds = [tape.seed for tape in tapes]
    if actual_seeds != expected_seeds:
        raise ValueError(f"unexpected seed set: {actual_seeds}")
    return tapes


def decimal_string(value: Fraction, places: int = 12) -> str:
    getcontext().prec = max(40, places + 20)
    decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
    quantum = Decimal(1).scaleb(-places)
    return format(decimal_value.quantize(quantum), "f")


def replay(repo: Path = REPO) -> dict[str, Any]:
    verified = verify_bound_inputs(repo)
    cost_model = _load_frozen_cost_model(repo)
    tapes = load_tapes(repo)
    per_seed: list[dict[str, Any]] = []

    for tape in tapes:
        hooks: list[dict[str, Any]] = []
        class_counts = {
            "core_only": 0,
            "ragged_k_only": 0,
            "ragged_n_only": 0,
            "both_ragged": 0,
        }
        current_total = 0
        selected_total = 0
        parent_calls = 0
        b1152_calls = 0
        b4096_calls = 0

        for index, (k, n) in enumerate(zip(tape.k_sequence, tape.n_sequence), start=1):
            parent = cost_model.owned_batched_candidate_bill(M_PRODUCTION, k, n)
            components = v5_components(M_PRODUCTION, k, n)
            eligible = (
                components.kc >= 8
                and components.nc >= 8
                and components.total < int(parent.total)
            )
            chosen_total = components.total if eligible else int(parent.total)
            classification = ragged_class(components)
            class_counts[classification] += 1
            hook_parent_calls = parent_runtime_calls(parent.strategy, n)
            hook_b1152_calls = (
                v5_group_calls(components, groups_per_product=14)
                if eligible
                else hook_parent_calls
            )
            hook_b4096_calls = (
                v5_group_calls(components, groups_per_product=5)
                if eligible
                else hook_parent_calls
            )
            current_total += int(parent.total)
            selected_total += chosen_total
            parent_calls += hook_parent_calls
            b1152_calls += hook_b1152_calls
            b4096_calls += hook_b4096_calls
            hooks.append(
                {
                    "hook": index,
                    "m": M_PRODUCTION,
                    "k": k,
                    "n": n,
                    "parent_strategy": parent.strategy,
                    "parent_total": int(parent.total),
                    "parent_runtime_calls": hook_parent_calls,
                    "v5_eligible": eligible,
                    "v5_components": asdict(components),
                    "selected_total": chosen_total,
                    "ragged_class": classification,
                    "b1152_calls": hook_b1152_calls,
                    "b4096_calls": hook_b4096_calls,
                }
            )

        if current_total != tape.recorded_current:
            raise AssertionError(
                f"seed {tape.seed} replayed current {current_total} != recorded {tape.recorded_current}"
            )
        if current_total != EXPECTED_CURRENT[tape.seed]:
            raise AssertionError(f"seed {tape.seed} current total contradicts proposal")
        if selected_total != EXPECTED_V5[tape.seed]:
            raise AssertionError(
                f"seed {tape.seed} V5 total {selected_total} != expected {EXPECTED_V5[tape.seed]}"
            )
        saving = current_total - selected_total
        saving_fraction = Fraction(saving, current_total)
        per_seed.append(
            {
                "seed": tape.seed,
                "source_role": tape.source_role,
                "hook_count": len(hooks),
                "current_total": current_total,
                "v5_selected_total": selected_total,
                "saving": saving,
                "saving_fraction": f"{saving_fraction.numerator}/{saving_fraction.denominator}",
                "saving_percent": decimal_string(100 * saving_fraction),
                "class_counts": class_counts,
                "all_hooks_v5_eligible": all(row["v5_eligible"] for row in hooks),
                "parent_runtime_calls": parent_calls,
                "b1152_calls": b1152_calls,
                "b4096_calls": b4096_calls,
                "hooks": hooks,
            }
        )

    if per_seed[0]["seed"] != 11:
        raise AssertionError("seed order is not canonical")
    seed11 = per_seed[0]
    if seed11["class_counts"] != {
        "core_only": 1,
        "ragged_k_only": 1,
        "ragged_n_only": 4,
        "both_ragged": 22,
    }:
        raise AssertionError(f"unexpected seed-11 ragged census: {seed11['class_counts']}")
    if (
        seed11["parent_runtime_calls"],
        seed11["b1152_calls"],
        seed11["b4096_calls"],
    ) != (544, 1078, 385):
        raise AssertionError("seed-11 call census mismatch")

    current_sum = sum(row["current_total"] for row in per_seed)
    v5_sum = sum(row["v5_selected_total"] for row in per_seed)
    saving_sum = current_sum - v5_sum
    saving_fractions = [Fraction(row["saving"], row["current_total"]) for row in per_seed]

    manifest_path = HERE / "STATIC_REPLAY_MANIFEST.json"
    manifest_hash = sha256_file(manifest_path) if manifest_path.is_file() else None
    calculator_hash = sha256_file(Path(__file__).resolve())
    return {
        "schema": "v31-v5d3-static-replay-v1",
        "status": "RETROSPECTIVE_STATIC_ARITHMETIC_ONLY_NO_CANDIDATE_CREDIT",
        "authority": {
            "generated_networks": False,
            "truth_or_scorer": False,
            "child_source_or_execution": False,
            "efficacy_or_promotion_claim": False,
        },
        "provenance": {
            "calculator_path": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
            "calculator_sha256": calculator_hash,
            "manifest_path": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": manifest_hash,
            "inputs": verified,
        },
        "geometry": {
            "m": M_PRODUCTION,
            "width": WIDTH_PRODUCTION,
            "hooks_per_tape": N_DEEP_HOOKS,
            "b1152": {"block_rows": 1152, "atomic_blocks": 56, "groups_per_product": 14},
            "b4096": {"block_rows": 4096, "full_blocks": 15, "remainder_rows": 3072, "groups_per_product": 5},
        },
        "fixture_64512_253_255": asdict(v5_components(64_512, 253, 255)),
        "per_seed": per_seed,
        "aggregate": {
            "tape_count": len(per_seed),
            "current_sum": current_sum,
            "v5_sum": v5_sum,
            "saving_sum": saving_sum,
            "current_mean": decimal_string(Fraction(current_sum, len(per_seed)), places=1),
            "v5_mean": decimal_string(Fraction(v5_sum, len(per_seed)), places=1),
            "saving_mean": decimal_string(Fraction(saving_sum, len(per_seed)), places=1),
            "minimum_saving_percent": decimal_string(100 * min(saving_fractions)),
            "maximum_saving_percent": decimal_string(100 * max(saving_fractions)),
        },
        "limitations": [
            "The widths are historical parent tapes, not widths produced by a reassociated V5 child.",
            "No float32 product, gate, estimator output, MSE, wall time, RSS, or official score was measured.",
            "The replay is neither a complete child bill nor a universal cost bound.",
            "B4096 versus B1152 remains unresolved until official memory and metering rules are bound.",
        ],
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the complete canonical receipt")
    parser.add_argument(
        "--write-receipt",
        type=Path,
        help="write the complete canonical receipt to this path",
    )
    args = parser.parse_args()
    payload = replay()
    rendered = canonical_json(payload)
    if args.write_receipt is not None:
        args.write_receipt.write_text(rendered, encoding="utf-8", newline="\n")
    if args.json:
        print(rendered, end="")
    else:
        aggregate = payload["aggregate"]
        print(
            "PASS static replay: "
            f"{aggregate['tape_count']} tapes, "
            f"current={aggregate['current_sum']}, "
            f"v5={aggregate['v5_sum']}, "
            f"saving={aggregate['saving_sum']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
