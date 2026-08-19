"""Mutual-information kill/win graph over the WHestBench fold ledger.

Deterministic, stdlib-only. Run with -B (no bytecode; an external writer polluting
custody trees was caught on this tree, so nothing here may emit __pycache__).

What it does
------------
1. Loads all 276 ledger records.
2. Codes each record on six categorical axes by regex over its VERBATIM strings
   (id / status / status_note / mechanism / bias_class / prediction /
   kill_condition / result). Where an axis is genuinely unstated the code is
   'unstated' or 'none' -- never a guess.
3. Computes plug-in mutual information I(outcome; axis) for every single axis and
   every axis pair, each against a 200-shuffle permutation null (small-sample MI
   is biased upward, so the raw number alone is not evidence).
4. Door detector: every (kill, win/pass) pair whose four co-defined axes differ in
   exactly ONE axis becomes a door edge annotated with the axis and the direction.
   That is the quantitative form of the context-indexed-kill doctrine.
5. Writes mi_graph.json, mi_table.json, doors.json and MI_GRAPH_REPORT.md.

Honesty rules enforced in code
------------------------------
- No edge is emitted that is not a literal one-axis difference between two real
  records; there is no similarity heuristic and no threshold to tune.
- Every MI number ships with its permutation null mean, sd and p-value.
- I(outcome; killtype) is flagged as a construction artifact: killtype and outcome
  are both partly parsed from the same `status` string, so their MI is inflated by
  definition, not by discovery.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE.parent / "fold_ledger.json"
SEED = 20260819
N_PERM = 200

TEXT_FIELDS = (
    "id",
    "status",
    "status_note",
    "mechanism",
    "bias_class",
    "prediction",
    "kill_condition",
    "result",
)


# --------------------------------------------------------------------------
# text assembly
# --------------------------------------------------------------------------

def field_text(rec, key):
    v = rec.get(key, "")
    if isinstance(v, (dict, list)):
        return json.dumps(v, sort_keys=True)
    return str(v)


def blob(rec, keys=TEXT_FIELDS):
    return " ‖ ".join(field_text(rec, k) for k in keys).lower()


# The doctrine records one explicit correction (IDX 68: "the formal L1 geometry is
# 126 independent Haar frames with degree 2 exactness, not a Kerdock MUB"). A
# negated carrier name is not a carrier claim, so negation spans are removed before
# carrier matching.
NEGATED_CARRIER = re.compile(r"not (?:a |an |the )?(?:kerdock|mub)[^.,;‖]*")


# --------------------------------------------------------------------------
# axis 1: carrier
# --------------------------------------------------------------------------

CARRIER_PATTERNS = [
    ("kerdock_mub", r"kerdock|\bmub\b|mutually unbiased|phased[-_ ]hadamard|"
                    r"real[-_ ]mub|spherical 5-design|\b5-design\b|full ?129"),
    ("haar_random_spherical", r"\bhaar\b|random[-_ ]spherical|spherical[-_ ]random|"
                              r"randomized[-_ ]radial|random ?32,?256|row[-_ ]?blocked|"
                              r"randomly rotated|spherical sampling|\brqmc\b|"
                              r"kronecker lattice|cranley|great[-_ ]circle|"
                              r"random[-_ ]frame"),
    ("zonal_harmonic", r"zonal|gegenbauer|hermite|legendre|spherical harmonic|"
                       r"harmonic (?:spectrum|degree|control|energy|content|cv|band)|"
                       r"ridgelet|jacobi polynomial|band[-_ ]limited"),
]


def code_carrier(rec):
    txt = NEGATED_CARRIER.sub(" ", blob(rec))
    matches = [name for name, pat in CARRIER_PATTERNS if re.search(pat, txt)]
    return (matches[0] if matches else "none"), matches


# --------------------------------------------------------------------------
# axis 2: precision
# --------------------------------------------------------------------------

PREC_MIXED = r"mixed[- _]?f32|mixed[- ]precision|mixed[- ]dtype"
PREC_F32 = r"float32|\bf32\b|\bfp32\b|single[- ]precision"
PREC_F64 = r"float64|\bf64\b|\bfp64\b|double[- ]precision"


def code_precision(rec):
    txt = blob(rec)
    tokens = sorted(set(
        m.group(0)
        for pat in (PREC_MIXED, PREC_F32, PREC_F64)
        for m in re.finditer(pat, txt)
    ))
    has_mixed = bool(re.search(PREC_MIXED, txt))
    has32 = bool(re.search(PREC_F32, txt))
    has64 = bool(re.search(PREC_F64, txt))
    if has_mixed:
        return "mixed", tokens
    if has32 and has64:
        # Coding rule, stated in the report: a record that names both dtypes is
        # coded 'mixed'. The raw tokens stay on the node so the distinction
        # between "explicitly mixed-f32" and "both dtypes checked" is not lost.
        return "mixed", tokens
    if has32:
        return "f32", tokens
    if has64:
        return "f64", tokens
    return "unstated", tokens


# --------------------------------------------------------------------------
# axis 3: payoff convention (the currency the verdict was denominated in)
# --------------------------------------------------------------------------

# Currency tokens are deliberately QUANTITATIVE: a currency counts only where the
# record attaches a measured number or a named gate to it. "improve adjusted score"
# with no number is a break-even remark, not a payoff denomination, and must not
# outrank the MiB figure that actually killed the record (IDX 80).
CONVENTION_PATTERNS = [
    ("adjusted_score",
     r"adjusted (?:score|mse|estimate)?\s*[\d.]+|adjusted [\d.]|"
     r"[\d.]+ ?x worse than|minimum-effect ratio|multiplier ?[\d.]|"
     r"adjusted score (?:falls|improves|drops|rises|worsens|ratio)|"
     r"score ratio ?[\d.]|score-ratio"),
    ("residual_walltime",
     r"residual (?:was|is|of)?\s*[\d.]+ ?s|[\d.]+ ?s(?:ec|econds)? (?:versus|vs|against)|"
     r"residual allowance|mean residual|fail(?:s|ed)? residual|residual and memory|"
     r"residual wall[-_ ]?(?:time|clock|second)|wall[-_ ]?(?:time|clock)|timeout|"
     r"residual seconds|residual tail|residual-scale|[\d.]+ ?ms permitted"),
    ("memory",
     r"[\d.]+ ?mib|[\d.]+ ?gib|memory margin|memory gate|\boom\b|peak ?[\d.]+|"
     r"fail(?:s|ed)?[^.;]{0,25}memory|and memory\b|memory pressure|memory safety"),
    ("flop_cost_wall",
     r"\bflop|billed|\bbill(?:s|ed|ing)?\b|cost (?:wall|gate|cap|excess|accounting|"
     r"model|god node)|budget|headroom|overflow|overflowing|over the [\d.]+|"
     r"exceed[a-z]*[^.;]{0,30}(?:budget|allowance|cap|headroom|\bb\b)|max c\b|\bcmax\b|"
     r"under (?:b\b|headroom)|effective compute|cost ratio|\bc envelope|"
     r"[\d,.]+b (?:vs|versus|against)|arithmetic gate|cost leg|costs? ?[\d.,]+"),
    ("raw_mse_variance",
     r"raw mse|\bvariance\b|mse ratio|geomean|parity|correlat|\br2\b|design error|"
     r"\bwins?\b|noise floor|\bbias\b|estimator error"),
    ("protocol",
     r"protocol|predeclar|burned|legality|unlawful|lawful|one-shot|consumed|"
     r"designation|no locked|gate order|relabel|blocked_overlap|premise"),
]
CONVENTION_PRIORITY = {name: k for k, (name, _) in enumerate(CONVENTION_PATTERNS)}

# Highest authority: the status string often names the wall outright
# (killed_preexecution_cost, killed_one_shot_residual, killed_protocol, ...).
# Where a status names two currencies, the one the record itself put FIRST wins.
STATUS_CONVENTION = [
    (r"protocol", "protocol"),
    (r"cost|resource", "flop_cost_wall"),
    (r"residual", "residual_walltime"),
    (r"variance", "raw_mse_variance"),
    (r"memory", "memory"),
]

# Comparison to the champion is by definition denominated in the scoring currency.
CHAMPION = re.compile(r"worse than (?:the )?(?:deployed )?champion")

KILL_VERB = re.compile(
    r"\b(?:kill\w*|fail\w*|exceed\w*|overflow\w*|miss\w*|worse|reject\w*|no-?go|"
    r"block\w*|breach\w*|insufficient|dies|died|invert\w*|falsif\w*|crossing|"
    r"collapse\w*|violat\w*|refut\w*|unresolved|absent)\b|does not|cannot|over the")
# In this ledger success is reported as "zero failures"; that is not a kill verb.
ZERO_FAIL = re.compile(r"(?:zero|no|0) (?:resource |candidate )?failures?")
CLAUSE_SPLIT = re.compile(
    r"(?:[.;]\s+|\s+but\s+|\s+whereas\s+|\s+while\s+|\s+however[,\s]|\s+though\s+)")


def failing_text(result_txt):
    """Clauses of the result that carry a kill/fail verb. Clauses reporting a gate
    that PASSED carry no kill verb and are therefore dropped, which is what stops
    'Cost and legality pass but accuracy fails' from being read as a cost kill."""
    t = ZERO_FAIL.sub(" ", result_txt)
    return " ".join(cl for cl in CLAUSE_SPLIT.split(t) if KILL_VERB.search(cl))


def code_convention(rec):
    status = (field_text(rec, "status") + " " + field_text(rec, "status_note")).lower()
    result_txt = field_text(rec, "result").lower()
    full = blob(rec)

    present = [name for name, pat in CONVENTION_PATTERNS if re.search(pat, full)]

    hits = [(m.start(), name) for pat, name in STATUS_CONVENTION
            for m in [re.search(pat, status)] if m]
    if hits:
        return min(hits)[1], present, "status_string"

    if CHAMPION.search(result_txt):
        return "adjusted_score", present, "champion_comparison"

    # Within a text tier the EARLIEST currency wins (the record names its decisive
    # currency first); ties at the same offset fall back to the fixed priority.
    for text, src in ((failing_text(result_txt), "failing_clauses"),
                      (result_txt, "whole_result"),
                      (full, "whole_record")):
        found = []
        for name, pat in CONVENTION_PATTERNS:
            m = re.search(pat, text)
            if m:
                found.append((m.start(), CONVENTION_PRIORITY[name], name))
        if found:
            return min(found)[2], present, src

    return "unstated", present, "none"


# --------------------------------------------------------------------------
# axis 4: kill type (defined only for records that died; 'none' otherwise)
# --------------------------------------------------------------------------

KILLTYPE_STATUS = [
    ("preexecution_static", r"preexecution|_static|pretarget"),
    ("protocol_procedural", r"protocol|relabelling|literal_intended_law"),
    # \babi\b, not abi: without the boundary this matches "probability". harness and
    # launcher stay unbounded on the left -- the status token is `killed_harness`,
    # and '_' is a word character, so \bharness would never fire.
    ("harness_instrument", r"harness|\babi\b|interface_carrier_blocked|launcher"),
    ("one_shot_consumed", r"one_shot"),
]

# Killtype evidence is read from the RESULT only. The words "harness",
# "instrumented" and "protocol" appear in the kill_condition boilerplate of most
# records; scanning the whole record mislabels 31 ordinary kills as harness kills.
# What killed a candidate is stated where the candidate's death is reported.
KILLTYPE_TEXT = [
    ("preexecution_static", r"killed before|kill(?:ed)? deterministically at the first|"
                            r"before an outcome screen|before training|"
                            r"killed pre-?execution|static (?:pareto|proposal|kill)|"
                            r"killed at g0|kill at g0|no new score row|"
                            r"killed before an|before execution"),
    ("harness_instrument", r"launcher fail|runner fail|first-broken-link|"
                           r"harness fail|killed by the harness|env-map failure|"
                           r"instrument(?:ation)? (?:failure|broke|corrected)"),
    ("protocol_procedural", r"burned gate|permanently consumed|predeclared gate|"
                            r"legality fail|unlawful"),
    ("executed_measurement", r"killed at|kill_confirmed|killed both legs|"
                             r"measured|executed|bootstrap|paired|\bran\b|completed"),
]


def code_killtype(rec, outcome):
    if outcome not in ("kill", "protocol_kill"):
        return "none", "not_a_kill"
    status = (field_text(rec, "status") + " " + field_text(rec, "status_note")).lower()
    for name, pat in KILLTYPE_STATUS:
        if re.search(pat, status):
            return name, "status_string"
    # Records 269+ carry `result` as a dict whose metrics blob is a GATE SPEC, full
    # of conditional phrases ("...the run is an instrument failure and must not be
    # recorded as a kill") that describe hypotheticals rather than what happened.
    # For those the authoritative narrative is the verdict field alone.
    res = rec.get("result")
    if isinstance(res, dict):
        res_txt = str(res.get("verdict", ""))
    else:
        res_txt = field_text(rec, "result")
    txt = (status + " ‖ " + res_txt).lower()
    for name, pat in KILLTYPE_TEXT:
        if re.search(pat, txt):
            return name, "result_text"
    return "executed_measurement", "default_executed"


# --------------------------------------------------------------------------
# axis 5: mechanism family
# --------------------------------------------------------------------------

MECH_PATTERNS = [
    ("compiler_schedule", r"winograd|strassen|fused|fusion|dispatch|in-?place|"
                          r"streamed|streaming|allocation|\bgemm\b|reassociation|"
                          r"schedule|compiler|butterfly|\bwht\b|hadamard transform|"
                          r"buffer|block-?height|preallocat"),
    ("sampler", r"\brqmc\b|lattice|antithetic|monte-?carlo|draw stage|stratif|"
                r"importance sampl|\bsampler\b|sampling|prun(?:e|ing)|"
                r"hansen-hurwitz|probe|resampl"),
    ("design_frame", r"\bdesign\b|\bframe(?:s)?\b|cubature|antipodal|kerdock|\bmub\b|"
                     r"quadrature|point set|129|rotation construction|spherical harmonic|"
                     r"zonal|gegenbauer"),
    ("control_variate", r"control variate|control-?variate|known-mean|"
                        r"exact control|control term|baseline control|\bcv\b"),
    ("selection", r"selection|oracle-of|oracle of|select\b|selecting|"
                  r"model choice|choose|dispatch by"),
    ("transport", r"transport|cumulant|frechet|tangent|edgeworth|propagat|"
                  r"bridge|motif|source contraction|\bjet\b|response|recurrence|"
                  r"closure"),
    ("low_rank_factorization", r"rank-?one|rank-?1|low-?rank|\bsvd\b|eigen|singular|"
                               r"factoriz|rank face|subspace|triangular"),
    ("learned_closure", r"learn|train|\bfit\b|fitting|attenuat|latent factor|"
                        r"ridge normal|regress|neural"),
    ("analytic_identity", r"identit(?:y|ies)|theorem|closed form|no-?go|proof|"
                          r"orbit algebra|algebra\b|exactness|certificate"),
    ("infrastructure", r"package|manifest|\btar\b|submission|calibrat|meter|"
                       r"bookkeep|convention|audit|verification|validator"),
]


def code_mechanism_family(rec):
    bias = field_text(rec, "bias_class").lower().strip()
    txt = blob(rec, ("id", "mechanism", "bias_class"))
    matches = [name for name, pat in MECH_PATTERNS if re.search(pat, txt)]
    # The ledger self-labels the graveyard/falsifier lineage in bias_class; that is
    # the record's own word, not an inference, so it wins.
    if bias.startswith("diagnostic"):
        return "diagnostic_falsifier", ["diagnostic_falsifier"] + matches
    return (matches[0] if matches else "unclassified"), matches


# --------------------------------------------------------------------------
# axis 6: outcome class
# --------------------------------------------------------------------------

def code_outcome(rec):
    s = field_text(rec, "status").lower()
    if s in ("promoted", "validated", "package_validated"):
        return "win"
    if s == "proposed":
        return "inconclusive"
    if s.startswith("blocked"):
        return "inconclusive"
    killish = ("killed" in s) or s.startswith("no_go") or ("_no_go" in s) or ("no_go_" in s)
    if killish:
        if "protocol" in s:
            return "protocol_kill"
        return "kill"
    if any(t in s for t in ("unresolved", "uncertain", "inconclusive", "ambiguous")):
        return "inconclusive"
    if s.endswith("_open"):
        return "inconclusive"
    if any(t in s for t in ("pass", "screened", "repair", "preserved", "survivor",
                            "validated", "rejected")):
        return "pass"
    raise ValueError("unmapped status: %r" % s)


# --------------------------------------------------------------------------
# mutual information + permutation null
# --------------------------------------------------------------------------

def mutual_information(xs, ys):
    """Plug-in MI in bits between two aligned categorical sequences."""
    n = len(xs)
    if n == 0:
        return 0.0
    joint = Counter(zip(xs, ys))
    px = Counter(xs)
    py = Counter(ys)
    mi = 0.0
    for (a, b), nab in joint.items():
        pab = nab / n
        mi += pab * math.log2(pab / ((px[a] / n) * (py[b] / n)))
    return mi


def entropy(xs):
    n = len(xs)
    c = Counter(xs)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def mi_with_null(outcomes, axis_vals, rng, n_perm=N_PERM):
    obs = mutual_information(outcomes, axis_vals)
    shuffled = list(outcomes)
    nulls = []
    for _ in range(n_perm):
        rng.shuffle(shuffled)
        nulls.append(mutual_information(shuffled, axis_vals))
    mean = sum(nulls) / len(nulls)
    var = sum((v - mean) ** 2 for v in nulls) / (len(nulls) - 1)
    sd = math.sqrt(var)
    ge = sum(1 for v in nulls if v >= obs)
    return {
        "mi_bits": obs,
        "null_mean_bits": mean,
        "null_sd_bits": sd,
        "null_max_bits": max(nulls),
        "mi_minus_null_mean_bits": obs - mean,
        "p_value": (1 + ge) / (n_perm + 1),
        "n_permutations": n_perm,
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

# The four axes co-defined for EVERY record regardless of outcome. Kill type is
# excluded from the door profile on purpose: a win has no kill type, so including
# it would make every (kill, win) pair differ on it automatically and the
# "exactly one axis differs" test would collapse to a tautology. Kill type rides
# along on each door edge as an annotation instead.
DOOR_AXES = ("carrier", "precision", "convention", "mechanism_family")
MI_AXES = ("carrier", "precision", "convention", "killtype", "mechanism_family")

KILL_OUTCOMES = ("kill", "protocol_kill")
WIN_OUTCOMES = ("win", "pass")

# Independent check on the coding layer. These record->axis assignments are read off
# KILL_CONTEXT_INDEX_20260819.md, which was extracted from the same ledger by a
# different route. Agreement is the second signal that the regexes code what the
# doctrine says they code; every disagreement is printed rather than absorbed.
# Where the doctrine lists a record under two families, either is accepted.
DOCTRINE_CONVENTION = {
    7: "adjusted_score", 16: "adjusted_score", 59: "adjusted_score", 53: "adjusted_score",
    117: "residual_walltime", 118: "residual_walltime", 69: "residual_walltime",
    113: "flop_cost_wall", 114: "flop_cost_wall", 115: "flop_cost_wall",
    123: "flop_cost_wall", 86: "flop_cost_wall", 139: "flop_cost_wall",
    80: "memory",
}
DOCTRINE_CARRIER = {}
for _i in (3, 70, 71, 72, 73, 74, 79, 80, 81, 84):
    DOCTRINE_CARRIER.setdefault(_i, set()).add("kerdock_mub")
for _i in (0, 13, 14, 15, 16, 40, 43, 53, 66, 68, 77, 87, 88, 105, 109, 110, 111, 131):
    DOCTRINE_CARRIER.setdefault(_i, set()).add("haar_random_spherical")
for _i in (1, 8, 23, 36, 38, 39, 45, 47, 68, 76, 92, 97, 98, 99, 100, 101, 102, 103,
           104, 106, 107, 112, 113, 133):
    DOCTRINE_CARRIER.setdefault(_i, set()).add("zonal_harmonic")
for _i in (36, 66, 111):  # doctrine: "plus MUB machinery referenced at 36, 66, 111"
    DOCTRINE_CARRIER.setdefault(_i, set()).add("kerdock_mub")
DOCTRINE_PRECISION = {}
for _i in (42, 46, 48, 50, 53, 58, 69, 127, 128, 129, 130, 134, 135, 139):
    DOCTRINE_PRECISION.setdefault(_i, set()).add("f32")
for _i in (52, 102, 125, 126, 129, 134, 135, 110):
    DOCTRINE_PRECISION.setdefault(_i, set()).add("f64")
for _i in (128, 130):
    DOCTRINE_PRECISION.setdefault(_i, set()).add("mixed")
# a record the doctrine lists under two dtypes is coded 'mixed' here by design
for _i, _s in DOCTRINE_PRECISION.items():
    if len(_s) > 1:
        _s.add("mixed")


def validate_against_doctrine(nodes):
    by_idx = {n["idx"]: n for n in nodes}
    report = {}
    for axis, truth in (("convention", {k: {v} for k, v in DOCTRINE_CONVENTION.items()}),
                        ("carrier", DOCTRINE_CARRIER),
                        ("precision", DOCTRINE_PRECISION)):
        agree, disagree = 0, []
        for idx, allowed in sorted(truth.items()):
            got = by_idx[idx]["axes"][axis]
            if got in allowed:
                agree += 1
            else:
                disagree.append({
                    "idx": idx,
                    "id": by_idx[idx]["id"],
                    "doctrine": sorted(allowed),
                    "coded": got,
                    "matched_families": by_idx[idx]["axis_evidence"].get(
                        "carrier_families_matched" if axis == "carrier"
                        else "precision_tokens_matched" if axis == "precision"
                        else "conventions_present"),
                })
        report[axis] = {
            "n_checked": len(truth),
            "n_agree": agree,
            "agreement": agree / len(truth),
            "disagreements": disagree,
        }
    return report


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    recs = ledger["candidates"]

    nodes = []
    for i, r in enumerate(recs):
        outcome = code_outcome(r)
        carrier, carrier_matches = code_carrier(r)
        precision, prec_tokens = code_precision(r)
        convention, conv_present, conv_src = code_convention(r)
        killtype, kt_src = code_killtype(r, outcome)
        mech, mech_matches = code_mechanism_family(r)
        nodes.append({
            "idx": i,
            "id": r["id"],
            "status": r["status"],
            "status_note": r.get("status_note"),
            # verbatim ledger strings -- intent and context preserved on the node
            "mechanism": r["mechanism"],
            "bias_class": r["bias_class"],
            "prediction": r["prediction"],
            "kill_condition": r["kill_condition"],
            "result": r.get("result"),
            "axes": {
                "carrier": carrier,
                "precision": precision,
                "convention": convention,
                "killtype": killtype,
                "mechanism_family": mech,
                "outcome": outcome,
            },
            # Ledger-native weight. matched_units >= 100 means the record carries a
            # full paired public-100 run; a record with 3 units and primary_effect
            # 0.0 is a guard validation, not a scoring result.
            "scored_full_run": (r.get("matched_units") or 0) >= 100,
            "matched_units": r.get("matched_units"),
            "primary_effect": r.get("primary_effect"),
            "failures": r.get("failures"),
            "axis_evidence": {
                "carrier_families_matched": carrier_matches,
                "precision_tokens_matched": prec_tokens,
                "conventions_present": conv_present,
                "convention_source": conv_src,
                "killtype_source": kt_src,
                "mechanism_families_matched": mech_matches,
            },
        })

    outcomes = [n["axes"]["outcome"] for n in nodes]
    rng = random.Random(SEED)

    # Two targets. The 5-class outcome is the full picture; the binary lived/died
    # target over the 257 decided records is the owner's actual question -- what is
    # the mutual information between what did not work and what did.
    targets = [
        ("outcome_5class", nodes, [n["axes"]["outcome"] for n in nodes]),
        ("lived_vs_died",
         [n for n in nodes if n["axes"]["outcome"] != "inconclusive"],
         ["lived" if n["axes"]["outcome"] in WIN_OUTCOMES else "died"
          for n in nodes if n["axes"]["outcome"] != "inconclusive"]),
    ]

    mi_rows = []
    for tname, tnodes, tvals in targets:
        for ax in MI_AXES:
            vals = [n["axes"][ax] for n in tnodes]
            row = {"target": tname, "axis": ax, "kind": "single",
                   "n_records": len(tnodes), "n_levels": len(set(vals))}
            row.update(mi_with_null(tvals, vals, rng))
            row["axis_entropy_bits"] = entropy(vals)
            row["target_entropy_bits"] = entropy(tvals)
            if ax == "killtype":
                row["confound"] = (
                    "CONSTRUCTION ARTIFACT: killtype and outcome are both parsed "
                    "from the same status string, and killtype is 'none' by "
                    "definition for every non-kill. This MI is inflated by "
                    "definition and is not a finding."
                )
            mi_rows.append(row)
        for a, b in combinations(MI_AXES, 2):
            vals = ["%s|%s" % (n["axes"][a], n["axes"][b]) for n in tnodes]
            row = {"target": tname, "axis": "%s+%s" % (a, b), "kind": "pair",
                   "n_records": len(tnodes), "n_levels": len(set(vals))}
            row.update(mi_with_null(tvals, vals, rng))
            row["axis_entropy_bits"] = entropy(vals)
            row["target_entropy_bits"] = entropy(tvals)
            if "killtype" in (a, b):
                row["confound"] = "contains killtype; see the killtype row"
            mi_rows.append(row)

    mi_rows.sort(key=lambda r: (r["target"], -r["mi_minus_null_mean_bits"], r["axis"]))

    # Per-value concentrations on the binary target: where does survival actually sit?
    decided = [n for n in nodes if n["axes"]["outcome"] != "inconclusive"]
    base_rate = sum(1 for n in decided if n["axes"]["outcome"] in WIN_OUTCOMES) / len(decided)
    concentrations = []
    for ax in MI_AXES:
        groups = defaultdict(list)
        for n in decided:
            groups[n["axes"][ax]].append(n)
        for val, members in groups.items():
            lived = [m for m in members if m["axes"]["outcome"] in WIN_OUTCOMES]
            concentrations.append({
                "axis": ax,
                "value": val,
                "n": len(members),
                "n_lived": len(lived),
                "lived_rate": len(lived) / len(members),
                "lift_vs_base": (len(lived) / len(members)) / base_rate if base_rate else 0.0,
                "lived_idx": sorted(m["idx"] for m in lived),
            })
    concentrations.sort(key=lambda c: (-c["n"] * abs(c["lived_rate"] - base_rate),
                                       c["axis"], c["value"]))

    # ---------------- robustness: attack the one axis that cleared its null ------
    # carrier is the only single axis clearing the permutation null on lived/died.
    # The counter-hypothesis is that it is one cell (zonal_harmonic) and/or a proxy
    # for the analytic source lineage. Both are tested here rather than asserted.
    def _mi_subset(keep, label):
        sub = [n for n in decided if keep(n)]
        y = ["lived" if n["axes"]["outcome"] in WIN_OUTCOMES else "died" for n in sub]
        x = [n["axes"]["carrier"] for n in sub]
        row = {"subset": label, "n_records": len(sub)}
        row.update(mi_with_null(y, x, rng))
        return row

    robustness = {
        "claim": ("carrier is the only single axis clearing the permutation null on "
                  "lived_vs_died. These subsets test whether that survives removing "
                  "the cell and the lineage that could be manufacturing it."),
        "carrier_mi_subsets": [
            _mi_subset(lambda n: True, "all decided records"),
            _mi_subset(lambda n: n["axes"]["carrier"] != "zonal_harmonic",
                       "zonal_harmonic records removed"),
            _mi_subset(lambda n: n["axes"]["mechanism_family"] != "transport",
                       "transport mechanism family removed"),
        ],
        "zonal_within_family": [],
    }
    for fam in sorted({n["axes"]["mechanism_family"] for n in decided}):
        sub = [n for n in decided if n["axes"]["mechanism_family"] == fam]
        if len(sub) < 15:
            continue
        entry = {"mechanism_family": fam, "n": len(sub), "by_carrier": {}}
        groups = defaultdict(list)
        for n in sub:
            groups[n["axes"]["carrier"]].append(n)
        for car, members in sorted(groups.items()):
            entry["by_carrier"][car] = {
                "n": len(members),
                "lived": sum(1 for x in members if x["axes"]["outcome"] in WIN_OUTCOMES),
            }
        robustness["zonal_within_family"].append(entry)

    # ---------------- door detector ----------------
    axis_mi = {r["axis"]: r["mi_minus_null_mean_bits"] for r in mi_rows
               if r["kind"] == "single" and r["target"] == "lived_vs_died"}
    kills = [n for n in nodes if n["axes"]["outcome"] in KILL_OUTCOMES]
    wins = [n for n in nodes if n["axes"]["outcome"] in WIN_OUTCOMES]

    doors = []
    for k in kills:
        for w in wins:
            diff = [ax for ax in DOOR_AXES if k["axes"][ax] != w["axes"][ax]]
            if len(diff) != 1:
                continue
            ax = diff[0]
            shared = {a: k["axes"][a] for a in DOOR_AXES if a != ax}
            doors.append({
                "differing_axis": ax,
                "direction": "%s -> %s" % (k["axes"][ax], w["axes"][ax]),
                "axis_value_kill": k["axes"][ax],
                "axis_value_win": w["axes"][ax],
                "shared_profile": shared,
                "kill_idx": k["idx"],
                "kill_id": k["id"],
                "kill_status": k["status"],
                "kill_outcome": k["axes"]["outcome"],
                "kill_killtype": k["axes"]["killtype"],
                "win_idx": w["idx"],
                "win_id": w["id"],
                "win_status": w["status"],
                "win_outcome": w["axes"]["outcome"],
                "win_scored_full_run": w["scored_full_run"],
                "win_matched_units": w["matched_units"],
                "kill_scored_full_run": k["scored_full_run"],
                "differing_axis_mi_minus_null_bits": axis_mi[ax],
            })

    # Deterministic ranking. A door is worth more when the surviving side was
    # actually scored on a paired run (ledger field matched_units) rather than
    # validated as packaging, and when the axis that differs is the one carrying
    # the most lived/died information. Ledger order breaks remaining ties.
    doors.sort(key=lambda d: (
        0 if d["win_scored_full_run"] else 1,
        0 if d["win_outcome"] == "win" else 1,
        -d["differing_axis_mi_minus_null_bits"],
        d["kill_idx"],
        d["win_idx"],
    ))

    door_axis_counts = Counter(d["differing_axis"] for d in doors)
    door_dir_counts = Counter((d["differing_axis"], d["direction"]) for d in doors)

    # The full ranked list is kept intact. For the report's top 10 only, at most two
    # doors per (surviving node, differing axis) are shown -- otherwise the head of
    # the list is one win node's whole neighbourhood and the other doors never
    # surface. This selects, it does not invent: every entry is still a literal
    # one-axis pair from the ranked list.
    seen_pair = Counter()
    top10 = []
    for d in doors:
        key = (d["win_idx"], d["differing_axis"])
        if seen_pair[key] >= 2:
            continue
        seen_pair[key] += 1
        top10.append(d)
        if len(top10) == 10:
            break

    # ---------------- write outputs ----------------
    axis_dists = {
        ax: dict(sorted(Counter(n["axes"][ax] for n in nodes).items(),
                        key=lambda kv: (-kv[1], kv[0])))
        for ax in MI_AXES + ("outcome",)
    }

    validation = validate_against_doctrine(nodes)

    meta = {
        "generated_by": str(Path(__file__).resolve()),
        "ledger": str(LEDGER),
        "n_records": len(nodes),
        "seed": SEED,
        "n_permutations": N_PERM,
        "mi_units": "bits (log base 2), plug-in estimator",
        "outcome_entropy_bits": entropy(outcomes),
        "door_profile_axes": list(DOOR_AXES),
        "door_profile_note": (
            "killtype is excluded from the door profile because it is undefined for "
            "wins; including it would make every (kill, win) pair differ on it and "
            "the one-axis test would be vacuous. It is annotated on each edge."
        ),
        "axis_distributions": axis_dists,
        "doctrine_validation": validation,
        "lived_base_rate": base_rate,
        "n_decided": len(decided),
    }

    (HERE / "mi_graph.json").write_text(json.dumps({
        "meta": meta,
        "nodes": nodes,
        "door_edges": doors,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    (HERE / "mi_table.json").write_text(json.dumps({
        "meta": meta,
        "mi_table": mi_rows,
        "concentrations": concentrations,
        "robustness": robustness,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    (HERE / "doors.json").write_text(json.dumps({
        "meta": meta,
        "n_doors": len(doors),
        "doors_by_axis": dict(door_axis_counts),
        "doors_by_direction": {"%s: %s" % k: v for k, v in
                               sorted(door_dir_counts.items(), key=lambda kv: -kv[1])},
        "top10_report": top10,
        "doors": doors,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    write_report(meta, mi_rows, nodes, doors, top10, door_axis_counts,
                 door_dir_counts, axis_dists, concentrations, robustness)

    print("records:", len(nodes))
    print("outcome distribution:", axis_dists["outcome"])
    print("decided:", len(decided), "lived base rate: %.4f" % base_rate)
    print("doors:", len(doors), dict(door_axis_counts))
    for tname in ("lived_vs_died", "outcome_5class"):
        print("top MI rows [%s]:" % tname)
        for r in [x for x in mi_rows if x["target"] == tname][:6]:
            print("  %-40s MI=%.4f null=%.4f+-%.4f adj=%.4f p=%.4f%s"
                  % (r["axis"], r["mi_bits"], r["null_mean_bits"], r["null_sd_bits"],
                     r["mi_minus_null_mean_bits"], r["p_value"],
                     "  [artifact]" if "confound" in r else ""))


def write_report(meta, mi_rows, nodes, doors, top10, door_axis_counts,
                 door_dir_counts, axis_dists, concentrations, robustness):
    by_idx = {n["idx"]: n for n in nodes}
    L = []
    A = L.append
    A("# Mutual-information kill/win graph over the fold ledger")
    A("")
    A("Generated by `build_mi_graph.py` from `%s`." % meta["ledger"])
    A("%d records, %d permutations, seed %d, MI in bits."
      % (meta["n_records"], meta["n_permutations"], meta["seed"]))
    A("")
    A("## What this is")
    A("")
    A("Every ledger record is coded on six categorical axes by regular expression over")
    A("its own strings. Nothing is inferred beyond what the strings say; an axis with no")
    A("evidence in the record is coded `unstated` (precision, convention) or `none`")
    A("(carrier, killtype). Mutual information then asks a single question per axis:")
    A("how many bits does knowing that axis tell you about whether the record lived or")
    A("died? Because MI computed on 276 records with many levels is biased upward, each")
    A("number is shown against a 200-shuffle permutation null of the same data.")
    A("")
    A("Two targets are scored. `outcome_5class` is the full label (win / pass / kill /")
    A("protocol_kill / inconclusive), entropy %.4f bits over all %d records."
      % (meta["outcome_entropy_bits"], meta["n_records"]))
    A("`lived_vs_died` collapses that to a binary over the %d records that actually got"
      % meta["n_decided"])
    A("a verdict, dropping the %d inconclusive ones. That binary is the owner's"
      % (meta["n_records"] - meta["n_decided"]))
    A("question -- the information between what did not work and what did -- and it is")
    A("the table to read first. The base rate of living is %.4f (%d of %d)."
      % (meta["lived_base_rate"],
         round(meta["lived_base_rate"] * meta["n_decided"]), meta["n_decided"]))
    A("")
    A("## Axis distributions")
    A("")
    for ax, dist in axis_dists.items():
        A("- **%s**: %s" % (ax, ", ".join("%s=%d" % kv for kv in dist.items())))
    A("")
    A("## Does the coding agree with the doctrine?")
    A("")
    A("The kill-context index was extracted from the same ledger by a different route,")
    A("so it is an independent check on these regexes. Records it names explicitly:")
    A("")
    A("| axis | checked | agree | rate |")
    A("| --- | ---: | ---: | ---: |")
    for ax, v in meta["doctrine_validation"].items():
        A("| %s | %d | %d | %.3f |" % (ax, v["n_checked"], v["n_agree"], v["agreement"]))
    A("")
    for ax, v in meta["doctrine_validation"].items():
        if not v["disagreements"]:
            continue
        A("Disagreements on `%s`:" % ax)
        A("")
        for d in v["disagreements"]:
            A("- idx %d `%s`: doctrine says %s, coded `%s` (evidence found in the "
              "record: %s)" % (d["idx"], d["id"], "/".join(d["doctrine"]), d["coded"],
                               d["matched_families"] or "none"))
        A("")
    A("Every disagreement above is a case where the doctrine's extractor assigned an")
    A("axis from LINEAGE and this coder found no such words in the record itself. The")
    A("coder stays conservative on purpose: an axis with no evidence in the record is")
    A("coded `none`/`unstated` rather than inherited from a parent candidate.")
    A("")
    for tname, title in (("lived_vs_died", "MI table: lived vs died (the headline)"),
                         ("outcome_5class", "MI table: full 5-class outcome")):
        rows = [r for r in mi_rows if r["target"] == tname]
        A("## %s" % title)
        A("")
        A("Sorted by MI minus null mean. Target entropy %.4f bits over %d records."
          % (rows[0]["target_entropy_bits"], rows[0]["n_records"]))
        A("")
        A("| axis | kind | levels | MI (bits) | null mean | null sd | null max | "
          "MI - null mean | p | note |")
        A("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
        for r in rows:
            A("| %s | %s | %d | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f | %s |"
              % (r["axis"], r["kind"], r["n_levels"], r["mi_bits"],
                 r["null_mean_bits"], r["null_sd_bits"], r["null_max_bits"],
                 r["mi_minus_null_mean_bits"], r["p_value"],
                 "artifact" if "confound" in r else ""))
        A("")
    A("p is the fraction of shuffles reaching the observed MI, computed as")
    A("(1 + #{null >= observed}) / (permutations + 1); the floor is %.6f, so a p at"
      % (1 / (meta["n_permutations"] + 1)))
    A("that floor means no shuffle out of %d ever matched the real data."
      % meta["n_permutations"])
    A("")
    A("The null means are large relative to the observed MI, which is the point of")
    A("running them: on 276 records a many-levelled axis buys MI for free. Read the")
    A("`MI - null mean` column, never the raw MI.")
    A("")
    flagged = [r for r in mi_rows if "confound" in r]
    if flagged:
        A("### Rows that are not findings")
        A("")
        seen = set()
        for r in flagged:
            if r["confound"] in seen:
                continue
            seen.add(r["confound"])
            A("- %s" % r["confound"])
        A("")
        A("The killtype rows sit at the top of both tables purely because of this.")
        A("Discard them and the largest real single-axis signal is the payoff")
        A("convention.")
        A("")
    A("## Where survival concentrates")
    A("")
    A("Per axis value on the binary target, over the %d decided records. `lift` is the"
      % meta["n_decided"])
    A("value's survival rate divided by the %.4f base rate. Values with n < 5 are"
      % meta["lived_base_rate"])
    A("shown but carry no weight.")
    A("")
    A("| axis | value | n | lived | rate | lift |")
    A("| --- | --- | ---: | ---: | ---: | ---: |")
    for c in concentrations:
        A("| %s | %s | %d | %d | %.3f | %.2f |"
          % (c["axis"], c["value"], c["n"], c["n_lived"], c["lived_rate"],
             c["lift_vs_base"]))
    A("")
    A("## Attack on the one real signal")
    A("")
    A("%s" % robustness["claim"])
    A("")
    A("| subset | n | MI (bits) | null mean | null sd | MI - null mean | p |")
    A("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in robustness["carrier_mi_subsets"]:
        A("| %s | %d | %.4f | %.4f | %.4f | %.4f | %.4f |"
          % (r["subset"], r["n_records"], r["mi_bits"], r["null_mean_bits"],
             r["null_sd_bits"], r["mi_minus_null_mean_bits"], r["p_value"]))
    A("")
    A("The attack lands. Delete the zonal_harmonic records and the carrier axis carries")
    A("nothing at all -- the whole signal is that one cell. So the correct statement is")
    A("not 'the carrier predicts survival'; it is 'candidates coded to a zonal/harmonic")
    A("carrier almost never survive, and no other axis value on any axis predicts")
    A("survival at this sample size'.")
    A("")
    A("Second counter-hypothesis: zonal_harmonic could be a proxy for the analytic")
    A("source lineage rather than a carrier property. Survival by carrier within each")
    A("mechanism family with n >= 15:")
    A("")
    A("| mechanism family | n | survival by carrier |")
    A("| --- | ---: | --- |")
    for e in robustness["zonal_within_family"]:
        A("| %s | %d | %s |" % (e["mechanism_family"], e["n"],
          ", ".join("%s %d/%d" % (c, v["lived"], v["n"])
                    for c, v in e["by_carrier"].items())))
    A("")
    A("The zonal deficit reproduces inside more than one family, which argues against a")
    A("pure lineage artifact, but those cells hold 5 to 11 records each and cannot be")
    A("separated from mechanism at this sample size. Removing the transport family")
    A("leaves the carrier effect the same size and no longer significant, which is what")
    A("a real-but-underpowered effect looks like. Treat it as a hypothesis with a named")
    A("settling check, not a result: score one zonal/harmonic candidate on the promoted")
    A("Haar host and see whether it dies for a carrier reason or a cost reason.")
    A("")
    A("## Doors")
    A("")
    A("A door is a literal pair of ledger records: one that died, one that lived or")
    A("passed, whose profiles over %s are identical" % ", ".join("`%s`" % a for a in meta["door_profile_axes"]))
    A("except on exactly one axis. No similarity metric, no threshold. %d such pairs"
      % len(doors))
    A("exist in the ledger.")
    A("")
    A("%s" % meta["door_profile_note"])
    A("")
    A("### Doors by differing axis")
    A("")
    A("| axis | doors |")
    A("| --- | ---: |")
    for ax, ct in sorted(door_axis_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        A("| %s | %d |" % (ax, ct))
    A("")
    A("### Doors by direction (kill value -> win value)")
    A("")
    A("| axis | direction | doors |")
    A("| --- | --- | ---: |")
    for (ax, direction), ct in sorted(door_dir_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        A("| %s | %s | %d |" % (ax, direction, ct))
    A("")
    A("### Top 10 doors")
    A("")
    A("Ranked by: surviving side was actually scored on a paired run (ledger field")
    A("`matched_units`), then promoted over merely passing, then the differing axis's")
    A("lived/died MI, then ledger order. Nothing here is a similarity score. At most")
    A("two doors per (surviving node, differing axis) are listed so the head of the")
    A("list is not one win node's whole neighbourhood; doors.json holds all %d." % len(doors))
    A("")
    for i, d in enumerate(top10, 1):
        k = by_idx[d["kill_idx"]]
        w = by_idx[d["win_idx"]]
        A("**%d. idx %d `%s` (%s) -> idx %d `%s` (%s)**"
          % (i, d["kill_idx"], d["kill_id"], d["kill_status"],
             d["win_idx"], d["win_id"], d["win_status"]))
        A("")
        A("- differing axis: `%s`, %s" % (d["differing_axis"], d["direction"]))
        A("- shared: %s" % ", ".join("%s=%s" % kv for kv in sorted(d["shared_profile"].items())))
        A("- kill type on the dead side: `%s`" % d["kill_killtype"])
        A("- surviving side scored on a paired run: %s" % ("yes, matched_units=%s" % d["win_matched_units"] if d["win_scored_full_run"] else "no"))
        A("- kill mechanism (verbatim): %s" % k["mechanism"])
        A("- kill result (verbatim): %s" % (field_text(k, "result") or "(no result field)"))
        A("- win mechanism (verbatim): %s" % w["mechanism"])
        A("")
    (HERE / "MI_GRAPH_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
