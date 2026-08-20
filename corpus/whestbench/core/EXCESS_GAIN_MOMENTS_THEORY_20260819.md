# EXCESS GAIN — THE MOMENT AND CUMULANT STRUCTURE (THEORY LANE)

**Date** 2026-08-19. **Lane** theory only; no arm per-network array was opened before the
signature block of §6 was written (§6 is a pre-registration and says so at its head).
**Custody** the arm reports are burned-Public100 DESCRIPTIVE data, licensed for science
reads and never for designation. Nothing here licenses a promotion, a validation, or a
designation move.

**Evidence tags.** `[O]` observed — a file read or a computation run this session.
`[D]` derived — follows from `[O]` items by algebra shown here. `[R]` reported — a corpus
document or channel entry says so and I did not re-derive it. `[A]` assumed — a default I
chose, named. `[G]` guessed — pattern match, labelled as such.

---

## 0. The verdict, before the derivation

**The excess gain is not a moment the forecast failed to model. It is an arm-A-only
mis-specification, and the second-moment account it sits inside is exactly correct in the
mean.** Three results carry this, in descending order of how much they change the picture.

1. **99.39% of the A→C gap is arm A's own miss.** The forecast predicts arm C's absolute
   MSE to `−0.15%` and arm B's to `+4.22%`, and misses arm A by `+28.46%`. In log units
   `ln(measured A→C / forecast A→C) = −0.251974`, of which arm C contributes `−0.001533`
   and arm A contributes `−0.250441` **[D, §2.4; from the four published aggregates]**.
   The finding "the design legs gain more than their defect shares allow" is more precisely
   "the Haar arm is 28% worse than any defect account of it predicts, and both structured
   arms are where they were predicted to be."

2. **The forecast's functional form `MSE = Σ_l E_l A_l` is a theorem, not a model.** For any
   fixed frame configuration and a Haar rotation, the cross-degree covariance is exactly
   zero by Schur's lemma, and the ensemble-mean MSE is exactly the energy-weighted defect
   sum (§1.4, §1.5). So item (2b) of the brief — "does the independence assumption bias the
   forecast?" — resolves to **no, in the mean, by exactly zero**. Cross-degree covariance
   moves the *variance* of the aggregate, never its expectation.

3. **Ensemble-tail deletion cannot explain the excess, and the F7 oracle magnitude is
   inapplicable rather than insufficient.** All three arms draw the *same* rotation seed
   (`int(mlp.seed)`, `predict()` in all three estimators **[O]**). Arm C performs no
   selection: `k = 1`. Deletion without selection is mean-preserving by construction
   (`E[F] = 1` for any lottery shape), so it moves a **ratio of means** by exactly `0`. The
   61.6% oracle-of-8 gain is what *selection over 8 tickets* buys; the required move is
   22.27% and even oracle-of-2 (34.69%) would cover it — **the magnitude is available and
   the mechanism is absent** (§3).

What is left as the live mechanism is item (2c), the **bias–variance interaction through
the fitted constants**: seven development-selected scalars — `λ = 0.9807112198896164`,
`pilot_base = 256`, `fold_pilot_base = 1024`, `dead_alpha = −2.0`, `on_alpha = 3.0`,
`phase_start/stop` — inherited from the Kerdock lineage and run unchanged on the Haar
carrier, where the pilot rows *are* frame rows and the regime classifier's detection power
is therefore a function of the carrier (§2.5). That channel is outside `Σ_l E_l A_l`
entirely, which is also what the completion leg's structural falsification demands (§2.3).

---

## 1. LAYER 1 — the exact decomposition of this estimator family

### 1.1 The estimator, stated so the algebra has something to attach to

**[O, `armA/estimator.py`, `armC/estimator.py`, `armB/estimator.py`, `orthogonal_fold3.py`,
`base_estimator.py`, `fold3_estimator.py`, all read this session.]**

The estimand is `μ_c = E_{x∼N(0,I_256)}[g_c(x)]`, the final-layer mean activation of output
channel `c` of a depth-32 ReLU MLP. The estimator is

```
    μ̂_c  =  (1/M) Σ_{i=1}^{M} g_c(r̄ u_i)  −  λ · T_c(δ)          M = 2 · n_base
```

with `{u_i} = {±ũ_j}` the antipodally doubled frame points, `r̄ = E‖X‖ = 15.98438266660852…`
the radial-conditioning radius (`radial_conditioning = True` **[O]**), `δ` the measured
first-layer moment and variance residuals, `T` the tangent (linearized forward) map, and
`λ = 0.9807112198896164` a frozen scalar. `n_base = 126·256` for arms A and C,
`129·256` for arm B; `M = 64,512` for A and C.

Three structural facts the decomposition turns on:

- **The estimator is deterministic given (network, configuration, rotation).** There is no
  Monte-Carlo sampling term at all. Conditional on those three things, the entire error is
  bias and the variance is exactly zero. Any "bias² + variance" split is therefore a
  statement about *which* randomization you average over, and the corpus's habit of calling
  `v126k` a "variance" already commits to one (§1.4).
- **All three arms apply the same per-network Haar rotation** `_haar_rotation(int(mlp.seed), width)`
  to the first-layer weights **[O, identical code in all three `predict()` methods]**. The
  rotation is a shared, paired factor; the configuration is the single manipulated variable.
- **Arm A draws its 126 Haar frames once**, in `setup()` from `ctx.seed`, and reuses that one
  draw across all 100 networks **[O, `orthogonal_fold3.py` lines 17–34]**. Arm A is one
  ensemble draw, not one hundred.

### 1.2 The quadrature error in harmonic coordinates

Expand `g_c(r̄ ·)` restricted to the sphere in real spherical harmonics
`{Y_{l,k}}`, normalized so `Σ_k Y_{l,k}(u)Y_{l,k}(v) = h_l P_l(⟨u,v⟩)` with `P_l` the
Gegenbauer polynomial normalized to `P_l(1) = 1` and `h_l = dim H_l(S^{255})`. Writing
`S_{l,k} = Σ_i Y_{l,k}(u_i)` and `S_l ∈ R^{h_l}`,

```
    Err_c  =  μ̂_c^{quad} − ∫ g_c dσ  =  Σ_{l≥1} ⟨f_{c,l}, S_l⟩ / M                (1)
```

The degree-0 term is integrated exactly (uniform weights on a full frame union), and **odd
`l` vanishes identically by antipodality**, since `{u_i}` is closed under `u ↦ −u` and
`P_l(−t) = −P_l(t)` for odd `l` — this is why `defect_mub`'s docstring restricts itself to
even `l` **[O]**.

### 1.3 The defect `A_l` is a squared norm — the "quadratic functional of projections"

