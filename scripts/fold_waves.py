"""fold_waves — DAG-parallel scheduling above fold_search.

Cells may declare `depends_on` (cell ids) and `writes` (paths).  This layer
computes topological waves, refuses cycles and same-wave write overlap (the
parallel-write guard), runs independent ready cells concurrently (subprocess
execution in parallel; ledger verdicts strictly serialized), and exports the
cell DAG as graphify-ready node-link JSON.  A dependent cell becomes ready
only when every parent's verdict is PASS_SCREEN — a killed parent ends its
whole downstream line, which is exactly the fold discipline.

Usage:
  python scripts/fold_waves.py plan CELLS_DIR
  python scripts/fold_waves.py ready CELLS_DIR
  python scripts/fold_waves.py run-wave CELLS_DIR --ledger PATH [--workers N]
  python scripts/fold_waves.py export-graph CELLS_DIR --out cells-graph.json
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import fold_search


class DagError(RuntimeError):
    """Cycle or unknown dependency in the cell graph."""


class WriteOverlapError(RuntimeError):
    """Two cells in the same wave declare overlapping write scopes."""


def _load_cells(cells_dir: Path) -> dict:
    cells = {}
    for pd_path in sorted(Path(cells_dir).glob("*/predeclaration.json")):
        pd = json.loads(pd_path.read_text(encoding="utf-8"))
        cells[pd["id"]] = {"dir": pd_path.parent, "pd": pd}
    return cells


def _paths_overlap(a: str, b: str) -> bool:
    pa, pb = Path(a).resolve(), Path(b).resolve()
    return pa == pb or pa in pb.parents or pb in pa.parents


def plan(cells_dir) -> list:
    """Topological waves over all cells; validates deps and write scopes."""
    cells = _load_cells(Path(cells_dir))
    deps = {}
    for cid, cell in cells.items():
        dlist = cell["pd"].get("depends_on", [])
        unknown = [d for d in dlist if d not in cells]
        if unknown:
            raise DagError(f"cell {cid!r} depends on unknown {unknown}")
        deps[cid] = set(dlist)

    waves, remaining = [], dict(deps)
    while remaining:
        ready = sorted(c for c, d in remaining.items() if not d)
        if not ready:
            raise DagError(f"dependency cycle among {sorted(remaining)}")
        for wave_i, a in enumerate(ready):
            for b in ready[wave_i + 1:]:
                for wa in cells[a]["pd"].get("writes", []):
                    for wb in cells[b]["pd"].get("writes", []):
                        if _paths_overlap(wa, wb):
                            raise WriteOverlapError(
                                f"cells {a!r} and {b!r} would run in the same "
                                f"wave and both write {wa!r} / {wb!r}")
        waves.append(ready)
        for c in ready:
            del remaining[c]
        for d in remaining.values():
            d.difference_update(ready)
    return waves


def _cell_status(cell_dir: Path) -> str:
    vpath = cell_dir / "verdict.json"
    if vpath.exists():
        return json.loads(vpath.read_text("utf-8"))["verdict"]
    rpath = cell_dir / "report.json"
    if rpath.exists():
        return json.loads(rpath.read_text("utf-8"))["outcome"]
    return "predeclared"


def ready_cells(cells_dir) -> list:
    """Cells whose one-shot is unspent and whose parents all PASS_SCREEN."""
    cells = _load_cells(Path(cells_dir))
    out = []
    for cid, cell in cells.items():
        if not (cell["dir"] / "GATE_TOKEN").exists():
            continue  # consumed or absent: never re-runnable
        parents = cell["pd"].get("depends_on", [])
        if all(_cell_status(cells[p]["dir"]) == "PASS_SCREEN"
               for p in parents if p in cells) and \
           all(p in cells for p in parents):
            out.append(cid)
    return sorted(out)


def run_wave(cells_dir, ids, ledger_path, workers: int = 4) -> list:
    """Execute the given cells in parallel; verdict them serially."""
    cells = _load_cells(Path(cells_dir))
    targets = [cells[c]["dir"] for c in ids]
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        list(pool.map(fold_search.run, targets))
    # The ledger is append-only and single-writer: verdicts never race.
    return [fold_search.verdict(t, ledger_path) for t in targets]


def export_graph(cells_dir, out_path) -> dict:
    """Node-link JSON of the search DAG, ready for graphify overlay/viz."""
    cells = _load_cells(Path(cells_dir))
    nodes, links = [], []
    for cid, cell in sorted(cells.items()):
        nodes.append({
            "id": cid,
            "label": cell["pd"]["hypothesis"][:80],
            "type": "search_cell",
            "status": _cell_status(cell["dir"]),
            "evidence_role": cell["pd"]["evidence_role"],
            "community": None,
        })
        for parent in cell["pd"].get("depends_on", []):
            links.append({"source": parent, "target": cid,
                          "relation": "unblocks", "confidence": "EXTRACTED",
                          "confidence_score": 1.0})
    data = {"directed": True, "multigraph": False,
            "graph": {"kind": "fold_search_cell_dag"},
            "nodes": nodes, "links": links}
    Path(out_path).write_text(json.dumps(data, indent=2, sort_keys=True),
                              encoding="utf-8")
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "ready"):
        p = sub.add_parser(name); p.add_argument("cells")
    r = sub.add_parser("run-wave"); r.add_argument("cells")
    r.add_argument("--ledger", required=True)
    r.add_argument("--workers", type=int, default=4)
    e = sub.add_parser("export-graph"); e.add_argument("cells")
    e.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    if ns.cmd == "plan":
        print(json.dumps(plan(ns.cells)))
    elif ns.cmd == "ready":
        print(json.dumps(ready_cells(ns.cells)))
    elif ns.cmd == "run-wave":
        ids = ready_cells(ns.cells)
        print(json.dumps(run_wave(ns.cells, ids, ns.ledger, ns.workers),
                         indent=2))
    elif ns.cmd == "export-graph":
        data = export_graph(ns.cells, ns.out)
        print(f"{len(data['nodes'])} cells, {len(data['links'])} edges -> {ns.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
