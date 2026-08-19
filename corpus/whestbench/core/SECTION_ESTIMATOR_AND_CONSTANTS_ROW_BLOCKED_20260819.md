# Drop-in manuscript section §1 (row_blocked host): the estimator, and exactly what is fitted

**Status:** draft section written 2026-08-19 by opus-5 for merge B9. Rules v12 §6
criterion (iii) artifact. Not yet inserted.

**Read this before anything else.** The committed section
`SECTION_ESTIMATOR_AND_CONSTANTS_20260812.md` **describes the `kerdock_v3` MRO and
does not apply to this host.** Its enumeration is drawn from
`experiments/v31_guards/package_source/` (`estimator.py` → `kerdock_v3_estimator.py`
→ `fold3_estimator.py` → `base_estimator.py`), a different source tree with a
different carrier, a different backend block height, and two constants that do not
exist here at all. Every number in that document that is cited about the deployed
`row_blocked` entry is cited about the wrong host. This document replaces it for the
`row_blocked_production` lineage. Neither supersedes the other; they describe two
promoted lineages and both must stand.

**Why this section is the one that matters.** Rules v12 §6 criterion (iii) is "the
ease of determining the actual performance impact of the contribution from the code
and writeup together." That is answered here or nowhere. The `kerdock_v3` section
carries a disclosure that a false fitted-structure claim shipped twice on that
lineage; on this lineage the failure mode was different and is disclosed below —
a correct-looking disclosure describing a source tree the deployed entry never
loads.

**Every value below was read from the deployed method-resolution order** in
`experiments/row_blocked_production/candidate_source/`, read-only, no import and no
bytecode, and is re-derived mechanically by `core/verify_row_blocked_disclosure.py`.

**Notation.** Sample counts are written in the factored form the source itself uses
(`126 * 256`, and its antipodal double) rather than as bare products. The kill-record
numeric scan forbids those bare products in `id` / `hypothesis` / `causal_mechanism`
fields; nothing in this document is a kill record, and the factored form is what the
code says in any case.

**Evidence tags.** `[O]` observed — read from source or computed this session.
`[D]` derived — follows from an observation by steps shown here. `[R]` reported — a
committed artifact says so. `[A]` assumed — a default chosen and labelled.

---

## SECTION — The estimator, and exactly which of its numbers were chosen

### The carrier, stated truthfully

The estimator integrates over **126 independent Haar-orthonormal frames of 256
directions each**, drawn per network from `ctx.seed` by QR of an i.i.d. Gaussian
matrix and scaled to the exact chi-mean radius, then closed antipodally inside
`predict`. `orthogonal_fold3.Estimator.setup` is nine lines of source and contains
the whole carrier [O]:

```python
rng = fnp.random.default_rng(ctx.seed)
raw = rng.standard_normal((n_frames, ctx.width, ctx.width), dtype=fnp.float32)
q, _r = fnp.linalg.qr(raw)
self._gaussian = (q.reshape((self.n_base, ctx.width)) * mean_radius).astype(fnp.float32)
```

Four consequences, each of which contradicts the committed `kerdock_v3` section if
that section is read as describing this host:

1. **There is no phased-Hadamard structure and no frozen design.** The tokens
   `kerdock`, `hadamard`, `phased`, `MUB`, `phase_start` and `phase_stop` do not
   occur anywhere in this source tree [O]. `phase_start = 2` and `phase_stop = 128`
   are `kerdock_v3` constants; on this host they do not exist, so they are neither
   fitted nor forced — they are absent.
2. **The frames are not frozen; they are redrawn per network.** The randomization is
   not "a per-network Haar rotation of a fixed design"; it is the entire direction
   set, resampled from `ctx.seed` at every `setup` [O].
3. **Degree-2 (and degree-3) exactness is forced by construction, not designed.**
   For an orthonormal basis `{e_i}` scaled to a fixed radius, `Σ_i (e_i·u)² = |u|²`
   is constant in `u`, so every degree-2 spherical harmonic averages to zero on each
   frame; antipodal closure kills every odd degree. Degree 4 is *not* killed —
   `Σ_i (e_i·u)⁴` depends on `u` — so this host carries the full i.i.d. degree-4
   design error [D], which is what makes the 129-completion cell valuable here and
   near-worthless on `kerdock_v3` [R, `KILL_CONTEXT_INDEX_20260819.md`]. This matches
   the ledger's own correction at IDX 68: "126 independent Haar frames with degree 2
   exactness, not a Kerdock MUB" [R].
