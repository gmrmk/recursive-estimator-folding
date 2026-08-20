# VERDICT - gm_ecn_psi / `ecn_exact_jspace_psi_streaming` (fold_ledger idx 35)

**KILL_CONFIRMED.** The original record stands, and it stands harder than it
predicted. The exact chain-rule-correct observable-Jacobian `psi` was
implemented, validated against central differences, and run on the identical
no-ladder cell over the same 32 frozen states. It does not merely fail to move
the ratio materially below 0.911472 - it is **worse than the surrogate on
32 of 32 units and worse than the generic q3 comparator overall**
(ratio 1.006451 vs 0.911472, wins 9/32 vs 32/32).

Both steps of the mined cheapest falsifier ran. Deployment stays closed and
was never touched.

## Deviations from PREDECLARATION.md

1. The frozen implementation lives outside the publish repo, at
   `<codex>/work/scorefloor_generation/ecn_jacobian_maxent_compressor/experiment.py`.
   It was imported read-only, never copied or edited. Declared in
   PREDECLARATION.md section 0 before any code was written.
2. No other deviation. No arm was added, no gate was retuned, no constant was
   selected on the data, no scale-down was applied.

## Step 1 - exact-Jacobian central-difference validation: PASS

Domain: every `(alpha, ell)` in the 32 frozen states,
`32 x 48 x 6 = 9,216` points, `18,432` derivative entries.
`alpha in [-2.3225, 2.0850]`, `sigma in [0.35453, 2.18113]`.

| gate | quantity | value | threshold | result |
|---|---|---:|---:|---|
| G1A | max rel err, `d/dalpha` vs `sigma Phi(alpha)`, h=1e-5 | `6.535666962912099e-10` | 1e-6 | PASS |
| G1B | max rel err, `d/dell` vs `sigma h(alpha)`, h=1e-5 | `3.6009255606963945e-10` | 1e-6 | PASS |
| G1D | same, h=5e-6 (step halving) | `3.4236629155771126e-10` / `5.142192866221394e-10` | 1e-6 | PASS |
| G1C | erf-free Gauss-Legendre observable vs frozen `gaussian_relu_mean` | `3.2687270594713815e-14` | 1e-10 | PASS |
| G1C | central differences of the GL observable vs analytic blocks | `1.401756002358895e-10` / `6.582785484237782e-11` | 1e-6 | PASS |
| extra | algebraic identity `h'(alpha) = Phi(alpha)` | `6.664295034754594e-10` | 1e-6 | PASS |

The record did not die at step 0. The judge's prescribed derivative blocks are
correct: `J_alpha = diag(sigma Phi(alpha))`, `J_ell = diag(sigma h(alpha))`.

## Step 2 - identical no-ladder cell, psi swapped: KILL

Same 32 seeds `2026080600..2026080631`, K=48, d=6, q=3. `tau`, `phi`, the
generator and the generic comparator are the frozen originals called by
reference.

| arm | aggregate RMS | ratio vs generic | bootstrap 95% | wins vs generic | mean unit ratio | median unit ratio |
|---|---:|---:|---:|---:|---:|---:|
| `generic_q3` | `0.014398754762932663` | `1.000000` | - | - | 1.000000 | 1.000000 |
| `jacobian_maxent` (surrogate psi, frozen) | `0.01312405877351071` | `0.9114717897200765` | `[0.894376, 0.929271]` | 32/32 | 0.914201 | 0.922277 |
| `jacobian_exact_psi` (this mutation) | `0.014491638980771332` | `1.0064508507414671` | `[1.000172, 1.013349]` | **9/32** | 1.008187 | 1.007423 |

Paired, exact vs surrogate, on the same units:

- exact psi is better on **0 of 32** units; two-sided exact sign test
  `p = 4.656612873077393e-10`.
- paired pooled-ratio difference `+0.09497906102139064`,
  bootstrap 95% `[0.07792182, 0.11131877]` - the whole interval is above zero,
  i.e. the exact metric is worse with the paired uncertainty accounted for.

Gates:

| gate | result |
|---|---|
| G2-PRIMARY `ratio <= 0.80` | **FAIL** (1.006451) |
| G2-PRIMARY `wins >= 24/32` | **FAIL** (9/32) |
| G2-MATERIALITY `ratio < 0.8942` | **FAIL** (1.006451; it moved the wrong way by +0.0950) |
| G2-STRUCTURAL (all 10 sub-gates) | PASS |
| G2-REPRO | PASS |

Structural detail for the new arm: max global-mean residual `1.073e-14`, max
global-covariance residual `6.439e-15`, negative-eigenvalue magnitude `0.0`,
repair magnitude `0.0`, Sinkhorn marginal residual `1.749e-15`, bin-mass
residual `1.110e-16`, minimum hard-assignment effective rank `2.673194`,
medoids unambiguous, component-permutation residual `1.665e-16`,
coordinate-gauge residual `2.220e-16`, all finite. Sinkhorn iterations
20-40 (adaptive rule left frozen, as declared).

So the exact `psi` is a structurally clean, symmetric, mass/mean/covariance/PSD
exact compressor whose routing is simply worse. The failure is the mechanism,
not the plumbing.

## Two-signal verification