For a homogeneous configuration,

```
    A_l  =  (1/M²) Σ_{i,j} P_l(⟨u_i, u_j⟩)  =  ‖S_l‖² / (M² h_l)   ≥ 0             (2)
```

so the quadrature defect **is** the squared length of the degree-`l` harmonic sum vector.
This is the object the brief calls a quadratic functional of projections onto a frame, and
(2) is what makes `A_l ≥ 0` structural rather than empirical. **[D]**

**The exact layer-1 table, reproduced bit-exact from the cell's own recurrence
[O, `runner_fc129.py` `gegenbauer`/`defect_mub`/`defect_random` re-executed this session in
exact `Fraction` arithmetic]:**

| `l` | `A_l` arm A (Haar-126) | `A_l` arm C (Kerdock-126) | `A_l` arm B (MUB-129) | `A_l^A/A_l^C` | `A_l^B/A_l^C` |
|---|---:|---:|---:|---:|---:|
| 2 | `0` | `0` | `0` | — | — |
| 4 | `3.136387499228e-05` | `7.350908201316e-07` | `0` (exact) | `128/3` | `0` |
| 6 | `3.099499781684e-05` | `3.194089008420e-05` | `3.122025216144e-05` | `4096/4221` | `2816/2881` |
| 8 | `3.100217149929e-05` | `3.097244080615e-05` | `3.025145454232e-05` | `9857662976/9848209601` | `413615274240/423473012843` |

`A_2 = 0` holds for **every** union of orthonormal frames, by Parseval: `2·P_2(1) +
2(d−1)·P_2(0) = 2 + 2(d−1)·(−1/(d−1)) = 0` **[D, one line]**. This is why the deg-2 channel
is exact for all three arms and why the entire design game lives at `l = 4` and `l = 6`.

**The high-degree tail is carrier-neutral, which eliminates truncation as a cause
[D, computed this session to `l = 24`]:** `P_l(1/16)` falls off geometrically
(`−3.09e−05`, `+9.53e−07`, `−3.00e−08`, `+1.04e−09`, …), so from `l = 12` upward the
Kerdock and Haar defects agree to six figures and `A_l^A/A_l^C = 1.000000`. Every omitted
degree therefore has ratio `1` on the A→C leg and `126/129` on B→C. **Including the omitted
tail would pull the forecast ratio *toward* 1 and widen the gap.** Truncation at `l = 8` is
not the error.

### 1.4 Theorem 1 — where the bias goes when the rotation is randomized

Under a Haar rotation `R` of the configuration, `S_l ↦ R_l S_l` where `R_l` is the image of
`R` in the degree-`l` irreducible representation of `SO(256)`. For `l ≥ 1` that
representation is nontrivial, so `E[R_l] = 0` and hence, from (1),

```
    E_R[Err_c] = 0     exactly, for every configuration and every network.           (3)
```

