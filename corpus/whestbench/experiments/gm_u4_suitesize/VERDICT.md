# VERDICT — gm_u4_suitesize: U4 (private re-evaluation suite size) — KILL CONFIRMED

Date 2026-08-10. Predeclared in `PREDECLARATION.md` (written before any
execution). Harnesses: `scan_u4.py`, `sentinel_check.py`, `verify.py`.
Numbers: `results.json`, `sentinel_results.json`, `signalA/B/C_hits.json`.

## DEVIATIONS (loud, at the top)

1. **The falsifier's own premise about where to look is FALSE, and this is a
   finding, not a workaround.** The mined falsifier says to grep "the
   rules/starter-kit sources under `corpus/whestbench/sources/`". The starter
   kit is NOT in the repository. `handoff/RESOURCE_PROVENANCE.md` line 14
   records it as a URL + commit reference only
   (`https://github.com/AIcrowd/whest-starterkit.git`,
   `c99ef4af15bae7dd19e1d9c46fa4794d90a91d40`) and the same file states "No API
   token, hosted model, paper PDF, challenge weight/truth file, scorer, Python
   environment, Ollama model blob, or third-party repository is included."
   `sources/` holds 25 research/source NOTES, not organizer artifacts. A true
   starter-kit re-read therefore requires the network and is NOT response-free.
   Consequence recorded rather than absorbed: the "cheap" label on U4 was wrong
   about its own instrument as well as about its answer.
2. **Scope widened from `sources/` to the whole repository** (1385 text files,
   30,152,341 bytes), because the mined kill condition is "the sources are
   silent after a FULL read". Widening can only make a KILL harder to reach, so
   it is conservative with respect to the verdict I predicted.
3. **Firewall exclusions** (never opened): `m243*`, `m244*`, `m245*` paths and
   `tasks/journal-m245*`. Verified zero leakage: 0 of 50,884 Signal-B hits and
   0 of 61 Signal-A hits carry an `m243/m244/m245` path.
4. **4 PDFs and 28 `.npz` / 3 `.gz` binaries were not text-scanned.** Named and
   classified: `sources/dprelu_2023.pdf`,
   `sources/relu_function_derived_review_2022.pdf`,
   `sources/weight_precision_neuron_count_icml2024.pdf` (third-party ML papers)
   and `experiments/dac_prize_report_extension/WHestBench-Algorithmic-Prize-
   Report-DRAFT-v2.pdf` (our own draft). None is organizer rules or starter-kit
   material. This is a stated coverage limit, not a silent one.
5. `SENTINEL_SYNTHETIC.md` in this directory is a FABRICATED sentinel written by
   `sentinel_check.py` as a positive control. It is not evidence and must never
   be cited as a source. The scanner excludes this directory from its own scan.
6. `signalB_hits.json` retains the 133 deduplicated candidates that were
   hand-adjudicated (from 13,947 private-family hits, from 50,884 total). The
   full set is regenerable by re-running `scan_u4.py`; it was 20 MB.

## Step 0 — arithmetic gate on the changed premise: PASS

Recomputed from `s1b_dispersion_corrected/s1b_results.json` (machine file, not
the prose table), 1e6-suite tail runs, matched-arm 50-net vs 100-net:

| arm | vD | P(>2.5e-7) 50 nets | P(>2.5e-7) 100 nets | G0a ratio | P(<1.6e-7) 50 | P(<1.6e-7) 100 | G0b ratio |
|---|---|---|---|---|---|---|---|
| s17_low | 0.08135950765383865 | 0.00046 (SE 1.959e-5) | 3e-06 (SE 1.714e-6) | **153.33** | 0.092107 | 0.027853 | **3.3069** |
| s17_high | 0.12203926148075797 | 0.00085 (SE 2.691e-5) | 7e-06 (SE 2.564e-6) | **121.43** | 0.105756 | 0.035410 | **2.9866** |

Gates: G0a (>=10x both arms) PASS; G0b (>=2x both arms) PASS. Step 0 PASS.

Honest note on the mined headline: the miner's "65-150x swing" understates the
matched-arm result (121-153x) and overstates its precision — the 100-net cells
are 3e-06 +/- 1.7e-06 and 7e-06 +/- 2.6e-06, so G0a is order-of-magnitude only.
The direction and the two-orders-of-magnitude size of the multiplier stand.

Step-0 cross-checks (independent of the quoted cells):
- `1 - P(<2.5e-7)` reproduces `P_above_2p5em7` to <= 9.51e-17 absolute in all
  four cells.
- Bootstrap SD vs closed form `S*sqrt((vD+(1+vD)*vF)/N)`: ratios 1.00091 /
  0.99989 (s17_low) and 1.00095 / 0.99989 (s17_high).
- sqrt(N) structural check: SD_50/SD_100 = 1.415655 and 1.415712 vs
  sqrt(2) = 1.414214 — relative deviation 1.02e-3 and 1.06e-3. The two arms
  differ by suite size and nothing else, so the gate measures what it claims.

## Main falsifier — full read of the committed corpus: KILL CONFIRMED

Coverage: 1385/1385 in-scope text files read, 30,152,341 bytes, 0 unreadable,
file-list SHA-256 `0725cc9c6794d4c34ecfdb898a78fbd618ab69b59d1310c4a2a7cd53e836e142`.
Signal A 61 hits, Signal B 50,884 hits (13,947 private-family; 133 adjudicated
candidates), Signal C 56 sentences. Nine candidates were read at source and
adjudicated in `results.json -> verification.adjudication`.

**Resolving statements found: 0.**

