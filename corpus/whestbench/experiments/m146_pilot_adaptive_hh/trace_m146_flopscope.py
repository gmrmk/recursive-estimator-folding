"""Paired target-shaped structural trace for the M146 proposal delta.

Fresh synthetic float32 inputs are created before each FlopScope context.  The
baseline traces the proposal/sampling path replaced from M133.  The candidate
traces q0 pilot scans, the exact O(n) pilot Gram norm, fading bincount states,
q_ad construction, defensive main scans, exact phase probabilities, and the
heterogeneous scale concatenation barrier.  It does not construct a generated
Gaussian state, call M131, run a response, touch contest data, or score an
estimator.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import math
from pathlib import Path
import time
import tracemalloc

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


WIDTH = 256
LAYERS = 31
TOTAL = 512
PILOT = 64
MAIN = 448
MAIN_BASE = 112
MAIN_ADAPTIVE = MAIN - MAIN_BASE
M133_COMPLETE = 94_940_940_240
ARITHMETIC_GATE = 251_412_480
RESIDUAL_GATE_S = 0.025
BRANCH_CEILING = 100_000_000_000
REPEATS = 3


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def memory_counters() -> dict[str, int]:
    counters = PROCESS_MEMORY_COUNTERS_EX()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = (
        wintypes.HANDLE,
        ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX),
        wintypes.DWORD,
    )
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    handle = kernel32.GetCurrentProcess()
    if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        raise OSError(ctypes.get_last_error(), "GetProcessMemoryInfo failed")
    return {
        "working_set_bytes": int(counters.WorkingSetSize),
        "peak_working_set_bytes": int(counters.PeakWorkingSetSize),
        "private_bytes": int(counters.PrivateUsage),
    }


def legal_draws(rng: np.random.Generator, count: int, width: int) -> np.ndarray:
    answer = np.empty((count, 3), dtype=np.int64)
    for position in range(count):
        i = int(rng.integers(width))
        raw_j = int(rng.integers(width - 1))
        j = raw_j + int(raw_j >= i)
        low, high = sorted((i, j))
        raw_k = int(rng.integers(width - 2))
        k = raw_k + int(raw_k >= low)
        k += int(k >= high)
        answer[position] = i, j, k
    return answer


def synthetic_inputs() -> dict[str, object]:
    rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence(146_014_600)))
    weights = []
    scales = []
    bridges = []
    coefficients = []
    draw_sets: dict[str, list[np.ndarray]] = {
        "baseline": [],
        "pilot": [],
        "main_base": [],
        "main_adaptive": [],
    }
    bank_sets: dict[str, list[np.ndarray]] = {key: [] for key in draw_sets}
    for _ in range(LAYERS):
        weights.append(rng.normal(scale=0.06, size=(WIDTH, WIDTH)).astype(np.float32))
        scales.append(rng.uniform(0.2, 1.4, size=WIDTH).astype(np.float32))
        raw = rng.normal(scale=0.08, size=(WIDTH, WIDTH)).astype(np.float32)
        bridge = 0.5 * (raw + raw.T)
        np.fill_diagonal(bridge, 1.0)
        bridges.append(bridge)
        coefficients.append(rng.normal(scale=0.02, size=TOTAL).astype(np.float32))
        for name, count in (
            ("baseline", TOTAL),
            ("pilot", PILOT),
            ("main_base", MAIN_BASE),
            ("main_adaptive", MAIN_ADAPTIVE),
        ):
            draw_sets[name].append(legal_draws(rng, count, WIDTH))
            bank_sets[name].append(rng.integers(0, 3, size=count, dtype=np.int64))
    return {
        "weights": weights,
        "scales": scales,
        "bridges": bridges,
        "coefficients": coefficients,
        "draw_sets": draw_sets,
        "bank_sets": bank_sets,
    }


def as_flopscope(inputs: dict[str, object]) -> dict[str, object]:
    return {
        "weights": [fnp.asarray(value, dtype=fnp.float32) for value in inputs["weights"]],
        "scales": [fnp.asarray(value, dtype=fnp.float32) for value in inputs["scales"]],
        "bridges": [fnp.asarray(value, dtype=fnp.float32) for value in inputs["bridges"]],
        "coefficients": [fnp.asarray(value, dtype=fnp.float32) for value in inputs["coefficients"]],
        "draw_sets": {
            name: [fnp.asarray(value) for value in collection]
            for name, collection in inputs["draw_sets"].items()
        },
        "bank_sets": {
            name: [fnp.asarray(value) for value in collection]
            for name, collection in inputs["bank_sets"].items()
        },
    }


def banks(repeated, singleton, edge_rs, edge_ss):
    endpoint_a = edge_rs * singleton[None, :]
    endpoint_sum = fnp.sum(endpoint_a, axis=1)
    center_a = repeated * repeated * fnp.maximum(
        endpoint_sum * endpoint_sum - fnp.sum(endpoint_a * endpoint_a, axis=1), 0.0
    )
    left = edge_rs * (repeated * repeated)[:, None]
    right = edge_ss * singleton[:, None]
    left_sum = fnp.sum(left, axis=0)
    right_sum = fnp.sum(right, axis=0)
    center_b = singleton * fnp.maximum(
        left_sum * right_sum - fnp.sum(left * right, axis=0), 0.0
    )
    center_c = center_b + fnp.zeros(WIDTH, dtype=fnp.float32)
    normalizer = fnp.sum(center_a) + fnp.sum(center_b) + fnp.sum(center_c)
    return {
        "endpoint_a": endpoint_a,
        "left": left,
        "right": right,
        "center_a": center_a,
        "center_b": center_b,
        "center_c": center_c,
        "normalizer": normalizer,
    }


def scan_sampler(table, draws, bank_code):
    # Bank and centre CDFs are reusable within a proposal.  Endpoint laws vary
    # by selected centre and therefore have target draw-by-width shape.
    bank_total = fnp.stack(
        (fnp.sum(table["center_a"]), fnp.sum(table["center_b"]), fnp.sum(table["center_c"]))
    )
    bank_cdf = fnp.cumsum(bank_total)
    centre_table = fnp.stack((table["center_a"], table["center_b"], table["center_c"]))
    centre_cdf = fnp.cumsum(centre_table, axis=1)

    centre = fnp.where(bank_code == 0, draws[:, 0], fnp.where(bank_code == 1, draws[:, 1], draws[:, 2]))
    first_label = fnp.where(bank_code == 0, draws[:, 1], draws[:, 0])
    endpoint_a = table["endpoint_a"][centre]
    left = fnp.transpose(table["left"])[centre]
    right = fnp.transpose(table["right"])[centre]
    right_sum = fnp.sum(right, axis=1)
    endpoint_b = left * (right_sum[:, None] - right)
    first = fnp.where((bank_code == 0)[:, None], endpoint_a, endpoint_b)
    first_cdf = fnp.cumsum(first, axis=1)

    exclusion = fnp.eye(WIDTH, dtype=fnp.float32)[first_label]
    second_a = endpoint_a * (1.0 - exclusion)
    second_b = right * (1.0 - exclusion)
    second = fnp.where((bank_code == 0)[:, None], second_a, second_b)
    second_cdf = fnp.cumsum(second, axis=1)
    return (
        bank_cdf[-1]
        + fnp.sum(centre_cdf[:, -1])
        + fnp.sum(first_cdf[:, -1])
        + fnp.sum(second_cdf[:, -1])
    )


def mass_probability(repeated, singleton, edge_rs, edge_ss, table, draws):
    i, j, k = draws[:, 0], draws[:, 1], draws[:, 2]
    mass = repeated[i] * repeated[i] * singleton[j] * singleton[k] * (
        edge_rs[i, j] * edge_rs[i, k]
        + edge_rs[i, j] * edge_ss[j, k]
        + edge_rs[i, k] * edge_ss[j, k]
    )
    uniform = np.float32(0.05 / float(WIDTH * (WIDTH - 1) * (WIDTH - 2)))
    return uniform + np.float32(0.95) * mass / table["normalizer"]


def gram_norm(weight, draws):
    x = weight[draws[:, 0]]
    y = weight[draws[:, 1]]
    z = weight[draws[:, 2]]
    u31 = fnp.stack((6.0 * x * y * z, 3.0 * x * x * z, 3.0 * x * x * y), axis=1)
    v31 = fnp.stack((x, y, z), axis=1)
    u22 = fnp.stack((2.0 * x * x, 2.0 * y * z, 4.0 * x * y, 4.0 * x * z), axis=1)
    v22 = fnp.stack((y * z, x * x, x * z, x * y), axis=1)

    def norm_sq(left, right):
        gram_left = fnp.sum(left[:, :, None, :] * left[:, None, :, :], axis=-1)
        gram_right = fnp.sum(right[:, :, None, :] * right[:, None, :, :], axis=-1)
        return fnp.sum(fnp.sum(gram_left * gram_right, axis=2), axis=1)

    return fnp.sqrt(fnp.maximum(norm_sq(u31, v31) + norm_sq(u22, v22), 0.0))


def fit_fields(draws, magnitude, probability):
    age_np = np.power(31.0 / 32.0, np.arange(PILOT - 1, -1, -1)).astype(np.float32)
    age = fnp.asarray(age_np, dtype=fnp.float32)
    maximum = fnp.max(magnitude)
    log_correction = fnp.log(fnp.maximum(magnitude, np.float32(2.0**-24) * maximum) / probability)
    centre = fnp.sum(age * log_correction) / fnp.sum(age)
    score = fnp.clip((log_correction - centre) / np.float32(math.log(16.0)), -1.0, 1.0)
    signed = age * score
    i, j, k = draws[:, 0], draws[:, 1], draws[:, 2]

    def state(ids, numerator_weight, denominator_weight, size):
        numerator = fnp.bincount(ids, weights=numerator_weight, minlength=size)
        denominator = fnp.bincount(ids, weights=denominator_weight, minlength=size)
        return numerator / (1.0 + denominator)

    g_r = state(i, signed, age, WIDTH)
    singleton_id = fnp.concatenate((j, k))
    g_s = state(singleton_id, fnp.concatenate((signed, signed)), fnp.concatenate((age, age)), WIDTH)
    rs_left = fnp.minimum(fnp.concatenate((i, i)), fnp.concatenate((j, k)))
    rs_right = fnp.maximum(fnp.concatenate((i, i)), fnp.concatenate((j, k)))
    rs_id = rs_left * WIDTH + rs_right
    rs_flat = state(
        rs_id,
        fnp.concatenate((signed, signed)),
        fnp.concatenate((age, age)),
        WIDTH * WIDTH,
    )
    rs_matrix = fnp.reshape(rs_flat, (WIDTH, WIDTH))
    g_rs = rs_matrix + fnp.transpose(rs_matrix)
    ss_left = fnp.minimum(j, k)
    ss_right = fnp.maximum(j, k)
    ss_flat = state(ss_left * WIDTH + ss_right, signed, age, WIDTH * WIDTH)
    ss_matrix = fnp.reshape(ss_flat, (WIDTH, WIDTH))
    g_ss = ss_matrix + fnp.transpose(ss_matrix)
    return g_r, g_s, g_rs, g_ss


def run_baseline(data: dict[str, object]) -> tuple[dict[str, float | int], dict[str, int]]:
    before = memory_counters()
    tracemalloc.start()
    ctx = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
    started = time.perf_counter()
    with ctx:
        identity = fnp.eye(WIDTH, dtype=fnp.float32)
        live = fnp.asarray(0.0, dtype=fnp.float32)
        for layer in range(LAYERS):
            weight = data["weights"][layer]
            row_norm = fnp.sqrt(fnp.sum(weight * weight, axis=1))
            residual = fnp.abs(data["bridges"][layer] - identity)
            table = banks(row_norm, row_norm, residual, residual)
            draws = data["draw_sets"]["baseline"][layer]
            bank = data["bank_sets"]["baseline"][layer]
            live = live + scan_sampler(table, draws, bank)
            live = live + fnp.sum(mass_probability(row_norm, row_norm, residual, residual, table, draws))
        _ = live + fnp.asarray(0.0, dtype=fnp.float32)
    outer = time.perf_counter() - started
    _, python_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    after = memory_counters()
    result = {
        "billed_flops": int(ctx.flops_used),
        "backend_s": float(ctx.flopscope_backend_time_s),
        "overhead_s": float(ctx.flopscope_overhead_time_s),
        "residual_s": float(ctx.residual_wall_time_s or 0.0),
        "outer_wall_s": outer,
    }
    memory = {
        "working_set_before": before["working_set_bytes"],
        "working_set_after": after["working_set_bytes"],
        "peak_working_set": after["peak_working_set_bytes"],
        "python_tracemalloc_peak": int(python_peak),
    }
    return result, memory


def run_candidate(data: dict[str, object]) -> tuple[dict[str, float | int], dict[str, int]]:
    before = memory_counters()
    tracemalloc.start()
    ctx = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
    started = time.perf_counter()
    with ctx:
        identity = fnp.eye(WIDTH, dtype=fnp.float32)
        live = fnp.asarray(0.0, dtype=fnp.float32)
        for layer in range(LAYERS):
            weight = data["weights"][layer]
            source_scale = data["scales"][layer]
            tau = source_scale * fnp.sqrt(fnp.sum(weight * weight, axis=1))
            residual = fnp.abs(data["bridges"][layer] - identity)
            q0_table = banks(tau, tau, residual, residual)

            pilot_draw = data["draw_sets"]["pilot"][layer]
            pilot_bank = data["bank_sets"]["pilot"][layer]
            live = live + scan_sampler(q0_table, pilot_draw, pilot_bank)
            pilot_q = mass_probability(tau, tau, residual, residual, q0_table, pilot_draw)
            pilot_norm = gram_norm(weight, pilot_draw)
            pilot_coefficient = data["coefficients"][layer][:PILOT]
            magnitude = fnp.abs(pilot_coefficient) * pilot_norm

            g_r, g_s, g_rs, g_ss = fit_fields(pilot_draw, magnitude, pilot_q)
            repeated = tau * fnp.exp(np.float32(math.log(2.0)) * g_r)
            singleton = tau * fnp.exp(np.float32(math.log(2.0)) * g_s)
            edge_rs = residual * fnp.exp(np.float32(math.log(2.0)) * g_rs)
            edge_ss = residual * fnp.exp(np.float32(math.log(2.0)) * g_ss)
            qad_table = banks(repeated, singleton, edge_rs, edge_ss)

            main_base_draw = data["draw_sets"]["main_base"][layer]
            main_base_bank = data["bank_sets"]["main_base"][layer]
            main_ad_draw = data["draw_sets"]["main_adaptive"][layer]
            main_ad_bank = data["bank_sets"]["main_adaptive"][layer]
            live = live + scan_sampler(q0_table, main_base_draw, main_base_bank)
            live = live + scan_sampler(qad_table, main_ad_draw, main_ad_bank)

            main_draw = fnp.concatenate((main_base_draw, main_ad_draw), axis=0)
            q0_main = mass_probability(tau, tau, residual, residual, q0_table, main_draw)
            qad_main = mass_probability(repeated, singleton, edge_rs, edge_ss, qad_table, main_draw)
            q1_main = np.float32(0.25) * q0_main + np.float32(0.75) * qad_main
            pilot_scale = pilot_coefficient / (np.float32(2 * TOTAL) * pilot_q)
            main_coefficient = data["coefficients"][layer][PILOT:]
            main_scale = main_coefficient / (np.float32(2 * TOTAL) * q1_main)
            heterogeneous_scale = fnp.concatenate((pilot_scale, main_scale))
            live = live + fnp.sum(heterogeneous_scale) + fnp.sum(q1_main)
        _ = live + fnp.asarray(0.0, dtype=fnp.float32)
    outer = time.perf_counter() - started
    _, python_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    after = memory_counters()
    result = {
        "billed_flops": int(ctx.flops_used),
        "backend_s": float(ctx.flopscope_backend_time_s),
        "overhead_s": float(ctx.flopscope_overhead_time_s),
        "residual_s": float(ctx.residual_wall_time_s or 0.0),
        "outer_wall_s": outer,
    }
    memory = {
        "working_set_before": before["working_set_bytes"],
        "working_set_after": after["working_set_bytes"],
        "peak_working_set": after["peak_working_set_bytes"],
        "python_tracemalloc_peak": int(python_peak),
    }
    return result, memory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("refusing to overwrite an existing trace")

    inputs_np = synthetic_inputs()
    synthetic_input_bytes = 0
    for key in ("weights", "scales", "bridges", "coefficients"):
        synthetic_input_bytes += sum(int(value.nbytes) for value in inputs_np[key])
    for collection in inputs_np["draw_sets"].values():
        synthetic_input_bytes += sum(int(value.nbytes) for value in collection)
    for collection in inputs_np["bank_sets"].values():
        synthetic_input_bytes += sum(int(value.nbytes) for value in collection)
    data = as_flopscope(inputs_np)

    pairs = []
    memories = []
    for _ in range(REPEATS):
        baseline, baseline_memory = run_baseline(data)
        candidate, candidate_memory = run_candidate(data)
        pairs.append({"baseline": baseline, "candidate": candidate})
        memories.append({"baseline": baseline_memory, "candidate": candidate_memory})

    baseline_bills = {int(pair["baseline"]["billed_flops"]) for pair in pairs}
    candidate_bills = {int(pair["candidate"]["billed_flops"]) for pair in pairs}
    if len(baseline_bills) != 1 or len(candidate_bills) != 1:
        raise ArithmeticError("deterministic structural bills changed across repeats")
    baseline_bill = baseline_bills.pop()
    candidate_bill = candidate_bills.pop()
    incremental_bill = max(0, candidate_bill - baseline_bill)
    residual_deltas = [
        max(0.0, float(pair["candidate"]["residual_s"]) - float(pair["baseline"]["residual_s"]))
        for pair in pairs
    ]
    protected_incremental_arithmetic = int(math.ceil(1.25 * incremental_bill))
    protected_residual = 1.0e11 * max(residual_deltas)
    crosswalk_complete = M133_COMPLETE + protected_incremental_arithmetic + protected_residual
    arithmetic_pass = incremental_bill <= ARITHMETIC_GATE
    residual_pass = max(residual_deltas) <= RESIDUAL_GATE_S
    ceiling_pass = crosswalk_complete <= BRANCH_CEILING
    deployment_survives = arithmetic_pass and residual_pass and ceiling_pass

    result = {
        "candidate": "M146 target-shaped proposal structural delta",
        "firewall": "fresh synthetic arrays only; no generated Gaussian state/M131 coefficient call/response/contest data/truth/scorer/submission",
        "shape": {
            "width": WIDTH,
            "layers": LAYERS,
            "total_per_layer": TOTAL,
            "pilot_per_layer": PILOT,
            "main_per_layer": MAIN,
            "main_base_component": MAIN_BASE,
            "main_adaptive_component": MAIN_ADAPTIVE,
        },
        "dtype": "float32",
        "flopscope": getattr(flops, "__version__", "unknown"),
        "numpy": np.__version__,
        "repeats": REPEATS,
        "pairs": pairs,
        "memory": {
            "synthetic_input_bytes": synthetic_input_bytes,
            "paired_measurements": memories,
            "peak_working_set_bytes": max(
                item[phase]["peak_working_set"] for item in memories for phase in ("baseline", "candidate")
            ),
            "peak_python_tracemalloc_bytes": max(
                item[phase]["python_tracemalloc_peak"] for item in memories for phase in ("baseline", "candidate")
            ),
        },
        "scope_included": [
            "M133 replacement baseline proposal banks, target-sized categorical scans, and sampled-q gathers",
            "M146 physical q0 and pilot categorical scans",
            "O(n) batched pilot F31/F22 Gram norm with all rank-one pair reductions",
            "fixed t=1..P fading log scores and node/edge bincount states",
            "role-aware q_ad banks and exact normalizer",
            "25/75 defensive main-component categorical scans",
            "q0/q_ad sampled mass, q1 mixture evaluation, and heterogeneous scale concatenation",
            "serial pilot-before-main Python/call/allocation barrier",
        ],
        "excluded_unchanged": [
            "the same 512 M131 coefficient evaluations already reserved by M133",
            "the same five rectangular source products",
            "M125b carrier/background and hard path/[2,2] samplers",
        ],
        "blocked_until_m147": [
            "generated-state construction",
            "endpoint-safe exact coefficient certification",
            "integrated coefficient-call residual and certificate failure behavior",
        ],
        "crosswalk": {
            "m133_complete_protected": M133_COMPLETE,
            "baseline_replaced_billed": baseline_bill,
            "m146_replacement_billed": candidate_bill,
            "incremental_billed": incremental_bill,
            "incremental_billed_gate": ARITHMETIC_GATE,
            "protected_incremental_arithmetic_1_25": protected_incremental_arithmetic,
            "paired_nonnegative_residual_deltas_s": residual_deltas,
            "max_incremental_residual_s": max(residual_deltas),
            "incremental_residual_gate_s": RESIDUAL_GATE_S,
            "protected_incremental_residual_bill": protected_residual,
            "complete_nonoverlap_protected": crosswalk_complete,
            "branch_ceiling": BRANCH_CEILING,
            "arithmetic_pass": arithmetic_pass,
            "residual_pass": residual_pass,
            "ceiling_pass": ceiling_pass,
            "deployment_survives_structural_gate": deployment_survives,
            "disposition": (
                "STATIC_DEPLOYMENT_COMPONENT_SURVIVES_PENDING_M147_INTEGRATION"
                if deployment_survives
                else "KILL_M146_DEPLOYMENT_CONFIGURATION_PRESERVE_ADAPTIVE_HH_THEOREM"
            ),
        },
        "response_outcome_run": False,
        "native_structural_trace": True,
        "integrated_endpoint_trace": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
