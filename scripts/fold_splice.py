"""fold_splice — the mutation chamber's mechanical half.

Enumerates splice candidates from the GEN6 failure-salvage atlas: pairs of
records that both carry real PASSED TISSUE, share at least one operator
family (composability), and failed on different primary boundaries (the
hypothesis being that A's surviving component does not live where B died).

This module PROPOSES ONLY.  It never revives a kill: both parents' reopening
constraints ride along on every stub, sentinel records ("No passed component
is asserted") can never be parents, and every stub must still clear judgment
plus a full fold_search predeclaration before anything runs.  Machine
enumerates; agents judge; the harness gates.

Usage:
  python scripts/fold_splice.py propose --atlas PATH [--out PATH] [--top N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SENTINEL_PREFIX = "No passed component"


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _real_tissue(record: dict) -> list:
    tissue = [t for t in record.get("passed_tissue", [])
              if not str(t).startswith(SENTINEL_PREFIX)]
    return tissue


def _primary_boundary(record: dict) -> str:
    bounds = record.get("failure_boundaries", [])
    return bounds[0] if bounds else ""


def propose(atlas_path, out_path=None, top: int = 25) -> list:
    atlas = json.loads(Path(atlas_path).read_text(encoding="utf-8"))
    parents = []
    for record in atlas["records"]:
        tissue = _real_tissue(record)
        if tissue:
            parents.append((record, tissue))

    stubs = []
    for i, (ra, ta) in enumerate(parents):
        for rb, tb in parents[i + 1:]:
            shared = sorted(set(ra.get("operator_families", []))
                            & set(rb.get("operator_families", [])))
            if not shared:
                continue
            if _primary_boundary(ra) == _primary_boundary(rb):
                continue
            disjoint = sorted(
                set(ra.get("failure_boundaries", []))
                ^ set(rb.get("failure_boundaries", [])))
            a, b = sorted([ra["id"], rb["id"]])
            score = (len(shared), len(disjoint), min(len(ta), len(tb)))
            stubs.append({
                "splice_id": f"splice_{a}__{b}",
                "parents": [a, b],
                "shared_families": shared,
                "disjoint_boundaries": disjoint,
                "tissue": {ra["id"]: ta, rb["id"]: tb},
                "failed_links": {ra["id"]: ra.get("failed_link", []),
                                 rb["id"]: rb.get("failed_link", [])},
                "reopening_constraints": sorted(
                    set(ra.get("reopening_condition", []))
                    | set(rb.get("reopening_condition", []))),
                "hypothesis_skeleton": (
                    f"Compose the passed tissue of {a} with the passed tissue "
                    f"of {b}: their failures lie on different primary "
                    f"boundaries ({_primary_boundary(ra)!r} vs "
                    f"{_primary_boundary(rb)!r}), so the composite may route "
                    f"around both first breaks. Must clear judgment plus a "
                    f"full fold_search predeclaration."),
                "note": ("splice composes passed tissue only and never "
                         "revives either parent's kill"),
                "rank_score": score,
            })

    stubs.sort(key=lambda s: (tuple(-x for x in s["rank_score"]),
                              s["splice_id"]))
    for s in stubs:
        s["rank_score"] = list(s["rank_score"])
    stubs = stubs[:top]

    if out_path is not None:
        Path(out_path).write_text(json.dumps({
            "atlas_sha256": sha256_file(atlas_path),
            "proposals": stubs,
        }, indent=2, sort_keys=True), encoding="utf-8")
    return stubs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("propose")
    p.add_argument("--atlas", required=True)
    p.add_argument("--out")
    p.add_argument("--top", type=int, default=25)
    ns = ap.parse_args(argv)
    stubs = propose(ns.atlas, out_path=ns.out, top=ns.top)
    print(f"{len(stubs)} splice proposals" + (f" -> {ns.out}" if ns.out else ""))
    for s in stubs[:5]:
        print(f"  {s['splice_id']}  families={s['shared_families']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
