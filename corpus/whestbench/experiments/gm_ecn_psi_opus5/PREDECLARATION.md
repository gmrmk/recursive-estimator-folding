# PREDECLARATION - graveyard revival gm_ecn_psi

Written BEFORE any code was written or run. Search key:
`ecn_exact_jspace_psi_streaming`. Ledger record: `fold_ledger.json`
candidates[35], `status=proposed`, no result field. Parent: candidates[34]
`ecn_jacobian_maxent_compressor`, `status=killed`.

## 0. Deviations declared up front

1. **The frozen implementation is not inside the publish repo.** It lives at
   `<codex>/work/scorefloor_generation/ecn_jacobian_maxent_compressor/experiment.py`
   (33,027 bytes, listed in `IMPLEMENTATION_HASHES.sha256`). I read it
   read-only and **import** it as a module; I do not copy, edit, or re-freeze
   it. All `tau` (`entropic_transport`), `phi` (`decode_total_moments`),
   generator (`make_instance`), and comparator (`generic_q3`) code paths are
   the frozen originals, called by reference.
2. **Nothing else is scaled down.** K=48, d=6, q=3, DEPTH=12, the same 32
   frozen seeds `range(2026080600, 2026080632)`.
3. Deployment remains closed regardless of outcome: the `4K^2p` geometry term
   at K=4qn=3072, p=512 is 19,327,352,832 FLOPs and the judge's projected total
   is 89,924,567,040 against the 80B ceiling. No cost mutation is attempted
   here and no cost gate is claimed to pass.
4. Only `psi` is mutated. `tau` keeps its adaptive Sinkhorn stopping rule (the
   judge's "exactly 64 iterations" repair is a *different* single-mechanism
   mutation and is out of scope for the cheapest falsifier). `phi` keeps its
   hardcoded K=48/d=6 shape (shape-genericity is likewise a different
   mutation). Sinkhorn iteration counts are recorded, not gated.

## 1. Mechanism under test

Replace the ECN compressor's SPD *surrogate* metric with the exact ReLU
observable Jacobian in the true component coordinates
`theta = (alpha, ell)`, `ell = 0.5 log diag(C)`.

The per-coordinate observable actually used by the frozen harness
(`gaussian_relu_mean`) is, for `z ~ N(mu, sigma^2)`, `alpha = mu/sigma`,
`sigma = e^ell`:

```text
o(alpha, ell) = mu Phi(alpha) + sigma phi(alpha) = sigma h(alpha),
h(alpha)      = alpha Phi(alpha) + phi(alpha).
```

Because `h'(alpha) = Phi(alpha) + alpha phi(alpha) + phi'(alpha) = Phi(alpha)`,
the exact Jacobian blocks are

```text
J_alpha = diag(sigma Phi(alpha)),
J_ell   = diag(sigma h(alpha)).
```

Per component `k`, `G_k = J_k^T J_k` with `J_k = [J_alpha,k | J_ell,k]`
(d x 2d). For a pair `(i,j)` the routing cost is the judge's prescribed
symmetric local pullback

```text
C(i,j) = Delta^T ((G_i + G_j)/2 + delta I) Delta,   Delta = theta_i - theta_j.
```

The frozen harness applies its ridge in robust-standardized feature
coordinates (`gram = S G S + delta I`, `delta = trace(S G S)/(100 * 2d)`).
I mirror that convention exactly: `S = diag(robust MAD scale of theta)`,
`G_k -> S G_k S`, `delta = trace(S Gbar S)/(100 * 2d)` with
`Gbar = mean_k G_k`, and distances computed in standardized theta.
Because the frozen `tau` divides all costs by their positive median, any
global positive rescaling of the metric is exactly cancelled; only the
ridge-to-signal ratio is a free choice, and it is fixed by the frozen
convention above. No other constant is introduced, tuned, or selected.

Everything downstream (`tau`, `phi`, q3, no-ladder topology, the 32 seeds,
the generic comparator) is byte-identical frozen code.

## 2. Predicted outcome, ON RECORD

- **Step 1 (central differences) PASSES.** The two blocks above are the
  analytically correct derivatives of the frozen observable; a correct
  derivative survives a finite-difference check. Predicted max relative error
  below 1e-8.
- **Step 2 FAILS both gates.** Predicted exact-psi aggregate ratio stays in
  `[0.85, 1.05]`, i.e. above 0.8942 and far above 0.80. Rationale on record
  (mining note): the surrogate-vs-exact difference is a change of routing
  *metric* only; the pre-repair ratio 0.911472 is 8.85% of improvement against
  a required 20%, and no mechanism-level argument predicts a metric change
  worth 12 percentage points. Expected gain for the score: ZERO.
- **Therefore predicted verdict: KILL_CONFIRMED for ledger idx 35.**

