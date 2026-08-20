# B-PRIME RE-PHASE — THE SYMMETRY GATE

**Date** 2026-08-19. **Rung** R0/R1 (committed-artifact reads, exact algebra, and one
disclosed off-protocol smoke on synthetic networks). **Status** the cell dies here.

```
symmetry_gate_verdict = CLOSED_BY_DERIVATION
cell_ready            = false
run cost spent        = 0 harness invocations, 0 seeds, 0 scored rows, 0 ledger writes
```

**Evidence tags** `[O]` observed or computed this session · `[D]` derived, steps shown ·
`[R]` reported by a committed artifact · `[A]` labelled assumption · `[GAP]` named hole
with its settling check.

---

## 0. VERDICT, FIRST

**Re-phasing arm B is a rigid rotation of its carrier, and the estimator already
integrates over the rotation group with the exactly right-invariant measure. The lever
therefore moves nothing — not the expected MSE, not any higher moment, not the regime
partition, not the billed FLOPs. The whole per-net, per-arm joint law is identical.**

The kill is stronger than the "Schur ⟹ every `A_l` is preserved" argument the brief
anticipated. Schur bounds the *quadrature* term; this gate closes the **non-quadrature**
term as well, because the regime partition — the sole nonlinearity in the deployed path,
and the only channel that can break `MSE = Σ_l E_l A_l` — is itself exactly
rotation-covariant. That was measured, not assumed: under the re-phase the 28-layer
active-set trajectory is bit-identical to the trajectory under the equivalent rotation
re-parameterisation, on 3/3 synthetic nets (§3).

Three consequences, each stated at its earned level:

1. **The named B-prime family is dead by derivation.** `{I} ∪ {H diag(φ_s) diag(ε)/16}`
   is exactly `Z · diag(ε)` — right-multiplication of the whole carrier array by a fixed
   orthogonal matrix. So is *any* construction preserving the pairwise `|⟨u,v⟩|`
   structure, that being precisely the condition for two ordered configurations to be
   related by an orthogonal map after row sign flips. `ΔE[MSE] = 0` exactly `[D + O]`.
2. **The frame-0 hazard (`P2`) cannot exist as a mechanism.** Arm B's all-plus Sylvester
   Walsh row sits in exactly one frame — frame 0, row 0 `[O]`. The rotation
   `Z · diag(φ_s)` with `s ≥ 4` moves that row out of both pilot windows and installs a
   genuinely phased row set at frame 0, verified for `s ∈ {1, 5, 63, 127}` `[O]`. A pure
   rotation provably changes nothing, so removing the all-plus row from the pilot buys
   exactly zero. The `P2` prediction band `B'/B ≤ 0.96` is refuted before it is measured.
3. **A per-net channel exists and is not a lever.** Per net, with the rotation held
   fixed, B and B′ genuinely differ — the output moves by `5.0e-4` to `1.2e-3` relative,
   and the regime trace differs. That movement is *exactly the size of a rotation
   re-draw* (`d2/d3 = 1.25 / 0.95 / 0.85`, §3) because it **is** a rotation re-draw. The
   channel survives as noise; it carries no design information.

**Second, independent reason the cell dies — an instrument reason.** Even granting a live
lever of the size both repairs demand (a `+4.4 %` to `+5.2 %` arm-B penalty
`[R, SYNTHESIS §3]`), a `B′/B` contrast at `n = 32` cannot decide it. The two arms
decorrelate to the rotation-lottery level, so `se_log(B′/B) ≈ 0.114` `[D, §5]`, against a
signal of `log 1.044 … log 1.052 = 0.043 … 0.051` — a `0.38σ` to `0.44σ` decision. A `2σ`
decision would need `n ≈ 864`. The cell was underpowered for its own hypothesis
independently of the symmetry.

**What this does not touch.** The `C→B` structural short of `≥ 3.84 %` is real as an
observation and untouched as a question (§4). Its one live mechanism — the regime
partition's misclassification *cost* — is exactly the channel this gate proves is
rotation-invariant, so no B-prime addresses it. The instrument that would price it is
already named (S7 open item (i)), and the campaign's cheapest live discriminator remains
`deg4_rung_dual_carrier` (§6).

