#!/usr/bin/env python3
"""Derive shared obstructions across the failure-salvage atlas.

The GEN6 atlas records, per candidate, *why it died* -- `failed_link` is 86%
unique and `kill_condition` 99% unique across 223 records. What it does not
record is *what would bring a candidate back*: `reopening_condition` is one
identical generic sentence on 177 of 223 records (79%), and the coarsest
failure boundary, `approximation_or_materiality`, is attached to 210 of 223
(94%), so neither field separates candidates.

This script adds the missing half. It groups candidates by the *specific*
obstruction their recorded evidence names, so that a new result can be asked a
question the atlas cannot answer: **which corpses does this revive, and which
open branches does it kill unopened?**

Descriptive only. An obstruction grouping is a search index over recorded
text, not evidence, and never promotes, revives, or kills anything by itself.
Every grouping is a hypothesis to be checked against the cited record.

## Measured reliability -- read before trusting any count

This matcher is a triage index, not a classifier, and its error rates were
measured rather than assumed:

- Against the atlas's own record text (thin: `failed_link` is often a single
  clause), **88 of 161 killed records (55%) match no obstruction at all**,
  including `latent_gate_aligned_split`, `latent_full_sigma`, and
  `latent_factor_rank3` -- all three of which are documented elsewhere as
  dying of width dilution. The atlas is derived from the fold ledger, and the
  ledger's per-record text is much thinner than the experiment reports, so the
  evidence needed for grouping is not in the artifact being grouped.
- Against the experiment reports (rich), coverage rises to 75% but precision
  falls: `residual_wall_allocation` matches 41% of 374 reports, because words
  like "buffer" and "allocation" appear in almost any long report.

So: **the obstruction statements below are the useful output; the counts are
not.** Use this to generate candidate groupings for a human or model to check
against the cited records. Do not cite a count from this script as evidence.
The corpse-by-corpse assignments that survived checking are recorded in
`corpus/whestbench/core/GRAVEYARD_RUN.md`.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATLAS = ROOT / "corpus" / "whestbench" / "headroom" / "GEN6_FAILURE_SALVAGE_ATLAS_20260809.json"

# Each obstruction is a specific mechanism named in the corpus, not a generic
# outcome category. Patterns are matched against the union of the record's
# free-text fields. Keep these conservative: a false grouping is worse than an
# unassigned record, so unassigned records are reported rather than forced.
OBSTRUCTIONS: dict[str, dict] = {
    "width_dilution": {
        "statement": "A fixed-dimensional summary of an n-dimensional state captures a "
                     "share that vanishes as width grows (O(1/n) coordinate dilution, "
                     "trace-share collapse).",
        "patterns": [r"o\(1/n\)", r"dilut", r"trace share", r"width law",
                     r"scale homogeneity", r"vanish\w* (?:share|with width)",
                     r"n4\s*->\s*n256", r"88\.4%"],
    },
    "four_point_vertex": {
        "statement": "The missing information is the connected finite-width four-point "
                     "vertex / terminal k3-k4 content, which no second-order state supplies.",
        "patterns": [r"four-point", r"\bvertex\b", r"\bk3\b", r"\bk4\b", r"cumulant",
                     r"non-?gaussian", r"\bskew", r"kurtos"],
    },
    "sign_transport": {
        "statement": "Local correction magnitude is recoverable but its transported sign "
                     "or direction is not stable downstream.",
        "patterns": [r"sign(?:s|ed)? (?:revers|flip|vary|instab|transfer)", r"cosine -",
                     r"reversed sign", r"\bicc\b", r"coefficient sign",
                     r"sign-transfer", r"orientation but"],
    },
    "superlinear_state_cost": {
        "statement": "The exact state or its formation grows as n^3-n^5 (or GiB-scale "
                     "memory), so what is affordable at screen width is impossible at n=256.",
        "patterns": [r"o\(n\^?[345]\)", r"o\(n[345]\)", r"o\(ln\^?4\)", r"o\(p3\)",
                     r"\btrillion\b", r"1\.855t", r"\bgib\b", r"dense (?:pair|tensor|exact|route)"],
    },
    "psd_or_conditioning": {
        "statement": "The propagated second-order state loses positive definiteness or "
                     "conditions badly, and the guard either refuses or fails to notice.",
        "patterns": [r"\bpsd\b", r"positive[- ]semi", r"condition(?:ed|ing|s)? above",
                     r"ill-conditioned", r"\bsingular\b", r"fail-?closed", r"non-?finite",
                     r"min eig", r"spectral psd"],
    },
    "not_closed_under_relu": {
        "statement": "The carried state is not closed under the next ReLU: it is "
                     "re-Gaussianized, recompressed, or projected away before it can act.",
        "patterns": [r"not closed", r"survive the next", r"re-?gaussian", r"reclosure",
                     r"washes? the effect", r"erases? (?:its|the|\d+%)", r"projected away",
                     r"tumbl"],
    },
    "residual_wall_allocation": {
        "statement": "Billed arithmetic is reduced but effective compute is not, because "
                     "allocation, temporaries, or call tails dominate the residual charge.",
        "patterns": [r"allocation", r"temporar", r"residual wall", r"call tail",
                     r"buffer", r"effective (?:compute|prox)"],
    },
    "no_exact_mean_control": {
        "statement": "A control variate needs an analytically known mean for arbitrary "
                     "weights; the candidate supplies only an approximate or constant mean.",
        "patterns": [r"exact mean", r"known expectation", r"nonidentif", r"underidentif",
                     r"does not identify", r"no right-hand side", r"\bblind\b",
                     r"anchor residual", r"approximate mean"],
    },
}

TEXT_FIELDS = ("failed_link", "kill_condition", "prediction", "passed_tissue",
               "reopening_condition")


def record_text(rec: dict) -> str:
    parts: list[str] = [rec.get("id", "")]
    for f in TEXT_FIELDS:
        v = rec.get(f)
        if isinstance(v, list):
            parts.extend(str(x) for x in v)
        elif v:
            parts.append(str(v))
    return " \n ".join(parts).lower()


def assign(rec: dict) -> list[str]:
    text = record_text(rec)
    hits = []
    for name, spec in OBSTRUCTIONS.items():
        if any(re.search(p, text) for p in spec["patterns"]):
            hits.append(name)
    return hits


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    ap.add_argument("--status", default="killed_or_closed",
                    help="canonical_status to analyze; 'all' for every record")
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()

    atlas = json.loads(args.atlas.read_text(encoding="utf-8"))
    recs = atlas["records"]
    if args.status != "all":
        recs = [r for r in recs if r["canonical_status"] == args.status]

    by_obs: dict[str, list[str]] = defaultdict(list)
    per_rec: dict[str, list[str]] = {}
    for r in recs:
        hits = assign(r)
        per_rec[r["id"]] = hits
        for h in hits:
            by_obs[h].append(r["id"])

    unassigned = [i for i, h in per_rec.items() if not h]
    print(f"records analyzed: {len(recs)} (status={args.status})")
    print(f"unassigned (no specific obstruction matched): {len(unassigned)} "
          f"({100*len(unassigned)/len(recs):.0f}%)\n")

    print(f"{'obstruction':<26} {'records':>8} {'share':>7}")
    print("-" * 44)
    for name in sorted(by_obs, key=lambda k: -len(by_obs[k])):
        n = len(by_obs[name])
        print(f"{name:<26} {n:>8} {100*n/len(recs):>6.0f}%")

    print("\nCo-occurrence (records sharing both obstructions):")
    names = sorted(by_obs)
    pairs = Counter()
    for hits in per_rec.values():
        for i, a in enumerate(hits):
            for b in hits[i + 1:]:
                pairs[tuple(sorted((a, b)))] += 1
    for (a, b), n in pairs.most_common(10):
        print(f"  {n:>4}  {a} + {b}")

    print("\nMulti-obstruction records (a kill that is really several):")
    multi = sorted(((len(h), i) for i, h in per_rec.items() if len(h) >= 4), reverse=True)
    for k, i in multi[:10]:
        print(f"  {k}  {i}: {', '.join(per_rec[i])}")

    if unassigned:
        print(f"\nUnassigned records (first 15 of {len(unassigned)}) -- these need "
              f"either a new obstruction or a richer record:")
        for i in unassigned[:15]:
            print(f"  {i}")

    if args.json_out:
        payload = {
            "schema_version": 1,
            "source_atlas_sha256": atlas.get("ledger_sha256"),
            "status_filter": args.status,
            "obstructions": {
                k: {"statement": v["statement"], "records": sorted(by_obs.get(k, []))}
                for k, v in OBSTRUCTIONS.items()
            },
            "unassigned": sorted(unassigned),
            "per_record": {k: sorted(v) for k, v in sorted(per_rec.items())},
        }
        args.json_out.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n",
                                 encoding="utf-8")
        print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
