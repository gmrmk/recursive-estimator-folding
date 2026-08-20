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
- Since the 2026-08-19 repair batch the coder is no longer purely record-local: a
  small, explicitly listed set of recodes carries evidence the regexes cannot see
  (a frozen artifact hash, a package lineage, an estimator source file). Every one
  of them is listed in the report with its evidence class, its literal evidence
  string is asserted present at build time, and the doctrine agreement rate is
  reported both including and excluding them so the independent check survives.

2026-08-19 repair batch (plan item W0.3) -- what changed and why
---------------------------------------------------------------
R1  `sensitivity` joined TEXT_FIELDS (the coder was blind to the field that holds
    idx 0's payoff statement).
R2  the adjusted_score currency accepts the past-tense verbs improved/worsened.
R3  `spherical 5-design` / `5-design` left the kerdock_mub alternation: a spherical
    5-design is a cubature property, not a claim about a Kerdock MUB carrier.
R4  the haar alternation gained normalized-Gaussian / uniform-sphere direction
    vocabulary (normalized Gaussian directions ARE Haar-uniform on the sphere).
R5  carrier by artifact identity: a record naming another record's frozen
    artifact_hash inherits that record's carrier when its own text names none.
R6  four explicitly listed relabels the regexes cannot reach (EXPLICIT_RELABELS).
R7  the ownership axis (W0.4) is coded, censused and judged against a
    pre-registered acceptance rule, in its own permutation stream.
R8  the fragility gate compares every row of this table against the frozen prior
    table `mi_table_prior_20260819.json`, and the idx 59 shadow reclassification
    rides as a sensitivity variant that never touches the base coding.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE.parent / "fold_ledger.json"
# Two frozen baselines for the fragility gate. Both are inputs, never outputs, so
# the gate verdict is identical on every rerun and the double-run sha identity
# survives.
#
# The 129 execution chain appended its own record to the shared ledger at
# 2026-08-19T09:35:15Z, while this repair was in flight. The published pre-repair
# table was therefore computed on a ledger one record shorter than the current one,
# and comparing straight against it would blend two different causes. So the gate
# runs twice:
#   PRIOR_PUBLISHED  pre-repair coder, pre-129 ledger -- the table the campaign has
#                    been reading; the comparison mixes coder repair with ledger
#                    drift and is reported for continuity.
#   PRIOR_SAME_LEDGER pre-repair coder re-run on the CURRENT ledger -- the ledger is
#                    held fixed, so this comparison isolates the repair batch, and
#                    it is the one the gate's causal claim rests on.
# A crossing in EITHER trips the gate; that is the conservative reading.
PRIOR_TABLE = HERE / "mi_table_prior_20260819.json"
PRIOR_TABLE_SAME_LEDGER = HERE / "mi_table_prior_oldcoder_ledger277.json"
SEED = 20260819
N_PERM = 200

# R1: `sensitivity` is appended, not inserted. The convention coder resolves ties
# by earliest offset, so appending leaves every existing offset ordering intact and
# the field can only add evidence where a record had none.
TEXT_FIELDS = (
    "id",
    "status",
    "status_note",
    "mechanism",
    "bias_class",
    "prediction",
    "kill_condition",
    "result",
    "sensitivity",
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
    # R3: `spherical 5-design` and `5-design` were removed from this alternation on
    # 2026-08-19. A spherical 5-design is a cubature exactness property that many
    # carriers can hold; it is not evidence that the carrier is a Kerdock MUB. The
    # deletion moves exactly one record on this ledger (idx 38, which uses the phrase
    # to describe the residual it scores, not its own directions).
    ("kerdock_mub", r"kerdock|\bmub\b|mutually unbiased|phased[-_ ]hadamard|"
                    r"real[-_ ]mub|full ?129"),
    # R4: normalized-Gaussian / uniform-sphere probe directions ARE Haar-uniform on
    # the sphere; the alternation named the randomized-radial dialect but not this
    # one. Measured blast radius on this ledger: one record (idx 43).
    ("haar_random_spherical", r"\bhaar\b|random[-_ ]spherical|spherical[-_ ]random|"
                              r"randomized[-_ ]radial|random ?32,?256|row[-_ ]?blocked|"
                              r"randomly rotated|spherical sampling|\brqmc\b|"
                              r"kronecker lattice|cranley|great[-_ ]circle|"
                              r"random[-_ ]frame|normalized[-_ ]?gaussian sphere|"
                              r"uniform[-_ ]sphere"),
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
    # R2: the verb list was present-tense only, so a record reporting its payoff in
    # the past tense ("adjusted score improved 6.44%") fell through to whatever
    # currency happened to be named earlier in the record.
    ("adjusted_score",
     r"adjusted (?:score|mse|estimate)?\s*[\d.]+|adjusted [\d.]|"
     r"[\d.]+ ?x worse than|minimum-effect ratio|multiplier ?[\d.]|"
     r"adjusted score (?:falls|improve[sd]|drops|rises|worsen(?:s|ed)|ratio)|"
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
# 2026-08-19 repair batch: recodes the record-local regexes cannot reach
# --------------------------------------------------------------------------

HEX64 = re.compile(r"\b[0-9a-f]{64}\b")


def hash_identity_recodes(recs, carriers):
    """R5. A record that names another record's frozen artifact_hash is talking
    about that artifact. Identity beats vocabulary, so the naming record inherits
    the owner's carrier -- but only when its own text carries no carrier word at
    all, so this can never overrule a record's own claim.

    Fully mechanical: no record index appears in this function. Measured blast
    radius on the 2026-08-19 ledger is one record.
    """
    owner = {}
    for i, r in enumerate(recs):
        h = str(r.get("artifact_hash") or "").strip().lower()
        if h:
            owner.setdefault(h, i)
    out = {}
    for i, r in enumerate(recs):
        if carriers[i] != "none":
            continue
        for tok in sorted(set(HEX64.findall(blob(r)))):
            j = owner.get(tok)
            if j is not None and j != i and carriers[j] != "none":
                out[i] = (carriers[j],
                          "names artifact_hash %s... which idx %d owns (%s)"
                          % (tok[:8], j, recs[j]["id"]))
                break
    return out


# R6/R7. Explicit recodes, one row per record, each carrying (a) the axis, (b) the
# new value, (c) an evidence class, (d) a literal substring that MUST be present in
# the record -- asserted at build time, so a ledger edit that removes the evidence
# breaks the build instead of leaving a stale label behind -- and (e) the argument.
#
# Two general rules were written, measured and REJECTED rather than shipped, and
# the rejections are recorded here because they are the reason these four rows are
# hand-written instead of derived:
#   * a mnemonic-lineage rule ("a record naming mXX inherits mXX's carrier") would
#     recode 14 records and produces obvious false positives, e.g. idx 78
#     (m79_common_axis_output_shrinkage) inheriting a Kerdock carrier from m71.
#   * a global zonal-before-haar priority reorder would flip four records, and one
#     of them (idx 251) replaces Gauss-Hermite nodes BY spherical-radial ones, so
#     the reorder would code it to the carrier it discards.
EXPLICIT_RELABELS = [
    dict(idx=74, axis="carrier", value="kerdock_mub",
         evidence_class="package_lineage",
         must_contain="run the sealed m76 package once",
         argument=(
             "M76 is idx 73 (m76_validator_fallback_v3), whose sealed archive is the "
             "same tarball idx 183 scored. This launcher's payload is therefore the "
             "Kerdock v3 package; the record names the package rather than the "
             "geometry, which is why no carrier word appears in it.")),
    dict(idx=39, axis="carrier", value="zonal_harmonic",
         evidence_class="lineage_only",
         must_contain="terminates the jspace estimator family",
         argument=(
             "The exactly-once structural inversion of idx 38's JSpace subspace "
             "choice, sharing its exact-mean high-degree control atoms. The record "
             "carries no zonal vocabulary of its own, so this is the weakest row in "
             "the batch: it is lineage-level evidence, not record-local evidence, "
             "and it is reported as such wherever it is used.")),
    dict(idx=106, axis="carrier", value="zonal_harmonic",
         evidence_class="construction_over_ambient_frame",
         must_contain="spherical zonals",
         argument=(
             "The carrier this record constructs is the zonal band; the Haar frame "
             "is the substrate the band is averaged over. The coder took the "
             "aggregation substrate for the carrier because the haar alternation is "
             "tested first.")),
    dict(idx=183, axis="mechanism_family", value="compiler_schedule",
         evidence_class="external_source_observed",
         must_contain="frozen kerdock m71 v3 entrypoint",
         argument=(
             "OBSERVED in experiments/v31_guards/package_source/ this session: "
             "kerdock_v3_estimator.py lines 134-136 override _sample_matmul to "
             "self._winograd.multiply(), where self._winograd is a "
             "RowBlockedBatchedWinograd (imported line 15, constructed lines 60 and "
             "87) at BLOCK_ROWS = 4096 (row_blocked_winograd.py line 20). The "
             "deployed route is the row-blocked Winograd schedule. The coder read "
             "design_frame off the word Kerdock in the record's id; the evidence "
             "that contradicts it lives in the estimator source, not in the record, "
             "which is why no regex can reach it.")),
]

# PRE-REGISTERED 2026-08-19, written into this file BEFORE the repaired coder was
# run (plan item INV-R3-8). idx 38 builds its control directions from the top
# eigendirections of a K=4 fused-VJP pilot estimate of E[J^T J]. That construction
# admits three readings, so all three are accepted in advance and none of them can
# be selected after the fact:
DOCTRINE_CARRIER_38_ACCEPT = {"kerdock_mub", "zonal_harmonic", "data_adaptive"}
# Disposition of the fourth possibility, fixed in advance at the same time: if the
# repaired coder emits `none` for idx 38, that is recorded as an AXIS-EXPRESSIVENESS
# disagreement -- the carrier axis has no data_adaptive level to emit -- and NOT as
# a coder defect. The regexes are not retuned in response, and idx 38 gets no
# explicit relabel.


# --------------------------------------------------------------------------
# W0.4 -- buffer ownership. PRE-REGISTERED CODING RULE.
#
# Written into this file before any record was coded on this axis and not revised
# afterwards. Three values, from the plan's own wording:
#
#   caller_owned_inplace           the text asserts writes into a caller-owned or
#                                  pre-existing activation/output buffer (in-place
#                                  overwrite, out=, preallocated destination)
#   separate_workspace_or_pingpong the text asserts a transient / workspace /
#                                  ping-pong / double-buffer allocation on the
#                                  active path
#   unstated                       otherwise
#
# MASKING: the labeller reads `mechanism` and `bias_class` only. `status`,
# `result`, `sensitivity` and the outcome are not in scope, so the coding cannot
# be steered by knowing which records lived.
#
# MANUAL-PASS CRITERIA, also fixed in advance:
#   M1  a record where BOTH families fire is adjudicated to the family its own
#       first-named active-path mechanism belongs to, and the adjudication is
#       recorded in OWNERSHIP_MANUAL with the quote that settles it;
#   M2  a match inside a quoted candidate id or a quoted prior record is not this
#       record's own assertion and is struck;
#   M3  a match on an English idiom rather than a buffer ("in place of X") is not
#       an assertion and is struck -- handled in the regex by a lookahead;
#   M4  naming the ownership dimension without asserting a value ("alias-liveness
#       variants") stays `unstated`; the axis records assertions, not topics.
# --------------------------------------------------------------------------

OWNERSHIP_FIELDS = ("mechanism", "bias_class")
OWNERSHIP_INPLACE = re.compile(
    r"in[- ]?place\b(?!\s+of\b)|out=|caller[- ]owned|owned activation|"
    r"activation backing|one[- ]buffer|buffer ownership|overwrit|"
    r"pre[- ]?allocat|destination buffer")
OWNERSHIP_WORKSPACE = re.compile(
    r"workspace|ping[- ]?pong|double[- ]?buffer|scratch|staging buffer|"
    r"separate buffer|transient (?:buffer|workspace|allocation)")

OWNERSHIP_MANUAL = {
    46: ("caller_owned_inplace", "M1",
         "both families fire; the record's own first-named active-path mechanism is "
         "'legal setup-preallocated out= buffers', and 'sequential scratch' is one of "
         "the alternatives it separately tests afterwards"),
    264: ("unstated", "M2",
          "the only match is 'preallocated_strassen_winograd', which is another "
          "candidate's id quoted inside a re-audit of that candidate's kill basis, "
          "not an assertion about this record's own active path"),
}

# Known misses of the frozen rule, found by reading the coding output AFTER the
# rule was run. They are DISCLOSED and NOT APPLIED: silently repairing a
# pre-registered rule once its output is visible is the failure the pre-registration
# exists to prevent. Neither can change the acceptance verdict, which fails on
# coverage by roughly a factor of thirty.
OWNERSHIP_KNOWN_MISSES = [
    (250, "gm_m116_streams",
     "asserts an in-place implementation as a camel-case class name "
     "('implemented as GroupedInplaceL3'). The word-boundary that keeps the rule "
     "off the idiom 'in place of' also keeps it off a name with a letter directly "
     "after 'place'. A later pass should allow the camel-case form; this pass does "
     "not touch the frozen rule."),
]


def code_ownership(rec, idx):
    txt = " ‖ ".join(field_text(rec, k) for k in OWNERSHIP_FIELDS).lower()
    if idx in OWNERSHIP_MANUAL:
        val, rule, why = OWNERSHIP_MANUAL[idx]
        return val, "manual_%s" % rule
    a = bool(OWNERSHIP_INPLACE.search(txt))
    b = bool(OWNERSHIP_WORKSPACE.search(txt))
    if a and b:
        # Deliberately a visible level rather than a silent tie-break: manual-pass
        # criterion M1 says a both-families record must be adjudicated by hand, so a
        # future one surfaces in the distribution instead of being guessed at.
        return "ambiguous_unadjudicated", "both_families"
    if a:
        return "caller_owned_inplace", "regex"
    if b:
        return "separate_workspace_or_pingpong", "regex"
    return "unstated", "regex"


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


# The pre-registered widening for idx 38 is applied here, not inline, so the
# accept set is visible next to the table it modifies.
DOCTRINE_CARRIER[38] = set(DOCTRINE_CARRIER_38_ACCEPT)


def validate_against_doctrine(nodes, recoded_idx):
    """`recoded_idx` maps axis -> set of record indices whose value was set by the
    2026-08-19 repair batch rather than by a regex over the record. Those records
    can no longer test the regexes, so each axis reports a second agreement rate
    over the untouched records; that is the number that stays an independent check.
    """
    by_idx = {n["idx"]: n for n in nodes}
    report = {}
    for axis, truth in (("convention", {k: {v} for k, v in DOCTRINE_CONVENTION.items()}),
                        ("carrier", DOCTRINE_CARRIER),
                        ("precision", DOCTRINE_PRECISION)):
        touched = recoded_idx.get(axis, set())
        agree, disagree = 0, []
        n_indep = n_indep_agree = 0
        for idx, allowed in sorted(truth.items()):
            got = by_idx[idx]["axes"][axis]
            ok = got in allowed
            if idx not in touched:
                n_indep += 1
                n_indep_agree += 1 if ok else 0
            if ok:
                agree += 1
            else:
                disagree.append({
                    "idx": idx,
                    "id": by_idx[idx]["id"],
                    "doctrine": sorted(allowed),
                    "coded": got,
                    "class": ("axis_expressiveness" if (idx == 38 and got == "none")
                              else "coder_vs_lineage"),
                    "matched_families": by_idx[idx]["axis_evidence"].get(
                        "carrier_families_matched" if axis == "carrier"
                        else "precision_tokens_matched" if axis == "precision"
                        else "conventions_present"),
                })
        report[axis] = {
            "n_checked": len(truth),
            "n_agree": agree,
            "agreement": agree / len(truth),
            "n_checked_independent": n_indep,
            "n_agree_independent": n_indep_agree,
            "agreement_independent": (n_indep_agree / n_indep) if n_indep else None,
            "n_set_by_repair_batch": len(truth) - n_indep,
            "disagreements": disagree,
        }
    return report


def apply_repair_batch(recs, raw):
    """Apply R5 (mechanical, artifact-identity) then R6/R7 (explicit, evidence-
    asserted). Returns the recode log and the set of touched indices per axis."""
    carriers = [x["carrier"] for x in raw]
    log = []
    touched = defaultdict(set)

    for i, (val, why) in sorted(hash_identity_recodes(recs, carriers).items()):
        log.append({"idx": i, "id": recs[i]["id"], "axis": "carrier",
                    "from": raw[i]["carrier"], "to": val, "rule": "R5",
                    "evidence_class": "artifact_hash_identity", "evidence": why,
                    "argument": ("A frozen archive hash is an identity, not a "
                                 "vocabulary match: the record is describing that "
                                 "artifact, so it carries that artifact's carrier.")})
        raw[i]["carrier"] = val
        touched["carrier"].add(i)

    for row in EXPLICIT_RELABELS:
        i, axis = row["idx"], row["axis"]
        haystack = blob(recs[i])
        if row["must_contain"] not in haystack:
            raise AssertionError(
                "repair-batch evidence missing from idx %d (%s): %r"
                % (i, recs[i]["id"], row["must_contain"]))
        log.append({"idx": i, "id": recs[i]["id"], "axis": axis,
                    "from": raw[i][axis], "to": row["value"], "rule": "R6/R7",
                    "evidence_class": row["evidence_class"],
                    "evidence": row["must_contain"],
                    "argument": row["argument"]})
        raw[i][axis] = row["value"]
        touched[axis].add(i)

    return log, touched


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    recs = ledger["candidates"]

    raw = []
    for r in recs:
        outcome = code_outcome(r)
        carrier, carrier_matches = code_carrier(r)
        precision, prec_tokens = code_precision(r)
        convention, conv_present, conv_src = code_convention(r)
        killtype, kt_src = code_killtype(r, outcome)
        mech, mech_matches = code_mechanism_family(r)
        raw.append({"outcome": outcome, "carrier": carrier, "precision": precision,
                    "convention": convention, "killtype": killtype,
                    "mechanism_family": mech,
                    "ev": {"carrier_families_matched": carrier_matches,
                           "precision_tokens_matched": prec_tokens,
                           "conventions_present": conv_present,
                           "convention_source": conv_src,
                           "killtype_source": kt_src,
                           "mechanism_families_matched": mech_matches}})

    recode_log, recoded_idx = apply_repair_batch(recs, raw)
    recoded_by_idx = defaultdict(list)
    for row in recode_log:
        recoded_by_idx[row["idx"]].append(row)

    nodes = []
    for i, r in enumerate(recs):
        outcome = raw[i]["outcome"]
        carrier = raw[i]["carrier"]
        precision = raw[i]["precision"]
        convention = raw[i]["convention"]
        killtype = raw[i]["killtype"]
        mech = raw[i]["mechanism_family"]
        ownership, ownership_src = code_ownership(r, i)
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
            # Pre-registered W0.4 axis. It is carried on every node but is NOT a
            # door axis and NOT in MI_AXES; it is judged separately, in its own
            # permutation stream, against its own acceptance rule.
            "ownership": ownership,
            "axis_evidence": dict(
                raw[i]["ev"],
                ownership_source=ownership_src,
                repair_batch_recodes=recoded_by_idx.get(i, []),
            ),
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

    # ------------- W0.4: the pre-registered buffer-ownership axis ---------------
    # Its own permutation stream. Everything above consumed `rng` in exactly the
    # order the pre-repair build did, so the base table diffs cleanly against the
    # frozen prior; a new axis must not shift a single number in it.
    own_rng = random.Random(SEED)
    own_all = Counter(n["ownership"] for n in nodes)

    def _own_mi(sub_nodes, label):
        y = ["lived" if n["axes"]["outcome"] in WIN_OUTCOMES else "died"
             for n in sub_nodes]
        x = [n["ownership"] for n in sub_nodes]
        row = {"subset": label, "n_records": len(sub_nodes),
               "n_levels": len(set(x))}
        row.update(mi_with_null(y, x, own_rng))
        return row

    own_rows = [
        _own_mi(decided, "all decided records"),
        _own_mi([n for n in decided if n["idx"] not in (71, 72)],
                "twin pair dropped (the two records that motivated the axis)"),
    ]
    # The bar the plan set: not merely above the null sd, above the null MAXIMUM,
    # on the same record set and the same 200-shuffle null as the four coded axes.
    own_null_max_bar = max(
        r["null_max_bits"] for r in mi_rows
        if r["kind"] == "single" and r["target"] == "lived_vs_died"
        and r["axis"] != "killtype")
    n_unstated = own_all.get("unstated", 0)
    # Upper bound on what ANY field scope could reach: the same two lexicons run
    # over every field of every record, masking abandoned. It is reported because a
    # coverage failure under masking would otherwise be indistinguishable from a
    # coverage failure caused by masking.
    unmasked_stated = sum(
        1 for r in recs
        if OWNERSHIP_INPLACE.search(blob(r)) or OWNERSHIP_WORKSPACE.search(blob(r)))
    crit = {
        "i_rule_preregistered": True,
        "ii_masked_coding_all_records": len(nodes) == len(recs),
        "iii_mi_above_null_max": (own_rows[0]["mi_minus_null_mean_bits"]
                                  > own_null_max_bar),
        "iii_bar_null_max_bits": own_null_max_bar,
        "iii_observed_mi_minus_null_bits": own_rows[0]["mi_minus_null_mean_bits"],
        "iv_survives_dropping_71_and_72": (own_rows[1]["mi_minus_null_mean_bits"]
                                           > own_null_max_bar),
        "v_unstated_under_200": n_unstated <= 200,
        "v_unstated_count": n_unstated,
        "v_stated_count": len(nodes) - n_unstated,
        "v_unmasked_upper_bound_stated": unmasked_stated,
        "v_unmasked_upper_bound_unstated": len(recs) - unmasked_stated,
    }
    crit["accepted"] = bool(
        crit["i_rule_preregistered"] and crit["ii_masked_coding_all_records"]
        and crit["iii_mi_above_null_max"] and crit["iv_survives_dropping_71_and_72"]
        and crit["v_unstated_under_200"])
    ownership_axis = {
        "rule_scope_fields": list(OWNERSHIP_FIELDS),
        "distribution": dict(sorted(own_all.items(), key=lambda kv: (-kv[1], kv[0]))),
        "stated_records": [
            {"idx": n["idx"], "id": n["id"], "value": n["ownership"],
             "source": n["axis_evidence"]["ownership_source"],
             "outcome": n["axes"]["outcome"]}
            for n in nodes if n["ownership"] != "unstated"],
        "manual_adjudications": [
            {"idx": k, "value": v[0], "criterion": v[1], "reason": v[2]}
            for k, v in sorted(OWNERSHIP_MANUAL.items())],
        "known_misses_disclosed_not_applied": [
            {"idx": i, "id": nm, "reason": why}
            for i, nm, why in OWNERSHIP_KNOWN_MISSES],
        "mi": own_rows,
        "acceptance": crit,
        "twin_pair_check": {
            "idx_71": next(n["ownership"] for n in nodes if n["idx"] == 71),
            "idx_72": next(n["ownership"] for n in nodes if n["idx"] == 72),
            "separated": (next(n["ownership"] for n in nodes if n["idx"] == 71)
                          != next(n["ownership"] for n in nodes if n["idx"] == 72)),
        },
    }

    # ------------- attribution: which recode moved the carrier axis? ------------
    # The carrier axis is the one the repair batch touched most, and the standing
    # rule is that it must never rank a door. The counter-hypothesis worth testing
    # is that its movement is manufactured by the batch's WEAKEST row -- idx 39,
    # whose evidence is lineage-level rather than record-local. Each variant reverts
    # exactly one recode and recomputes the axis; each gets its own permutation
    # stream, so read the variants against each other, never against the main table.
    attr_variants = [({}, "all repairs in place (as shipped)")]
    pre_carrier = {}
    for row in recode_log:
        if row["axis"] == "carrier":
            pre_carrier[row["idx"]] = row["from"]
    # idx 43 moved through the R4 vocabulary repair rather than a recode row, so it
    # has no log entry; it is reverted here by its known pre-repair value.
    for n in nodes:
        if n["idx"] == 43 and n["axes"]["carrier"] == "haar_random_spherical":
            pre_carrier[43] = "none"
    for i, v in sorted(pre_carrier.items()):
        attr_variants.append(({i: v}, "revert idx %d (back to %s)" % (i, v)))
    attr_variants.append((dict(pre_carrier), "every carrier repair reverted"))

    carrier_attribution = []
    for override, label in attr_variants:
        entry = {"variant": label, "reverted": sorted(override), "rows": []}
        for tname in ("lived_vs_died", "outcome_5class"):
            if tname == "lived_vs_died":
                sub = decided
                y = ["lived" if n["axes"]["outcome"] in WIN_OUTCOMES else "died"
                     for n in sub]
            else:
                sub = nodes
                y = [n["axes"]["outcome"] for n in sub]
            x = [override.get(n["idx"], n["axes"]["carrier"]) for n in sub]
            r = {"target": tname}
            r.update(mi_with_null(y, x, random.Random(SEED)))
            entry["rows"].append(r)
        carrier_attribution.append(entry)

    # ------------- W0.5: the idx 59 shadow reclassification (SENSITIVITY) -------
    # The ledger is internally inconsistent on idx 59: its status codes to `pass`
    # here, while the kill-context index counts it among the three kills measured on
    # the full adjusted score (ratio .990674633 against a .99 gate). This variant
    # asks what the convention result would be if the kill reading were right. It is
    # a VARIANT: it never touches the base coding, and its own permutation stream
    # keeps it from touching the base numbers either.
    shadow_rng = random.Random(SEED)
    shadow_rows = []
    for tname in ("outcome_5class", "lived_vs_died"):
        if tname == "outcome_5class":
            sub = nodes
            base_y = [n["axes"]["outcome"] for n in sub]
            shadow_y = ["kill" if n["idx"] == 59 else n["axes"]["outcome"] for n in sub]
        else:
            sub = decided
            base_y = ["lived" if n["axes"]["outcome"] in WIN_OUTCOMES else "died"
                      for n in sub]
            shadow_y = ["died" if n["idx"] == 59 else
                        ("lived" if n["axes"]["outcome"] in WIN_OUTCOMES else "died")
                        for n in sub]
        x = [n["axes"]["convention"] for n in sub]
        base_row = dict(target=tname, variant="base", n_records=len(sub))
        base_row.update(mi_with_null(base_y, x, shadow_rng))
        sh_row = dict(target=tname, variant="idx59_shadow_died", n_records=len(sub))
        sh_row.update(mi_with_null(shadow_y, x, shadow_rng))
        shadow_rows.append({"target": tname, "base": base_row, "shadow": sh_row,
                            "delta_mi_minus_null_bits":
                                sh_row["mi_minus_null_mean_bits"]
                                - base_row["mi_minus_null_mean_bits"]})

    # ------------- fragility gate against the frozen prior table ---------------
    # INV2's falsifier adopted as policy: if ANY row's null-corrected MI crosses its
    # null maximum in EITHER direction between the pre-repair and post-repair
    # tables, the table is too fragile to rank doors and every MI-ranked candidate
    # drops to unranked. The comparison baseline is a frozen input file, so this
    # verdict is identical on every rerun.
    def _compare(prior_path, label, isolates):
        out = {"label": label, "baseline_file": prior_path.name,
               "isolates": isolates, "rows": [], "crossings": [],
               "available": prior_path.exists()}
        if not out["available"]:
            return out
        pj = json.loads(prior_path.read_text(encoding="utf-8"))
        out["baseline_n_records"] = pj["meta"]["n_records"]
        prior = {(r["target"], r["axis"]): r for r in pj["mi_table"]}
        for r in mi_rows:
            p = prior.get((r["target"], r["axis"]))
            if p is None:
                continue
            was_above = p["mi_minus_null_mean_bits"] > p["null_max_bits"]
            now_above = r["mi_minus_null_mean_bits"] > r["null_max_bits"]
            row = {
                "target": r["target"], "axis": r["axis"], "kind": r["kind"],
                "prior_mi_minus_null_bits": p["mi_minus_null_mean_bits"],
                "new_mi_minus_null_bits": r["mi_minus_null_mean_bits"],
                "delta_bits": r["mi_minus_null_mean_bits"] - p["mi_minus_null_mean_bits"],
                "prior_null_sd_bits": p["null_sd_bits"],
                "delta_in_prior_null_sd": (
                    (r["mi_minus_null_mean_bits"] - p["mi_minus_null_mean_bits"])
                    / p["null_sd_bits"]) if p["null_sd_bits"] else None,
                "prior_null_max_bits": p["null_max_bits"],
                "new_null_max_bits": r["null_max_bits"],
                "prior_above_null_max": was_above,
                "new_above_null_max": now_above,
                "crossed": was_above != now_above,
                "prior_p": p["p_value"], "new_p": r["p_value"],
                "is_construction_artifact": "confound" in r,
            }
            out["rows"].append(row)
            if row["crossed"]:
                out["crossings"].append(row)
        real = [c for c in out["crossings"] if not c["is_construction_artifact"]]
        out["n_rows_compared"] = len(out["rows"])
        out["n_crossings_total"] = len(out["crossings"])
        out["n_crossings_excluding_artifacts"] = len(real)
        out["verdict"] = "TRIPPED" if real else "HELD"
        return out

    comparisons = [
        _compare(PRIOR_TABLE_SAME_LEDGER,
                 "same coder, current ledger (isolates the repair batch)",
                 "repair batch only"),
        _compare(PRIOR_TABLE,
                 "published pre-repair table (pre-129 ledger)",
                 "repair batch AND one appended ledger record"),
    ]
    tripped = [c for c in comparisons
               if c.get("verdict") == "TRIPPED" or not c["available"]]
    fragility = {
        "comparisons": comparisons,
        "gate": "TRIPPED" if tripped else "HELD",
        "rows": comparisons[0]["rows"] if comparisons[0]["available"] else [],
        "n_rows_compared": comparisons[0].get("n_rows_compared", -1),
        "n_crossings_total": comparisons[0].get("n_crossings_total", -1),
        "n_crossings_excluding_artifacts":
            comparisons[0].get("n_crossings_excluding_artifacts", -1),
        "baseline": str(PRIOR_TABLE_SAME_LEDGER),
    }
    fragility["consequence"] = (
        "At least one axis crossed its null maximum, so the table is too fragile to "
        "rank doors and every MI-ranked candidate drops to unranked."
        if tripped else
        "No axis crossed its null maximum in either direction, in either comparison. "
        "MI ranking survives the repair batch -- subject to the standing rule that "
        "carrier MI never ranks a door, which is independent of this gate.")

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

    validation = validate_against_doctrine(nodes, recoded_idx)

    meta = {
        "generated_by": str(Path(__file__).resolve()),
        "ledger": str(LEDGER),
        # The ledger is a live, shared file: the 129 chain appended to it while this
        # repair was in flight. Recording its digest makes the double-run identity
        # check detect a concurrent ledger write instead of blaming the code.
        "ledger_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
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
        "repair_batch_20260819": recode_log,
        "ownership_axis_status": (
            "ACCEPTED as a fifth axis" if ownership_axis["acceptance"]["accepted"]
            else "REJECTED by its own pre-registered acceptance rule; coded and "
                 "reported, never used to rank anything"),
        "fragility_gate": fragility["gate"],
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
        "ownership_axis": ownership_axis,
        "carrier_repair_attribution": carrier_attribution,
        "convention_shadow_idx59": shadow_rows,
        "fragility_gate": fragility,
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
                 door_dir_counts, axis_dists, concentrations, robustness,
                 recode_log, ownership_axis, shadow_rows, fragility,
                 carrier_attribution)

    print("records:", len(nodes))
    print("outcome distribution:", axis_dists["outcome"])
    print("decided:", len(decided), "lived base rate: %.4f" % base_rate)
    print("doors:", len(doors), dict(door_axis_counts))
    print("repair batch: %d recodes" % len(recode_log))
    for row in recode_log:
        print("  idx %3d %-40s %s: %s -> %s  [%s]"
              % (row["idx"], row["id"], row["axis"], row["from"], row["to"],
                 row["evidence_class"]))
    print("ownership axis: %s | unstated %d/%d | MI-null %.4f vs bar %.4f | "
          "drop-71/72 %.4f | ACCEPTED=%s"
          % (ownership_axis["distribution"],
             ownership_axis["acceptance"]["v_unstated_count"], len(nodes),
             ownership_axis["acceptance"]["iii_observed_mi_minus_null_bits"],
             ownership_axis["acceptance"]["iii_bar_null_max_bits"],
             ownership_axis["mi"][1]["mi_minus_null_mean_bits"],
             ownership_axis["acceptance"]["accepted"]))
    print("ledger sha256:", meta["ledger_sha256"])
    print("fragility gate: %s" % fragility["gate"])
    for c in fragility["comparisons"]:
        print("  %-52s baseline n=%s rows=%s crossings=%s (excl artifacts %s) -> %s"
              % (c["label"], c.get("baseline_n_records", "?"),
                 c.get("n_rows_compared", "?"), c.get("n_crossings_total", "?"),
                 c.get("n_crossings_excluding_artifacts", "?"),
                 c.get("verdict", "BASELINE MISSING")))
    for s in shadow_rows:
        print("idx59 shadow [%s]: convention MI-null %.4f -> %.4f (delta %.4f), "
              "p %.4f -> %.4f"
              % (s["target"], s["base"]["mi_minus_null_mean_bits"],
                 s["shadow"]["mi_minus_null_mean_bits"],
                 s["delta_mi_minus_null_bits"], s["base"]["p_value"],
                 s["shadow"]["p_value"]))
    for tname in ("lived_vs_died", "outcome_5class"):
        print("top MI rows [%s]:" % tname)
        for r in [x for x in mi_rows if x["target"] == tname][:6]:
            print("  %-40s MI=%.4f null=%.4f+-%.4f adj=%.4f p=%.4f%s"
                  % (r["axis"], r["mi_bits"], r["null_mean_bits"], r["null_sd_bits"],
                     r["mi_minus_null_mean_bits"], r["p_value"],
                     "  [artifact]" if "confound" in r else ""))


def write_report(meta, mi_rows, nodes, doors, top10, door_axis_counts,
                 door_dir_counts, axis_dists, concentrations, robustness,
                 recode_log, ownership_axis, shadow_rows, fragility,
                 carrier_attribution):
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
    A("## The 2026-08-19 repair batch")
    A("")
    _n_mech = sum(1 for r in recode_log if r["rule"] == "R5")
    _n_expl = len(recode_log) - _n_mech
    A("The coder's known defects were repaired in one edit and the whole table was")
    A("rebuilt once, because at these sample sizes a single-record change moves a")
    A("statistic by about a null standard deviation and cell-by-cell reporting would")
    A("invite reading noise as movement. Three of the repairs are changes to the")
    A("regexes themselves and generalise to any future record; one is a mechanical")
    A("identity rule that fires here on %d record; and %d are explicit per-record"
      % (_n_mech, _n_expl))
    A("recodes carrying evidence no regex over the record could reach. All %d recodes"
      % len(recode_log))
    A("are listed below. Every explicit one asserts its evidence string against the")
    A("record at build time, so a ledger edit that removes the evidence breaks the")
    A("build rather than leaving a stale label in place.")
    A("")
    A("| idx | id | axis | from | to | evidence class |")
    A("| ---: | --- | --- | --- | --- | --- |")
    for row in recode_log:
        A("| %d | `%s` | %s | %s | %s | %s |"
          % (row["idx"], row["id"], row["axis"], row["from"], row["to"],
             row["evidence_class"]))
    A("")
    for row in recode_log:
        A("- **idx %d `%s` (%s -> %s)**, evidence `%s`. %s"
          % (row["idx"], row["id"], row["from"], row["to"], row["evidence"],
             row["argument"]))
    A("")
    A("The regex-level repairs, with their measured blast radius on this ledger:")
    A("")
    A("- `spherical 5-design` / `5-design` deleted from the kerdock_mub alternation.")
    A("  A spherical 5-design is a cubature exactness property, not a claim that the")
    A("  carrier is a Kerdock MUB. Moves one record.")
    A("- normalized-Gaussian / uniform-sphere direction vocabulary added to the haar")
    A("  alternation. Normalized Gaussian directions are Haar-uniform on the sphere.")
    A("  Moves one record.")
    A("- `sensitivity` added to the scanned fields, and the adjusted-score currency")
    A("  taught the past-tense verbs improved/worsened. Measured effect on this")
    A("  ledger: zero records change value. Three records carry a sensitivity field,")
    A("  and in the one that also has no result field the currency is still decided")
    A("  earlier in the record. The defect was real and is now closed, but on this")
    A("  ledger it was IMMATERIAL, which is what the plan's own kill clause for it")
    A("  asked to be recorded rather than a fix claimed.")
    A("")
    A("## Does the coding agree with the doctrine?")
    A("")
    A("The kill-context index was extracted from the same ledger by a different route,")
    A("so it is an independent check on these regexes. Records it names explicitly:")
    A("")
    A("A record whose value was set by the repair batch can no longer test the")
    A("regexes -- it agrees by construction. The right-hand columns therefore repeat")
    A("the count over only the records the batch did not touch, and that is the number")
    A("that remains an independent check.")
    A("")
    A("| axis | checked | agree | rate | set by repair batch | independent checked | "
      "independent agree | independent rate |")
    A("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for ax, v in meta["doctrine_validation"].items():
        A("| %s | %d | %d | %.3f | %d | %d | %d | %s |"
          % (ax, v["n_checked"], v["n_agree"], v["agreement"],
             v["n_set_by_repair_batch"], v["n_checked_independent"],
             v["n_agree_independent"],
             "%.3f" % v["agreement_independent"]
             if v["agreement_independent"] is not None else "n/a"))
    A("")
    A("idx 38 carries a pre-registered three-way accept set")
    A("(kerdock_mub / zonal_harmonic / data_adaptive), written into the build script")
    A("before the repaired coder was run. Its directions come from the top")
    A("eigendirections of a pilot estimate of the Jacobian Gram, so the reading was")
    A("genuinely open, and the disposition of a fourth outcome was fixed at the same")
    A("time: a coded `none` is an AXIS-EXPRESSIVENESS disagreement -- the carrier axis")
    A("has no data_adaptive level to emit -- and not a coder defect, and the regexes")
    A("are not retuned in response. Each disagreement below carries that class.")
    A("")
    for ax, v in meta["doctrine_validation"].items():
        if not v["disagreements"]:
            continue
        A("Disagreements on `%s`:" % ax)
        A("")
        for d in v["disagreements"]:
            A("- idx %d `%s`: doctrine says %s, coded `%s` [%s] (evidence found in "
              "the record: %s)" % (d["idx"], d["id"], "/".join(d["doctrine"]),
                                   d["coded"], d["class"],
                                   d["matched_families"] or "none"))
        A("")
    A("A `coder_vs_lineage` disagreement is a case where the doctrine's extractor")
    A("assigned an axis from LINEAGE and this coder found no such words in the record")
    A("itself. Outside the explicitly listed repair-batch rows the coder stays")
    A("conservative on purpose: an axis with no evidence in the record is coded")
    A("`none`/`unstated` rather than inherited from a parent candidate.")
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
    A("## Fragility gate")
    A("")
    A("Adopted as policy from INV2's falsifier and binding on everything downstream:")
    A("if any row's null-corrected MI crosses its own null maximum in EITHER direction")
    A("between the pre-repair and post-repair tables, the table is too fragile to rank")
    A("doors and every MI-ranked candidate drops to unranked.")
    A("")
    A("The 129 execution chain appended its own record to the shared ledger while this")
    A("repair was in flight, so the published pre-repair table was computed on a")
    A("ledger one record shorter than this one. Comparing straight against it would")
    A("blend a coder change with a data change. The gate therefore runs against two")
    A("frozen baselines, both of which are inputs and never outputs, so the verdict is")
    A("identical on every rerun.")
    A("")
    A("| comparison | baseline file | records | what it isolates | rows | crossings | "
      "crossings excl. artifacts | verdict |")
    A("| --- | --- | ---: | --- | ---: | ---: | ---: | --- |")
    for c in fragility.get("comparisons", []):
        if not c.get("available"):
            A("| %s | %s | - | %s | - | - | - | BASELINE MISSING |"
              % (c["label"], c["baseline_file"], c["isolates"]))
            continue
        A("| %s | `%s` | %d | %s | %d | %d | %d | %s |"
          % (c["label"], c["baseline_file"], c["baseline_n_records"], c["isolates"],
             c["n_rows_compared"], c["n_crossings_total"],
             c["n_crossings_excluding_artifacts"], c["verdict"]))
    A("")
    A("**GATE: %s.** %s" % (fragility.get("gate", "unknown"),
                            fragility.get("consequence", "")))
    A("")
    A("Every row of the repair-isolating comparison, both targets, sorted by absolute")
    A("movement. `delta / prior null sd` is the movement measured in units of the")
    A("prior row's own permutation noise; anything under 1 is inside the instrument's")
    A("resolution.")
    A("")
    A("| target | axis | prior MI - null | new MI - null | delta | delta / prior null sd | "
      "prior null max | new null max | prior p | new p | crossed |")
    A("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for r in sorted(fragility.get("rows", []),
                    key=lambda x: (x["target"], -abs(x["delta_bits"]), x["axis"])):
        A("| %s | %s | %.4f | %.4f | %+.4f | %s | %.4f | %.4f | %.4f | %.4f | %s |"
          % (r["target"], r["axis"], r["prior_mi_minus_null_bits"],
             r["new_mi_minus_null_bits"], r["delta_bits"],
             ("%+.2f" % r["delta_in_prior_null_sd"])
             if r["delta_in_prior_null_sd"] is not None else "n/a",
             r["prior_null_max_bits"], r["new_null_max_bits"],
             r["prior_p"], r["new_p"],
             "YES" if r["crossed"] else ""))
    A("")
    A("Two things the gate does not say, stated so its verdict is not read as more")
    A("than it is. First, on this ledger no non-artifact row sat above its null")
    A("maximum on EITHER side of the repair, so the only direction in which the gate")
    A("could actually have tripped was upward; a held gate here means nothing rose")
    A("through the ceiling, not that the table is two-sided stable. Second, the")
    A("standing rule is independent of the gate and unaffected by its holding: carrier")
    A("MI fails leave-one-win-out on a four-win ledger and must never rank a door.")
    A("")
    A("### Which recode moved the carrier axis")
    A("")
    A("The carrier axis absorbed most of the batch and produced its largest movement")
    A("-- +1.17 prior null standard deviations on the 5-class target, landing 0.0038")
    A("bits under its own null maximum, the closest anything came to tripping the")
    A("gate. The counter-hypothesis worth testing is that the movement was")
    A("manufactured by the batch's weakest row, idx 39, whose evidence is")
    A("lineage-level rather than record-local. Each variant below reverts exactly one")
    A("recode; each has its own permutation stream, so read them against each other")
    A("and never against the main table.")
    A("")
    A("| variant | target | MI - null | p | null max |")
    A("| --- | --- | ---: | ---: | ---: |")
    for e in carrier_attribution:
        for r in e["rows"]:
            A("| %s | %s | %.4f | %.4f | %.4f |"
              % (e["variant"], r["target"], r["mi_minus_null_mean_bits"],
                 r["p_value"], r["null_max_bits"]))
    A("")
    A("The counter-hypothesis fails, and the honest reading cuts the other way. The")
    A("movement is carried almost entirely by idx 73, the one recode resting on a")
    A("mechanical identity -- it names the frozen artifact hash that idx 183 scored --")
    A("while reverting the lineage-only idx 39 barely moves the axis at all. So the")
    A("batch's best-evidenced row is also its most consequential one, which is the")
    A("right way round. But note what that means: idx 73 is one of only four wins in")
    A("the ledger, and moving a single win between carrier values shifts the axis by")
    A("more than a null standard deviation. That is the same one-record fragility that")
    A("disqualified carrier MI from ranking doors, measured again from a new")
    A("direction, and it is a reason to keep that disqualification rather than to")
    A("revisit it.")
    A("")
    A("## The buffer-ownership axis (pre-registered, W0.4)")
    A("")
    A("The four coded axes cannot separate idx 71 from idx 72: identical on all four,")
    A("opposite outcomes, and what differs between them is who owns the activation")
    A("buffer. This section asks whether that variable can be read off the ledger at")
    A("all. The coding rule, its field scope and its manual-pass criteria were written")
    A("into the build script before any record was coded on this axis, and were not")
    A("revised afterwards.")
    A("")
    A("Scope: the labeller reads `%s` only. Status, result, sensitivity and outcome"
      % "` and `".join(ownership_axis["rule_scope_fields"]))
    A("are out of scope, so the coding cannot be steered by knowing which records")
    A("lived.")
    A("")
    A("Distribution: %s"
      % ", ".join("%s=%d" % kv for kv in ownership_axis["distribution"].items()))
    A("")
    A("| criterion | requirement | result | verdict |")
    A("| --- | --- | --- | --- |")
    c = ownership_axis["acceptance"]
    A("| i | rule pre-registered before coding | written into the build script | %s |"
      % ("PASS" if c["i_rule_preregistered"] else "FAIL"))
    A("| ii | masked coding across all records | %d of %d coded | %s |"
      % (meta["n_records"], meta["n_records"],
         "PASS" if c["ii_masked_coding_all_records"] else "FAIL"))
    A("| iii | MI - null above the null MAXIMUM of the coded axes | %.4f vs bar %.4f | %s |"
      % (c["iii_observed_mi_minus_null_bits"], c["iii_bar_null_max_bits"],
         "PASS" if c["iii_mi_above_null_max"] else "FAIL"))
    A("| iv | survives dropping idx 71 and idx 72 | %.4f vs bar %.4f | %s |"
      % (ownership_axis["mi"][1]["mi_minus_null_mean_bits"],
         c["iii_bar_null_max_bits"],
         "PASS" if c["iv_survives_dropping_71_and_72"] else "FAIL"))
    A("| v | unstated bucket at most about 200 | %d unstated, %d stated | %s |"
      % (c["v_unstated_count"], c["v_stated_count"],
         "PASS" if c["v_unstated_under_200"] else "FAIL"))
    A("")
    A("**Verdict: %s.**" % ("ACCEPTED" if c["accepted"] else "REJECTED"))
    A("")
    A("The decisive criterion is coverage, and it is decided before any statistic is")
    A("read: %d of %d records state a buffer-ownership discipline in the fields the"
      % (c["v_stated_count"], meta["n_records"]))
    A("masked rule may read. Running the same two lexicons over EVERY field of every")
    A("record -- masking abandoned, which is the most permissive scope that could ever")
    A("exist -- reaches only %d stated and %d unstated, so the shortfall is a property"
      % (c["v_unmasked_upper_bound_stated"], c["v_unmasked_upper_bound_unstated"]))
    A("of the ledger, not of the masking. At most about 200 unstated means at least")
    A("%d records must state the discipline: the masked coding reaches %d of that,"
      % (meta["n_records"] - 200, c["v_stated_count"]))
    A("and the unmasked ceiling reaches %d."
      % c["v_unmasked_upper_bound_stated"])
    A("")
    A("| subset | n | levels | MI (bits) | null mean | null sd | null max | MI - null | p |")
    A("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in ownership_axis["mi"]:
        A("| %s | %d | %d | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f |"
          % (r["subset"], r["n_records"], r["n_levels"], r["mi_bits"],
             r["null_mean_bits"], r["null_sd_bits"], r["null_max_bits"],
             r["mi_minus_null_mean_bits"], r["p_value"]))
    A("")
    tw = ownership_axis["twin_pair_check"]
    A("Validity check on the rule itself: it must at minimum separate the pair that")
    A("motivated it. idx 71 codes `%s`, idx 72 codes `%s`, separated: %s."
      % (tw["idx_71"], tw["idx_72"], "yes" if tw["separated"] else "NO"))
    A("")
    A("Records that state an ownership discipline:")
    A("")
    A("| idx | id | value | source | outcome |")
    A("| ---: | --- | --- | --- | --- |")
    for s in ownership_axis["stated_records"]:
        A("| %d | `%s` | %s | %s | %s |"
          % (s["idx"], s["id"], s["value"], s["source"], s["outcome"]))
    A("")
    A("Manual-pass adjudications, each with the criterion it was made under:")
    A("")
    for m in ownership_axis["manual_adjudications"]:
        A("- idx %d -> `%s` (%s): %s" % (m["idx"], m["value"], m["criterion"],
                                         m["reason"]))
    A("")
    A("Known misses of the frozen rule, disclosed and deliberately NOT applied --")
    A("repairing a pre-registered rule once its output is visible is the failure the")
    A("pre-registration exists to prevent, and adding every miss listed here would")
    A("still leave the stated count an order of magnitude under the %d records the"
      % (meta["n_records"] - 200))
    A("coverage criterion demands:")
    A("")
    for m in ownership_axis["known_misses_disclosed_not_applied"]:
        A("- idx %d `%s`: %s" % (m["idx"], m["id"], m["reason"]))
    A("")
    A("What this result is, stated at its earned level. It is not evidence that buffer")
    A("ownership fails to decide outcomes -- idx 71 and idx 72 are one measured")
    A("counterexample to that, and the axis does separate them. It is evidence that")
    A("the LEDGER does not record the variable: the discipline is stated in the")
    A("mechanism of about one record in %d and is otherwise mentioned, if at all, in"
      % round(meta["n_records"] / max(1, c["v_stated_count"])))
    A("results written after the fact. The plan's own third cited example,")
    A("idx 48's transient workspace and activation overlap, sits in that record's")
    A("`result` field and is invisible to a masked coder by construction -- masking")
    A("the outcome also masks the place this campaign happens to discuss ownership.")
    A("The actionable consequence is a predeclaration-time one: buffer ownership")
    A("belongs in the fold_search REQUIRED_FIELDS, declared before a run, where it is")
    A("both readable and unable to be written with the outcome already known. Coding")
    A("it after the fact cannot recover it.")
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
    A("## The convention governor")
    A("")
    A("Round law, adopted 2026-08-19. Two kinds of move exist in this campaign and")
    A("they are denominated in different currencies. Conflating them is how a")
    A("bookkeeping correction gets spent as though it were a discovery.")
    A("")
    A("**An EVIDENCE move changes what the ledger knows about a result that already")
    A("exists.** Re-pricing a verdict out of one currency into another is the type")
    A("case: the run happened, the numbers are unchanged, and what changes is which")
    A("wall the outcome is measured against. Evidence moves cost no compute, consume")
    A("no one-shot gate, and are reversible -- the prior pricing stays in the record.")
    A("Their risk is not spend, it is self-service: an evidence move must be legal")
    A("under a rule that was fixed before the result was seen, or it is just moving")
    A("the goalposts, and the write-up has to say which rule and when it was fixed.")
    A("")
    A("**A DESIGN move changes the estimator.** Carrier flips and mechanism-family")
    A("flips are design moves: they produce a different program, so they need a run to")
    A("say anything, and the run consumes a predeclared gate under kill finality.")
    A("Design moves are irreversible in the ledger's own bookkeeping.")
    A("")
    A("The measured basis for the rule is in the tables above. Convention -- the")
    A("currency a verdict was priced in -- is the strongest real single axis on the")
    A("5-class outcome and is null on lived/died. The ledger knows which wall a")
    A("candidate hit; it does not know whether the idea was good. So convention is a")
    A("gate a candidate reached, not a design knob a candidate can be turned toward,")
    A("and the adjusted_score cell's high survival lift is largely survivorship: a")
    A("record only reaches that coding after it has already passed cost, memory,")
    A("parity and legality. That lift must never be quoted as a reason to spend on a")
    A("design move.")
    A("")
    A("Three consequences, stated so they can be checked rather than believed:")
    A("")
    A("1. A kill made at a wall that has since been retired or re-ruled is")
    A("   re-priceable evidence, not a dead idea, and re-pricing it is free.")
    A("2. A design move may not be justified by an MI ranking on the convention axis,")
    A("   because that axis carries no lived/died information; and it may never be")
    A("   justified by an MI ranking on the carrier axis at all, which fails")
    A("   leave-one-win-out on a four-win ledger.")
    A("3. Recodes of this instrument are themselves evidence moves and are held to the")
    A("   same standard: every one is listed with its evidence class, the two general")
    A("   rules that were measured and rejected are recorded next to the four that")
    A("   were kept, and the doctrine agreement rate is reported over the untouched")
    A("   records so the check does not quietly become circular.")
    A("")
    A("### The governor's own fragile record: the idx 59 shadow")
    A("")
    A("The rule above rests on the convention axis, so the axis was attacked at its")
    A("weakest point. The ledger is internally inconsistent about idx 59: its status")
    A("codes to `pass` here, while the kill-context index counts it among the three")
    A("kills measured on the full adjusted score, because it missed its own frozen")
    A("minimum-effect gate by 0.000674633. It is one of only six records coded to the")
    A("adjusted_score currency, so if the top single axis is one borderline record,")
    A("this is the record.")
    A("")
    A("SENSITIVITY VARIANT, never a base change: idx 59 is reclassified as died and")
    A("the permutation MI for convention is recomputed. The base coding is untouched,")
    A("and the variant runs in its own permutation stream so it cannot move a single")
    A("number in the table above.")
    A("")
    A("| target | variant | MI (bits) | null mean | null max | MI - null | p |")
    A("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for s in shadow_rows:
        for key, lab in (("base", "base coding (idx 59 lived)"),
                         ("shadow", "shadow (idx 59 died)")):
            r = s[key]
            A("| %s | %s | %.4f | %.4f | %.4f | %.4f | %.4f |"
              % (s["target"], lab, r["mi_bits"], r["null_mean_bits"],
                 r["null_max_bits"], r["mi_minus_null_mean_bits"], r["p_value"]))
    A("")
    for s in shadow_rows:
        A("- **%s**: MI - null moves %+.4f bits (%.4f -> %.4f), p %.4f -> %.4f."
          % (s["target"], s["delta_mi_minus_null_bits"],
             s["base"]["mi_minus_null_mean_bits"],
             s["shadow"]["mi_minus_null_mean_bits"],
             s["base"]["p_value"], s["shadow"]["p_value"]))
    A("")
    _s5 = next(s for s in shadow_rows if s["target"] == "outcome_5class")
    _s2 = next(s for s in shadow_rows if s["target"] == "lived_vs_died")
    A("**The axis survives its most fragile record.** The door's own falsifier was")
    A("that convention would drop below significance under the shadow, which would")
    A("have meant the campaign's top single axis was one borderline record. It does")
    A("not: on the 5-class target the effect loses %.1f%% of its size and p stays at"
      % (100.0 * abs(_s5["delta_mi_minus_null_bits"])
         / _s5["base"]["mi_minus_null_mean_bits"]))
    A("the permutation floor, meaning no shuffle out of %d reached the observed value"
      % meta["n_permutations"])
    A("with idx 59 counted either way. The lived/died leg falls from %.4f to %.4f, but"
      % (_s2["base"]["mi_minus_null_mean_bits"],
         _s2["shadow"]["mi_minus_null_mean_bits"]))
    A("it was already null before the shadow was applied, so nothing was riding on it.")
    A("The convention governor may therefore be adopted as round law without a")
    A("dependency on how idx 59 is classified -- which also means the ledger's")
    A("internal inconsistency about idx 59 can be settled on its own merits, with no")
    A("statistical result pulling on the answer.")
    A("")
    A("One number in that table is worth reading twice. This block draws its own")
    A("permutation null, so its base row for convention on the 5-class target reads")
    A("%.4f where the main table reads %.4f. That %.4f-bit gap between two draws of"
      % (_s5["base"]["mi_minus_null_mean_bits"],
         next(r["mi_minus_null_mean_bits"] for r in mi_rows
              if r["target"] == "outcome_5class" and r["axis"] == "convention"),
         abs(_s5["base"]["mi_minus_null_mean_bits"]
             - next(r["mi_minus_null_mean_bits"] for r in mi_rows
                    if r["target"] == "outcome_5class" and r["axis"] == "convention"))))
    A("the same quantity is the instrument's own resolution at %d shuffles, and it is"
      % meta["n_permutations"])
    A("the right yardstick for every delta reported anywhere in this document.")
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