---

## 1. THE CODE PATH — where the carrier actually enters

Read from the fenced sources this session, all three arms
(`experiments/frame_completion_129/arm{A,B,C}/`) `[O]`.

### 1.1 The carrier has exactly one entry point

`fold3_estimator.Estimator.predict` touches `z = self._gaussian` in exactly two places:

```python
first_pre = self._first_sample_matmul(z, mlp.weights[0])     # line 70
radius_sq = fnp.sum(z * z, axis=1)                           # line 60, else-branch
```

The second is under `if self.radial_conditioning: final_weights = None / else:`, and
`orthogonal_fold3.Estimator` sets `radial_conditioning = True` `[O]`. The radial-reweight
branch is unreachable on this host — the corpus already records it as "present,
unreachable" `[R, SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819]`, and
CENTRAL_MOMENT_LADDER §3.a.4 proves its four literals are the exact rational optimum of
their span. **So the carrier enters the estimator through one matrix product and nowhere
else.**

### 1.2 The rotation is applied to `W₀`, which is the same as rotating the carrier

All three arms carry the identical `predict` wrapper `[O]`:

```python
rotation = self._haar_rotation(int(mlp.seed), mlp.width)
rotated  = MLP(..., weights=[rotation.T @ mlp.weights[0], *mlp.weights[1:]], ...)
```

so `first_pre = Z (Rᵀ W₀) = (Z Rᵀ) W₀`. Row `i` of `Z Rᵀ` is `R u_i` read as a column.
**The estimator's effective design is `R · F` for the frame set `F`**, and only layer 0 is
rotated; layers 1…31 act on `x`, downstream of that product.

`_haar_rotation` is QR of a Gaussian with the diagonal-sign fix
(`rotation * signs[None, :]`, a column-sign scaling that preserves orthogonality) — the
standard exactly-Haar construction `[O]`.

**The rotation genuinely varies across networks.** The `full` split's first 132 rows carry
132 distinct `mlp_seed` values, and rows 100–131 share no seed with rows 0–99
`[O, metadata-only column read of the Arrow shards; no weights loaded]`. So a 100-net
aggregate is an average over 100 distinct Haar draws, which is what makes the
expectation-over-`R` argument operational rather than nominal.

### 1.3 Antipodal doubling makes per-row sign flips exactly inert

```python
x = fnp.concatenate((fnp.maximum(first_pre, 0.0), fnp.maximum(-first_pre, 0.0)), axis=0)
```

Flipping the sign of carrier row `i` swaps `x[i] ↔ x[n_base + i]`. Every consumer of `x`
is invariant under that swap `[D, exact]`:

| consumer | why invariant |
|---|---|
| `fnp.mean(x, axis=0)`, `fnp.mean(x*x, axis=0)` | means over all `2·n_base` rows |
| main-loop pilot `concat(x[:256], x[n_base:n_base+256])` | the slice is antipodally symmetric, so the swap permutes rows *within* the pilot set; `fnp.max(pilot_pre, axis=0)` is permutation-invariant |
| fold pilots `pilot_x29`, `pilot_x30_kink`, `pilot_x31_kink` | same slicing pattern at `pilot_n = 1024`; `_refine_dead`/`_refine_on` use `max`/`min` over those rows |

Invariance holds up to floating-point summation **order**, not bit-exactly. That residual
is measured at `2e-7` relative in §3 and is the noise floor of the whole argument.

### 1.4 What the estimator can and cannot distinguish

Collecting §1.1–1.3: the estimator's entire output is a deterministic function of

> the **ordered tuple** of effective directions `(R u_1, …, R u_N)` together with the
> network `W`, and it is invariant under per-row sign flips and under any row permutation
> that preserves the three index blocks `[0, 256)`, `[256, 1024)`, `[1024, N)` setwise.

Nothing reads the carrier in the original coordinate frame; nothing reads a row norm
(they are all exactly `r̄` by construction); nothing reads a frame index beyond those
three blocks.

---

## 2. THE THEOREM

**T1 — rotation covariance.** By §1.1–1.2 the output is `F(Z Rᵀ, W)`; `Z` occurs nowhere
else in the path `[O, source]`.

