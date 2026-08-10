# PREDECLARATION — gm_u4_suitesize (graveyard revival of U4)

Written 2026-08-10, BEFORE any falsifier execution. Nothing below is revised
after results are seen; deviations are appended to VERDICT.md, never edited in.

## 0. The record under revival

Ledger id (verbatim from the mining record):
`U4 private-suite size 50 vs 100 (UNCERTAINTY_LADDER_20260810 §A; UNCERTAINTY_RECURSION table, 'OPEN cheap')`

Primary record text, verified read this session:
- `core/UNCERTAINTY_LADDER_20260810.md` line 18-20: "U4. PRIVATE-SUITE SIZE
  (50 vs 100 nets). Level: assumed (50 used in all S1/S4 bootstraps). Scales
  every probability we quote (P-thresholds tighten at 100). Settle: rules
  re-read; rider on the U1 question."
- `core/UNCERTAINTY_RECURSION_20260810.md` line 36: "| U4 | private suite 50 vs
  100 nets | rules re-read / rider on U1 | scales all P-tables | fable | OPEN cheap |"
- same file line 33: U1 "CLOSED (overtaken)".
- same file line 61: "U4 (suite size) folds into the U1 organizer question."
- same file line 68: U4 listed among "EXTERNAL organizer facts (U1/U4/U10/U17 —
  we cannot resolve, only ask/watch)".

what_the_kill_actually_measured (mined): nothing was measured; the settling
check ("rules re-read") was armed and never fired, then folded into a question
declared moot the same day.

## 1. Mechanism claimed by the revival

Un-fold U4 from the dead U1 rider and fire its own settling check independently:
read the private re-evaluation suite size directly out of the committed rules /
starter-kit / organizer texts already in the repo. No compute, no organizer
contact, no network. The quantity is the integer N_private = number of MLPs
(nets) in the private/fresh re-evaluation suite.

## 2. Quantity and equation (the multiplier this parameter carries)

Suite score = mean over N nets of per-net MSE. Under the S1/S1b model the
across-suite SD obeys the committed closed form

    SD(suite score) = S * sqrt( (vD + (1+vD)*vF) / N )

so every quoted tail probability is a function of N. N is therefore a pure
multiplier on the whole statistics section: it does not change the mean
(1.83e-7) and changes every P-cell.

## 3. Step-0 arithmetic gate (run FIRST; stop if it kills)

The revival's changed premise is that under corrected dispersion the 50-vs-100
gap is now the single largest remaining multiplier. That premise is arithmetic
on committed numbers and is checked before any document search, recomputed from
`experiments/s1b_dispersion_corrected/s1b_results.json` (the machine-readable
file, NOT the markdown table, so the check is independent of the prose).

Step-0 PASS requires BOTH, using matched-arm (same vD) 50-net / 100-net ratios
on the two bracket-validated arms s17_low (vD=0.0814) and s17_high (vD=0.1220):

- G0a: ratio P(>2.5e-7 | 50 nets) / P(>2.5e-7 | 100 nets) >= 10x on both arms.
- G0b: ratio P(<1.6e-7 | 50 nets) / P(<1.6e-7 | 100 nets) >= 2x on both arms.

If either fails, the changed premise is refuted, U4 is immaterial, and the run
STOPS at step 0 with gate_result = KILL_CONFIRMED (status KILLED_AT_STEP0).

Predicted (on record, before running): G0a and G0b both PASS. Predicted values:
G0a matched ratios ~120x and ~150x; G0b matched ratios ~3.0x and ~3.3x. I also
predeclare a note that the miner's headline "65-150x" is a loose rendering of a
range whose matched-arm values I expect to land ABOVE 100x, and that the 100-net
2.5e-7 cells carry batch SE comparable to their own magnitude (3e-6 +/- 2e-6),
so G0a is order-of-magnitude only.

## 4. The cheapest falsifier, exactly as mined (no scope enlargement)

Verbatim from the mining record:
"Response-free: grep the committed rules/starter-kit sources under
corpus/whestbench/sources/ and the Aug-4 update text for the private
re-evaluation suite size. If the size is stated, U4 is settled at reported level
and every P-table gets one suite size. If the sources are silent after a full
read, U4 is falsified as 'cheap' and must be recorded as BLOCKED-EXTERNAL
(organizer) rather than folded — which is itself the finding."

