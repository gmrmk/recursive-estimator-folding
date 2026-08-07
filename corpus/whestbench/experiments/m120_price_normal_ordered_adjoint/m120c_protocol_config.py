"""Immutable, prospective configuration for the M120C component falsifier.

The numeric namespaces are declared here before any M120C network is sampled.
They do not reuse the earlier exploratory PCG streams and must not be selected,
extended, or retried from a measured outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class M120CConfig:
    protocol_id: str
    widths: tuple[int, ...]
    depths: tuple[int, ...]
    replicas_per_cell: int
    network_bit_generator: str
    network_root_seed: int
    network_seeds: dict[tuple[int, int], tuple[int, ...]]
    direction_bit_generator: str
    direction_root_seed: int
    direction_count: int
    global_mean_limit: float
    cell_worst_output_limit: float
    fail_closed_floor: float
    output_path: str
    manifest_path: str
    execution_mode: str
    atomic_no_retry_claim: bool


# `M120C-NET-v1` is a simple public arithmetic namespace: root + 100000*width
# + 1000*depth + replica.  The nine tuples below are written out deliberately;
# the binding grid is 3 widths * 3 depths * 3 Philox networks = 27 networks.
NETWORK_SEEDS: dict[tuple[int, int], tuple[int, ...]] = {
    (8, 2): (2_026_882_700, 2_026_882_701, 2_026_882_702),
    (8, 3): (2_026_883_700, 2_026_883_701, 2_026_883_702),
    (8, 4): (2_026_884_700, 2_026_884_701, 2_026_884_702),
    (12, 2): (2_027_282_700, 2_027_282_701, 2_027_282_702),
    (12, 3): (2_027_283_700, 2_027_283_701, 2_027_283_702),
    (12, 4): (2_027_284_700, 2_027_284_701, 2_027_284_702),
    (16, 2): (2_027_682_700, 2_027_682_701, 2_027_682_702),
    (16, 3): (2_027_683_700, 2_027_683_701, 2_027_683_702),
    (16, 4): (2_027_684_700, 2_027_684_701, 2_027_684_702),
}


CONFIG = M120CConfig(
    protocol_id="M120C-EXACT-PREEXEC-v1",
    widths=(8, 12, 16),
    depths=(2, 3, 4),
    replicas_per_cell=3,
    network_bit_generator="Philox",
    network_root_seed=2_026_080_700,
    network_seeds=NETWORK_SEEDS,
    direction_bit_generator="Philox",
    # Independent `M120C-DIR-v1` namespace, with no output index in its seed.
    direction_root_seed=2_026_180_701,
    direction_count=4,
    global_mean_limit=0.05,
    cell_worst_output_limit=0.10,
    fail_closed_floor=1e-10,
    output_path=str(HERE / "out" / "M120C_EXACT_GENERATED_OUTCOME" / "m120c_binding_result.json"),
    manifest_path=str(HERE / "m120c_protocol_manifest.json"),
    execution_mode="OPERATIONAL_AWAITING_EXTERNAL_MANIFEST",
    atomic_no_retry_claim=True,
)


def network_seed(width: int, depth: int, replica: int) -> int:
    """Return one already-frozen Philox network seed or reject the request."""

    if replica < 0 or replica >= CONFIG.replicas_per_cell:
        raise ValueError("replica outside the frozen M120C range")
    try:
        return CONFIG.network_seeds[(int(width), int(depth))][int(replica)]
    except KeyError as error:
        raise ValueError("width/depth outside the frozen M120C grid") from error


def directional_seed(width: int, depth: int, layer: int, direction: int) -> int:
    """Return a Philox seed from the independent, outcome-free direction namespace."""

    if width not in CONFIG.widths or depth not in CONFIG.depths:
        raise ValueError("width/depth outside the frozen M120C grid")
    if layer < 0 or layer >= depth - 1:
        raise ValueError("layer outside the frozen hidden-ReLU range")
    if direction < 0 or direction >= CONFIG.direction_count:
        raise ValueError("direction outside the frozen M120C range")
    return (
        CONFIG.direction_root_seed
        + 10_000 * int(width)
        + 1_000 * int(depth)
        + 100 * int(layer)
        + int(direction)
    )