**T2 — Haar right-invariance.** For fixed orthogonal `G` and `R ∼ Haar`, `R Gᵀ ∼ Haar`.
Then `(Z G) Rᵀ = Z (G Rᵀ) = Z (R Gᵀ)ᵀ`, so the carrier `Z G` under rotation `R` has the
same law as the carrier `Z` under a Haar rotation `[D]`.

**T3 — sign invariance.** §1.3 `[D, exact]`.

> **COROLLARY (the gate).** For any fixed orthogonal `G ∈ O(256)` and any per-row sign
> pattern, the carrier `Z′ = D_sign · Z · G` induces the **same joint distribution** as
> `Z` for every quantity the estimator produces — the final-layer vector, the
> dead/kink/on partition at every layer, `flops_used`, and hence `final_layer_mse` and
> `adjusted_final_layer_score`. In particular `E[MSE_{B′}] = E[MSE_B]` **exactly**, and so
> is every higher moment, the per-net distribution, and the ensemble ratio of means.

### 2.1 The named family is a special case

Arm B's setup builds `block[s] = r̄ · H diag(φ_s)` for `s = 0…127` and
`block[128] = r̄ · I` `[O, armB/estimator.py:69-79]`. Right-multiplying the whole array by
`diag(ε)`, `ε ∈ {±1}²⁵⁶`:

```
H diag(φ_s) · diag(ε) = H diag(φ_s ⊙ ε)      (the phased frames re-phase)
I           · diag(ε) = diag(ε)              (the identity frame, row signs flipped only)
```

and `diag(ε)`'s doubled row set is the doubled identity frame's row set. So

```
{I} ∪ {H diag(φ_s) diag(ε)/16}   ==   Z · diag(ε)   with diag(ε) ∈ O(256)
```

**exactly** — the brief's family is the corollary's `G = diag(ε)` `[D]`. Verified in
float64 that the re-phased design is still an exact complete real MUB-129: within-frame
Gram error `0.0`, cross-frame `max | |⟨u,v⟩| − 1/16 | = 0.0`, over all `129·128/2` frame
pairs `[O]`. And `A_4^{B′} = 0` exactly, since `A_l` is a Gram functional `[D]`.

The re-phase is **not** a relabelling of arm B: for `ε = φ_s` the new phase set shares
only 2 of its 128 elements with the old one `[O]`. It is a genuinely different complete
real MUB-129 design that happens to be a rotation of arm B's.

### 2.2 "Any construction preserving the pairwise |⟨u,v⟩| structure"

Two ordered configurations with equal Gram matrices are related by an orthogonal map;
equal `|Gram|` within one switching class means equal Gram after row sign flips. That is
exactly the hypothesis of the corollary, so **every design in arm B's switching class is
equidistributed with arm B** `[D]`. The brief's own clause names the kill condition.

### 2.3 The frame-0 hazard, killed at its own mechanism

Arm B's frame 0 is `H diag(φ_0)` with `φ_0` the all-plus vector — verified directly from
`kerdock_phases.npz`, `s = 0` `[O]`, independently reproducing S7 ledger item 12. A row of
`H diag(t)` equals `±(all-ones)/16` iff `t` is `±` a Walsh row, i.e. iff `H t` is a single
spike. Scanning all 128 phases `[O]`:

| design | frames containing the all-plus Walsh row |
|---|---|
| arm B as shipped | **frame 0 only** (row 0) |
| `Z · diag(φ₁)` | frame 1 only |
| `Z · diag(φ₅)` | frame 5 only |
| `Z · diag(φ₆₃)` | frame 63 only |
| `Z · diag(φ₁₂₇)` | frame 127 only |

and in each case frame 0 becomes exactly `H diag(φ_s)`, a bent-phase row set `[O]`.

**So `P2`'s construction — "index 0 is a phased row, not the all-plus Walsh row" — is
achievable by a pure rotation for any `s ≥ 4`, which puts the all-plus row outside both
the 256-row main-loop pilot and the 1024-row fold pilot.** A pure rotation changes nothing
by the corollary. The hazard `P2` names cannot exist.