Task guidance widens the read set to "the committed rules/starter-kit sources +
the Aug-4/Aug-10 organizer texts". Implemented scope: EVERY text file in the
repo (read-only), because a full read is what the kill condition requires, minus
the firewalled held lane.

Excluded by firewall (never opened): any path matching `m243*`, `m244*`,
`m245*`, `tasks/journal-m245*`. Excluded as non-text: binaries, `.png`, `.npz`,
`.pyc`, `.git`.

### Definitions fixed in advance

- PRIMARY source = a committed file that reproduces or directly quotes organizer
  material: the competition rules text, the starter kit, an organizer discourse
  post (incl. 18125 / 18130 / the Aug-4 update), or an organizer email.
- RESOLVING statement = an explicit integer count of nets/MLPs/models in the
  PRIVATE / held-out / fresh / re-evaluation / re-run suite, attributable to
  organizer material. Our own modelling assumption ("we assume 50", "50 used in
  all S1/S4 bootstraps") is NOT resolving. The public-half count (the 50 public
  MLPs we are scored on now) is NOT resolving unless the rules state the private
  suite equals it.

## 5. Gate (main), fixed in advance

- REVIVED_PASS: at least one RESOLVING statement in a PRIMARY source, quoted
  verbatim with file:line. U4 settles at REPORTED level; every P-table takes one
  suite size.
- KILL_CONFIRMED: full read of the in-scope corpus yields ZERO resolving
  statements. This confirms the original record's own disposition-in-substance
  (U4 is an EXTERNAL organizer fact, recursion line 68) while falsifying its
  label: "OPEN cheap / rules re-read" is wrong, and the correct disposition is
  BLOCKED-EXTERNAL (organizer), not "folds into the U1 organizer question".
- INCONCLUSIVE: a count appears but is unattributable to organizer material, or
  two primary sources conflict.

## 6. Predicted outcome, on record

I predict KILL_CONFIRMED. Basis: the recursion document's own taxonomy already
files U4 under external organizer facts "we cannot resolve, only ask/watch"
(line 68), and the adjudicator's spot-check reported rules v12 §5.4 language
("live score is only the 50-MLP public half... Phase-II prizes use a fresh
unseen rerun") plus `research_phase1_top_arc_repo_20260803.md` line 66 ("rerun
on a fresh unseen MLP suite") with no size stated. I predict the corpus states
the PUBLIC half is 50 MLPs and states the private re-run is "fresh/unseen"
WITHOUT a size, i.e. the resolving statement does not exist and the 50-vs-100
question is genuinely unanswerable from documents we hold.

Secondary prediction, on record: the phrase "100" as a private-suite size will
appear nowhere attributable to organizer text; if 100 appears at all it will be
our own scenario/sensitivity arm (S1b's 100-net extension).

## 7. Two-signal verification protocol

Signal A (keyword-driven, ripgrep): case-insensitive regex families over the
in-scope file set for suite/net/MLP-count phrasings and for the private/
held-out/fresh vocabulary.

Signal B (number-driven, independent Python scan, different logic): for every
in-scope file, extract every integer token in {50, 100, 80, 129, 250, 500, 1000}
and every `\b\d{2,4}\b` occurring within +/-120 characters of any of
{suite, MLP, net, model, private, held-out, holdout, hidden, unseen, fresh,
re-run, rerun, re-evaluat, re-eval}, and dump all hits for hand adjudication.
Signal B is not derived from Signal A's pattern list and would surface a
resolving statement phrased in words A does not contain.

Agreement rule: the KILL stands only if BOTH scans independently return zero
RESOLVING statements, AND coverage accounting shows the scans read the same
complete in-scope file set (file count and byte count reported).

Third check (cheap, run regardless): explicit verbatim extraction of every
sentence in the corpus containing "50" adjacent to "MLP" or "suite", so the
public-vs-private distinction is adjudicated on quotes rather than on my summary.

## 8. Kill honesty

A KILL here CONFIRMS the substance of the original ledger record (U4 is not
resolvable from documents we hold) and is reported plainly as a full success. It
does not license retuning, re-scoping, or a second falsifier. Nothing in this
experiment touches the frozen Phase-1 selection, the held m243/m244/m245 lane,
any scorer/truth/holdout artifact, or the network.

## 9. Artifacts to be written

- `PREDECLARATION.md` (this file)
- `scan_u4.py` (harness: step-0 gate + Signal A + Signal B + coverage)
- `results.json` (verbatim numbers, all candidate hits)
- `VERDICT.md`
