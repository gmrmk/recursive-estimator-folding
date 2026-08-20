# VERDICT - gm_latent_cubature

**KILL CONFIRMED.** The frozen `tau=0.5` adaptive sparse spherical-radial
cubature candidate (`fold_ledger.json` index 11,
`latent_sparse_radial_cubature`, previously `status = proposed` with no
`result` field) has now been measured on its own predeclared eight-case
width-64 bank and it fails its own accuracy gate.

The record was right to be pending and is right to be closed as a kill. The
resource postmortem was also right: the 24.6 GB / 13.8 GB failure was an
orchestration fault, not the estimator. With the repaired reducer and one
separately killable process per case, the whole bank runs in **41.98 s** at a
peak working set of **85.80 MB**, and the case that never returned
(seed 18563) now completes in **0.155 s**.

## DEVIATIONS, recorded loudly

1. **My predeclared step-0 prediction was falsified.** PREDECLARATION section 6
   said gate 4 would land "well below 80e9" on both dtype readings. Under
   FlopScope 0.10.0's measured `float64` dtype rate of **2.0**, the conservative
   target arithmetic is **86,396,699,264.6 billed FLOPs >= 80e9**, i.e. a kill.
   Under `float32` (rate 1.0) with the same 25% contingency the sibling used it
   is **53,997,937,040.4 < 80e9**, a pass. I did not predeclare a dtype rate, so
   gate 4 is **dtype-conditional** and is NOT a clean unilateral step-0 kill.
2. **Therefore I did not stop at step 0.** PREDECLARATION section 4 says the run
   stops at gate 4 "if it kills". A straddle is not a kill, and the accuracy
   falsifier is the mined cheapest falsifier proper and costs 42 s, so I ran it.
   Both readings of gate 4 are reported; neither is used to soften the verdict.
