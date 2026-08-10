#!/usr/bin/env python
"""Second-signal verification for gm_u4_suitesize, appended to results.json.

1. sqrt(N) structural check on step 0: the only thing that differs between the
   50-net and 100-net arms is N, so SD_50/SD_100 must equal sqrt(2) = 1.414214.
   If it does not, the two arms differ by something other than suite size and
   the step-0 gate is measuring the wrong thing.
2. Independent closed-form recomputation of both SDs from
   S*sqrt((vD + (1+vD)*vF)/N) using only the committed vD, vF and anchor --
   no bootstrap number reused.
3. Adjudication ledger for the document search: every candidate hit that a
   human read, with the disposition and the reason.
"""
import json
import math
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))
S1B = os.path.join(REPO, "corpus", "whestbench", "experiments",
                   "s1b_dispersion_corrected", "s1b_results.json")

d = json.load(open(S1B, encoding="utf-8"))
vF = d["calibration"]["vF"]
anchor = d["anchor"]

v = {"sqrt_N_structural_check": {}, "closed_form_recomputation": {}}
for arm in ("s17_low", "s17_high"):
    a = d["arms"][arm]
    sd50, sd100 = a["tail_50"]["sd"], a["tail_100"]["sd"]
    v["sqrt_N_structural_check"][arm] = {
        "sd_50": sd50, "sd_100": sd100,
        "ratio": sd50 / sd100,
        "sqrt2": math.sqrt(2.0),
        "rel_dev_from_sqrt2": abs(sd50 / sd100 - math.sqrt(2.0)) / math.sqrt(2.0),
    }
    vD = a["vD"]
    cf50 = anchor * math.sqrt((vD + (1 + vD) * vF) / 50.0)
    cf100 = anchor * math.sqrt((vD + (1 + vD) * vF) / 100.0)
    v["closed_form_recomputation"][arm] = {
        "vD": vD, "vF": vF, "anchor": anchor,
        "closed_form_sd_50": cf50, "bootstrap_sd_50": sd50,
        "ratio_50": sd50 / cf50,
        "closed_form_sd_100": cf100, "bootstrap_sd_100": sd100,
        "ratio_100": sd100 / cf100,
    }

# ---- document-search adjudication ledger (hand-read, quoted at source) ----
v["adjudication"] = [
    {"file": "corpus/whestbench/core/RULES_V12_ANALYSIS_20260808.md", "line": 73,
     "quote": "- **Phase-end standings use all 100 MLPs** (50 public + 50 private, "
              "§5.4) — the live leaderboard shows only the public half, so even the "
              "Phase-1 standing is not what today's board displays.",
     "primary": True,
     "resolving_for_U4": False,
     "reason": "Sizes the PHASE-END STANDINGS benchmark (public+hidden halves of the "
               "Phase suite), not the September Private Re-evaluation suite, which the "
               "same document describes (lines 13-15) as 'a separate, fresh, never-seen "
               "test suite ... generated from private seeds that were not used during "
               "either Phase 1 or Phase 2' with NO count. Strongest available prior for "
               "the fresh-suite size, not a statement of it."},
    {"file": "corpus/whestbench/core/RULES_V12_ANALYSIS_20260808.md", "line": 13,
     "quote": "The Private Re-evaluation runs **Sept 20-30, 2026** on \"a separate, fresh, "
              "never-seen test suite ... generated from private seeds that were not used "
              "during either Phase 1 or Phase 2.\"",
     "primary": True, "resolving_for_U4": False,
     "reason": "Verbatim rules quote of the exact object U4 asks about; states seeds and "
               "freshness, states NO size. This is the decisive negative."},
    {"file": "corpus/whestbench/sources/research_top_method_forensics_20260803.md", "line": 26,
     "quote": "Section 5.4 says the live score is only the 50-MLP public half; Phase-I "
              "prizes combine public and hidden halves, and Phase-II prizes use a fresh "
              "unseen rerun.",
     "primary": True, "resolving_for_U4": False,
     "reason": "Sizes the PUBLIC half (50). Explicitly leaves the fresh unseen rerun "
               "unsized. Corroborates the 50+50 composition."},
    {"file": "corpus/whestbench/sources/research_phase1_top_arc_repo_20260803.md", "line": 65,
     "quote": "Phase II requires designating one entry, which is rerun on a fresh unseen "
              "MLP suite; public-suite tuning and accounting-dependent tricks may not "
              "survive that rerun or code review.",
     "primary": True, "resolving_for_U4": False,
     "reason": "'a fresh unseen MLP suite' -- no count."},
    {"file": "corpus/whestbench/core/HOSTED_INTEL_20260808.md", "line": 49,
     "quote": "- **Designation slots: TWO.** Official facts panel: \"Fresh private rerun "
              "of each team's **up to two nominated submissions, per phase**.\"",
     "primary": True, "resolving_for_U4": False,
     "reason": "Organizer official-facts panel quoted verbatim; sizes the nomination "
               "count, not the suite."},
    {"file": "corpus/whestbench/core/FLIP_READINESS_20260810.md", "line": 21,
     "quote": "Prize ranking is EXCLUSIVELY the private re-evaluation, on a freshly "
              "generated suite with private seeds unused in either phase.",
     "primary": True, "resolving_for_U4": False,
     "reason": "Aug-10 organizer-text read (Aug-4 update email 19fcb021d19e8278 + "
               "discourse 18125). No count."},
    {"file": "corpus/whestbench/core/GEN3_RECURSION_PACKET_20260808.md", "line": 99,
     "quote": "the Phase standings add a withheld 50, and the prize adds fresh private "
               "seeds",
     "primary": False, "resolving_for_U4": False,
     "reason": "Internal restatement; corroborates the withheld half = 50 and again "
               "leaves the prize suite unsized."},
    {"file": "AGENT_CHANNEL.md", "line": 611,
     "quote": "the prize is decided by ONE draw of a 100-net private suite",
     "primary": False, "resolving_for_U4": False,
     "reason": "OUR OWN seed-idea prose (2026-08-09), not a source. It is also the single "
               "place in the corpus where 100 is asserted as the private-suite size, and "
               "it contradicts the 50 used in every S1/S4/U9 bootstrap -- an internal "
               "inconsistency this scan surfaces, not evidence."},
    {"file": "corpus/whestbench/handoff/RESOURCE_PROVENANCE.md", "line": 14,
     "quote": "| WHest starter kit | https://github.com/AIcrowd/whest-starterkit.git | "
              "`c99ef4af15bae7dd19e1d9c46fa4794d90a91d40` |",
     "primary": True, "resolving_for_U4": False,
     "reason": "DECISIVE COVERAGE FACT: the starter kit is referenced by URL+commit and "
               "deliberately NOT vendored ('No ... competition binaries', 'No API token, "
               "hosted model, paper PDF, challenge weight/truth file, scorer ... is "
               "included'). The falsifier's premise 'the starter kit already sitting in "
               "sources/' is false -- sources/ holds research notes only. A starter-kit "
               "re-read is therefore NOT response-free/offline; it needs the network."},
]
v["n_adjudicated"] = len(v["adjudication"])
v["n_resolving"] = sum(1 for r in v["adjudication"] if r["resolving_for_U4"])

res = json.load(open(os.path.join(OUT, "results.json"), encoding="utf-8"))
res["verification"] = v
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
print(json.dumps(v["sqrt_N_structural_check"], indent=1))
print(json.dumps(v["closed_form_recomputation"], indent=1))
print("adjudicated:", v["n_adjudicated"], "resolving:", v["n_resolving"])
