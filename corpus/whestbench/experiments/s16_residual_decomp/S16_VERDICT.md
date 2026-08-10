# S16 — residual/norm decomposition (CONFIRMATORY)

Ledger id: `s16_residual_norm_decomposition_confirm`. Date: 2026-08-09.
Runner: `run_s16.py`. Machine-readable: `s16_results.json`.

## VERDICT: CONFIRMED

**residual decomposition = antipodal symmetrization.** The residual/norm split
is not a new lever; it is a re-derivation of the champion's existing antipodal
pairing, and its "analytic linear + Gaussian corrections" deep reading is the
M181/T2 closure family — the known non-Gaussianity wall, above the sampling
floor. No surprise.

| gate | measurement | bar | pass |
|---|---|---|---|
| G1 layer-1 identity | max abs dev = **0.0** (bit-exact, all 3 nets, 8.26M entries each) | < 1e-10 | ✅ |
| G2 residual-split MSE match | ratio resid/champ = **1.000000**; max final abs dev = **0.0** | within 1% | ✅ |
| G3a linear-part mean ≈ 0 | mean magnitude decays **~2.26×** when n grows 4× (sqrt(4)=2.0 predicted) | 1/√n noise | ✅ |
| G3b closure at M181 wall | arm1 Gaussian-closure MSE **1.28e-6** vs sampling arm0 **3.41e-7** (3.7× above) | above sampling | ✅ |
| surprise: resid beats champ >10% at matched FLOPs | ratio 1.000000 | — | none |
| surprise: any layer near-identity R_l<0.3 | min R_l = 1.108 | — | none |

## Deviations (recorded first, loudly)

1. **Closure numbers CITED, not re-run** (task-sanctioned). The Gaussian-closure
   MSE/bias for G3b are the committed M181 `arm1_univariate`/`arm2_pairprop`
   values from `m181_g0_results.json`; S16 re-runs only the cheap linear-mean
   check.
