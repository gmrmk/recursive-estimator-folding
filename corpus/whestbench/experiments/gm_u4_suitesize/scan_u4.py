#!/usr/bin/env python
"""gm_u4_suitesize -- falsifier harness for graveyard revival of ledger record U4
(private re-evaluation suite size, 50 vs 100 nets).

Read-only. No network. No git. Writes only into this experiment directory.

Structure (matches PREDECLARATION.md):
  STEP 0  arithmetic gate on the changed premise, recomputed from
          s1b_dispersion_corrected/s1b_results.json (machine file, not prose).
          If it fails, we stop and report KILLED_AT_STEP0.
  SIGNAL A  keyword-driven regex scan (suite/net/MLP-count phrasings).
  SIGNAL B  independent number-driven scan (numbers in a +/-120 char window of
            private/held-out/fresh/suite vocabulary). Different logic from A.
  SIGNAL C  every sentence with "50" adjacent to MLP/suite (public-vs-private
            adjudication on quotes).
  COVERAGE  file count + byte count actually read, so "full read" is auditable.
"""
import json
import os
import re
import sys
import hashlib

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- firewall
# Held lane: never opened. Also skip our own output dir so the scan cannot
# read its own findings back in.
HELD = re.compile(r"(^|[\\/])(m243|m244|m245)[^\\/]*([\\/]|$)|journal-m245", re.I)
SELF = os.path.basename(OUT)
SKIP_DIRS = {".git", "__pycache__", ".maestro", SELF}
TEXT_EXT = {".md", ".txt", ".py", ".json", ".jsonl", ".log", ".err", ".out",
            ".yml", ".yaml", ".ps1", ".sha256", ".tag", ".bak", ".html", ""}
BIN_EXT = {".npz", ".gz", ".pdf", ".pyc", ".png", ".jpg", ".tar"}


def in_scope_files():
    kept, skipped_held, skipped_bin = [], [], []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs
                   if d not in SKIP_DIRS and not HELD.search(d)]
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, REPO)
            if HELD.search(rel):
                skipped_held.append(rel)
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext in BIN_EXT:
                skipped_bin.append(rel)
                continue
            if ext not in TEXT_EXT:
                skipped_bin.append(rel)
                continue
            kept.append(rel)
    return sorted(kept), sorted(skipped_held), sorted(skipped_bin)


# ---------------------------------------------------------------- step 0
def step0():
    p = os.path.join(REPO, "corpus", "whestbench", "experiments",
                     "s1b_dispersion_corrected", "s1b_results.json")
    d = json.load(open(p, encoding="utf-8"))
    out = {"source": os.path.relpath(p, REPO), "arms": {}}
    ok_a, ok_b = True, True
    for arm in ("s17_low", "s17_high"):
        a = d["arms"][arm]
        t50, t100 = a["tail_50"], a["tail_100"]
        p_above_50 = t50["p_above_2p5em7"]["value"]
        p_above_100 = t100["p_above_2p5em7"]["value"]
        p16_50 = t50["p_below"]["1.60e-07"]["value"]
        p16_100 = t100["p_below"]["1.60e-07"]["value"]
        r_a = p_above_50 / p_above_100
        r_b = p16_50 / p16_100
        # independent recomputation of the same ratio from the complement of
        # P(<2.5e-7): a second way to get the tail mass out of the same file.
        alt_50 = 1.0 - t50["p_below"]["2.50e-07"]["value"]
        alt_100 = 1.0 - t100["p_below"]["2.50e-07"]["value"]
        out["arms"][arm] = {
            "vD": a["vD"],
            "n_suites_tail": t50["n_suites"],
            "P_above_2.5e-7_50net": p_above_50,
            "P_above_2.5e-7_50net_se": t50["p_above_2p5em7"]["se"],
            "P_above_2.5e-7_100net": p_above_100,
            "P_above_2.5e-7_100net_se": t100["p_above_2p5em7"]["se"],
            "ratio_G0a": r_a,
            "P_below_1.6e-7_50net": p16_50,
            "P_below_1.6e-7_100net": p16_100,
            "ratio_G0b": r_b,
            "crosscheck_1_minus_Pbelow_2.5e-7_50net": alt_50,
            "crosscheck_1_minus_Pbelow_2.5e-7_100net": alt_100,
            "crosscheck_abs_err_50": abs(alt_50 - p_above_50),
            "crosscheck_abs_err_100": abs(alt_100 - p_above_100),
            "analytic_sd_ratio_50": t50["sd"] / t50["sd_analytic"],
            "analytic_sd_ratio_100": t100["sd"] / t100["sd_analytic"],
        }
        ok_a = ok_a and r_a >= 10.0
        ok_b = ok_b and r_b >= 2.0
    out["G0a_ratio_ge_10x_both_arms"] = ok_a
    out["G0b_ratio_ge_2x_both_arms"] = ok_b
    out["step0_pass"] = bool(ok_a and ok_b)
    return out