### 2.4 The residue, stated honestly

A **literal frame reorder** of arm B (same multiset, `φ_s` moved to index 0) is *not*
covered by the corollary. The rotation forced by matching frame 0 is `G = diag(φ_s)`
(since `H` is symmetric orthogonal, `H·H = I` to machine zero `[O]`), and that `G` sends
frame `t` to `H diag(φ_t ⊙ φ_s)`, which is not in arm B's phase set: the phase set is
**not** closed under elementwise product — 16,002 of the 16,384 products fall outside it
`[O]` — so it is not a group, and the reorder is not a rotation.

What survives is therefore a difference between two switching classes of complete real
MUB-129 designs, with:

- **no named mechanism** — `P2`'s mechanism (§2.3) is dead;
- **no sign prediction** — no committed artifact states a direction for it, and the
  grep-level check is that `P2`'s band is the only directional claim on file for the
  B-family frame order, and §2.3 refutes its mechanism;
- **three direction-nulls already on file** `[R, S7]`: the detector-power ratio
  `×0.9994` on 4,000 synthetic draws; the layer-1 paired detector at `n = 2,048` exactly
  paired columns (`t = −0.279 / +0.450`, win rates 49.8 % / 50.1 %); and the archived
  `n = 100` FLOP channel for B vs C after removing the row ratio (`t = −0.046`);
- **a measurement floor** set by the rotation lottery (§5).

`[GAP]` I did not enumerate the switching classes of complete real MUB-129 designs in
`R²⁵⁶`. **Settling check:** for a candidate reorder `B_π`, test whether the signed Gram of
`B_π` is switching-equivalent to that of `B` — a `33,024²` sign-consistency check, zero
billed compute. It is not worth running: even a positive result would only re-open a
lever the §5 power calculation cannot measure.

---

## 3. SECOND SIGNAL — the mechanical check

**Off-protocol smoke, fully disclosed.** No harness invocation, no seed consumed, no
scored row, no ledger write, **no dataset network evaluated** — the three MLPs are
synthetic He-initialised width-256 depth-32 nets built inside the script, so no custody
question arises. Compute: frozen venv
`C:/Users/strid/.venvs/whestbench-frozen-m178`, `python -B`,
`PYTHONDONTWRITEBYTECODE=1`, `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`. Total wall
**44.20 s** for 12 `predict` calls (**3.68 s/predict**). The arm-B sources were copied to
the scratchpad and run unmodified; all eight files verified SHA-256-identical to the
fenced originals after the run `[O]`, so the fence is intact and the smoke exercised
production code.

Three distances on the estimator's final-layer output vector, per net, with `ε` a random
sign vector (130 of 256 negative):

