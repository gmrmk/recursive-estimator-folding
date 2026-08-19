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