## 3. Step 1 - exact-Jacobian central-difference validation (kill gate)

Evaluation domain: every `(alpha, ell)` actually present in the 32 frozen
instances, `32 x 48 x 6 = 9,216` scalar coordinates, both derivative blocks
(18,432 derivative entries).

- **G1A** `max |dCD/dalpha - sigma Phi(alpha)| / (|sigma Phi(alpha)| + 1e-12) <= 1e-6`,
  central difference step `h = 1e-5` on `alpha` with `sigma` held, using the
  frozen `gaussian_relu_mean` as the observable.
- **G1B** same for the `ell` block against `sigma h(alpha)`, `<= 1e-6`.
- **G1C (independent second signal)** an erf-free Gauss-Legendre quadrature of
  `int_0^inf z N(z; mu, sigma^2) dz` (400 nodes on `[0, mu + 14 sigma]`,
  smooth integrand) reproduces the frozen `gaussian_relu_mean` to max relative
  error `<= 1e-10`, AND central differences of *that* quadrature observable
  match the analytic blocks to max relative error `<= 1e-6`.
- **G1D** step-halving consistency: the `h = 1e-5` and `h = 5e-6` central
  differences agree with the analytic value to within the same 1e-6 bound
  (guards against a lucky step size).

**KILL CONDITION FOR THE WHOLE RECORD:** if G1A, G1B, G1C or G1D fails, the
record `ecn_exact_jspace_psi_streaming` dies here, step 2 is NOT run, and the
verdict is KILL_CONFIRMED with zero compression runs.

## 4. Step 2 - identical no-ladder cell, psi swapped (only on step-1 pass)

Arms, all on the same 32 frozen states:

| arm | source |
|---|---|
| `generic_q3` | frozen, denominator |
| `jacobian_maxent` (surrogate psi, no ladder) | frozen, reproduction anchor |
| `jacobian_exact_psi` (no ladder) | this mutation |

Gates:

- **G2-REPRO (two-signal anchor, must pass or the run is void)**
  in-process re-run of the frozen arms reproduces the cached
  `results.json` values: `generic_q3` aggregate RMS `0.014398754762932663`
  and `jacobian_maxent` aggregate ratio `0.9114717897200765`, each to
  relative `<= 1e-12`.
- **G2-PRIMARY (the original idx-34/35 effect gate)**
  `ratio(jacobian_exact_psi) <= 0.80` AND wins vs `generic_q3` `>= 24/32`.
- **G2-MATERIALITY (the mined gate vs 0.911472)**
  `ratio(jacobian_exact_psi) < 0.8942` - the lower endpoint of the judge's
  whole-state bootstrap 95% interval `[0.8942, 0.9291]` for the surrogate
  no-ladder ratio. This is a pre-existing number from
  `ECN_JACOBIAN_MAXENT_JUDGE.md`, not one I invented.
- **G2-STRUCTURAL** for the new arm: max global-mean residual `<= 2e-10`,
  max global-covariance residual `<= 2e-10`, PSD violation `<= 2e-10`,
  Sinkhorn marginal residual `<= 2e-10`, bin-mass residual `<= 2e-8`,
  minimum hard-assignment effective rank `>= 2.5`, medoids unambiguous,
  component-permutation and coordinate-gauge residuals `<= 2e-10`, all finite.
  A structural failure is itself a kill.

Secondary statistics (reported, not gated): paired per-unit sign test
exact-vs-surrogate, and a 10,000-resample whole-state bootstrap 95% interval
for the exact-psi pooled ratio and for the paired ratio difference, at a fixed
predeclared seed 20260810.

## 5. Verdict map

- step 1 fails -> **KILL_CONFIRMED** (record dies, no compression run).
- step 1 passes, G2-PRIMARY fails and G2-MATERIALITY fails -> **KILL_CONFIRMED**.
- step 1 passes, G2-MATERIALITY passes but G2-PRIMARY fails -> **INCONCLUSIVE**
  (science moved; deployment stays closed by the K^2 p arithmetic).
- G2-PRIMARY and G2-MATERIALITY and G2-STRUCTURAL all pass -> **REVIVED_PASS**
  (still a science-only pass; deployment stays closed).
- G2-REPRO fails -> **INCONCLUSIVE**, harness not trusted.

## 6. Firewall

Synthetic frozen generator only. No WHest rows, no truth, no scorer, no
private/holdout data, no network, no submissions, no git. No read or import of
`m245_*`, `M243`, `M244`, or `journal-m245*`. Writes confined to
`corpus/whestbench/experiments/gm_ecn_psi_opus5/`. Interpreter pinned to
`<codex>/work/whest-v014/Scripts/python.exe` (Python 3.14.4, numpy 2.4.6),
identical to the environment recorded in the frozen `results.json`.