| quantity | meaning | predicted |
|---|---|---|
| `d1` | `‖out(Z·diag(ε), R) − out(Z, R·diag(ε))‖ / ‖out‖` | `≈ 0` if the re-phase is a rotation re-parameterisation |
| `d2` | `‖out(Z·diag(ε), R) − out(Z, R)‖ / ‖out‖` | the per-net move the lever makes |
| `d3` | `‖out(Z, R_{seed+7919}) − out(Z, R)‖ / ‖out‖` | the rotation-lottery move (SYNTHESIS §4.2's probe) |

```
net             d1          d2          d3        d2/d3   trace(B',R)==trace(B,R·D)   trace(B')==trace(B)
synthetic-0   2.024e-07   1.154e-03   9.244e-04   1.248            True                      False
synthetic-1   2.654e-07   1.043e-03   1.092e-03   0.955            True                      False
synthetic-2   1.926e-07   4.982e-04   5.883e-04   0.847            True                      False

active-set sums over the 28 main-loop layers (the discrete regime fingerprint):
  net 0   B 5957   B' 5978   Z@R·D 5978   rot-offset 5958
  net 1   B 5855   B' 5862   Z@R·D 5862   rot-offset 5870
  net 2   B 5775   B' 5760   Z@R·D 5760   rot-offset 5780
```

**Three readings** `[O]`:

1. `d1 ≈ 2e-7` is float32 round-off across a `33,024 × 256` product and a 32-layer
   pipeline, and the **28-layer active-set trajectories are identical, integer for
   integer**, on 3/3 nets. The equivalence therefore holds *through the regime partition*,
   not merely through the linear quadrature. This is the load-bearing observation: the one
   channel that can break Schur is itself exactly rotation-covariant.
2. `d2 ≈ d3` to within the spread of three nets. The lever's per-net effect **is** the
   rotation lottery.
3. `trace(B′) ≠ trace(B)` on 3/3 nets. The lever is not trivially inert per net — it moves
   the regime partition by exactly as much as re-drawing the rotation does, and no more.
   That is the wobble, reported rather than smoothed: the corollary is a statement about
   the law, not about a realisation.

`[A]` The corollary needs the law of `R` to be right-invariant. `_haar_rotation` is the
exact Haar construction in exact arithmetic; in float32 it deviates at the `1e-7` scale,
which is the same order as the measured `d1` and four orders below the `3.84 %` the C→B
short would need. **Settling check:** a Monte-Carlo test of `E[Q_l(⟨R e_i, R G e_j⟩)]`
against the exact Gegenbauer value — not run, and not load-bearing at this ratio.

---

## 4. THE `C→B` STRUCTURAL SHORT — each candidate priced

All figures recomputed this session in exact rational arithmetic and from the committed
per-network arrays `[O]`; they reproduce SYNTHESIS §1.2 and THEORY §2.3 to the printed
digit.

```
ceiling  max_l A_l^B / A_l^C  = 2816/2881 = 0.9774383894481083   (attained at degree 6;
                                verified exactly over degrees 4…40, limit 126/129)
measured raw MSE ratio C→B    = 1.0149700854688666
excess over the ceiling       = 1.038398017129192   →  structural short 3.8398 %
paired-delta se_log(C→B)      = 0.029255094280737824
z against the ceiling         = 1.287952007947121
influence-function excess kurtosis 26.3957  →  effective df 7.0433
```

### 4.1 Regime-classification differences — **LIVE, and the only survivor**

Why it is consistent with Schur: `E_R[MSE] = Σ_l E_l A_l` holds for any estimator that is
a **fixed linear functional of the empirical measure**, and the tangent control is exactly
such a functional — its coefficients come from `_diagonal_gaussian_pass`, which reads only
`mlp.weights` `[R, CENTRAL_MOMENT_LADDER §1.4(c)]` — so the ceiling binds on the
*combined* error field, tangent included. The regime partition is the sole sample-dependent,
discontinuous map in the path: a confirmed-dead neuron is dropped from `next_active` and
its sampled activation is treated as exactly `0` on all `2·n_base` rows, with downstream
propagation `[R, S7 §6.3]`. That is a squared-bias term living outside every `A_l`.

Priced with what exists:

| quantity | value | source |
|---|---|---|
| B vs C main-loop decision disagreement | `10.570 %` of 13,756 decisions — **the highest of the three arm pairs** | `[R, S7 §3]` |
| B vs C terminal disagreement | `3.125 %` (dead rescue), `2.519 %` (on demotion) | `[R, S7 §3]` |
| B − C dead-and-unrescued count | `+8.0` per net, `se 5.355`, `t = +1.494`, `n = 8`, 95 % CI `[−4.66, +20.66]` | `[R, S7 §2.3]` |
| direction on the archived `n = 100` FLOP channel (row ratio removed) | `t = −0.046` | `[R, S7 §5]` |
| **cost of a misclassification** | **unpriced** | `[R, S7 open item (i)]` |

**And decisively for this cell:** §3 measures that the regime partition is exactly
rotation-covariant. **No B-prime in the re-phase family can move this channel by any
amount.**

### 4.2 The identity frame's interaction with radial conditioning — **priced at 0**

`radial_conditioning = True` ⟹ `final_weights = None` ⟹ the plain mean, and the
`radius_sq`/`q1`/`q2` reweight branch never executes `[O, §1.1]`. Both arms build rows of
norm exactly `r̄`: `r̄·e_i` for the identity frame, `r̄·h_i` with `‖h_i‖ = 1` for the
phased-Hadamard frames. `_radial_covariance = r̄²/width` is identical.

The only residual is float32: `r̄·e_i` has exact norm `r̄`, while `r̄·h_i` has norm
`r̄(1 + O(2⁻²⁴)) ≈ r̄(1 ± 6e-8)`. That perturbation lives on `1/129` of the rows, so its
aggregate effect is `≤ 5e-10` — **seven orders of magnitude below the `3.84 %` required**
`[D]`.

### 4.3 Finite-sample realized-defect fluctuation — **priced at exactly 0 on this leg**

Arms B and C both load frozen deterministic designs from `kerdock_phases.npz`; neither
setup path calls an RNG at `width = 256` `[O, armB/armC estimator.py]`. `A_l` is a
function of the Gram matrix alone and is therefore invariant under the per-net Haar
rotation. **The realized `A_l` equals the exact `A_l` with zero variance, for every net
and every rotation draw.** There is no realized-defect lottery on the `C→B` leg at all.
(Arm A does draw its frames once from `default_rng(ctx.seed)`; even there the deviation is
`1e-4`, with `h₄ = 1.83e8` in the denominator `[R, SYNTHESIS §1.2(a)]`.)

What does fluctuate is the network draw and the per-net rotation draw, and both are inside
`se_log = 0.029255`. **So the honest reading of the short is `z = 1.288` on a leg with
`7.04` effective degrees of freedom, one-sided `p(T₇) ≈ 0.12` — suggestive, not
established** — which is exactly where SYNTHESIS §1.2 demoted it.

### 4.4 The tangent control — **priced at 0 as a ceiling-breaker** (candidate not in the brief)

Added because it is the obvious fourth place to look. `delta_mean` is the image of
`(Δμ, Δv)` under a linear map with sample-independent coefficients, so the estimator's
total error remains a single linear functional of the empirical measure of a combined
field `[R, CENTRAL_MOMENT_LADDER §1.4(c), re-read this session]`. The Schur decomposition
applies to that field's energy profile, and `max_l A_l^B/A_l^C` bounds the ratio for every
nonnegative profile. The tangent cannot exceed the ceiling `[D]`.

### 4.5 Summary

| candidate | verdict | closing number |
|---|---|---|
| regime-classification / DEAD-KINK-ON split | **LIVE — the only one** | cost unpriced; count direction null (`t = +1.49`, `n = 8`); **rotation-covariant, so no B-prime reaches it** |
| identity frame × radial conditioning | dead | `≤ 5e-10` of the aggregate vs `3.84e-2` required |
| finite-sample realized-defect fluctuation | dead | exactly `0` — both designs deterministic, `A_l` rotation-invariant |
| tangent control | dead | exact linearity ⟹ the ceiling binds |
| cross-degree covariance | dead | `0` at order 2 by Schur; `4.999e-07` suppression at order 4 `[R, CML §3.b]` |

---

## 5. THE INDEPENDENT INSTRUMENT KILL

Even granting a live lever, `n = 32` cannot decide it.

A `B′/B` contrast has no pairing benefit beyond the shared network, because the entire
difference is the rotation lottery (§3). Building the leg's per-net influence dispersion
from the fitted null `[R, SYNTHESIS §2.2: σ_FB = 0.3960]` and SYNTHESIS §4.2's own
prediction `ρ ≈ 0.05–0.15` for the rotation-offset correlation `[A, both labelled]`:

```
SD(log b′ − log b)  = sqrt(2 · 0.3960² · (1 − 0.10))                = 0.5313
ratio-of-means inflation, calibrated on the B/A leg
    measured se_log(B/A) = 0.073837 at n = 100  vs  sqrt(σ_FA²+σ_FB²)/10 = 0.06068
    inflation factor                                                = 1.217
effective per-net influence SD for B′/B                             = 0.6466
se_log(B′/B)  at n = 32                                             = 0.1143
              at n = 100                                            = 0.0647
```

Against the demanded effect (`+4.4 %` to `+5.2 %`, i.e. `log = 0.04306…0.05069`), that is
a **`0.377σ` to `0.444σ`** decision at `n = 32`. A `2σ` decision needs `n ≥ 902` networks
at the lower edge of the demanded band and `n ≥ 651` at the upper edge `[D]`.

**And the instrument's own precision is poor at that `n`,** by the rung-2k law
`[R, CENTRAL_MOMENT_LADDER §2.1]`, `sd(ŝ)/σ = ½√((κ − (n−3)/(n−1))/n)` — recomputed this
session on the 129 cell's measured influence-function kurtoses `[O]`:

| leg | `κ` (influence fn) | `n` | eff. df | rel. sd of the reported `se` | 95 % window multiplier on `se` |
|---|---:|---:|---:|---:|---|
| B/A | 6.6924 | 100 | 35.13 | ±11.95 % | `[0.766, 1.234]` |
| B/A | 6.6924 | **32** | **11.24** | **±21.21 %** | `[0.584, 1.416]` |
| C/A | 5.5953 | 100 | 43.52 | ±10.74 % | `[0.789, 1.211]` |
| C/A | 5.5953 | **32** | **13.93** | **±19.08 %** | `[0.626, 1.374]` |
| B/C | 29.3957 | 100 | 7.04 | ±26.65 % | `[0.478, 1.522]` |
| B/C | 29.3957 | **32** | **2.25** | **±47.15 %** | `[0.076, 1.924]` |

`T_CRIT` two-sided 95 % at `df = 31` is `2.039513446396273`; at `df = 99` it is
`1.9842169515864128`, reproducing the 129 cell's committed constant to 10 digits `[O]` —
which is the check that the quadrature behind this table is sound.

The bottom row is the one that matters for any future B-family cell: a `C/B`-shaped leg at
`n = 32` reports a standard error good to a factor of two. **Under the rung-2k
prescription such a cell would be INSTRUMENT-SUSPECT on filing**, before the symmetry
question is even asked.

---

## 6. WHAT REMAINS LIVE (named, not executed)

1. **`deg4_rung_dual_carrier`** — add the degree-4 rung to the already-built
   `deg_ladder_own_axis_capture_v2` ladder `[R, DEG4 §6.2 / ULTRAMATH_SLATE entry 8]`.
   `cost_vs_B ≈ 0`, strictly cheaper than rungs already consumed, and the instrument gates
   *better* at degree 4 than at every rung already run (`feature_reach` 1.001 at degree 6,
   falling monotonically). Predeclared prediction `3.35×` the degree-six rung. It measures
   the single number the whole `2.81×` demand turns on. **Untouched by this gate.**
2. **The misclassification-cost instrument** — S7 open item (i): a per-net MSE
   decomposition with the rescue set forced to a common choice across arms. It is the only
   route to the `C→B` short, and it is a new instrument, not an arm.
3. **The rotation-offset probe** `[R, SYNTHESIS §4.2]` still needs its custody ruling. This
   gate has already measured its *magnitude* on synthetic nets: `d3 ≈ 5.9e-4 … 1.1e-3`
   relative on the output vector, the same size as the re-phase move (§3). Its open
   question — whether the per-net *ratio* decorrelates on the burned panel — is unchanged.

**A harness finding for whichever cell runs next** `[O, `whest run --help` read this
session]`: there is no row-offset or row-range flag. The only selector is `--n-mlps N`,
which takes the **first** `N` rows of the split. Rows 100–131 of `full` are unburned (132
distinct seeds in the first 132 rows; zero seed overlap with rows 0–99 `[O]`), so an
unburned block requires `--n-mlps 132` with a predeclared restriction to indices 100–131
in the analysis layer, and the mechanics disclosed exactly. Budget, from this session's
measured `3.68 s/predict` on synthetic nets against the 129 cell's `6.7 s/net` production
rate: `132 nets × 4 arms × 6.7 s ≈ 59 min`, and a `wall_seconds` cap of `5400` would carry
`1.5×` margin. Recorded so the next cell does not have to re-derive it.

---

## 7. ATTACK ON THIS DOCUMENT

**The strongest way this is wrong: the corollary proves a distributional identity, and the
cell would have measured a single realisation.** Priced and answered — that is exactly the
wobble in §0.3 and §3.3. Per net the lever moves the answer by `~1e-3` relative, and the
regime trace changes. What §3 establishes is that the move is a rotation re-draw of the
estimator's own randomization, whose mean is exactly zero over the 132 distinct seeds the
split supplies. The way this would have bitten is if the seeds were degenerate — one
rotation reused across all nets — which would have collapsed the expectation to a single
draw. **I tested that specific way:** the first 132 rows carry 132 distinct `mlp_seed`
values `[O]`. The attack did not land, and it was the one that could have.

**Second attack: the phase set might have been a group, in which case §2.4's residue would
have been empty and the kill would have been total.** It is not — 16,002 of 16,384
elementwise products fall outside the set `[O]` — so the literal frame reorder is *not*
covered, and §2.4 says so rather than over-claiming. The attack landed partially and the
result is in the document.

**Third attack: `H diag(φ_s)` might be a degenerate frame, making the §2.3 rotation
illegitimate.** Tested: the re-phased design is an exact complete real MUB-129
(within-frame Gram error `0.0`, cross-frame deviation from `1/16` equal to `0.0` in
float64) with `A_4 = 0` exactly `[O]`. It is as legitimate an arm B as arm B.

**Fourth attack: the smoke's synthetic nets might not exercise the pilot.** They do — the
main-loop active sets move (5957 → 5978 under the re-phase on net 0), so cold neurons
exist and rescue decisions flip. Had all neurons been structurally active, the regime-trace
equality would have been vacuous.

**What I did not look at.** I ran no dataset network and computed no MSE against ground
truth — the smoke compares estimator *outputs*, which is sufficient because MSE is a
deterministic function of the output. I did not enumerate MUB switching classes (§2.4
`[GAP]`). I did not price the misclassification cost (§4.1) — that needs S7's named
instrument and is out of this gate's scope.

---

## 8. CUSTODY AND INVENTORY

Zero billed compute against `B = 2.72e11`: no harness invocation, no estimator run on any
dataset network, no seed consumed, no scored row, no ledger write, no designation surface.
Writes confined to this file and the session scratchpad. Reads: the three arm source trees
under `experiments/frame_completion_129/` (fenced, read-only — copied to scratch and
verified SHA-256-identical afterwards, all 8 files), the three committed arm reports,
`armB/kerdock_phases.npz`, `runner_fc129.py`, `whest run --help`, and a metadata-only
column read (`mlp_seed`, `mlp_name`) of the `full` split's Arrow shards with no weight
column materialised. `PHASE2_CONTRIBUTION_DRAFT` and the disclosure were not opened for
writing and were not modified.

**Concurrency note** `[O]`. The v1.4 manuscript workflow is editing `core/` in parallel.
Every `[R]` citation above is to the version on disk at this session's read, whose mtimes
were `EXCESS_GAIN_MOMENTS_SYNTHESIS 12:07:31`, `CENTRAL_MOMENT_LADDER 12:02:25`,
`S7_RESCUE_PROBE 13:07:12`, `DEG4_ENERGY_SHARE_TRACE 13:49:43` — all earlier than the
read, so none of the four moved under this lane. `PHASE2_CONTRIBUTION_DRAFT` (14:11:20)
and `SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED` (14:13:50) are that workflow's writes;
this lane cites the latter only at second hand, through CENTRAL_MOMENT_LADDER §3.a.4.

Scratchpad (`…/7c1d8a18-611c-4493-9d65-0b4a9ad5fd33/scratchpad/bprime/`):
`phase_group.py` (phase-set group test, Hadamard properties), `allplus_fix.py` (all-plus
Walsh row localisation before and after the re-phase), `design_and_pricing.py` (MUB
verification of the re-phased design, exact defect ladder and the `2816/2881` ceiling,
measured legs, rung-2k `se` calibration, Student-`t` criticals),
`invariance_smoke.py` + `armB_copy/` (the mechanical check of §3), `seedcheck2.py` (the
seed-distinctness read). Re-run with
`C:/Users/strid/.venvs/whestbench-frozen-m178/Scripts/python.exe -B <script>` under
`PYTHONDONTWRITEBYTECODE=1` and the four single-thread environment variables.

*Symmetry gate, closed by derivation. 2026-08-19.*