1. **Cached-reference reproduction (bit-exact).** The in-process re-run of the
   frozen arms reproduced the committed `results.json` exactly:
   generic aggregate RMS `0.014398754762932663` (relative difference `0.0`),
   no-ladder ratio `0.9114717897200765` (relative difference `0.0`),
   no-ladder aggregate RMS `0.01312405877351071`, 32/32 wins.
2. **Independent recomputation of the new geometry.** Every pairwise distance
   was rebuilt the slow explicit way - materialise each `6 x 12` Jacobian,
   form `G_k = J_k^T J_k`, form `(G_i + G_j)/2 + delta I`, evaluate
   `Delta^T M Delta` - and matched the vectorised closed form to
   max relative difference `2.2283794924492745e-15`
   (max absolute `1.7763568394002505e-15`). This kills the strongest
   counter-hypothesis, that the exact arm loses because my cost formula is
   buggy.
3. **Bit repeat.** A second independent process wrote a byte-identical
   `step2_results.json`, SHA-256
   `cde475ceba8ad3a2511ba76aa6d49d9e5766dbbfc4d27c9c514268faf743b784`.
4. **Third-party agreement.** My 10,000-draw whole-state bootstrap for the
   frozen surrogate arm gives `[0.894376, 0.929271]` against the judge's
   independently computed `[0.8942, 0.9291]`; my mean/median unit ratios
   `0.914201 / 0.922277` reproduce the judge's `0.914201 / 0.922277`.

## Attack on the conclusion

- *Is the exact arm crippled by a degenerate ridge?* No. The regularizer is
  `3.154e-4` to `5.827e-4` and the ridge term carries only
  **1.03% to 1.67%** of total pairwise cost. The metric is dominated by the
  pullback, as intended, and the routing does not collapse
  (effective rank `2.673`, medoids unambiguous).
- *Is the closed-form cost wrong?* Ruled out by the explicit-matrix
  recomputation above at `2.23e-15`.
- *Is the derivative wrong?* Ruled out by step 1 at `6.5e-10`, against two
  independent observable implementations.
- *Could a different admissible ridge rescue it?* The transport standardises
  costs by their positive median, so a global rescaling of the metric is
  exactly cancelled; only the ridge share is free, and it is already small.
  Moving it is a new tuned constant on these same 32 units, which the fold
  protocol prohibits and which I did not do.

## Honest limitation

The prescribed mutation bundles two changes that cannot be separated inside
the judge's own recipe: the feature space moves from
`[gate_response, active_response]` to `theta = [alpha, ell]`, and the metric
moves from the averaged surrogate gram to the exact per-component local
pullback. The measurement therefore establishes that the chain-rule-correct
pullback *as prescribed* routes worse than the surrogate; it does not
attribute that loss between coordinates and metric. Decomposing it would need
two arms that were never predeclared, and no such arm was run.

## Interpretation for the ledger and the writeup

The mining record predicted "zero for the score" and gave the reason as
"no mechanism-level reason to expect a metric change to move it 12%". The
measurement is stronger than the prediction: the correct metric is not
neutral, it is actively harmful, and the surrogate's 8.85% advantage was an
artifact of the surrogate. The frozen ensemble builds `alpha_out` and
`log_scale` out of the same gate/active memories that the surrogate `psi`
consumes, so the surrogate features are aligned with the generator's own
latent regime structure (three `REGIME_CENTERS`), while `theta` is that
structure plus the terminal noise. Routing on the exact observable
sensitivity is routing on a quantity that is nearly flat across the regimes
that actually determine the compression error.

Consequences:

- Ledger idx 35 `ecn_exact_jspace_psi_streaming` is now **measured and killed**,
  not merely proposed. The judge's "unresolved family: attenuation under a
  chain-rule-correct metric" is resolved in the negative at screening scale.
- The judge's own fallback instruction applies verbatim: "If the exact-Jacobian
  rung does not retain the synthetic advantage, preserve entropic transport and
  total-moment decoding, locally kill this `psi`, and stop the ECN ladder family
  rather than tuning its constants." `tau` and `phi` passed every structural
  gate again here and remain salvageable; the ECN ladder family stops.
- The parent idx 34 kill is untouched and unflipped.
- **Deployment remains closed** independent of this result. At target shape
  `K = 4qn = 3072`, `p = 2n = 512`, the builder's own `4K^2p` geometry term is
  `19,327,352,832` FLOPs and the projected total is `89,924,567,040` against
  the `80,000,000,000` ceiling. No cost mutation was attempted and no cost gate
  is claimed. (Noted without being claimed as a gate: the exact pullback happens
  to have an `O(K^2 d)` closed form with no `K x K x p` materialisation, which
  removes the judge's 38.65 GB delta tensor but not the `K^2 p`-order arithmetic.
  It buys memory, not FLOPs, and it is now moot.)

The Phase-1 selection is untouched. Payoff is Phase-2 hygiene and writeup
completeness: the entropic-transport family can now be described as measured
under a chain-rule-correct metric rather than mis-described.

## Files

- `PREDECLARATION.md` - written before any code
- `step1_jacobian_cd.py` / `step1_results.json`
- `step2_psi_swap.py` / `step2_results.json`
- `step3_crosscheck.py` / `step3_crosscheck.json`
- `results.json` - consolidated verdict record