3. **The mining note's stated step-0 mechanism is falsified.** The note predicted
   the gate might close on data movement ("the adaptive leading-subspace node
   selection is gather-heavy"). Measured against the installed weight table,
   data movement is **0.576%** of the worst-case charged total and **0.113%**
   with the observed structure. The lever that actually moves gate 4 is the
   float64 dtype rate, which the note did not name.
4. **My win-count prediction was slightly wrong**: predicted `W <= 3`, observed
   `W = 4`. The gate still fails (`W >= 6` required).
5. **Added, not predeclared**: a case-level bootstrap, a paired sign-flip
   permutation null, and an exact binomial on the win count. These are
   descriptive statistics computed on already-collected case records; they
   change no gate and add no arm. They are reported because they materially
   qualify how strong the kill is (see "Honest strength of the kill").

## Gate table

| gate | quantity | threshold | measured | result |
|---|---|---|---:|---|
| 1 accuracy | aggregate MSE ratio vs corrected fullcov | `<= 0.80` | **1.0319985295056737** | **FAIL** |
| 2 wins | cases beating corrected fullcov | `>= 6 / 8` | **4 / 8** | **FAIL** |
| 3 invariance | permutation / positive-scale, rel tol `1e-10`, equal ranks | pass | perm `2.0378868031173505e-16`, scale `4.2737583849311574e-16`, ranks equal | PASS |
| 4 step-0 arithmetic | conservative `n=256,L=32` ops under FlopScope 0.10.0 | `< 80e9` | float64 `86,396,699,264.61`; float32+25% `53,997,937,040.38` | dtype-conditional |

Survival required all four. Gates 1 and 2 both fail.

## Per-case result, full frozen bank

| depth | seed | corrected-fullcov MSE | sparse-radial MSE | ratio | win | rank min/max |
|---:|---:|---:|---:|---:|:--:|---:|
| 16 | 18560 | 3.6883632778490836e-4 | 1.2147148740874424e-3 | 3.2933710228126416 | no | 1 / 11 |
| 16 | 18561 | 8.2109632505381e-4 | 6.269647056412461e-4 | 0.7635702249674036 | yes | 2 / 12 |
| 16 | 18562 | 1.4425199155688232e-3 | 1.5212349114110606e-3 | 1.0545677012793255 | no | 2 / 12 |
| 16 | 18563 | 2.0847053245471415e-4 | 4.65128546114589e-4 | 2.2311476861394235 | no | 1 / 12 |
| 32 | 18720 | 3.183393828079917e-4 | 2.208483385352833e-3 | 6.937512304862679 | no | 1 / 12 |
| 32 | 18721 | 2.80918997993452e-3 | 5.633429093333263e-4 | 0.20053571077683305 | yes | 1 / 12 |
| 32 | 18722 | 3.0040728236955323e-4 | 1.9489957918787676e-4 | 0.6487844690399893 | yes | 1 / 12 |
| 32 | 18723 | 5.99216069023735e-4 | 2.930752304831001e-4 | 0.489097748931515 | yes | 1 / 12 |

`baseline_mse_sum = 0.0068680758149980555`,
`candidate_mse_sum = 0.0070878441416114745`,
`aggregate_ratio = 1.0319985295056737`, `wins = 4/8`.

Recomputed a third time from the pass-2 child records, reconstructing every MSE
from the stored predictions and the banked truth rather than reusing any
pass-1 number: `baseline_sum = 0.0068680758149980555`,
`candidate_sum = 0.007087844141611474`,
`aggregate_ratio = 1.0319985295056735`, `wins = 4`. The `...35` versus `...37`
difference is one ulp, from `numpy.sum` versus Python `sum` ordering; it is
`4.4e-16` relative and touches no gate.

Seed 18563 is the case that hung the original harness. It is the third-worst
case in the bank (ratio 2.23), so its absence had been flattering the partial
record, not penalising it.

## Honest strength of the kill

The gate is a point condition on this frozen bank and it fails cleanly: the
candidate needed a 20% aggregate improvement and delivered a 3.2% degradation.
But eight cases carry real dispersion, and I will not overstate:

- case-level bootstrap (B = 200,000, seed 20260810) 95% interval on the
  aggregate ratio: **[0.4429038640994148, 2.637812140330009]**;
- bootstrap probability the ratio would land at or below 0.80: **0.275315**;
- paired sign-flip permutation null on the mean log ratio: **p = 0.757455**
  (observed mean log ratio `0.12001765036405765`);
- exact binomial for `W >= 6` under a fair coin: **p = 0.14453125**.

Read plainly: on this bank the candidate is **statistically indistinguishable
from the comparator it had to beat by 20%**. It is not decisively worse; it is
decisively not better. That is a gate failure either way, and it is a far worse
position than the sibling that passed the identical gate (index 13, Haar + chi2:
aggregate ratio 0.631599, 7/8 wins), which this candidate would additionally
have had to beat by roughly 50x to matter for the score.

The causal reading matches index 13's factorial exactly. That factorial isolated
angular randomisation as the repair (`fixed axes / sqrt(n)` ratio 8.87160 ->
`Haar / sqrt(n)` 0.66880). This candidate keeps fixed covariance eigen-axes and
only sparsifies the rank, so it inherits the angular aliasing the factorial
identified. Rank truncation to `tau = 0.5` does improve on the full-rank
fixed-axis parent (aggregate 8.8716 -> 1.0320), but not into the gate.

## Two-signal verification

| seal | what it proves | number | tolerance | result |
|---|---|---:|---:|---|
| 1 weights/bank | my regenerated weights + frozen `corrected_fullcov.py` reproduce the banked comparator predictions | max abs delta `1.3156142841808105e-14`; banked baseline MSE delta `0.0` | `1e-12` | PASS |
| 2 repair neutrality | the zero-progress guard changed no mathematics on the three cases the original run completed | max relative MSE delta `6.467534916416456e-14` | `1e-12` | PASS |
| 3 bit repeat | the whole bank rerun in eight fresh child processes | 8/8 candidate MSEs bitwise identical | exact | PASS |
| 4 step-0 cross-check | independent recomputation of gate 4 with observed structure instead of the worst-case bound | float64 `85,996,669,871.36`, float32+25% `53,747,918,669.60`; same side of 80e9 as the static number on both dtype readings | - | PASS |

Seal 2 detail (original killed run -> revived build):
`18560` `1.2147148740873806e-3 -> 1.2147148740874424e-3` (rel `5.08757447117818e-14`);
`18561` `6.269647056412867e-4 -> 6.269647056412461e-4` (rel `6.467534916416456e-14`);
`18562` `1.5212349114110606e-3 -> 1.5212349114110606e-3` (rel `0.0`).

## Re-freeze against the retained hashes

Both SHA-256s the postmortem retained are reproduced bit-for-bit from the files
actually executed here:

```text
candidate  a31fd01802ff79167efe00c1b3b129c2744853d9ad0a9897c990af5988c4f24c  (matches retained A31FD018...C4F24C)
contract   df2ef00fff7b77fc365fc80536524dfec388363f6a77993aa81c9c47c97a400a  (matches retained DF2EF00F...C97A400A)
truth bank a07455ae94a0be47cd351a430e457be76de6c4cd6fc0bd31858e0f9bd72f8dc1  (matches the bank index 13 used)
```

The frozen files were loaded by path and never edited. The single change is the
revival mechanism: `reduce_components` replaced in-process by the
zero-progress-guarded compressor. Guard telemetry on the eight cases shows
`last_bin_absorb` firing 115-208 times per case and `zero_capacity_advance`
firing 0 times, i.e. the repaired branch is exactly the last-bin path the
postmortem localised, and seal 2 shows it is mathematically inert where the
original terminated.

## Resource containment

| | original killed harness (index 12) | this run |
|---|---|---|
| peak working set | 24.6 GB and 13.8 GB, externally stopped | **85,803,008 bytes (85.80 MB)** |
| cases completed | 3 of 8 | **8 of 8** |
| max case wall | never returned on seed 18563 | **5.42 s** |
| total wall | - | **41.98 s** |
| containment | in-process monitor, could not preempt | one child process per case, 2 GB RSS watchdog at 0.25 s, 600 s wall cap |

## Firewall statement

No truth generation: truth vectors and comparator predictions were read from the
committed bank `latent_full_sigma/fresh_n64_results.json`. No WHest data,
scorer, holdout, private suite, API, network, submission, or login. No git
commands. No contact with the held `m245_*` / `M243` / `M244` / `tasks` /
`journal-m245*` lane. All writes are inside
`corpus/whestbench/experiments/gm_latent_cubature/`. Frozen sources were read
and imported, never modified.

## Ledger disposition proposed

Index 11 `latent_sparse_radial_cubature`: `proposed` -> `killed`, with

> Measured at last on its own frozen eight-case n=64 bank under repaired
> last-bin recompression and per-case process containment. Aggregate ratio
> 1.0319985295056737 against a `<=0.80` gate with 4/8 wins against a `>=6/8`
> gate; both accuracy clauses fail. Invariance passes (permutation
> 2.04e-16, scale 4.27e-16, ranks equal). Conservative n=256,L=32 arithmetic is
> dtype-conditional under FlopScope 0.10.0: 86.397B billed at the frozen
> candidate's float64 (>= 80e9, fails) versus 53.998B at float32 with 25%
> contingency (passes). Rank truncation improves the fixed-axis parent from
> 8.8716 to 1.0320 but does not reach the gate; the missing repair is angular
> randomisation, as index 13's factorial already isolated. Peak working set
> 85.80 MB, 8/8 cases, 41.98 s, retained candidate/contract SHA-256s reproduced.

This closes one of the three no-result records in the 242-record ledger. Score
impact: zero, as the mining record predicted.
