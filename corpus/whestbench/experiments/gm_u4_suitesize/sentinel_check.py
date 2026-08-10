#!/usr/bin/env python
"""Positive control for the gm_u4_suitesize KILL.

The verdict is an ABSENCE claim ("no committed source states the private
re-evaluation suite size"). An absence claim is worthless unless the detector
would have fired on a presence. This script feeds the SAME Signal-A patterns
and the SAME Signal-B window logic used by scan_u4.py a set of synthetic
resolving sentences (which MUST all be detected) and a set of near-miss
non-resolving sentences (which are allowed to be detected -- Signal A/B are
deliberately over-inclusive, so the real discipline is hand adjudication; what
must not happen is a MISS on a true positive).

It also writes a real sentinel FILE into this experiment directory and runs the
same file-level scan over it, so the detection is proved end-to-end on disk and
not only on in-memory strings.
"""
import json
import os
import re

import scan_u4 as S

OUT = os.path.dirname(os.path.abspath(__file__))

TRUE_POSITIVES = [
    "The Private Re-evaluation is run on a fresh, never-seen suite of 100 MLPs "
    "generated from private seeds.",
    "Rules v12 5.4: the private re-evaluation suite contains 50 MLPs.",
    "Each designated submission is rerun on 100 fresh unseen networks.",
    "the private rerun uses a 100-net suite",
    "Number of nets in the private re-evaluation: 100.",
    "suite size for the September re-run is 50",
    "The held-out re-evaluation set comprises 200 MLPs.",
    "prize ranking comes from a rerun over 100 private MLPs",
]

NEAR_MISSES = [
    "Phase-end standings use all 100 MLPs (50 public + 50 private).",
    "the live score is only the 50-MLP public half",
    "This re-run produces the final (private) leaderboard on a separate, "
    "fresh, never-seen test suite generated from private seeds.",
    "Fresh private rerun of each team's up to two nominated submissions.",
]


def a_hits(text):
    out = []
    for name, pat in S.A_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            out.append((name, m.group(0)))
    return out


def b_hits(text):
    out = []
    for m in S.KW_RE.finditer(text):
        w = text[max(0, m.start() - S.WIN):m.end() + S.WIN]
        for nm in S.NUM_RE.finditer(w):
            out.append((m.group(0), int(nm.group(0))))
    return out


def main():
    res = {"true_positives": [], "near_misses": [], "misses": []}
    for s in TRUE_POSITIVES:
        a, b = a_hits(s), b_hits(s)
        rec = {"sentence": s, "signalA": [x[0] for x in a],
               "signalB_numbers": sorted(set(n for _, n in b))}
        res["true_positives"].append(rec)
        if not a and not b:
            res["misses"].append(s)
    for s in NEAR_MISSES:
        a, b = a_hits(s), b_hits(s)
        res["near_misses"].append({"sentence": s, "signalA": [x[0] for x in a],
                                   "signalB_numbers": sorted(set(n for _, n in b))})

    # end-to-end on-disk sentinel
    sp = os.path.join(OUT, "SENTINEL_SYNTHETIC.md")
    with open(sp, "w", encoding="utf-8") as f:
        f.write("# SYNTHETIC SENTINEL -- NOT A SOURCE, NOT EVIDENCE\n\n"
                "Fabricated line, written by sentinel_check.py purely to prove\n"
                "the scanner detects a resolving statement when one exists:\n\n"
                "Rules v12 5.4: the Private Re-evaluation is run on a fresh,\n"
                "never-seen suite of 137 MLPs generated from private seeds.\n")
    txt = open(sp, encoding="utf-8").read()
    a, b = a_hits(txt), b_hits(txt)
    res["ondisk_sentinel"] = {
        "path": os.path.relpath(sp, S.REPO),
        "signalA_patterns_fired": sorted(set(x[0] for x in a)),
        "signalA_matches": [x[1][:160] for x in a],
        "signalB_found_137": 137 in set(n for _, n in b),
        "detected": bool(a) and 137 in set(n for _, n in b),
    }
    res["all_true_positives_detected"] = not res["misses"]
    res["n_true_positives"] = len(TRUE_POSITIVES)
    res["n_missed"] = len(res["misses"])
    json.dump(res, open(os.path.join(OUT, "sentinel_results.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