The decisive negative, quoted verbatim from the corpus's own full read of the
authoritative document (`core/RULES_V12_ANALYSIS_20260808.md`, lines 3-4 and
13-15 — "Primary source: the challenge's Official Rules v12 page, read
directly. Quotes verbatim."):

> The Private Re-evaluation runs **Sept 20-30, 2026** on "a separate, fresh,
> never-seen test suite ... generated from private seeds that were not used
> during either Phase 1 or Phase 2."

Seeds, freshness and dates are stated. **A count is not.** Every other primary
source repeats the same unsized description:

- `sources/research_phase1_top_arc_repo_20260803.md:65` — "Phase II requires
  designating one entry, which is rerun on **a fresh unseen MLP suite**".
- `sources/research_top_method_forensics_20260803.md:26` — "Section 5.4 says the
  live score is only the **50-MLP public half**; Phase-I prizes combine public
  and hidden halves, and Phase-II prizes use **a fresh unseen rerun**."
- `core/HOSTED_INTEL_20260808.md:49` (organizer official-facts panel, verbatim)
  — "**Fresh private rerun of each team's up to two nominated submissions, per
  phase.**"
- `core/FLIP_READINESS_20260810.md:21` (Aug-4 update email 19fcb021d19e8278 +
  discourse 18125, read 2026-08-10) — "Prize ranking is EXCLUSIVELY the private
  re-evaluation, on **a freshly generated suite with private seeds unused in
  either phase**."

The one sized primary statement in the entire corpus is about a DIFFERENT
object, and mistaking it for U4's answer is the trap this scan was built to
catch (`core/RULES_V12_ANALYSIS_20260808.md:73`):

> - **Phase-end standings use all 100 MLPs** (50 public + 50 private, §5.4) —
>   the live leaderboard shows only the public half, so even the Phase-1
>   standing is not what today's board displays.

That sizes the PHASE benchmark (public half + hidden half), corroborated
independently by `core/GEN3_RECURSION_PACKET_20260808.md:99` ("the Phase
standings add a withheld 50, and the prize adds fresh private seeds"). It is
not the September fresh suite, whose size no committed source states.

**Gate outcome per the predeclaration: KILL_CONFIRMED.** The substance of the
original ledger record is confirmed — U4 cannot be settled from documents we
hold — while its LABEL is falsified: "OPEN cheap / settling check: rules
re-read" is wrong on both counts, and "U4 (suite size) folds into the U1
organizer question" (`UNCERTAINTY_RECURSION_20260810.md:61`) folded it into a
question closed as moot the same day. The correct disposition is the one the
same document's own taxonomy already implies at line 68:

> **U4 = BLOCKED-EXTERNAL (organizer). Owner: Jonah (ask), fable (watch).**
> Settling check: the organizer nomination-instructions email (U19 inbox watch)
> or a direct organizer question; NOT a rules re-read.

## Two-signal verification

1. **Independent engine.** ripgrep (different tool, different regex family) over
   the same tree for `\d{2,4}\s*(MLPs?|nets?|networks?|models?)` adjacent to the
   private/hidden/unseen/fresh/rerun vocabulary returns, outside this experiment
   directory, exactly two lines: `RULES_V12_ANALYSIS_20260808.md:73` (the
   phase-end 100 = 50+50, already adjudicated non-resolving) and
   `m152_.../M152_FROZEN_SOURCE_ONLY_PROTOCOL_20260807.md:95` (an internal
   experiment's "28/32 MLPs have positive held-out paired gain"). Zero
   resolving statements — agreeing with the Python scan.
2. **Positive control (the discriminating check).** `sentinel_check.py` feeds
   the SAME Signal-A patterns and Signal-B window logic 8 synthetic resolving
   sentences in different phrasings: **8/8 detected, 0 missed**. An on-disk
   sentinel file containing "the Private Re-evaluation is run on a fresh,
   never-seen suite of 137 MLPs generated from private seeds" fires
   `A2_count_then_private` and `A3_suite_size_literal` and is picked up by
   Signal B with `num=137`. The absence claim is therefore an absence, not a
   blind detector. The 4 near-miss controls behave as designed: the real
   §5.4 quote ("separate, fresh, never-seen test suite ... private seeds")
   produces NO number, because there is none to produce.
3. **Step-0 numbers re-derived two ways** (complement identity to 1e-16, and
   closed-form SD to 1e-3), plus the sqrt(2) structural check above.

## What this changes downstream (writeup / Phase-2 planning only)

- U4's row in `UNCERTAINTY_LADDER_20260810.md` §A and
  `UNCERTAINTY_RECURSION_20260810.md` should read BLOCKED-EXTERNAL (organizer),
  level **assumed**, with the settling check re-pointed at the organizer
  channel. Its level does NOT rise to "reported": we hold no organizer statement
  of this number.
- The writeup's dual-band hedge is JUSTIFIED and must stay:
  `PHASE1_WRITEUP_DRAFT_20260808.md:261-263` states both
  [1.54e-7, 2.16e-7] (50-net) and [1.62e-7, 2.06e-7] (100-net). Collapsing to
  one band would be level inflation.
- One internal inconsistency surfaced and is now on the record:
  `AGENT_CHANNEL.md:611` asserts "the prize is decided by ONE draw of a 100-net
  private suite", while every S1/S4/U9 bootstrap uses 50. Both are our own
  prose; neither is sourced. The 100 in that line has no evidentiary basis.
- Best available PRIOR, if one is wanted for Phase-2 planning and labelled as a
  prior: the Phase benchmark is 100 MLPs (50 public + 50 hidden, §5.4), which is
  the only sized suite the organizers have described.

## Firewall compliance

Read-only outside this directory. No network, no submission, no login, no git.
No scorer/truth/private/holdout artifact read. Held lane (m243/m244/m245,
tasks/journal-m245*) never opened — verified by path audit over all hits. The
frozen Phase-1 selection is untouched; nothing here is a mechanism change.