4. **The QR sign convention does not matter here, and that needs saying rather than
   assuming.** Householder QR of a Gaussian matrix returns `Q = H·D` with `H` Haar
   and `D` a diagonal of signs; the code does not apply the usual sign correction
   [O], so `Q` alone is not exactly Haar-distributed [R]. The estimator is invariant
   under `D`: `predict` forms `x = concat(relu(+z W), relu(−z W))` and then averages
   over all rows, so flipping the sign of any direction permutes the sample set and
   leaves every output unchanged [D]. The deployed estimator is therefore a function
   only of the sign-quotient of `Q`, on which the induced law is exactly Haar [D].
   "Haar frames" is an accurate description of the carrier for every quantity this
   code computes.

The radius is **computed, never stored**: `mean_radius = exp(½ log 2 + lgamma((w+1)/2)
− lgamma(w/2))` [O]. At `w = 256` the exact value is `15.9843826666085274777751974…`
(computed here at 70-digit precision from `√(2π)·256!/(2²⁵⁶·128!·127!)`) [O]; the
deployed float64 `lgamma` evaluation of the same closed form returns
`15.984382666607859`, low by `4.18e-14` relative [O]. That gap is arithmetic, not a
choice, and no constant in the source encodes either digit string.

### The deployed method-resolution order

`estimator.Estimator` → `orthogonal_fold3.Estimator` → `fold3_estimator.Estimator`
→ `base_estimator.Estimator` → `whestbench.BaseEstimator` [O].

Two overrides in that chain are load-bearing for this disclosure and are easy to get
wrong by reading a single class:

- `estimator.Estimator.setup` calls `super().setup(ctx)`, which lands in
  `orthogonal_fold3.Estimator.setup`, **which does not call `super().setup`** [O].
  `base_estimator.Estimator.setup` therefore never runs on this host. The Sobol
  asset, the Owen `2**32` scramble and the Box–Muller pair map in that method are
  dead code on the deployed path, notwithstanding the `base_estimator` docstring
  "Randomized Sobol-antipodal pilot rescue" [O]. The docstring is stale; the class it
  documents is only reached for its class attributes and its two module-level
  helpers.
- `fold3_estimator.Estimator.predict` fully overrides `base_estimator.Estimator.predict`
  [O]. Nothing in the base `predict` executes.

### What is forced, with nothing tunable in it

The exact radial identity (a bias-free ReLU network is positively one-homogeneous,
so `E[f(X)] = E‖X‖ · E[f(U)]` holds exactly at every layer; the radial degree of
freedom is removed, not reduced); the chi-mean radius above; orthonormality and
antipodal closure of each frame, and with them the degree-2 and degree-3 exactness;
the seven Strassen leaf products and the eight input / seven output adds in the
Winograd core, which are the algorithm's arithmetic and not a setting [O].

### What was selected during development, and is therefore fitted in the sense an auditor cares about. There are six scalars, one switch, and one structural integer

| constant | value, exactly as written in source | defined in | role |
|---|---|---|---|
| `n_base` | `126 * 256` | `estimator.py` | frame count × width; the base direction count, antipodally doubled in `predict` |
| `pilot_base` | `256` | `orthogonal_fold3.py` | pilot antipodal pairs for the deep-layer cold-neuron rescue |
| `fold_pilot_base` | `1_024` | `orthogonal_fold3.py` | pilot antipodal pairs for the terminal fold |
| `dead_alpha` | `-2.0` | `base_estimator.py` | cold/dead threshold on the analytic α |
| `on_alpha` | `3.0` | `fold3_estimator.py` | always-on threshold in the fold |
| `moment_tangent_lambda` | `0.9807112198896164` | `base_estimator.py` | first-layer moment-tangent control coefficient |

| non-scalar selection | value | defined in | role |
|---|---|---|---|
| `radial_conditioning` | `True` | `orthogonal_fold3.py` | switch; overrides `False` in `base_estimator.py`. Setting it `True` is what makes the radial-reweight branch unreachable (below) |
| fold arity | `3` | `fold3_estimator.py`, in control flow | the terminal fold spans `depth-3`, `depth-2`, `depth-1`; the deep loop runs `range(1, depth - 3)`. Not a named attribute, and the only reason this is a three-layer fold rather than a two- or four-layer one |