**Consequence, stated because it settles the brief's first question.** *Conditional on the
rotation, the error is 100% bias and 0% variance. Unconditionally on the rotation, the error
is 0% bias and 100% variance.* `A_l` is simultaneously a conditional-bias second moment and
an unconditional variance, and which name it takes is a choice of randomization, not a
property of the estimator. The runner names it a variance (`v126k`, "committed variance
shares" **[O]**) and this document follows that convention.

The one genuinely irreducible bias, present under *both* readings and invariant to every
frame choice, is the **radial-conditioning bias**: all points sit at `‖z‖ = r̄` exactly, so
the estimator targets `∫_S g(r̄u)dσ(u)` rather than `∫_S E_r[g(ru)]dσ(u)` **[O,
`radial_conditioning = True`]**. Call it `B²`. It is carrier-independent, and §2.4 shows it
cannot be the missing term because a common additive floor moves a ratio the *wrong way*.

### 1.5 Theorem 2 — cross-degree covariance is exactly zero (brief item 2b, answered)

For `l ≠ l'` the representations `R_l` and `R_{l'}` are inequivalent irreducibles of
`SO(256)`, so by Schur's lemma

```
    E_R[ (R_l S_l)(R_{l'} S_{l'})^T ] = 0        exactly.                            (4)
```

Therefore, taking (1) and squaring,

```
    E_R[Err_c²]  =  Σ_{l≥2 even} E_{c,l} · A_l ,      E_{c,l} = ‖f_{c,l}‖² / ‡      (5)
```

with **no cross-degree term at all**. Summing over output channels and networks gives
exactly the runner's `forecast(defects) = Σ_l energy[l]·float(defects[l])` **[O, line 333]**.

**The answer to brief item 2b is therefore: the degree channels do share frame vectors, and
that sharing biases the forecast of the mean by exactly zero, in either direction.** What
the sharing does move is the *second* moment of the realized aggregate: the cross term
`2⟨f_4,S_4⟩⟨f_6,S_6⟩` has zero mean but nonzero variance, so it inflates `se_log` without
touching the point estimate. That is a layer-3 effect and it is priced in §5.

Also settled by (5): the runner's use of `defect_random` — the *ensemble mean* `E[A_l]` for
Haar frames — is the correct object for the mean, not an approximation.

### 1.6 Theorem 3 — the realized Haar defect is deterministic for practical purposes

Within one antipodally doubled orthonormal frame the inner products are `±1` and `0`
regardless of orientation, so `‖S_l^{(f)}‖² = h_l W_l` with
`W_l = 4d(P_l(1) + (d−1)P_l(0))` is a **constant**: only the *direction* of `S_l^{(f)}` in
`R^{h_l}` is random. Write `S_l^{(f)} = ρ_l θ_f`, `ρ_l = √(h_l W_l)`, `‖θ_f‖ = 1`. The orbit
of a fixed vector under an irreducible orthogonal representation is isotropic in second
moment (Schur), so `E[θ_f] = 0` and `E[θ_fθ_f^T] = I/h_l`. With `m` independent frames,
`S_l = ρ_l Σ_f θ_f` and, from (2),

```
    E[A_l] = W_l m / M² = (P_l(1) + (d−1)P_l(0)) / (dm)      ← exactly defect_random
    Var(A_l)/E[A_l]²  =  2(m−1) / (m · h_l)                                          (6)
```

**[D, derived this session; validated numerically at four independent `(d, l, m)` points —
`(8,4,3)`, `(12,4,3)`, `(8,6,2)`, `(16,4,4)` — empirical/theoretical `CV²` ratios
`1.004 / 1.004 / 0.997 / 0.987` over 12,000–20,000 Haar replicates each, with the mean
matching the exact `defect_random` to `≤5e-4` in every case. `mc.py`, run this session
[O].]**

At `d = 256, m = 126`:

| `l` | `h_l` | `CV(A_l)` |
|---|---:|---:|
| 2 | `3.2895e+04` | `7.77e-03` |
| 4 | `1.8315e+08` | `1.04e-04` |
| 6 | `4.1417e+11` | `2.19e-06` |
| 8 | `5.0944e+14` | `6.24e-08` |

**The realized Haar defect fluctuates by one part in ten thousand at degree 4.** The
"conditioning lottery" therefore does *not* live in `A_l`. It lives one level down, in the
projection of `S_l` onto the network's own few effective directions — `A_l` averages
`‖S_l‖²` over all `1.8e8` harmonic directions, while a network's error samples a handful.
That is the correct home of the `vF = 0.3642` dispersion, and §4 places it there.

---

## 2. What the defect-share forecast structurally cannot see

### 2.1 The forecast, reproduced bit-exact

`v126k = 2.4977e-07`, `share4 = 0.004497`, `share8 = 0.86`, `share6 = 0.135503`;
`energy[l] = share_l · v126k / A_l^C`; `forecast(arm) = Σ_l energy[l]·A_l^{arm}`
**[O, `runner_fc129.py` lines 320–335]**. Re-executed this session:

```
  vA = 2.957745761410703e-07      A→C = 0.8444606810318669   (draft: identical)
  vB = 2.428829624941814e-07      A→B = 0.8211759295306633   (draft: identical)
  vC = 2.4977e-07 (identity)      C→B = 0.9724264823404788   (draft: identical)
```

**[O, absolute difference `0.0` on all six figures.]**

### 2.2 The degree-4 share the measurement demands

Since `forecast(A→C) = 1 / Σ_l s_l (A_l^A/A_l^C)`, the leg is a one-line inversion.
Holding the `(6,8)` split in its committed proportion:

| leg | implied `share4` | multiple of the committed `0.004497` |
|---|---:|---:|
| A→C (`0.656370`) | `0.012641` | **`2.81x`** |
| A→B (`0.666196`) | `0.010883` | **`2.42x`** |

**[D, bisection to 1e-90, this session.]** The two legs disagree by **14.94%** of their
mean, so *no single degree-4 share repairs both*: the `A→C`-implied share predicts
`A→B = 0.633050` against a measured `0.666196`.

**And the two legs cannot be fit jointly, because they are nearly collinear.** Eliminating
`s_8`, the `2×2` design matrix in `(s_6, s_4)` is

```
    A-leg:  [ −0.030573743565537,  +41.6657068 ]
    B-leg:  [ +0.000716705430560,   −0.9767217 ]      det = −1.6e-05,  cond = 8.7e+18
```

**[D]**. The two design legs carry **one** independent piece of spectral information, not
two: degrees 6 and 8 are not separable by this cell at any precision. Any "re-fit the
energy table" repair is therefore under-determined by construction, and the settling check
§11b names (the post-control per-degree energy table) has to come from an artifact read,
not from these three arms.

### 2.3 The completion leg refutes the model shape, for **every** nonnegative share vector

`max_l (A_l^B / A_l^C) = 2816/2881 = 0.9774383894481083` **[D, exact]**, attained at `l = 6`.
Since `forecast(C→B) = Σ_l s_l A_l^B / Σ_l s_l A_l^C` is a weighted average of the per-degree
ratios, it is bounded above by that maximum for any `s_l ≥ 0`. The measured `C→B` raw MSE
ratio is `1.0149700854688666` **[R, draft §13b; the anchor supplied in the brief]**.

```
    1.0149700854688666 / 0.9774383894481083 = 1.0384   →  the model is short by ≥ 3.84%
```

**This is a structural falsification and it does not depend on any energy estimate.** The
measured completion leg is unreachable by `Σ_l E_l A_l` with `E_l ≥ 0`. There is a term in
this estimator's MSE that is **not** an energy-weighted quadrature defect, it is at least
3.84% of arm C's MSE in size, and it grows going `126 → 129` on the same design family.
§2.5 names the candidate.

### 2.4 The gap is arm A's, and only arm A's

Against the four published aggregates **[R, draft §13b layer-one table: `3.799496813883252e-07`
/ `2.531207893952114e-07` / `2.493874381315209e-07`]**:

| arm | forecast | measured | measured/forecast |
|---|---:|---:|---:|
| A (Haar-126) | `2.957746e-07` | `3.799497e-07` | **`1.284592`  (+28.46%)** |
| B (MUB-129) | `2.428830e-07` | `2.531208e-07` | `1.042151`  (+4.22%) |
| C (Kerdock-126) | `2.497700e-07` | `2.493874e-07` | **`0.998468`  (−0.15%)** |

Decomposing each leg's log miss into the two arms' own misses **[D, exact identity]**:

```
  ln(meas A→C / fc A→C) = −0.251974  =  (−0.001533 from arm C)  +  (−0.250441 from arm A)
                                          0.61% of the gap          99.39% of the gap
  ln(meas A→B / fc A→B) = −0.209154  =  (+0.041287 from arm B)  +  (−0.250441 from arm A)
```

Two things follow that the leg-wise framing hid.

- **Arm C's forecast is an identity by construction and it also came true by measurement,
  to 0.15%.** The caveat that matters: `v126k` is a *committed* manuscript value, and I did
  not establish that it was sourced from a different run than the one arm C reproduces. If
  it was sourced from the same local pipeline the agreement is partly circular
  **[GAP, named; the settling check is `v126k`'s provenance record]**. The *attribution* of
  the leg gap to arm A is exact arithmetic either way and does not depend on this.
- **The runner's own external check validated the forecast against the wrong object.** It
  compared `vA = 2.9577e-07` to the committed public `random32,256` raw MSE
  `3.089512726e-07`, "an agreement of 4.3%" **[O, `predeclaration.json`]**. The measured
  arm A on *this* pipeline is `3.7995e-07`, i.e. **+22.98% above** that public number
  **[D]**. The check passed against a value that does not describe this cell's arm A.

**A carrier-independent floor is ruled out by sign.** If `MSE = B² + Σ_l E_l A_l` with `B²`
common (the radial bias of §1.4), the ratio is pulled *toward 1* — the forecast would be too
*optimistic* about the gain, not too pessimistic. Fitting `B² = measured_A − forecast_A =
8.4175e-08` and applying the same absolute floor to arm C over-predicts arm C by `+33.9%`
**[D]**. The missing term is **specific to the Haar arm**.

### 2.5 Brief item 2c — the bias–variance interaction, which is where the live mechanism is

The forecast's blind spot is not a moment. It is that **six of the estimator's constants are
fitted, and three of them read frame rows directly**, so the estimator's *own behaviour*
changes with the carrier in a way `A_l` cannot express.

- `pilot_base = 256` and `fold_pilot_base = 1024`: the cold/dead-neuron rescue and the
  terminal fold read `x[:pilot_n]` and `x[n_base : n_base + pilot_n]` — **the first frame's
  rows and their antipodes** **[O, `fold3_estimator.py` lines 102–103, 127, 149–150,
  182–183]**. For arm A that probe is one Haar orthonormal basis. For arms B and C it is a
  phased Hadamard: every coordinate of every probe direction has magnitude exactly
  `r̄/16`.
- The rescue test is `max(pilot_pre, axis=0) > 0` **[O, `base_estimator.py` line 160]** — a
  *detection* question, not an averaging one. A flat `±` probe attains `|⟨u,w⟩|` up to
  `(r̄/16)‖w‖₁`, against `≈(r̄/16)‖w‖₂` for a generic direction, and `‖w‖₁/‖w‖₂ ≈ 16` for a
  dense weight row in `R^256`. **The Hadamard pilot is a materially better firing detector
  than the Haar pilot at identical cost.** Neurons arm A misclassifies as dead are replaced
  by the analytic diagonal-Gaussian mean, which carries its own error and is invisible to
  every `A_l`. This has the right sign and the right arm. **[D for the mechanism and its
  sign; its magnitude is unmeasured — see §7.]**
- `dead_alpha = −2.0`, `on_alpha = 3.0`, `λ = 0.9807112198896164`: frozen thresholds
  calibrated on the Kerdock lineage and inherited **[R, `SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md`:
  "inherited and active"; and its own finding that `n_base = 126·256` is *forced* on
  `kerdock_v3` and *selected* on the Haar host]**. A control coefficient tuned for one
  configuration costs `Var(D)(λ − λ*)²` on another — quadratic in the mismatch, and a pure
  bias–variance interaction term.

**And a named candidate for the completion leg's reversal.** Arm B's frames are
`phases[0:128]` ∪ `{I}`, with the identity deliberately placed **last** so the pilot would
not read it **[O, `armB/estimator.py` docstring: "putting the coordinate basis there would
make the regime-classification pilot a deterministic, maximally structured probe"]**. But
`phases[0]` is the **all-plus** row — I verified this directly from the asset: `s=0` has
`sum = +256.0`, zero negatives, while every other row has exactly 120 negatives
**[O, `kerdock_phases.npz` unpacked this session]**. So arm B's frame 0 is the *unphased*
Sylvester Hadamard, and its 256-row pilot is the raw Walsh basis. Arm C's trim is
`phases[2:128]`, so arm C's pilot is `H·diag(φ₂)`, a pseudorandom sign pattern. **The
structured-probe hazard the docstring guarded against at index 128 re-entered at index 0.**
This is a concrete, carrier-dependent, non-quadrature difference between arms B and C — the
class of term §2.3 proved must exist — and it is checkable without a new production run.

---

## 3. The F7 oracle reconciliation, quantitatively

**First, a fact-check on the brief's figure.** The brief states "F7's measured oracle-of-8 =
50.3% MSE reduction". The committed corpus figure is **61.6%**:
`q1_oracle8_gain = 0.6160089092709584`, bootstrap CI95 `[0.4875960415272378,
0.6684345412032086]`, panel `oracle_mse = 1.3105e-07` against `single_mean_mse =
3.4128e-07` **[O, `pb1_premise_battery/p2_results.json`]**. Per-net oracle-of-8 gains are
`{101: 0.555551, 202: 0.688349, 303: 0.487681}`. A grep for `50.3` / `0.503` across the
whole `whestbench` tree returns nothing at this label **[O]**. The nearest committed values
are net 303's **oracle-of-16** at `0.501069` and the panel **oracle-of-4** at `0.519242`.
**I used 61.6% and its CI. If 50.3% came from a round-4 continuation note outside the
committed corpus, the conclusion below is unchanged, because it does not turn on the
magnitude.** Note also that `"F7"` is a continuation-queue label that "does not appear in
the committed corpus" **[R, `SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md`]**;
the ledger records are 204/245.

**The arithmetic of what the measurement would require.**

```
  A→C forecast 0.844461, measured 0.656370, excess 0.188091 ratio units  (18.81 points)
  required drop in arm C's mean, arm A held : 1 − 0.777265 = 22.27%
  required rise in arm A's mean, arm C held : 1.286563 − 1 = 28.66%
```

**[D.]** Against the same lottery pool's selection ladder — oracle-of-2 `34.69%`, of-4
`51.92%`, of-8 `61.60%`, of-16 `66.14%` **[O]** — **even a single binary choice would more
than cover the 22.27% needed.** The magnitude is not the problem.

**The mechanism is. Is deleting the Haar tail sufficient? No — it is inapplicable, and the
quantitative statement is that it contributes exactly zero.**

1. **All three arms use the same rotation.** `rotation = self._haar_rotation(int(mlp.seed),
   mlp.width)` appears verbatim in `armA/estimator.py`, `armB/estimator.py`,
   `armC/estimator.py` **[O]**. Arm C buys the same ticket as arm A. `k = 1`. Selection
   gain at `k = 1` is `0` by definition.
2. **Deletion without selection is mean-preserving.** The lottery factor satisfies `E[F] = 1`
   for *any* shape, so replacing arm C's lottery by a point mass at its own mean changes the
   **ratio of means** by exactly `0`. The runner measures a ratio of means and says so
   ("A ratio of means, never a mean of ratios" **[O, line 260]**).
3. **The only route by which shape alone can move a log ratio is the Jensen/median bias,
   and it is three orders of magnitude too small.** `E[ln M̂] − ln E[M] ≈ −CV²/(2n)`. With
   `n = 100` and `vF = 0.3642` for arm A:

   | arm-C CV | net bias on `ln(C/A)` | ratio moved by | needed |
   |---|---:|---:|---:|
   | `0.60` | `+0.000021` | `+0.002%` | `−22.27%` |
   | `0.40` | `+0.001021` | `+0.102%` | `−22.27%` |
   | `0.20` | `+0.001621` | `+0.162%` | `−22.27%` |
   | `0.00` (full deletion) | `+0.001821` | `+0.182%` | `−22.27%` |

   **[D.]** Note the sign as well as the size: complete tail deletion in arm C moves the
   ratio **up**, i.e. it *shrinks* the measured gain. Tail deletion is not merely
   insufficient; it is the wrong sign by a factor of 122.

4. **What tail deletion *does* move is the mean-versus-median statistic, by ~13%.** If arm C
   had no lottery and arm A's is `χ²_ν/ν` with `ν = 2/vF = 5.4915`, then
   `mean/median = 1.1319` **[D]**, so the aggregate (ratio-of-means) gain of `34.36%` would
   sit against a median-based gain of `25.70%` — an `8.66`-point spread. **That spread, not
   the aggregate, is the diagnostic the data lane should compute** (§6, signature S3).

**Conclusion for brief item 2a: deleting the Haar tail is not sufficient, is not necessary,
and is not what happened. The oracle-of-8 measures a selection gain that no arm in this cell
performs.**

---

## 4. LAYER 2 — the ensemble distribution, measured and placed

The lottery pool: 3 nets × 16 rotations of the plain-antipodal Kerdock forward, each net
mean-normalized and pooled **[O, `p2_results.json` `mse_per_rotation`; S1's construction,
`S1_VERDICT.md`]**. Recomputed this session:

```
  vF (ddof=0) = 0.364200          ← S1 records 0.3642, exact reproduction  [O]
  CV = 0.603489    skew = 1.6009    kurtosis = 5.2948    E|F−1|³ = 0.4607
  max/min = 11.0732    median = 0.918382    mean/median = 1.0889
  χ² dof matched to CV:  ν = 2/vF = 5.4915
     χ²_ν predicts skew √(8/ν) = 1.2198 (observed 1.6009) and excess kurtosis
     12/ν = 2.2317 (observed 2.0765) — the shape is χ²-like with a fatter third moment.
```

**The effective degrees of freedom are ~5.5**, which is the physically meaningful number: a
depth-32 composed error over 256 output channels, all driven by one shared frame draw,
behaves like a 5-to-6-dimensional chi-square, not like a 256-dimensional one. This is the
`‖P_{eff} S_l‖²` of §1.6 — the projection of a `1.8e8`-dimensional harmonic sum onto the
network's handful of effective directions.

**Two honest attacks on the corpus's 99.79% figure, recorded because they are mine to make.**

- **S1's rotation share is conditional on an assumed difficulty spread that was never
  measured.** S1 implemented the difficulty factor as log-uniform with `max/min = 1.1`
  "taken from the ledger as given, not re-measured" **[O, `S1_VERDICT.md` Limitation 4]**.
  Sensitivity **[D]**:

  | assumed difficulty `max/min` | `vD` | rotation share | implied total CV |
  |---|---:|---:|---:|
  | `1.1` (S1's) | `0.00076` | **`99.79%`** | `0.604` |
  | `1.4` | `0.00943` | `97.50%` | `0.614` |
  | `2.0` | `0.04004` | `90.44%` | `0.647` |
  | `3.0` | `0.10058` | `79.94%` | `0.708` |

  The pool's own support (`max/min = 11.07`) times `1.1` reaches `12.2x`, against S1's own
  recorded observation of a `15.53x` 80-net spread **[O, Limitation 1]** — so the true
  difficulty spread exceeds `1.1` and the share is below `99.79%`. It stays dominant across
  the whole plausible range, which is why the qualitative conclusion survives; the precise
  figure should not be quoted without its assumption.
- **The pool is a Kerdock-carrier measurement without the deployed fold, controls, or
  pilots.** Using it as arm A's lottery is a transfer **[A, named]**. §5 shows the transfer
  is off by about 20% in the direction that matters and derives the deployed-arm CV
  independently.

**The shared rotation buys almost no cross-arm cancellation, and this is derivable.** For a
common Haar `R` and two configurations,
`Cov(⟨f, R S_l^A⟩, ⟨f, R S_l^C⟩) = ‖f‖² ⟨S_l^A, S_l^C⟩ / h_l`, so the induced correlation is
exactly the cosine between the two configurations' harmonic-sum vectors in `R^{h_l}`. For
two unrelated configurations that cosine is `O(1/√h_l) ≈ 7e-05` at `l = 4` **[D]**. **The
pairing that the shared seed appears to buy is, at the quadrature level, worth nothing.**
What genuine cross-arm correlation exists comes from the shared network (common `E_{c,l}`),
not from the shared rotation.

Inverting the achieved `se_log` under that model gives the deployed per-arm dispersion:
`se_log ≈ CV·√(2(1−ρ))/√n` with `n = 100` and `se_log = 0.073272` (A→C) / `0.073892` (A→B)
**[R, draft]** gives `CV ≈ 0.518` at `ρ = 0`, rising to `≈0.61` at `ρ ≈ 0.28` **[D]**. A
direct simulation with two independent `CV = 0.603` lotteries returns a median bootstrap
`se_log` of `0.0849` at `n = 100`, against the achieved `0.0705` **[O, `l3.py`]** — the
pool over-states the deployed dispersion by about 20%, which is what a working tangent
control is supposed to do.

---

## 5. LAYER 3 — why the same tail breaks the instruments

### 5.1 `1/√n` does not fail; the plug-in `σ̂` does, and the validity threshold is `n ≫ κ`

`se(mean) = σ/√n` is exact for iid draws at any tail weight. What carries a fourth-moment
correction is the **estimate** of `σ`. With `κ = E[(F−μ)⁴]/σ⁴` the standardized fourth
moment, `Var(s²) = σ⁴(κ−1)/n`, and by the delta method on `s = σ√(1+u)`:

```
    E[s]/σ − 1  ≈  −(κ − 1)/(8n)        (the correction term the brief asks for)
    sd(s)/σ     ≈  ½ √((κ − 1)/n)
    valid only while (κ−1)/n ≪ 1, i.e.  n ≫ κ  —  NOT n ≫ 30.                       (7)
```

**[D.]** Evaluated:

| `κ` | `n` | rel. bias of `ŝe` | rel. sd of `ŝe` |
|---:|---:|---:|---:|
| `5.29` (pool) | `5` | `−0.107` | `0.463` |
| `5.29` | `100` | `−0.005` | `0.104` |
| `50` | `100` | `−0.061` | `0.350` |
| `2e4` | `5` | `−500` | `31.6` |
| `2e4` | `100` | `−25.0` | `7.07` |

**The recorded `kurtosis of order 2e4` note is exactly this regime.** Its home in the corpus
is the `deg6_own_axis_zonal_capture_v1` predeclaration, describing the judge's smoke reading
its zonal instruments "noise-dominated (ratio 0.758, feature norm 0.734) — consistent with
the documented heavy-tail (kurtosis of order 2e4) at toy sample counts, resolving at
production scale" **[O, `cells/deg6_own_axis_zonal_capture_v1/predeclaration.json`]**. It is
a statement about a *different* channel (zonal features), so it is not the MSE channel's
`κ`. It is quoted here because (7) explains precisely why it resolves at production scale
and not before: at `κ = 2e4` the plug-in `σ̂` is meaningless below `n ∼ 2e4`, and the
"resolving at production scale" claim is a claim that the production `κ` is far smaller.

**Inverting the production channel's own `κ` from the judge's record.** The judge records "a
symmetric bootstrap SE bias of 6.2%" at `n = 100` **[R, channel `2026-08-19T09:53:09Z`]**.
Identifying that with (7): `(κ−1)/800 = 0.062 → κ ≈ 50.6` — about **9.6x the P2 rotation
pool's `5.29`** **[D, under the stated identification, which I did not verify against the
judge's definition; if the 6.2% is a CI-method difference rather than a plug-in SE bias this
inversion does not hold]**. A production `κ ≈ 50` is independently consistent with the m185
80-net spread of `15.53x` exceeding what the pool (`11.07x`) can generate.

### 5.2 The `3.7x` blowout, and the diagnosis the corpus has not written down

The pre-registration's arithmetic was right and its premise was wrong **[R, draft §10b]**:
`0.0843 / √20 = 0.018850053050323227` against an achieved `0.07054498655771349`, an
overshoot of `3.7129x` on the projection and `2.3515x` on the window ceiling **[R]**.

Simulating the same projection under the calibrated lottery **[O, `l3.py`, 4,000 replicates
at `n = 5`, 1,500 at `n = 100`]**:

```
  median bootstrap se_log at n = 5   : 0.28774        (the smoke measured 0.0843)
  its 1/√20 projection                : 0.06434        (the spec projected 0.018850)
  median bootstrap se_log at n = 100 : 0.08466        (achieved 0.070545)
  P( projection ≤ 0.018850 )          : 0.012
  quantiles of se_log(n=5): 5% 0.1263  |  50% 0.2877  |  95% 0.4995
```

**The projection method loses only `1.32x` on a median draw. The remaining `2.8x` is that
the smoke's five networks were an unusually tight sample — `0.0843` sits below the 5th
percentile of what the calibrated lottery produces at `n = 5`.** So the honest diagnosis is
**not** "`1/√n` fails under heavy tails" (it does not) but: *a five-network `σ̂` on a channel
with `κ ≳ 50` has a relative sd of `0.46–1.0` by (7), so it is not an estimate of anything,
and this particular one was a `~1%` low draw.*

**That the same five networks also produced a sign-flipped point estimate is the part that
should not be absorbed.** The smoke returned raw MSE ratio `1.0387` — arm B worse — against
production's `0.6662`, a gap of `5.27` smoke-SE **[R, draft]**. Two coincidences in one
five-network sample (a `~1%`-low dispersion draw *and* a `5.3`-SE point draw) is worse
evidence for bad luck than for a systematic difference between the smoke's subset at
harness seed `424242` and production's at seed `0`. The draft files this as unexplained;
this document adds that the *dispersion* anomaly and the *location* anomaly are two
anomalies, not one, and that their joint probability under the calibrated lottery is of
order `1e-4`.

### 5.3 Left-skew of the log ratio — the effect is real but cancels between like arms

Second-order delta method on `M̂ = μ(1+U)`, `L = ln M̂ = ln μ + U − U²/2 + …`, using
`E[U²] = CV²/n`, `E[U³] = γCV³/n²`, `E[U⁴] ≈ 3(CV²/n)²`:

```
    skew(ln M̂)  ≈  (γ − 3·CV) / √n                                                   (8)
```

**[D.]** For any `χ²_ν` shape, `γ = 2·CV` exactly, so (8) reduces to `−CV/√n` — **the log of
a mean of heavy-tailed positives is left-skewed**, magnitude `CV/√n`. With the pool's
`γ = 1.601, CV = 0.603, n = 100`: `skew(ln M̂) = −0.021`.

**But the estimand is a log *ratio* of two arms, and for like-shaped arms the skew cancels
to this order:** `skew(ln(Ĉ/Â)) = (s_C σ_C³ − s_A σ_A³)/(σ_C² + σ_A²)^{3/2}`, which is `0`
when the two arms share a shape. Simulation returns `−0.0502` at `n = 100`, against a
Monte-Carlo standard error on skewness of `√(6/1500) = 0.063` **[O]** — consistent with
zero. **The left-skew of the ratio therefore exists only to the extent the two arms differ
in shape, and its sign is positive (right-skewed) when arm A is the heavier one.** That
makes it a signature rather than a nuisance (§6, S5).

### 5.4 What the `3.44 SE` is actually worth

```
  gap = ln(0.8444606810318669 / 0.6563696466865464) = 0.251974 log units
  achieved se_log(A→C) = 0.073272   →   3.439 SE
  Gaussian two-sided p                     : 5.84e-04
  simulated p under the calibrated lottery : 4.7e-03   (≈ 8x larger)
  Berry–Esseen bound |F_n − Φ| ≤ 0.4690·E|F−1|³/(CV³√n) : 0.4396 at n=5, 0.0983 at n=100
```

**[D and O.]** Three readings, all of which are needed:

- The heavy tail inflates the tail probability by about `8x`. It does not rescue the
  forecast: `p ≈ 5e-03` still rejects.
- The Berry–Esseen bound at `n = 100` is `0.098`, larger than the nominal `p` by two orders
  of magnitude. **A normal tail probability at `3.44` SE on this channel is not a number
  anyone should quote**, in either direction. The corpus's own `2.83 SE` and `3.44 SE`
  figures are correct as *distances* and should be read as distances, not as `p`-values.
- For the gap to be a one-SE event the true `se_log` would have to be `0.2520`, a `3.44x`
  understatement. The simulated 95% range of the `n = 100` bootstrap `se_log` is
  `[0.0717, 0.0960]` **[O]** — it does not reach a third of that. **Sampling fluctuation is
  ruled out as the sole explanation at any reasonable tail weight.**

---

## 6. PREDICTED SIGNATURES FOR THE DATA LANE

**Pre-registration.** Written before any arm's per-network array was opened. The three
`report_arm*.json` files were never read in this session; the only arm quantities used
anywhere above are the four aggregates already printed in `PHASE2_CONTRIBUTION_DRAFT_20260819.md`
§13b and supplied in the brief. Verifiable by the absence of those paths from this session's
reads.

The brief names four signatures for the "ensemble-tail deletion" hypothesis. **Three of the
four are non-diagnostic and one has its sign backwards**, and the corrected versions are
below with magnitudes.

### S1 — rank correlation of per-net gain with arm-A per-net MSE
**Brief's prediction: positive. Mine: positive, but that is the NULL, not the signature.**

Under a no-mechanism model (`MSE_A = D·μ_A·F_A`, `MSE_C = D·μ_C·F_C`, `F` independent across
arms with `sd(ln F) = 0.5527` from the pool, `D` the shared network difficulty):

```
    corr( ln(MSE_C/MSE_A), ln MSE_A ) = −σ_F / (√2 · √(σ_D² + σ_F²))
      σ_D = 0    →  −0.707     ⇒  corr(gain, MSE_A) = +0.707
      σ_D = 0.2  →  −0.664     ⇒                      +0.664
      σ_D = 0.4  →  −0.571     ⇒                      +0.571
```

**[D.]** **Predicted Spearman `ρ(gain, MSE_A) ≈ +0.57 to +0.71`, with `+0.65 ± 0.08` as the
point prediction.** This is pure regression to the mean and would appear with no tail
deletion whatsoever. **The observation only becomes informative if it exceeds `+0.75`**,
which is what a genuinely lighter-tailed arm C would add. A value in `[0.55, 0.72]`
**confirms nothing**; a value below `+0.45` would mean the arms are far more correlated than
§4 predicts and would falsify the near-orthogonality argument of §4.

### S2 — mean gain vs median gain
**Brief's prediction: mean > median. Mine: it depends entirely on which "mean", and under
the most natural reading the brief's sign is backwards.**

- **Mean of per-net ratios vs median of per-net ratios:** `E[F_C/F_A] = E[1/F_A] =
  ν/(ν−2) = 1.5728` at `ν = 5.49`, so mean-of-ratios gain `= 1 − 0.6564·1.5728 = −0.032`
  against a median-of-ratios gain of `+0.344`. **Mean gain is NEGATIVE and far BELOW median
  gain — a `37`-point inversion.** Per-net gain is bounded above by 1 and unbounded below,
  so it is strongly left-skewed. **[D.]** This is exactly why the runner takes a ratio of
  means, and any data-lane table reporting "mean per-net gain" will look catastrophic for
  reasons that are pure Jensen.
- **Aggregate (ratio of means) vs median of per-net ratios:** *this* is the diagnostic
  version. Predicted **aggregate `34.36%` vs median-based `25.70%`, a spread of `8.66`
  points**, if arm C's lottery is fully deleted; **`0` points** if the two arms have the same
  shape. **[D.]** Expect something in `[0, 9]` points; the *measured* value of this spread
  is a direct read-off of how much lighter arm C's tail is. My point prediction, given §4's
  finding that both arms carry a rotation lottery of similar size: **`2 ± 3` points, i.e.
  closer to the no-deletion end.**

### S3 — top-decile arm-A share of the aggregate gain
**Predicted: disproportionate, and again mostly for a null reason.** Under a `χ²_5.49`
lottery, the top decile of arm-A per-net MSE carries roughly `28–32%` of `Σ MSE_A` **[D,
from the fitted `ν`; not simulated]**, against `10%` under a point mass. Since the aggregate
gain is `Σ MSE_A − Σ MSE_C`, an arm-A-heavy top decile mechanically dominates it.
**Predicted top-decile share of the aggregate gain: `30–40%`.** The diagnostic quantity is
the *difference* between arm A's and arm C's top-decile shares, not arm A's alone.
**Predicted difference: `≤ 5` points**, because §4 says both arms carry a comparable lottery.
A difference above `10` points would be genuine evidence for tail deletion and would be the
first thing in this whole analysis to support that hypothesis.

### S4 — skewness and kurtosis of the two arms' per-net MSE distributions
**Brief's prediction: arm A materially higher. Mine: barely different, and this is the
sharpest test in the set.**

§1.6 proved the realized *defect* fluctuates by `1e-04` at degree 4, and §4 proved the
shared rotation induces essentially zero cross-arm correlation but also no shape difference:
both arms' per-net MSE is a projection of a rotated harmonic sum onto the network's few
effective directions, and the *shape* of that projection is `χ²`-like with the same `ν` for
both. **Predicted: `skew_A / skew_C ∈ [0.9, 1.3]` and `kurt_A / kurt_C ∈ [0.9, 1.4]`,
with both arms near `skew ≈ 1.6`, `κ ≈ 50` (§5.1's inversion).** If the measured
`kurt_A / kurt_C` exceeds `2`, my whole §3 conclusion is wrong and tail deletion is back on
the table; that is the single observation that would overturn this document.

### S5 — skew of the bootstrap log-ratio distribution
**New, from §5.3, and it carries a sign.** `skew(ln(Ĉ/Â))` is `0` for like-shaped arms and
**positive** when arm A is the heavier one. **Predicted: `+0.00 ± 0.07` at `n = 100`.** A
value above `+0.15` indicates a real shape asymmetry in arm A's favour and is the cleanest
tail-deletion evidence available from data already in hand — it needs no new run, only the
20,000 bootstrap draws the cell already computed.

### S6 — the arm-level attribution (the one that matters most)
**Predicted, and already established in §2.4 from published aggregates, so this is a
consistency check rather than a forecast:** the per-network forecast residual
`MSE_m − Σ_l E_l A_l` will be **near zero for arms B and C and systematically positive for
arm A on most networks** — a location shift, not a tail. **Predicted: arm A's per-net ratio
`MSE_{A,m}/forecast_A` has median in `[1.15, 1.35]` and a positive residual on `> 70%` of
networks.** If instead the `+28.46%` is carried by fewer than 15 networks, the mechanism is
a tail after all and §2.5's pilot argument is wrong.

### S7 — the pilot mechanism, directly
**Predicted from §2.5, checkable without any statistics:** arm A classifies **more** neurons
as dead-and-unrescued than arms B and C on the same networks, because its pilot is a Haar
basis and theirs is a flat `±` Hadamard. **Predicted direction: strict. Predicted magnitude:
unknown** — I have derived the sign and the `‖w‖₁/‖w‖₂ ≈ 16` lever but not the count. If the
dead-neuron counts are equal across arms, §2.5's leading candidate is dead and the live
mechanism reverts to the `λ`/threshold mis-tuning channel alone.

---

## 7. Attack on this document's own conclusions

**The strongest way this is wrong.** §2.4's attribution rests on comparing measured
aggregates to a forecast whose arm-C leg is an identity by construction. If `v126k` was
itself fitted to a run of this same local pipeline, then "arm C matches to 0.15%" is
circular and the correct reading is that *all three* arms are mis-forecast and only arm C's
error was absorbed into the constant. **The attribution of `99.39%` of the leg gap to arm A
survives regardless** — it is exact arithmetic on `ln(m/f)` differences — but the claim
"the model is right about the structured arms" does not. **Settling check: the provenance
record for `v126k = 2.4977e-07`. Cost: one artifact read.**

**Second strongest.** §2.5's pilot mechanism has a derived sign and no measured magnitude. I
verified that the pilot reads frame rows **[O, code]**, that arm B's frame 0 is the unphased
Hadamard **[O, asset]**, and that flat `±` probes have a `‖w‖₁/‖w‖₂` advantage **[D]**. I did
**not** verify that any neuron's classification actually differs between arms. It is a
hypothesis with a named check (S7), not a finding.

**Where the attack already landed and changed the answer.** I began with the brief's frame —
ensemble-tail deletion, with the F7 oracle as its magnitude — and tried to price it. The
pricing killed it: `E[F] = 1` makes deletion mean-preserving, the shared `mlp.seed` makes
`k = 1`, and the Jensen route is `122x` too small and points the other way. That is why §3
reads as a refutation rather than a quantification, and why §6 rewrites three of the four
requested signatures as nulls. The parts of the brief's framing that survived intact are the
instrument analysis (§5, where the heavy tail genuinely is the mechanism) and the owner's
own sentence — the excess does live in "the other elements and the inference between them",
just not in the elements the tail-deletion story nominated.

**What I did not look at.** No `report_arm*.json` per-network array (by design, §6). No
`spec.json` beyond the runner. No hosted-vs-local transfer question. No re-derivation of the
`E6/E4 < 19.71` carrier-optimality condition or the Delsarte floor; both are `[R]` here and
neither is load-bearing for anything above.

---

## 8. Evidence ledger

| # | claim | level | signal 1 | signal 2 |
|---|---|---|---|---|
| 1 | exact defect table and the three forecast ratios | `[O]` | `Fraction` re-derivation this session, abs diff `0.0` on all six | matches `PHASE2_CONTRIBUTION_DRAFT` §11b/§13b table |
| 2 | `A_2 = 0` for every orthonormal-frame union | `[D]` | one-line Parseval identity | `k32_base_sensitivity_v3` `base1.A2 = 0.0` `[R]` |
| 3 | `E_R[Err] = 0`; cross-degree covariance exactly `0` | `[D]` | Schur on inequivalent `SO(256)` irreps | reproduces `defect_random` and the runner's summation form exactly |
| 4 | `Var(A_l)/E[A_l]² = 2(m−1)/(m h_l)` | `[D]` | harmonic-orbit derivation | Haar Monte Carlo at 4 `(d,l,m)` points, ratios `0.987–1.004` `[O]` |
| 5 | high-degree tail is carrier-neutral | `[D]` | exact `A_l` to `l = 24`, ratio `1.000000` from `l = 12` | `P_l(1/16)` geometric decay, same computation |
| 6 | no nonneg shares reach the measured `C→B` | `[D]` | `max_l A_l^B/A_l^C = 2816/2881` exact | measured `1.01497` `[R]`, short by `3.84%` |
| 7 | `99.39%` of the A→C gap is arm A's miss | `[D]` | exact log decomposition of published aggregates | independent check: a common floor over-predicts arm C by `+33.9%` |
| 8 | implied `share4` = `2.81x` / `2.42x`, legs disagree, system near-singular | `[D]` | bisection | `det = −1.6e-05`, `cond = 8.7e+18` |
| 9 | pool `vF = 0.364200`, `ν = 5.49`, `κ = 5.29` | `[O]` | recomputed from `p2_results.json` | exactly reproduces S1's recorded `0.3642` at `ddof=0` |
| 10 | oracle-of-8 = `61.6%`, CI `[48.76%, 66.84%]`; no `50.3%` in corpus | `[O]` | `p2_results.json` | tree-wide grep for `50.3`/`0.503` returns nothing at this label |
| 11 | all three arms share `int(mlp.seed)`; `k = 1` | `[O]` | identical `predict()` in three estimator files | arm A's frames drawn once in `setup()` from `ctx.seed` |
| 12 | tail deletion moves a ratio of means by `0`; Jensen route `122x` too small, wrong sign | `[D]` | `E[F] = 1` identity | `−CV²/(2n)` table, `+0.182%` max against `−22.27%` needed |
| 13 | `E[s]/σ − 1 ≈ −(κ−1)/(8n)`; validity `n ≫ κ` | `[D]` | delta method on `Var(s²) = σ⁴(κ−1)/n` | inverts the judge's `6.2%` to `κ ≈ 50.6`, consistent with the `15.53x` 80-net spread |
| 14 | the `3.7x` blowout is `1.32x` method + `2.8x` an unlucky 5-net draw | `[D]` | simulation: median projection `0.0643` vs truth `0.0847` | `P(projection ≤ 0.018850) = 0.012`; smoke below the 5th percentile |
| 15 | `skew(ln M̂) ≈ (γ − 3CV)/√n`, cancels between like arms | `[D]` | delta-method expansion | simulated ratio skew `−0.050 ± 0.063` at `n = 100` |
| 16 | `p ≈ 5e-03` not `6e-04`; Berry–Esseen `0.098` at `n = 100` | `[D]` | simulation under the calibrated lottery | closed-form BE bound from the pool's `E|F−1|³` |
| 17 | arm B's frame 0 is the unphased Hadamard | `[O]` | `kerdock_phases.npz`: `s=0` sum `+256.0`, `0` negatives, all others `120` | arm C's trim is `phases[2:128]`, so its pilot is `H·diag(φ₂)` |
| 18 | the pilot reads frame rows; the rescue test is a max | `[O]` | `fold3_estimator.py` lines 102–103/127/149–150/182–183 | `base_estimator.py` line 160, `max(pilot_pre) > 0` |
| 19 | shared rotation buys ~no cross-arm cancellation | `[D]` | `Cov ∝ cos(S^A_l, S^C_l) = O(1/√h_l) ≈ 7e-05` | achieved `se_log 0.0733` requires `ρ ≈ 0.28`, not `ρ ≈ 1` |
| 20 | S1's `99.79%` is conditional on an unmeasured `1.1x` difficulty spread | `[O]` | `S1_VERDICT.md` Limitations 1 and 4 | sensitivity table: `79.9%–99.8%` across `1.1x–3.0x` `[D]` |

**Open items with named checks.** (i) `v126k` provenance — one artifact read, settles the
circularity in §2.4. (ii) Per-arm dead-neuron counts — settles S7 and §2.5. (iii) The
post-control per-degree energy table — the check §11b already named, and the only route to
a defensible `share4`; note §2.2's near-singularity means the three arms cannot supply it.
(iv) The judge's definition of the `6.2%` bootstrap SE bias — settles the `κ ≈ 50.6`
inversion in §5.1. (v) The brief's `50.3%` oracle figure — locate or retire it.
