"""Suite-level incumbent: the crowned tier-7 call price applied uniformly across the
champion's production shape -- 32 layers x 15.75 canonical tiles per net-layer.

THE frozen constant of this model IS the uniformity: every layer billed as an anonymous
(4096,256,256) call, the design billed as anonymous rows, W-side transforms re-billed
per tile, pruned shapes billed full. Ladder 2 exists to break exactly that. Run with
cwd = the repo root (relative import of the tier-7 module).
"""
import importlib.util
import sys
from dataclasses import dataclass

_T7_PATH = "corpus/whestbench/headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py"


def _t7():
    spec = importlib.util.spec_from_file_location("t7base", _T7_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


@dataclass(frozen=True)
class SuiteBill:
    strategy: str
    call_total: int
    layers: int
    tiles_per_layer: float
    total: float


def suite_bill_per_net(m=4096, k=256, n=256):
    call = _t7().inplace_verbatim_leaves_candidate_bill(m, k, n).total
    layers, tiles = 32, 64512 / m
    return SuiteBill("uniform_t7_suite", call, layers, tiles, layers * tiles * call)


if __name__ == "__main__":
    b = suite_bill_per_net()
    print(b.strategy, int(b.total))