# ---------------------------------------------------------------- signal A
A_PATTERNS = [
    ("A1_private_then_count",
     r"(private|held[\s-]?out|holdout|hidden|unseen|fresh|re-?run|re-?eval\w*)"
     r"[^.\n]{0,160}?\b(\d{1,4})\b[^.\n]{0,40}\b(nets?|mlps?|models?|suite)"),
    ("A2_count_then_private",
     r"\b(\d{1,4})[\s-]?(nets?|mlps?|models?)\b[^.\n]{0,100}"
     r"(private|held[\s-]?out|holdout|hidden|unseen|fresh|re-?run|re-?eval\w*)"),
    ("A3_suite_size_literal",
     r"suite[\s-]?(size|of|has|contains|comprises|is)\b[^.\n]{0,30}\b\d{1,4}\b"),
    ("A4_n_net_suite",
     r"\b\d{1,4}[\s-]?(net|mlp|model)s?[\s-]+(suite|set|benchmark|half|pool)"),
    ("A5_number_of_nets",
     r"(number|count)\s+of\s+(nets?|mlps?|models?)[^.\n]{0,40}\b\d{1,4}\b"),
]

KW = ("suite", "mlp", "net", "model", "private", "held-out", "held out",
      "holdout", "hidden", "unseen", "fresh", "re-run", "rerun",
      "re-evaluat", "re-eval", "reevaluat")
KW_RE = re.compile("|".join(re.escape(k) for k in KW), re.I)
NUM_RE = re.compile(r"\b\d{1,4}\b")
WIN = 120

C_RE = re.compile(r"[^.\n]{0,140}\b50\b[^.\n]{0,60}\b(mlp|suite|net)s?\b[^.\n]{0,80}"
                  r"|[^.\n]{0,80}\b(mlp|suite|net)s?\b[^.\n]{0,60}\b50\b[^.\n]{0,140}", re.I)


def scan():
    files, held, binf = in_scope_files()
    a_hits, b_hits, c_hits = [], [], []
    nbytes = 0
    nread = 0
    unread = []
    for rel in files:
        p = os.path.join(REPO, rel)
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except Exception as e:                      # pragma: no cover
            unread.append([rel, repr(e)])
            continue
        nread += 1
        nbytes += len(txt)
        low = txt.lower()
        # cheap prefilter for A/C only when the file mentions any keyword
        if not KW_RE.search(low):
            continue
        for name, pat in A_PATTERNS:
            for m in re.finditer(pat, txt, re.I):
                s = max(0, m.start() - 60)
                a_hits.append({"file": rel, "pattern": name,
                               "line": txt.count("\n", 0, m.start()) + 1,
                               "match": m.group(0)[:220],
                               "context": txt[s:m.end() + 60].replace("\n", " ")[:340]})
        for m in KW_RE.finditer(txt):
            s = max(0, m.start() - WIN)
            e = min(len(txt), m.end() + WIN)
            w = txt[s:e]
            for nm in NUM_RE.finditer(w):
                b_hits.append({"file": rel,
                               "line": txt.count("\n", 0, m.start()) + 1,
                               "kw": m.group(0),
                               "num": int(nm.group(0)),
                               "context": w.replace("\n", " ")[:280]})
        for m in C_RE.finditer(txt):
            c_hits.append({"file": rel,
                           "line": txt.count("\n", 0, m.start()) + 1,
                           "sentence": m.group(0).replace("\n", " ")[:300]})
    return {
        "files_in_scope": len(files),
        "files_read": nread,
        "bytes_read": nbytes,
        "files_unreadable": unread,
        "files_skipped_held_lane": held,
        "n_files_skipped_binary": len(binf),
        "files_skipped_binary_sample": binf[:20],
        "file_list_sha256": hashlib.sha256(
            "\n".join(files).encode("utf-8")).hexdigest(),
    }, a_hits, b_hits, c_hits


def main():
    res = {"experiment": "gm_u4_suitesize",
           "repo_root": REPO,
           "python": sys.version}
    res["step0"] = step0()
    print("STEP 0:", json.dumps(res["step0"], indent=1))
    if not res["step0"]["step0_pass"]:
        res["status"] = "KILLED_AT_STEP0"
        json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
        print("STEP 0 KILL -- stopping as predeclared.")
        return
    cov, a, b, c = scan()
    res["coverage"] = cov
    res["signalA_n_hits"] = len(a)
    res["signalB_n_hits"] = len(b)
    res["signalC_n_hits"] = len(c)
    with open(os.path.join(OUT, "signalA_hits.json"), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=1)
    with open(os.path.join(OUT, "signalB_hits.json"), "w", encoding="utf-8") as f:
        json.dump(b, f, indent=1)
    with open(os.path.join(OUT, "signalC_hits.json"), "w", encoding="utf-8") as f:
        json.dump(c, f, indent=1)
    # number histogram from signal B, restricted to the "suite-ish" keywords
    hist = {}
    for h in b:
        if h["kw"].lower() in ("suite", "private", "unseen", "fresh", "holdout",
                               "held-out", "held out", "hidden", "re-run",
                               "rerun", "re-evaluat", "re-eval", "reevaluat"):
            hist[h["num"]] = hist.get(h["num"], 0) + 1
    res["signalB_number_histogram_suitewords"] = dict(
        sorted(hist.items(), key=lambda kv: -kv[1])[:40])
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "coverage"}, indent=1)[:3000])
    print("COVERAGE:", json.dumps({k: v for k, v in cov.items()
                                   if not k.startswith("files_skipped")}, indent=1))


if __name__ == "__main__":
    main()