All eight were frozen before grading [A — I did not re-check freeze timestamps this
session; the settling check is the ledger's freeze record for IDX 53].

**`n_base` is fitted on this host, and is not fitted on `kerdock_v3`.** This is the
correction that most matters, and it is why the count is six rather than the five the
merge brief expected. On `kerdock_v3`, `126 * 256` is the size of the frozen design —
forced, a fact about the object, not a budget anyone picked. On this host there is no
design: QR produces as many orthonormal frames as you ask it for, and 126 is a number
someone chose [D]. The same literal is forced on one lineage and selected on the
other, which is precisely the kind of claim that does not survive being copied
between hosts.

The other five match the merge brief exactly, and the source agrees with the brief on
every value: `pilot_base 256`, `fold_pilot_base 1_024`, `dead_alpha -2.0`,
`on_alpha 3.0`, `moment_tangent_lambda 0.9807112198896164` [O].

### Shadowed values that must never be quoted as deployed

| shadowed value | where it is written | what actually applies |
|---|---|---|
| `n_base = 14_000` | `fold3_estimator.py`, `base_estimator.py` | overridden to `126 * 256` in `estimator.py` [O] |
| `radial_conditioning = False` | `base_estimator.py` | overridden to `True` in `orthogonal_fold3.py` [O] |
| `pilot_base = 256` | `base_estimator.py` | same value as the override; harmless, but it is not the definition that resolves [O] |
| `fold_pilot_base = 1_024` | `fold3_estimator.py` | same value as the override; likewise [O] |

Reading a constant from a base class the deployed subclass overrides is the exact
error the `kerdock_v3` section committed on its first repair. Four attributes on this
host are shadowed, and two of them by a *different value*.

### Frozen implementation constants, carrying no development selection

| constant | value | where | why it is not in the fitted column |
|---|---|---|---|
| `BLOCK_ROWS` | `8192` | `row_blocked_winograd.py` | scratch height for the streamed Winograd left operand. It is **billing-neutral**: summed over blocks the left stack fills total `7·(m/2)·hk`, the output adds total `7·(m/2)·hn`, the leaves total `7·direct_cost(m/2, hk, hn)`, and the right-hand pack is hoisted out of the row loop, so the bill is independent of the block count [D, and `independently_expanded_bill` in the same file is the source's own statement of that identity]. It sets memory and wall-time, not FLOPs. |
| `1e-12` | `1e-12` | `base_estimator._diagonal_gaussian_pass` | variance floor before the square root; a guard against a non-positive pre-activation variance, live on the deployed path [O] |
| frame ordering | — | `orthogonal_fold3.setup` | the reshape order of `q`; no selection |

**`BLOCK_ROWS` is `8192` here and `4_096` on `kerdock_v3`** [O, both files read this
session]. The committed section's "`BLOCK_ROWS = 4,096`" is correct for the host it
describes and wrong for this one.

### Present in the source, unreachable on this host

These carry numeric literals that would otherwise read as an undeclared fitted
surface. They are declared here so that the mechanical check can distinguish
"undeclared" from "unreachable", and they are not claimed to be unfitted — their
classification belongs to the randomized-radial lineage's own disclosure, not to this
one.

| literal group | where | why unreachable |
|---|---|---|
| `257.0`, `66563.0`, `2600.0 / 537689.0`, `3.0 / 537689.0` | `fold3_estimator.predict`, radial-reweight branch | guarded by `if self.radial_conditioning:` … `else:`; `radial_conditioning` resolves `True`, so the `else` never runs [O]. `257.0` and `66563.0 = 257 × 259` are the exact second and fourth moments of a chi-square at 257 degrees of freedom [D], i.e. the branch reweights toward a radial law this host does not use. |
| the whole of `base_estimator.predict` (same four literals, plus `0.5`, `2.0`, `1.0`) | `base_estimator.py` | fully overridden by `fold3_estimator.predict` [O] |
| the whole of `base_estimator.setup` (`2**32`, `0.5`, `1e-12`, `2.0`) | `base_estimator.py` | never invoked; `orthogonal_fold3.setup` does not call `super().setup` [O] |
| `calls > 8` engineering limit | `cost_model.candidate_bill` | the deployed path calls `batched_candidate_bill` only, via `RowBlockedBatchedWinograd.multiply` [O] |

### Live numeric literals, complete inventory

Every `NUMBER` token on the deployed path, tokenized mechanically. Anything outside
this set is an undeclared constant and fails the check.

- `estimator.py`: `126`, `256`, `2` (the antipodal doubling in `2 * self.n_base`).
- `orthogonal_fold3.py`: `256`, `1_024`, `0.5`, `1.0`, `2.0` (the last three are the
  chi-mean closed form).
- `fold3_estimator.py`: `0`, `1`, `2`, `3`, `0.0`, `0.5`, `1.0`, `2.0`, `3.0`,
  `1_024`, plus the shadowed `14_000` and the unreachable radial group.
- `fold_estimator.py`: `0`, `0.0` (axis indices and the ReLU firing test).
- `base_estimator.py`, live portion: `256`, `-2.0` via `2.0`,
  `0.9807112198896164`, `1e-12`, `0`, `0.0`, `2.0`, `1.0`, `0.5`.

### No performance number appears in this section, and that is deliberate

The ablation percentages in the committed `kerdock_v3` section — the pruning and
folding fractions of `B`, and the isolated frame factor — come from
`experiments/wc1_winner_ablation/wc1_results.json`, whose own firewall field reads
"cached m181 truths + **kerdock_phases.npz** + sobol read-only; **frozen v3 imported
read-only**" [O]. That ablation was run on the `kerdock_v3` host. Its component
values are **not** evidence about this host and are not restated here. The shared
`n_base` in that file's `constants` block does not disambiguate the two lineages; the
firewall string does.

Any performance number added to this section later — and in particular anything
derived from a `full.json` — must carry the caveat **"pending round-4 bill repair
re-run"**, because the cost model that produced those numbers was wrong in both
directions. No such number is present as of this writing.

### What we have stated wrongly

The `kerdock_v3` section published "zero fitted structure anywhere in the estimator",
then a repair that read a base class the deployed subclass overrides. Both are left
on that page rather than quietly replaced. This host adds a third failure of the same
family, and it is the reason this document exists: the corrected `kerdock_v3`
enumeration was allowed to stand as *the* estimator disclosure while the deployed
`row_blocked` entry was a different tree with a different carrier. Nothing in that
section was false about its own host. It was cited about the wrong one, which is a
cheaper mistake to make and a harder one to see, because every individual number in
it checks out against a real file.

Concretely, transplanting that section onto this host would assert: a frozen
phased-Hadamard exact 2-design (there is none); a per-network Haar rotation as the
sole randomization (the entire frame set is redrawn); `phase_start = 2` and
`phase_stop = 128` as fitted constants (they do not exist); `BLOCK_ROWS = 4,096`
(it is `8192`); seven selected scalars (there are six, and one of them, `n_base`, is
forced on that host and selected on this one).

### Forward clause — F7 rotation-selection

If **F7 rotation-selection is ever adopted on this host, its selected surfaces must
be added to this table before designation.** At minimum: the **proxy choice** (which
statistic ranks candidate rotations), the **selection-of-8** (the candidate count,
and the rule for picking among them), and the **frame count** (whether 126 survives
selection unchanged, since a selection pass over rotations changes what `n_base` is
buying). Each is a development-selected surface in exactly the sense this section
uses the word, and a selection rule is a larger fitted object than any scalar already
in the table: a scalar cannot depend on the network it is estimating, while a
selection rule ranks rotations by a statistic computed from that network, and
whatever that statistic proxies for is the target.

The predicate is live rather than hypothetical: the rotation-selection oracle is
recorded at ledger records 204/245 as unharvested headroom, with its pilot proxies
killed **on the Kerdock host** [R, `KILL_CONTEXT_INDEX_20260819.md`;
`HANDOFF_CODEX_SOL_20260808.md` records the proxy correlation as −0.089]. A kill on
Kerdock is not a kill here — kills are context-indexed and the carrier is an axis —
which is exactly why the clause is written before rather than after any adoption.
"F7" is the label the round-4 continuation queue uses; it does not appear in the
committed corpus [O, grep], so whoever adopts it should re-bind the label to a ledger
record in the same edit that fills in this table.

### What we claim, precisely

The fitted surface on the deployed `row_blocked` host is six scalars, one boolean
switch and one structural integer, frozen before grading, confined to budget,
threshold and correction coefficients, containing nothing that could learn the
target, and no component was fit to the evaluation suite. Low measured bias does not
prove absence of fitting, and we do not claim it does. The carrier is 126 Haar
frames of 256 orthonormal directions, redrawn per network from `ctx.seed`, degree-2
and degree-3 exact by construction and carrying the full i.i.d. degree-4 error.

---

## Notes for whoever inserts this

- Insert this **alongside** `SECTION_ESTIMATOR_AND_CONSTANTS_20260812.md`, not
  instead of it, and add a one-line host banner to the top of that file. Two promoted
  lineages, two disclosures. A single merged section would have to hedge every
  sentence about the carrier, which is how the confusion started.
- The three-tier split (forced / selected / frozen-implementation) is carried over
  from the `kerdock_v3` section because it was the right shape. This host needs a
  fourth tier — *present but unreachable* — because `radial_conditioning = True`
  strands a fitted-looking radial polynomial in a live file.
- Do not write "no fitted constants", "zero fitted structure", or "correction-proof"
  as live claims, and on this host also do not write "phased-Hadamard", "exact
  spherical 2-design", `phase_start` or `phase_stop`.
  `core/verify_row_blocked_disclosure.py` fails on any of them outside a withdrawal
  context.
- Run `python -B core/verify_row_blocked_disclosure.py` after any edit to this file
  or to `experiments/row_blocked_production/candidate_source/`. It re-greps every
  declared scalar against source, checks the MRO resolution, and fails on any
  numeric literal in the fitted surface that this document does not declare.

---

## ADDENDUM [2026-08-19] — the lawfulness classification this section declined to make

**Status:** appended 2026-08-19, append-only. **Nothing above is rewritten**; every
statement in the section as first drafted stands where it was written, and this
addendum sits beside the two places it bears on. Source:
`core/CENTRAL_MOMENT_LADDER_20260819.md` §3–§4 (inferential/constructive lane,
hostile-verified, verdict `lawful_construction_verdict = CLOSED-BY-DERIVATION`), whose
arithmetic was re-derived independently in exact `fractions.Fraction` under
`python -B -P` before this addendum was written. Cross-referenced from
`core/PHASE2_CONTRIBUTION_DRAFT_20260819.md` §15 (draft v1.4). Zero billed compute; no
estimator import, no harness run, no seed consumed.

**What this addendum does and does not do.** It changes **no value in any table above**,
adds **no literal** to the deployed path, and asserts **no performance number**. The
deployed fitted surface is still what the section claims: **six scalars**, one boolean
switch, one structural integer. What changes is the *classification* of two surfaces the
section left unclassified or classified one step off, and the closure of a construction
question the section did not open. All three are criterion-(iii) results — they change
what a reader must be told, not what the code computes.

### A1. The radial-reweight branch's four literals are theorem-fixed, not a fitted surface

The section lists that branch under *present in the source, unreachable on this host*,
declines to classify its lawfulness — "their classification belongs to the
randomized-radial lineage's own disclosure, not to this one" — and identifies `257.0`
and `66563.0 = 257 × 259` as moments of a chi-square at 257 degrees of freedom. **The
integers are right and the object they centre is one step off, and that step is the
whole classification.**

At `d = 256`, with `S = ‖z‖²` and `R = ‖z‖`, the chi moment-ratio identity
`E[R^{k+2}]/E[R^k] = d + k` gives [D, re-derived this session in exact `Fraction`
arithmetic from the integer raw moments `E[S^k] = d(d+2)…(d+2k−2)`]:

```
E[R³]/E[R] = d + 1         = 257
E[R⁵]/E[R] = (d+1)(d+3)    = 257 × 259 = 66563
```

So `q₁ = S − 257` and `q₂ = S² − 66563` are exactly orthogonal **to `R`**, not to `1`:
`E[q₁R] = E[q₂R] = 0` identically. That is precisely the tilting that makes the
*multiplicative* weight `w(S) = 1 + a·q₁ + b·q₂` unbiased for **every one-homogeneous
integrand and every `(a, b)`** — and a bias-free ReLU network is positively
one-homogeneous, which the "What is forced" section above already relies on for the
exact radial identity. These are therefore the right centres for this host's own
geometry, and not a reweighting toward a radial law belonging to some other lineage.

With unbiasedness automatic for every `(a, b)`, the pair is free to minimise
`Var(w(S)·R) = E[w²S] − E[R]²`. Every `χ²` raw moment is an integer, so the normal
equations have integer coefficients and the minimiser is **rational**. Solved exactly
[D, this session]:

```
a = −2600/537689        b = 3/537689        <- the deployed literals, exactly
E[w²S]/E[S] = 536640/537689 = 0.9980490580986406      (exact rational)
```

**Classification, stated plainly.** The four literals are **theorem-fixed** — closed
forms and exact rationals forced by the dimension — and are therefore lawful under the
death law's own criterion, which admits theorem-fixed coefficients and rejects fitted
ones. They are not a fitted surface, and this addendum retracts the section's declining
to classify them rather than its description of them.

**They are also strictly dominated, which is why nothing follows for the deployed
path.** That optimum reduces the radial variance by a factor of roughly `7.17e3`, while
the deployed switch `radial_conditioning = True` sets the radial variance to **exactly
zero**. The branch is both lawful and worse than the branch that runs. The design is
closed at both ends of that axis and there is nothing to construct on it.

**The attack that produced this, recorded because it landed.** The first hypothesis
tested was that the weights satisfy the one-homogeneous unbiasedness constraint
`a + (2d+3)b = 0` against raw `χ²_257` moments. That predicts `a/b = −517` (and `−515`
/ `−519` at `d = 256` / `258`) against the deployed `−866.666…` — a clean falsification.
Correcting the reading to `R`-tilted centres at `d = 256` is what made the exact match
above possible, and it is the reason the section's own attribution needed a step added
rather than a number changed.

### A2. `moment_tangent_lambda` has a theorem-fixed substitute, and the surface would become five

The section declares `moment_tangent_lambda = 0.9807112198896164` as one of the six
selected scalars, and that declaration is correct as deployed. Two facts about it were
not available when the section was written.

**First, the coefficient is a pure variance knob and carries exactly zero bias.** The
control subtracts `λ · delta_mean`, where `delta_mean` is the image of `(Δμ, Δv)` under
the **exact first-order tangent** of the analytic Gaussian map. Because that image is
exact rather than approximate, the control is **exactly unbiased for every `λ`, on every
network** — `λ` cannot move the estimate's bias at all, only its variance:

```
Var(M̂ − λΔ) = Var(M̂)(1 − ρ²) + Var(Δ)·(λ − λ*)² ,    λ* = Cov(M̂, Δ)/Var(Δ)
```

**Second, the only value any theorem fixes is `1`.** Every other value is a
variance-minimising choice that has to be estimated from data — fitted, and therefore
dead under the death law. Substituting the theorem-fixed `1` for the deployed constant
would **remove this host's only fitted scalar in the correction path**, taking the
declared surface from **six scalars** to five, and would **save 256 FLOPs** (the
width-256 multiply disappears; `ΔC/C = −1.151e-09`). Its exact cost:

```
(1 − λ)²/λ² = 3.8683631417925867e-04     of the MSE the tangent control removes
(1 − λ)²    = 3.7205703814672980e-04
```

[D, both recomputed this session] under the labelled assumption that the frozen `λ` sits
at the optimum `λ*` [A]. **Settling check:** one offline `λ`-sweep over the stored
tangent and the sampled arms — no forward passes. The control's realised share of the
MSE is not measured in any artifact read for this addendum [GAP]; **settling check:** one
ablation at `moment_tangent_lambda = 0.0` against the deployed value on the stored panel,
whose ratio is the share.

**No closed form for the deployed constant was found** [O]. Seven candidates were
scanned — `E[R]²/d = 0.9980488`, `(d−1)/d`, `√(E[R]²/d)`, `126/128.478`, `1 − 1/51.845`,
`1 − 2/103.7` among them — with a nearest miss of `1.43e-6`, which is not a match at 16
digits. **The constant stays classified as fitted**, exactly as this section has it, and
the substitution above is offered as the lawful alternative rather than as a
rediscovery.

**Stated exactly, because the distinction is the whole point of this section.** The
deployed surface **is** six scalars. Five is what it becomes **if** the substitution is
adopted. It is not adopted here, and no statement in this document assumes it. **Forward
clause:** if it is ever adopted, this addendum's declaration must move into the tables
above in the same edit — `moment_tangent_lambda` leaves the selected-scalar table, the
count in the section heading and in "What we claim, precisely" changes, and
`core/verify_row_blocked_disclosure.py` must be updated in the same commit, since it
asserts both the constant's resolved value and the word "six" against this file.

### A3. The `k`-statistic construction question is closed by derivation on this host

The section enumerates what was selected; it does not ask whether the variance-side
arithmetic could be improved by lawful machinery. Three candidates were priced, and two
close at identically zero [all D, exact]:

- **Exact finite-`n` unbiasing of the squared-deviation mean — closes at `0`.** The
  `n/(n−1)` factor corrects a sample-mean-centred second moment. The deployed code does
  not form one: it centres on the **exact analytic mean**, so `first_variance_residual`
  is already the *known-mean* central second moment, whose bias is exactly `0` at every
  `n` rather than `O(1/n)`. The correction multiplies an object this estimator never
  builds. Cost `0` FLOPs, benefit `0` MSE.
- **`μ₄`-aware weighting of direction contributions — closes at `0`.** Within one frame
  the 256 directions are exchangeable, and the 126 frames are drawn independently, so for
  weights summing to one, `Var(Σ wᵢYᵢ) = c + (v − c)·Σ wᵢ²` within a frame, which is
  minimised at `wᵢ = 1/N` **exactly** whenever `v > c` — and the margin is exactly known,
  `c/v = Q₄(0) = 1/21845` at degree 4. The deployed plain mean over all `2 × 126 × 256`
  rows already applies that weight. More sharply: any admissible weight must be
  measurable with respect to an observable rotation-invariant covariate, the only one is
  the radius, and `radial_conditioning = True` fixes the radius exactly. **The weight
  space has zero free dimensions on this host.**
- **More control channels, or per-channel coefficients — unlawful, or identical.**
  Splitting `λ` per input channel costs `8,110,592` extra FLOPs (`ΔC/C = 3.6468e-5`) and
  adding a third central-moment control costs `41,148,672` (`ΔC/C = 1.8502e-4`). Both are
  dead before the price matters: the only coefficient any theorem fixes is `1` on every
  channel, and `(1, 1)` is arithmetically the deployed single-`λ` structure. They are
  also rank-deficient — the first-layer moment ladder `Δμ, Δv, Δ₃, …` consists of
  functions of `t = u·wⱼ` alone, all zonal about the **same** axis, so their degree-`l`
  projections are scalar multiples of one zonal harmonic and the ladder spans a
  one-dimensional subspace per neuron at every degree.

**The consequence for this section is a negative one and belongs in it for that reason:**
there is no lawful variance-side construction available on this host that the deployed
arithmetic is not already performing, and the two candidates that could have been
performance claims are exactly zero rather than small.

### A4. One further precision about two declared thresholds — a behaviour note, not a correction

`dead_alpha = -2.0` and `on_alpha = 3.0` are declared correctly above: they are the
literals that were selected, and they are what the source resolves. What the pilot's
finite row count does to them is worth stating because a reader will otherwise take the
nominal numbers as the operative cuts. Because the regime tests are `max`/`min` over
pilot rows, they are **order statistics rather than moments**, and their survival
probabilities are exceedances: at 2048 fold-pilot rows a nominal `on_alpha = 3.0` unit
survives with probability `0.0629`, and a nominal `dead_alpha = -2.0` unit stays dead
with probability `3.4e-21` [R, `core/CENTRAL_MOMENT_LADDER_20260819.md` §5, attack 4].
**The operative cut is `|α| ≈ 3.40` and it is symmetric.** Nothing in the tables above
changes; the two literals remain declared at their source values. The note is here
because any future cell touching `dead_alpha`, `on_alpha`, `pilot_base` or
`fold_pilot_base` must predeclare against an exceedance bound and not against a variance
[R, same source, and `PHASE2_CONTRIBUTION_DRAFT_20260819.md` §13d].

### What this addendum claims, precisely

The deployed fitted surface is unchanged: **six scalars**, one boolean switch, one
structural integer, frozen before grading. Two of the surfaces this section describes are
now classified where they were not: the radial branch's four literals are theorem-fixed
exact rationals forced by two independent routes and are lawful under the death law's own
criterion, and `moment_tangent_lambda` is a pure variance knob with a theorem-fixed
substitute at `1` that would reduce the declared count to five at a 256-FLOP saving if it
were ever adopted, which it has not been. No performance number is asserted anywhere in
this addendum, and the standing caveat above — that any performance number added later
must carry **"pending round-4 bill repair re-run"** — is inherited unchanged.