2. **Linear-mean check uses own MC** (task-sanctioned: "your own high-sample
   MC"), fresh N(0,I) at n=200k and 800k per net, disjoint seed streams.
3. **Form-1 R_l** computed on the antipodal doubled design set (2·32,256 =
   64,512 rows), one rotation seed per net, averaged over the 3 nets. This is
   the exact activation set the champion forward propagates.
4. **Champion cross-check is sub-ppm, not bit-identical** to the stored M181
   arm0: fresh recompute gives per-net ratios 0.99999722 / 0.99999870 /
   0.99999719 (float summation order in the MSE average). It confirms the S16
   champion IS the committed m181 arm0 antipodal Kerdock forward mean.

## Test 1 — layer-1 identity (the core check)

For every design point on all 3 nets, computing BOTH matmuls with the actual
`+points` and `-points`:

    ReLU(W1 (r u)) + ReLU(W1 (r(-u)))  ==  |W1 (r u)|

**max abs deviation = 0.0 (exactly), 8,257,536 entries per net.**

Mechanism (second signal, why it is bit-exact rather than merely tiny): the
negation is exact in IEEE-754 round-to-nearest — `W1(r(-u)) == -(W1(r u))` to
0.0 (measured `max_abs_neg_dev = 0.0`) — and for any float `x`, `max(x,0) +
max(-x,0)` equals `|x|` bitwise (the ReLU pair is a clamp partition). So the
odd half `z/2` is cancelled EXACTLY by antipodal pairing; the pair sum keeps
only the even half `|z|`. Antipodal pairing **is** the residual even-part split
at layer 1.

## Test 2 — full-estimator equivalence (matched billed samples)

Champion = frozen `antipodal_forward_mean` (concat ReLU(±z), propagate the
64,512-row set). Residual-split = build the layer-1 set from the even/odd
decomposition `|z|/2 ± z/2` (= ReLU(z), ReLU(−z)) then run the identical deep
tail. Both bill 64,512 final-layer samples. 3 nets × 16 rotation seeds:

| net | MSE champion | MSE residual-split | ratio | max final |dev| |
|---|---|---|---|---|
| 101 | 1.9972e-07 | 1.9972e-07 | 1.000000 | 0.0 |
| 202 | 5.8721e-07 | 5.8721e-07 | 1.000000 | 0.0 |
| 303 | 2.3692e-07 | 2.3692e-07 | 1.000000 | 0.0 |

**Panel MSE ratio resid/champ = 1.000000; max final abs deviation = 0.0 over
all 48 (net,seed) 256-vectors.** The two estimators are bit-identical because
`|z|/2 + z/2` and `|z|/2 − z/2` reconstruct `ReLU(z)` and `ReLU(−z)` bitwise;
keeping "only the even half" while integrating the odd half to its known zero
mean reproduces the same 2N antipodal set the champion already propagates.

Independent cross-check: the S16 champion MSE reproduces the committed M181
arm0 baseline to < 3e-6 relative on every net (mean ratio 1.000).

## Test 3 — deep / closure arm (the closure wall)

**Linear part carries no signal.** Replacing every ReLU with identity gives
`f_lin(x) = x · (first_eff · W1 · … · W31) = x·M`. Under E[x]=0, E[f_lin] =
Mᵀ E[x] = 0 exactly. The MC mean is exactly `x̄·M` (x̄ = input sample mean),
pure 1/√n noise:

| net | rms(mean) n=200k | rms(mean) n=800k | decay (√4=2.0 pred) |
|---|---|---|---|
| 101 | 2.058e+02 | 8.996e+01 | 2.29 |
| 202 | 1.578e+02 | 5.442e+01 | 2.90 |
| 303 | 1.490e+02 | 9.296e+01 | 1.60 |

Mean decay ≈ 2.26 (brackets the 1/√n prediction). A real nonzero mean would not
shrink; the decay is decisive that the linear part is exactly zero-mean. Hence
the entire E[f] lives in the ReLU corrections — the non-Gaussian part.

**Closure lands at the M181 wall, above sampling** (M181 committed, cited). The
"analytic linear + Gaussian corrections" predictor is exactly the M181/T2
family. One terminal Gaussian-closure step (M181 arm1) has raw MSE
9.87e-7 / 1.79e-6 / 1.06e-6 (mean 1.28e-6), bias²-dominated (bias share
0.67–0.78); two steps (arm2) ≈ doubles it. That is **3.7× ABOVE** the sampling
floor arm0 mean 3.41e-7 (~2.5e-7 order), never below. Per-neuron closure
deviation rms ≈ 9.66e-4 vs plain-MC noise ≈ 2.5e-4 (M181_G0_NOTES). The residual
view IS the killed closure family; it cannot beat sampling.

## Form-1 reparametrization (owner scope add)

Rewrite each layer y_{l+1} = y_l + F_l, F_l = ReLU(W_{l+1} y_l) − y_l, and
measure the per-layer residual magnitude ratio
R_l = mean_u‖F_l‖₂ / mean_u‖y_l‖₂ for l = 1..31 (the 31 hidden layers, on the
64,512-row antipodal design set, averaged over the 3 nets).

**R_l profile: min = 1.108, median = 1.162, max = 1.231.**

Every layer has R_l > 1 — the residual (the change a layer makes) is *larger*
than the state it acts on. **No layer has R_l < 0.3**; there is no near-identity
candidate at any depth. The layers genuinely transform (they do not perturb an
identity), so a residual/skip perturbative truncation offers no lever, and
Form-1 reduces to the S8 contraction law. This is consistent with S8's
0.87/layer contraction and c_32 = 0.975 coherence: the map moves points
substantially. **Verdict: R_l = O(1) at all depths — Form-1 reduces to S8, no
perturbative lever (predicted; confirmed).**

## Files

- `run_s16.py` — the harness (tests 1–3 + Form-1 profile + gates)
- `s16_results.json` — machine-readable results, gates, per-net tables
- `S16_VERDICT.md` — this file
- `_probe.py` — pre-run timing / truth-match probe (scratch)
