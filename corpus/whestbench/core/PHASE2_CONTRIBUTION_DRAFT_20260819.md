# Phase-2 Algorithmic Contribution writeup — draft v1.1

Status: DRAFT v1.1, 2026-08-19. **First assembly, hostile-reviewed, editorially
revised.** v1 was returned NEEDS_WORK by a hostile verifier with four punctures; this
revision closes all four — carrier-lineage qualifiers on every compute claim (§0, §4,
§9, §10), the named denominator for §4's percentages, the pre-registration amendment
of §11 and §13, and lineage statements on the eight cells — and upgrades the `128/3`
open item of §11 from a flagged coincidence to a theorem. This document collects the ten
Phase-2 artifacts into one argument. It supersedes nothing: the Phase-1 filing of
2026-08-17 (short form, 3,451 words, sent ~21:36 UTC to arc-whestbench@aicrowd.com,
Gmail message id `1a011a886c288f40`) stands as filed, and every erratum E1–E13 it
carries is still in force. What is new here is the connective tissue. The Phase-1
document was a map of one boundary; this one states the law that the boundary turned
out to be an instance of, and reports the eight measurements and two certificates
taken since.

Two of the ten items are **not results**. The Public100 re-measurement of the folded
compute floor and the 129-frame completion cell are pre-registered predictions with
filed falsifiers, and they are marked as such at every mention. Nothing in this
document claims a score.

---

## Beyond the closure wall: a regime-indexed information floor for deep random
## ReLU networks, and the compute floor that is left when the accuracy floor binds

### 0. How to read this, and how to check it without trusting it

Evidence tags follow the scheme introduced in companion P1 (front matter, lines
39–43): **[O]** observed — a run in this corpus produced it; **[D]** derived —
follows by steps shown inline; **[R]** reported — a committed artifact or a channel
entry says so and it is not re-derived here; **[A]** assumed — a stated modelling
choice. A fifth tag, **[GAP]**, marks a known hole together with the check that
would close it; it is used in this document and in P5/P6 and is not part of P1's
four-tag scheme.

Every quantitative claim below carries a cell id, a ledger record id, an artifact
path, or a channel timestamp. Cells are the sealed-gate experiments under
`corpus/whestbench/cells/<cell_id>/`, each with a `predeclaration.json`, a
`GATE_TOKEN.consumed`, a `report.json` whose SHA-256 is recorded in `verdict.json`,
and the git commit at which the gate was sealed **before** the value existed.
Ledger records are the 276 entries in `corpus/whestbench/headroom/fold_ledger.json`.

**A carrier-lineage convention, because §1's own doctrine demands it of us and not
only of competitors.** Two estimator lineages run in this corpus and they do not share
a design carrier. `row_blocked` (ledger id `row_blocked_winograd_production`) builds
**Haar-random** orthonormal frames and therefore carries full iid degree-4 strength;
`kerdock_v3` (ledger id `t4_kerdock_v3_descriptive_rescore`) builds the **126
phased-Hadamard (Kerdock) frames** and suppresses degree 4 by the exact factor §11
derives. The winner fold currently hosts on `row_blocked`; the leaderboard score this
document reports for itself in §12 was earned by `kerdock_v3`, as submission #326094
**[R, `core/KILL_CONTEXT_INDEX_20260819.md`; `core/CODEX_HANDOFF_20260810.md:270`]**.
That split is the **host fork**, it is the campaign's largest open strategic question,
and it is not resolved here. Every measured section below states which lineage its
numbers were taken on, or states that the measurement is carrier-free; where a result
is carrier-indexed and its transfer to the other lineage is unmeasured, that is said in
the same breath rather than left for a reader to discover by cross-reading §4 against
§11.

**A citation-hygiene erratum, stated first because it affects how to read Phase-1.**
Phase-1 cites ledger records by position ("ledger record 202", "ledger 241",
"ledger 242"). Those positions are not stable. In the current 276-record ledger,
record 241 is `s18_cell_membership_probe` and record 242 is
`gen7_svdv_rotation_construction`, matching Phase-1 — but record 202 is
`wc1_winner_ablation_map` (created 2026-08-17, after that citation was written), and
the `on_alpha` dial sweep Phase-1 attributes to record 202 is
`pb1_dial_battery_m188_m189` at position 203 **[O, read from the ledger this
session]**. The record is correct and the pointer drifted. This document cites
ledger entries by their string `id`, which is stable, and we recommend the same
for anyone re-checking Phase-1.

---

### 1. The spine: one law, two campaigns, and its regime refinement

Two campaigns ran against this benchmark without sharing a mechanism, a codebase,
or a result until the end. They arrived at the same sentence. Ours arrived at it
through the Gaussian-closure measurement of Phase-1 §2 and eleven subsequent kills;
Codex's arrived at it through an independent estimator-folding program, and states
it in `ESTIMATOR_FOLDING_POSTMORTEM` as: "A deterministic correction has almost
nothing stable to subtract" **[R, Codex clone corpus, mined 2026-08-18 ~15:0x UTC]**.

That is the law. Stated in our own terms: on depth-32 random ReLU networks at this
width, the part of the output that a deterministic, weight-derived correction can
predict *and* that is stable across networks is small enough that every correction
of that shape costs more in compute or bias than it returns in variance. The
Phase-1 boundary result — analytic Gaussian structure pays when *subtracted* and
fails when *predicted* — is the special case of this law for the Gaussian-moment
family.

**The refinement Phase-2 adds is that kills are regime-indexed.** A kill is final in
the regime it was measured in: carrier, design family, `A_l` regime, precision,
depth, and payoff convention are context axes, and an axis change is a premise
change, not a revival **[owner doctrine adopted 2026-08-19 ~01:3x UTC]**. This is
not a softening. It is what makes the kill field searchable: every kill record
already carries a `kill_condition` and a premise-change field, and the doctrine says
those fields are search coordinates rather than epitaphs.

The rule binds this document's own results first. §0's carrier-lineage convention names
the lineage of every measured section below, and §4, §9 and §10 carry the consequence
that the largest numbers in the compute programme are Kerdock-carrier quantities while
the estimator that ships is on Haar. A hostile reader who put §4 next to §11 would have
found that in a minute; it is stated here instead.

The refinement is not an assertion of convenience. It was validated on the sharpest
public disagreement in this competition. Three independent parties measured the same
intervention — completing a 126-frame design to 129 frames — and reported gains of
19% (Puffi), 0.9% (ely2sh), and ~0.45% (ours) **[R, Discourse sweep 2026-08-18
~16:0x UTC]**. A 20x spread on a single, exactly-specified design change is the kind
of number that usually means somebody is wrong. Section 11 shows it is two regimes
of one quantitative law, and files the prediction that settles it.

The rest of this document is the ten artifacts, each stated at exactly the strength
its evidence earns.

---

### 2. Artifact 1 — subtract-not-predict, and the 340x closure gap

**Claim [O for the measurement, D for the ratio].** A pairwise-exact, assumed-Gaussian
full-covariance recurrence, propagated through all 32 layers and metered at
8.30e9 FLOPs (3.05% of budget), predicts the depth-32 final-layer mean with bias MSE
`9.6055e-5`. The graded sampling estimator's raw final-layer MSE on the same target
is `2.818e-7`. The like-for-like ratio, raw against raw, is **340.86x**
**[D, recomputed this session: 9.6055e-5 / 2.818e-7 = 340.86]**. Making the covariance
exact rather than diagonal buys a factor of ~7.5 (diagonal closure `7.18e-4`).

**Lineage of the ratio, and why the law outlives it.** The sampler side of that ratio is
the hosted graded champion, submission #326094, which is the **`kerdock_v3`** lineage and
not the deployed `row_blocked` carrier **[R, `core/CODEX_HANDOFF_20260810.md:270`; raw
final-layer MSE `2.818e-7` from `s11_results.json`]**. The closure side is analytic and
carrier-free. The number `340.86` is therefore indexed to that sampler. The *law* is not:
the regime audit of 2026-08-19 classifies closures as one of eight **regime-universal**
families, whose kills do not move with the carrier axis **[R, channel 2026-08-19 ~02:1x
UTC]**, and the mechanism is why — a Gaussian-closure predictor's bias is set by the
network, and no design change on the estimator side touches it.

**Scope, unchanged from Phase-1 and repeated because it is easy to inflate.** This
kills *this implementation* as a competitive estimator. It is not a theorem that no
Gaussian-informed method can work. Granting the closure the most favourable possible
compute multiplier (the `0.1` score floor) gives an adjusted-against-adjusted ratio
of `52.4x`, not the `524x` an earlier draft printed by mixing raw against adjusted
(Phase-1 erratum E7).

**Where the design principle comes from.** The same exact Gaussian structure, used
on the *subtract* side as a first-layer moment-tangent control, measured −19.8%
adjusted on its lineage. Used on the *predict* side it lands 46x outside the
competitive boundary. Four insertion points of the closure family — predictor,
control variate, corrector, smoother — were killed independently, each with its own
measured mechanism of failure [`m181_terminal_smoothing_g0`, killed].

**The double witness, and a correction to how it has been described.** The
2026-08-18 competitor sweep recorded "butterbaugh's 340x closure gap" as an
independent corroboration of subtract-not-predict **[R, channel 2026-08-18 ~16:0x
UTC]**. `jonah_butterbaugh` is our own competition handle: the board snapshot of
2026-08-10 lists "jonah_butterbaugh rank 64 at 1.832e-7", which is exactly our
graded adjusted score for submission #326094 **[O, channel 2026-08-10 15:2x UTC]**.
That entry is therefore our own public post at Discourse topic 18147, not a
third-party witness, and we withdraw it as one. The genuine second witness is
Codex's postmortem sentence in §1 — a different campaign, a different mechanism
class, no shared code — and that one stands.

We take the convergence seriously for a specific reason. A single campaign that
measures a wall has measured its own competence as much as the problem. Two
campaigns that never shared a mechanism and hit the same wall have measured the
problem. That is the strongest available evidence that the MSE frontier here is an
information floor rather than an engineering gap **[insight 169]** — and it is
evidence, not proof: neither campaign enumerated the space of methods, and both
would look the same if the true obstruction were a shared blind spot.

---

### 3. Artifact 2 — the fitted-coefficient transfer death, and its corollary

Two mechanisms, killed a week apart on different objects, are the same death.

**DGFL-1, the rotational Stein Fourier ladder [R].** Status
`KILLED_F075_D256_SPARSE_CONTROL_TRANSFER`, sole reason
`FIT_NETWORK_CROSS_TRANSFER_NONPOSITIVE`. The numbers: a coefficient vector fitted
on net0 and applied to net1 scores `R² = −0.17042408432478973`; net1's applied to
net0 scores `−1.0609521690926718`. Yet a *shared* coefficient fitted jointly on both
improves both fits — `R² = 0.10413395` and `0.06745303`, pooled `0.0901300`.
Single-net coefficient cosine is `−0.61465` with 4 of 10 signs matching. The
covariance the method wanted to exploit is there; the coefficient that exploits it
is per-network. Held nets 2 and 3 were never opened.

**Evidence level, stated plainly.** These figures are reported by the partner agent
in the channel of 2026-08-12 02:57 UTC, with `F075_RESULTS.json` SHA-256
`9CBA9C35…716DAFCB`. **That file is absent from this repository tree** — the debt is
recorded in the channel entry of 2026-08-17 21:28 UTC and remains open. The DGFL
kill is therefore **[R], not [O]**, and the Phase-1 short form deliberately omitted
it for that reason. We restate it here because it is half of the corollary, and we
restate its evidence status in the same breath.

**k32 base sensitivity, the replication [O].** The only mechanism that ever showed
positive cross-network transfer was the frozen four-rung `k=32` Fourier family,
whose rungs transferred positively in both directions (`0.0222838`, `0.0150659`)
with production coefficient
`[0.010775500390224034, −0.005378503176404927, −0.006768684712987893, −0.0066378281140845]`
**[R, channel 2026-08-12]**. It was never re-run. It has now been run, three times.

- `k32_base_sensitivity_v1` (gate `a70464d`, seeds 20260817–19) reached scientific
  completion and was **PROTOCOL-KILLed**: the spec named the metric
  `one_minus_median_signed_cos_hi` and the runner emitted `metric`. The
  malformed-metrics gate fired as designed.
- `k32_base_sensitivity_v2` declared fresh seeds while the frozen runner still
  carried v1's constants — a bit-identical deterministic rerun of already-observed
  data. Caught by comparing outputs, recorded as carrying no independent weight, and
  the harness gained a structural seed-agreement check (`spec.seeds` against
  runner-reported `config.seeds`; contradiction is a protocol kill).
- `k32_base_sensitivity_v3` (gate `0bca673`, seeds 20260820–22) is the true
  fresh-seed replication.

Across the six independent seeds of v1 and v3: per-seed paired `t` of
−1.87 / −2.04 / +0.32 and −3.03 / −5.61 / −0.13, with mean held `R²` negative in 5 of
6 seeds. Base-to-base coefficient cosine −0.066 / −0.559 / −0.237 and
+0.176 / −0.065 / −0.925, with all four rung signs preserved in **zero** of six seeds
**[O, `cells/k32_base_sensitivity_v{1,3}/report.json`]**.

**The mechanical verdict, stated exactly.** Both cells record
`verdict_view = "INCONCLUSIVE(phenomenon_absent)"` with `phenomenon_absent = true`,
and the transport metric pinned at the predeclared inconclusive value `0.25`. This
is the protocol working: a transport hypothesis cannot be *killed* by data in which
the phenomenon being transported is absent. The channel headline of 2026-08-18
03:02 UTC reads "TRANSPORT BROKEN 6/6", which the sign and cosine data support, but
the gated metric declines to convert that into a KILL and we do not convert it here
either. The defensible statement: **on width-256 challenge-family networks with
Gram-Schmidt-deflated pullback anchors, the k-high control produces no positive held
variance reduction, and its coefficients do not transport across bases in any of six
seeds.** The instrument is verified — both bases are exact 2-designs (`A2 = 0.0`),
their degree-4 defects differ by 4x (`3.9518e-3` against `9.8823e-4`), and the
degree-energy separation at degree ≥ 6 is 0.278 against 0.006, so the perturbation
lived exactly where the mechanism required.

**Lineage, stated because the doctrine binds our own cells [O, predeclarations read this
session].** Neither k32 cell ran on a deployed carrier. The networks are synthetic
width-256 challenge-family He nets standing in for a hand-built original that exists
nowhere on this machine, and both bases were constructed for the cell: `base1` is a
single complete frame, `base2` a union of four distinct phased-Hadamard frames, chosen so
that the two agree exactly at degree 2 and differ only from degree 4 up. All three
premise shifts are declared in the predeclaration rather than discovered later. One
consequence worth recording: `base1`'s measured defect `A_4 = 0.0039518` is the
one-block value of the closed form proved in §11 (`3.951848e-3`), so the k32 instrument
sat at exactly full iid degree-4 strength, and that measurement is a fourth independent
anchor of the A_4 law. The DGFL figures are on the partner agent's F0.75 networks — a
third network family again, and one whose bytes are still missing.

**The corollary [D].** DGFL died on cross-network coefficient heterogeneity; k32
died on cross-base coefficient transport. One restriction covers both: **only
theorem-fixed coefficients transport.** A coefficient obtained by fitting — to
networks, to bases, to realised residuals — is fitting noise that happens to have
the right dimension. This is the sharpest search-space cut the campaign owns
**[insight 150]**, and it is the cut that pre-kills an entire competitor family: the
offline ridge and GRU correctors in the public write-ups sit inside it **[R,
Discourse sweep]**.

**Residual caveat, carried honestly [GAP].** The k32 operationalization recovered
the spec from primary sources; two elements — the exact symmetry family and the
exact anchor construction — are undefined in-source and were reconstructed. Nothing
recoverable supports the reconstruction being wrong, and no recoverable test exists
that would separate the two. The settling check would be the original hand-built
implementation, which does not exist on any machine here (verified by exhaustive
byte-hunt, 2026-08-18 03:02 UTC).

---

### 4. Artifact 3 — the design-boundary lemma, and CReLU as its constructive proof

**The lemma [D, measured corroboration below].** Exact algebraic structure imposed
on the inputs of a deep ReLU network penetrates exactly **one** nonlinearity. After
that boundary, structure survives only as an attenuating remnant.

The lemma has two faces, and Phase-2 measured both. The destructive face is
sections 5 and 6: whatever exact structure is placed at the input, its zonal and
harmonic signature at depth 32 is one to two orders of magnitude below any
materiality bar. The constructive face is that at the boundary itself the structure
is *exactly* exploitable — and worth real compute.

**The odd channel.** For each antipodal design pair `(+u, −u)`, layer-1 activations
satisfy the exact identities

```
relu(z) − relu(−z) = z          (odd channel: exactly linear)
relu(z) + relu(−z) = |z|        (even channel: nonlinear)
```

so the layer-2 preactivations of the pair are
`z₂(±) = ( W₂|z| ± (W₂W₁)u ) / 2`. The odd term `(W₂W₁)u` is linear in `u`, and `u`
still carries the Hadamard frame structure of the design. So `W₂W₁` can be
precomputed once per network (`2n³ = 3.4e7`) and then evaluated per frame as
`((W₂W₁)D_j)Hᵀ` by fast Walsh–Hadamard transform. Layer 2's paid work collapses to
the even channel alone: half the rows at full price
**[`headroom/FWHT_SPLICE_STAGED_20260818.md`, judge op-count, D]**.

**Why it does not recurse — the boundary, stated as the honest limit.** At layer ≥ 3
the pair difference `relu(a+b) − relu(a−b)` is no longer globally linear, because
the even channel has mixed in. The generic per-layer even/odd split
`relu(z) = z/2 + |z|/2` costs two matmuls (telescoped linear chain plus even
channel) where direct evaluation costs one. **CReLU pays exactly once, at the design
boundary, where the first nonlinearity's odd channel is still linear in
Hadamard-structured inputs.** That is the lemma, constructively: one nonlinearity,
no more.

**The arithmetic, its denominator, and what survived hostile verification.** The shares
below are shares of the **fringe-priced champion suite bill**, which is
`504 × 418,238,464 = 210,792,185,856` FLOPs per net — 32 layers at 15.75 tiles each,
priced at the fringe per-call route. That denominator is named here because v1 printed
the percentages without it **[D, recomputed this session; the 15.75-tile layer bill and
the tile price are the judge op-count in `headroom/FWHT_SPLICE_STAGED_20260818.md`]**.
Numerator and denominator are priced on the same route, so the column is internally
consistent. It is *not* a share of the `152,760,682,368` suite baseline of §9, which
prices the same 504 tiles at the crowned per-call route `303,096,592`; the two bills
differ by exactly that per-tile factor **[D: 152,760,682,368 = 504 × 303,096,592]**.

| splice | per-net saving | share of the fringe-priced suite bill (210,792,185,856) |
|---|---:|---:|
| FWHT layer-1 design evaluation (88.6x on layer 1) | 6.513e9 | 3.09% |
| CReLU odd-channel layer 2 (6.587e9 → 3.402e9) | 3.186e9 | 1.511% |
| combined | — | **4.601%** |

Both went up the suite ladder as seeded tiers under drafter-plus-hostile-verifier
protocol; nothing was adopted on judge arithmetic alone. The FWHT tier was
**rejected in its unnormalized form** by hostile verification and survives only with
its `1/16` normalization — one of exactly two exactness rejections in the whole suite
ladder **[insight 160; channel 2026-08-18 ~17:0x UTC]**. CReLU at layer 2 is the
first win in the crowned suite arc.

**Which carrier these wins are valid on — the qualifier this document owes its own
doctrine.** Both splices are exact on a **phased-Hadamard (Kerdock) design**, and only
there. The FWHT identity's premise is stated in the first line of its own staging
document — "the design IS 126 phased-Hadamard frames, so the FIRST-LAYER evaluation of
the whole design admits the fast Walsh–Hadamard transform" — and the CReLU odd channel
rides the same frame algebra one layer up. On the deployed `row_blocked` (Haar) lineage
of §11 the odd channel is not a butterfly, and our own shipped code says so:
`USE_CRELU_SPLIT` in
`experiments/fold_floor_splice/candidate_source/fold3_estimator.py` is "DEFAULT OFF, and
the reason is measured rather than assumed: the suite's win comes from `o` being a
phased-WHT butterfly, which needs the Kerdock design. On this lineage's Haar-QR frames
`o` is a real half-height product … That is a small loss, so the flag ships off"
**[O, read at HEAD this session]**. The `4.601%` is therefore a **Kerdock-carrier**
quantity. What part of it transfers to the deployed carrier is a separate question with
a partial measured answer, and §9 states it rather than assuming it. The *lemma* is
carrier-free — it is a statement about ReLU and exact input structure, and it would hold
for any exactly-structured design — but the compute the lemma buys is carrier-indexed,
which is the same distinction §1 draws for kills.

**Also swept, and closed with keys rather than corpses.** Smooth ReLU surrogates
(softplus/GELU) fall to the M181 smoothing kill (bias 4–6x baseline MSE); the key is
an exact computable smoothing-bias correction, and none is known. Max-plus/tropical
readings land on the Crofton/facet door, whose key is unchanged (m202's ESS proof,
m86's ownership, and m168's certificate simultaneously). Leaky and parametric mixes
are elementwise identities against a matmul-dominated bill and move nothing.
Per-layer even/odd everywhere costs more than it saves, per the boundary argument
above. No door.

---

### 5. Artifact 4 — the kink-tail transport identity

**Claim [O].** The degree profile of the depth-32 readout's own-axis harmonic
content is the *entry-layer kink tail*, transported forward with its shape intact.

The measurement is `deg_ladder_own_axis_capture_v2` (gate `e605f2b` sealed before
the value; production seeds 20260904–06; wall 398.0 s of a 600 s cap;
`report.json` SHA-256 `eab0a2f6…41aba7`). **Lineage: carrier-free [O, predeclaration].**
This is a function-side measurement — the object is the network's own harmonic content on
synthetic width-256 challenge-family networks, read through network-adaptive axis pools
against matched random-axis floors — so no estimator design carrier enters it, and the
axis that would make it topical again is the network family or the depth, not the
carrier. Own-axis captured energy at the readout, as a fraction of the degree-≥3 residual
energy, by harmonic degree:

| degree n | ρ_own | random-axis floor | own/floor | ratio to degree 6 | λ_n²/λ_6² (exact) |
|---:|---:|---:|---:|---:|---:|
| 6 | 0.003816 | 8.6e-5 | 44.2 | 1 | 1 |
| 8 | 0.001750 | 8.8e-5 | 19.8 | 0.459 | 0.445 |
| 12 | 0.000483 | 5.3e-5 | 9.2 | 0.127 | 0.147 |
| 16 | 0.000229 | 4.3e-5 | 5.3 | 0.060 | 0.068 |
| 24 | 0.000108 | 7.1e-5 | 1.5 | 0.028 | — (not gated) |
| 48 | 0.000019 | 4.0e-5 | 0.5 | 0.005 | — (not gated) |

The right-hand column is the closed-form Gegenbauer coefficient of a single ReLU
kink, squared and normalised to degree 6:
`λ_n` = `0.00277366, −0.00184936, −0.00106436, −0.000725044` at
`n = 6, 8, 12, 16` **[O, `metrics.geometry.lambda_closed_form`]**, evaluated against
an exact-rational reference to `1.9e-15` maximum relative error at degree 48. The
measured profile tracks the exact kink tail to within 14% of the exact ratio at every
gated rung; at degree 8 the exact value sits inside the three-seed spread of the
measured ratio (`[0.399, 0.498]` against 0.445), and at degrees 12 and 16 it sits
just above it (`[0.117, 0.140]` against 0.147; `[0.055, 0.065]` against 0.068), so
the agreement is in the shape rather than in the seed noise
**[D, per-seed ratios recomputed this session from `metrics.per_degree_readout`]**.
**The own-axis share never rises with degree** — there is no band at
which structure re-concentrates.

**Gating, and why it cannot select on the answer.** A rung enters the metric only if
all three hold: measured readout noise over the 6 × seeds random-pool draws is at
most `R2_BAR / n_rungs = 0.003333`; the instrument recovers the exact in-span
degree-n energy of the second-layer preactivation to within a factor of two; and the
sampled mean of the zonal feature square, whose true value is exactly 1, reaches at
least half of it. Degrees 6, 8, 12, 16 gate; degrees 24 and 48 are reported and not
gated, failing the feature-reach bar at 0.489 and 0.371 — exactly the plateau the
power analysis predicted. The own-axis capture is never consulted by the gate.

**The verdict, and its two legs.** Metric 2.0, KILL. Structural leg 0.043007:
cumulative own-axis capture is **23.3x** the summed random floor, so the
concentration is real and decisively resolved. Material leg fully clipped at 2.0:
the summed own-axis capture over gated rungs is `0.006278`, i.e. **0.63%** of the
degree-≥3 residual against a predeclared 2% materiality bar — 3x short. Real, and
immaterial.

**Anchor honesty.** Degree-6 `ρ_own` is `0.003816` here against `0.001872` in the v1
cell, on different production networks — 44.2x its matched floor here against 10.2x
there, and 0.38% against 0.19% of residual. The *order* replicates and both stay an
order of magnitude under the 2% bar; the exact value, and its multiple of the floor,
are network-dependent and are recorded as such rather than averaged away.

---

### 6. Artifact 5 — the depth-resolved zonal concentration surface, and ridge collinearity

The hypothesis this pair of cells tested came from splicing two failures. Layer-1
neuron functions `relu(w_i·u)` are exactly zonal about their own weight rows, so a
network's degree-6 error energy need not be uniformly dispersed over
`dim H_6 = 4.14e11`; and the replicated pullback collinearity of §3 suggested deep
composition concentrates preferred directions further. The earlier dispersion kill
had used a *fixed* tractable basis. The network-adaptive zonal basis had never been
measured.

**Result [O, `deg6_own_axis_zonal_capture_v1`, gate `7c5ab10`, seeds 20260901–03].**
The hypothesis was half right, in the instructive direction. Own-axis degree-6
capture at the readout is `ρ_own = 0.001872` against a matched random-axis floor of
`0.000183` — **10.2x the floor**, per-seed `[0.00177, 0.00208, 0.00176]` against a
resolvable-at-3sd threshold of `0.00049`. The concentration is real and cleanly
resolved. And it is worth `0.19%` of the degree-≥3 residual energy against a 2% bar:
an order of magnitude short, 40x short of PASS.

**The depth surface [O, `metrics.depth_ladder`].** Own-axis degree-6 capture by
layer, first of two probe networks:

```
L1 0.1578 → L2 0.1376 → L3 0.0362 → L4 0.0206 → L6 0.0092 → L8 0.0062
   → L12 0.0046 → L16 0.0020 → L24 0.0029 → L32 0.0036 → readout 0.0019
```

**Correction to the summary of this curve.** The channel entry and insight 157
describe the ladder as decaying monotonically at roughly 0.4–0.5 per layer. The
committed data support neither the monotonicity nor the single rate. Over layers
1–8 the decay is real and steep — a factor of 25.5 across seven layers, geometric
mean **0.63 per layer** **[D, recomputed this session: (0.006187/0.15782)^(1/7) =
0.6296]** — and the steepest stretch, L2→L4, runs at 0.39 per layer, which is where
the "0.4–0.5" figure comes from. From layer 12 onward the curve **plateaus and
bounces** between 0.002 and 0.004 (L16 0.00197 < L24 0.00289 < L32 0.00358), with
the random floor plateauing too, so the own/floor ratio stays at roughly 10–20x
through the deep tail. The corrected reading: structure is destroyed fast over the
first eight layers and then stops being destroyed, sitting at an immaterial but
non-vanishing residue for the remaining twenty-four.

Notably, the network-**adaptive** basis at depth 32 lands at 0.19% — the same order
as m191's **fixed** 24-function basis at 0.23–0.29%. Adaptivity does not beat the
dispersion at depth; it only survives it. That comparison crosses a lineage boundary and
is quoted at order-of-magnitude strength for exactly that reason: this cell is
carrier-free while m191 was measured on the **Kerdock** lineage **[R, regime audit,
channel 2026-08-19 ~02:1x UTC]**, so the two agree on the order and nothing finer is
claimed from the pair.

**Ridge collinearity — a harmonic-free instrument [O,
`deg_ladder_own_axis_capture_v2`, `metrics.ridge_collinearity`].** A function
exactly zonal about one axis has a gradient collinear with that axis everywhere, so
the top-1 share of the input-gradient second-moment spectrum is exactly 1 at layer 1
and its decay measures, with no harmonic machinery at all, how far the deep kink
surfaces have bent away from great spheres about any fixed axis:

```
L1 1.000 → L2 0.499 → L3 0.323 → L4 0.231 → L6 0.144 → L8 0.079
   → L12 0.059 → L16 0.045 → L24 0.036 → L32 0.028 → readout 0.040
```

against an isotropic null top-1 share of `0.006057` and participation ratio `240.9`;
the readout measures participation ratio `88.9`. Top-8 share is `0.1895` against a
null of `0.0471` — a 4.0x concentration, consistent with v1's 3.6x
(`0.170` against `0.047`, participation ratio 97 against 241).

**A second summary correction.** The channel entry of 2026-08-18 09:2x UTC quotes an
isotropic null of "~0.011" for the readout top-1 share. The committed report gives
`0.006057`. We use the committed value; the discrepancy is in the summary, not the
artifact, and we have not reconstructed how it arose.

**What the surface says, stated at its strength.** Deep kink cones are curved and
zonal about nothing: concentration relative to isotropy is a real 4–7x, and
concentration relative to what any theorem-fixed zonal control could harvest is
0.19–0.63% against a 2% bar. Both cells are the design-boundary lemma seen twice.

**Door and key, recorded.** Layers 1–4 capture 2–16% per rung. Any future estimator
variant that consumes early-layer targets directly — none exists today — inherits a
constructible theorem-fixed zonal control for free. Reopening the deep case requires
a *different axis family* than W1-rows-plus-pullbacks, not a bigger budget on this
one.

---

### 7. Artifact 6 — the covariance-recurrence lottery, ReLU as spectral restorer, and the relative-stricter inversion

The campaign's largest open structural lane was the exact-control spine
`M151 → M179 → M198 → M205 → M125b`. Everyone was aiming at blocker A, the missing
physical fourth-order provider. A theorem-splice swarm of 13 agents across 6 lanes
surfaced blocker B, which sits upstream of it: `gm_m179_m199`'s reachability kill,
where the production-width covariance crosses the M198 variance floor mid-trace and
the fail-closed guard refuses. A perfect provider cannot run past a guard that has
already fired **[channel 2026-08-18 03:5x UTC]**.

**Lineage: no spherical carrier at all.** The covariance recurrence is a property of
He-initialized weights and of the arc-cosine ReLU map, and the kill-context index records
that the whole `m141`–`m207` analytic block names no spherical carrier on any record
**[R, `core/KILL_CONTEXT_INDEX_20260819.md`]**; the regime audit classifies the spine as
regime-universal. The axis that does bind here is precision, and it is named in the
terminal logic below: the closure is f64-specific.

**m207 — the mechanism is not what the record assumed [O,
`m207_reachability_v1`, gate `21bd94f`, seeds 20260823–24, widths 64/128/256].**
Metric `log10 κ₁₂ = 10.48`, mechanically INCONCLUSIVE in the predeclared marginal
band. The data inside the band are the result:

- **Trace stable** at every width and repetition: the gauge log spans 0.16–0.34
  decades over 32 layers. The scale-decay branch is refuted on production seeds —
  no lawful gauge transformation can repair the wall, because there is no scale to
  remove.
- **The width-monotone fingerprint is falsified**: width-64 rep-0 gives
  `κ = 10^10.96`, above width-256 rep-0's `10^10.48`. The wall is not a smooth
  Lyapunov collapse at a fixed layer.
- The revised mechanism **[D, 2 seeds × 3 widths = 6 width-reps]** is an **intermittent
  stochastic near-singularity**: each layer's Gaussian congruence occasionally
  produces a near-rank-deficient covariance, the arc-cosine map restores it, and
  whether any layer dips below the floor is a per-network lottery draw.
  `gm_m179_m199`'s "layer-12 wall" was one rep's draw of that process.

**m207b — the owner's semantics change, measured [O, `m207b_semantics_v1`, gate
`783cc10`, n = 200 production-width networks plus 40 pure-congruence controls;
`report.json` SHA-256 `7b41ca3a…1805aea`].** The owner authorised changing M198's
variance-floor semantics from absolute to relative — the named premise change on
which the lane reopens. The measurement, on *identical* eigendecompositions:

| floor semantics | per-network guard-fire probability | Wilson 95% CI | 24-net sweep risk |
|---|---:|---|---:|
| absolute | 0.015 | [0.0051, 0.0432] | 30.4% |
| relative | **0.130** | [0.0903, 0.1837] | **96.5%** [89.7, 99.2] |

**The inversion is the finding.** In the trace-stable regime with maximum eigenvalue
above one, a relative floor at the same numeric bar is **8.7x stricter** than the
absolute floor it replaces. The authorised repair makes the lane deader, and it was
the measurement the ruling authorised that refuted the ruling. Condition-number
quantiles (log10): q50 10.8, q90 12.3, q99 15.0, max 16.2 — the tail reaches past
the f64 epsilon wall. Crossings are near-uniform across depth (argmax octile
histogram `[20, 31, 20, 20, 19, 24, 34, 32]`): there is no wall at layer 12.

**ReLU as spectral restorer [O].** The control arm removes the ReLU covariance map
and keeps everything else: **40 of 40** pure-congruence chains collapse to
non-positive spectra by roughly layer 8, with the condition metric pinned at the
`10^30` cap and an argmax histogram of `[7, 33, 0, 0, 0, 0, 0, 0]`. The ReLU map is
the only thing keeping the recurrence alive across 32 layers — and the balance it
strikes, between Lyapunov spreading and spectral restoration, is precisely what
leaves a heavy-tailed conditioning lottery behind.

**Terminal logic, developed to conclusion [D].** (a) No numeric value of a relative
or absolute floor is simultaneously f64-meaningful and rarely crossed: reaching
`p ≤ 0.003` needs a bar below the q99.7 of the max-κ distribution, at or beyond
epsilon, where a floor no longer separates signal from roundoff. (b) Higher
precision does not exit — the conditioning is real mathematics, so quad-precision
production measures the same κ and any f64 consumption inherits `κ·ε` up to O(1)
relative error, destroying the spine's exactness class. (c) The gauge exit died in
m207. (d) The provider exit is moot and over budget: a naive unit-basis owner table
costs ~4.3e9 FLOPs for **one** layer against a strict headroom `H = 1.987e9`, 69x
over for 32 layers. The spine is closed under every floor semantics, and it
terminates on measurement rather than on fiat.

**The keys, recorded.** The lottery curve is itself an instrument: guard-fire
probability as a function of width, depth, and precision is now a measurable
function, useful to anyone building deep-covariance pipelines. And the closure is
f64-specific — a mixed-precision trace (f128 recurrence, f64 consumption,
condition-aware routing) was closed by *argument*, not measurement **[GAP; the
settling check is one f128 sweep at n ≈ 200]**.

---

### 8. Artifact 7 — the dual-witness certificate

`papers/DUAL_WITNESS_CERTIFICATE_20260818.md`, with companion
`papers/dual_witness_certificate.py` (38 checks, exact rational arithmetic, pure
standard library, no randomness, two runs byte-identical at SHA-256
`8e1c89d9…832321`).

**The collapse that makes a finite witness possible [D].** Weighting the 129
canonical real mutually-unbiased blocks of `R^256` looks like a 128-dimensional
design problem. Because every cross-block inner product is `±1/16` and every
within-block off-diagonal inner product is `0`, the degree-`l` block-summary matrix
has exactly two distinct entries, and a block mixture `w` enters every
rotation-averaged error functional through the single scalar `‖w‖²`. The design
space collapses from 128 dimensions to one.

**Theorem 2, equal compute, unconditional [D + O].** On any support of `k` blocks,
the uniform mixture is the unique global minimiser of `Q_l` at every even `l ≥ 4`
simultaneously, hence of every nonnegative spectral mixture. Exact KKT; the script
evaluates both sides in `Fraction` at all 19 active degrees for `k = 126` and the
duality gap is the exact rational `0` at every one.

**Theorems 3–5, the full game [D + O].** With compute proportional to block count,
the payoff is two affine lines with opposite slopes,
`R_4(k) = (129−k)/3` and `R_6(k) = (4095+k)/4221`, both normalised to 1 at `k = 126`.
Hence `max_l R(k, l) > 1` at every other block count, and the minimax value is
exactly 1, attained uniquely at 126. The matching dual witness is a two-point
spectral energy, `y_4 = 16637/555357`, `y_6 = 538720/555357`, satisfying
`y_4 G_4(1/16) + y_6 G_6(1/16) = 0` exactly and checkable by hand in four lines.
Primal value 1, dual value 1, gap 0.

The degree-4 line has since acquired a structural reading it did not have when the
certificate was written: §11 proves that `R_4(k)` **is** the `k`-block degree-4 design
defect multiplied by the compute factor `k/126`, exactly, for every `k` from 1 to 129.
The affine shape of `R_4` is therefore not an artifact of the payoff convention; it is
the design defect itself, and the payoff convention only rescales it.

**The claim, at exactly its proven strength — and the boundary, stated because the
first draft overstepped it.** A hostile verifier rejected one prose paragraph (§5.1
Consequence) as claiming more than the LP delivers, and the judge narrowed it. The
narrowed text now reads: within the game the certificate formalizes — mixtures over
the 129 canonical real-MUB blocks, the stated payoff, spectral energy entering only
through the stated `α_l` weights — no mixture at or below the champion's block count
improves on uniform-126, and the optimum there is unique. **The certificate does not
bound estimators outside this block family, other payoff conventions, or the
deployed carrier's empirical score.** The deployed row-blocked carrier was found to
run Haar-random frames rather than these blocks (§11), so the 126-versus-129
question *on that carrier* is an empirical cell, not a corollary of this LP.

**The dependency, named rather than hidden.** The score is `MSE × C/B`, so the
conclusion turns on the completion's marginal compute. The exact break-even ratio is
`2881/2816 = 1.0230824`; the cheapest possible ratio — one extra block being one
extra frame of 512 points — is `129/126 = 1.0238095`. The margin is `1408/1407`, or
`0.0711%`. Flipping the certificate requires finding `1.298e8` FLOPs of savings in
the completion; the only saving the corpus identifies (the identity frame needs no
Walsh butterfly) is `5.24e5`, short by 247.5x.

**Under the frozen spectrum [D, conditional on R0].** The whole block-mixture axis,
tested and untested, is worth `δ = 0.4388%` of adjusted score, satisfying the closed
form `δ = s_4 − (1/42) Σ_{l≥6} a_l G_l(1/16) / V`: the value of the entire axis is
the degree-4 share of the error minus a higher-degree correction. The predicted
`129/126` score ratio is `0.99561`, which falls inside MUB129's measured 16-network
interval `1.00087 ± 0.01855` **[O, `papers/dual_witness_certificate.json`,
`frozen_spectrum.measured_16_fresh_net_ratio` and `measured_CI_half_width`; the
certificate's prose rounds that interval to `[0.9825, 1.0196]`, one part in ten
thousand wide at each end]**. The observed null is what the certificate predicts.

**Certainty, as the certificate itself declares it:** Theorem 1 and the closed forms
99%; Theorem 2 99%; Theorems 3–5 97%, conditional on compute being at least
proportional to block count (the 0.07% margin is why it is not higher); `δ = 0.44%`
under the frozen spectrum 90%, since R0's energy profile under-predicts measured
`s17` absolute MSE by 2.1–3.7x and `δ` is a ratio in which most of that scale
cancels.

---

### 9. Artifact 8 — certified compute floors, and the constant-unfreezing pattern

When the accuracy floor binds, the score `MSE × max(0.1, C/B)` still has a live
term. Phase-2 drove it to a certified floor twice.

**The per-call floor: 303,096,592 [O, re-executed this session].** A 30-tier
recursion over the champion's matmul schedule banked seven hostile-verified wins,
zero rejected claims:

| tier | change | bill |
|---:|---|---:|
| — | frozen incumbent route at ladder start | 418,238,464 |
| 1 | `depth_swept_winograd` — unfreeze the hard-coded two-level recursion | 335,934,144 |
| 2 | `view_elided_interior_stacks` | 326,599,104 |
| 3 | `ancestor_scattered_leaf_stacks` | 319,026,624 |
| 4 | `alternative_basis_winograd` — Karstadt–Schwartz basis conjugation | 304,210,704 |
| 5 | `level_graded_basis` | 303,932,176 |
| 6 | `psi_scattered_root_stacks` | 303,294,880 |
| 7 | `inplace_verbatim_leaves` | **303,096,592** |

Deltas sum to `115,141,872`, exactly the difference **[D, checked this session]**.
Ratios: `0.724698` against the route at ladder start, `0.642546` against the parent
`owned_batched` route (`471,711,744`), `0.565666` against direct (`535,822,336`).
The champion's matmul schedule now costs 56.6% of naive, by exact identities only.

Two independent signals: the judge's re-execution recorded in the channel
(2026-08-18 05:4x, clock-corrected to 08:39 UTC), and a fresh execution of
`headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py` in this session, which
prints `total: 303096592`, strategy `winograd_l6_inplaceleaf`, and the full depth
table with the L=6 argmin **[O]**. The same integer appears independently in
`experiments/fold_floor_splice/full.json` as `selfchecks.tier07_floor_4096_256_256`.

**Carrier: none, and this is the one large compute number here that is carrier-free.**
The per-call ladder optimizes the schedule of a fixed `4096 × 256 × 256` matmul by exact
identities on the matmul alone. The design vocabulary that the suite ladder runs on —
`kerdock`, `phased`, `hadamard` — appears **zero** times across all eight per-call tier
scripts **[O, grepped this session]**, and the kill-context index independently records
that the fold's schedule route applies to both lineages' deep layers **[R,
`core/KILL_CONTEXT_INDEX_20260819.md`]**. Whichever way the host fork of §0 settles,
`303,096,592` is the floor.

**The proof that it is a floor [O].** Three consecutive dry tiers, each carrying its
own arithmetic: tier 8 shut the cost-reweighting door with the only remaining money;
tier 9 shut weighted redistribution elementwise, with the 1.07% transform-lane slack
closed by two independent walls; tier 10 established that nothing lawful beats the
number at the canonical shape. The stop is an adjudication, not an exhausted
searcher.

**The suite floor: 144,867,083,088 per net [O, re-executed this session].** The
suite-level ladder ran to tier 27 and adjudicated 23 of them: 18 hostile-verified
wins, 2 exactness rejections (the unnormalized FWHT form; tier-6 cross-side reuse),
and 3 proof-carrying dry closures. Tiers 21–24 produced no adjudication at all and
are the infrastructure failures described below. The win arc, in order: CReLU layer-2 → weight-stack hoisting → antipodal
base rows → cross-net design stack → orphaned negation → direct-top/subtracted
antipode → ReLU-write-free → normalization placement → butterfly
destination/frame-independence (stages 1–2, stage 3 proved shut) → deployed-butterfly
repricing of layer 1 (the FWHT repair, self-found) → crowned-schedule butterfly →
counterfactual repricing → dead-lane removals → precompute depth and stack riding →
scalar-seat exhaustion.

Verified this session by running the lineage files from the repository root:
`suite_00_incumbent.py` prints the uniform baseline `152,760,682,368`, and
`suite_19_…` prints `144,867,083,088`, a ratio of `0.948327` (−5.167%)
**[O; ratio recomputed: 144867083088/152760682368 = 0.9483270]**. Tier 19's own
docstring prices the last term it took — the odd channel's normalization, 65,536
FLOPs, or 0.0000452% of the whole bill — which is what an exhausted ladder looks
like from the inside.

**Carrier: Kerdock — and the transfer is partly measured, partly open.** The suite ladder
prices layer-1 design evaluation as a phased-WHT butterfly from tier 01 onward, so
`144,867,083,088` is a **Kerdock-carrier** floor, not a floor for the deployed Haar
route. Every one of the 23 adjudicated suite tier scripts names the phased/butterfly
algebra; the per-call tiers name it nowhere **[O, grepped this session]**. The campaign's
own transfer analysis, filed 2026-08-18 ~19:0x UTC, partitions the suite delta against
the deployed `row_blocked` route into class A (real route changes) `5.76e9` plus a
`2.01e9` butterfly port, class B (already deployed, no re-bankable value) `2.36e9`, and
class C (model-only) `8.3e6`, and records **non-transferring `2.37e9`, or 1.55%**
(quoted as filed, not re-derived from the class totals); the same
entry records that tier-14's butterfly is class B on `kerdock_v3` — already inside its
bill — while on `row_blocked` layer 1 is a real Winograd matmul **[R, channel
2026-08-18 ~19:0x UTC]**. That partition and §4's shipped-off `USE_CRELU_SPLIT` flag are
two statements about the same transfer taken at different times, and this document does
not reconcile them **[GAP]**. The settling check is named and running: the itemized
FlopScope receipt from the Public100 fold measurement pre-registered as P1 in §13 bills
the deployed route line by line, which is the only instrument that resolves it.

**Two false endings, both caught.** The first stop fired on one genuine dry plus two
API-529 infrastructure failures the script had counted as dry. The judge ruled it
not an earned certificate, and the ladder was resumed from cache. The continuation
then hit twelve consecutive 529s; the fixed dry-counter correctly advanced on none
of them and the run ended `dry_stop_earned = false` rather than minting a fake
certificate. The certificate was finally earned by tiers 20, 25, and 26 — three
consecutive genuine adjudications, each closing its doors with executed arithmetic.
The ladder lesson, recorded: **a failed draft is not a dry**, and a dry counter that
cannot distinguish adjudication from infrastructure will manufacture floors.

**The constant-unfreezing pattern [D, insight 159].** The two largest single-tier
savings in the per-call ladder — tier 1 at `82,304,320` and tier 4 at `14,815,920`,
together 84% of the total win — both did the same thing: they **unfroze a constant
the incumbent had hard-coded**. Tier 1 unfroze the recursion depth, which the
incumbent had fixed at two levels; tier 4 unfroze the single global basis. Neither
invented an algorithm. Both swept a parameter whose value had been a decision
nobody had revisited. This is the transferable search heuristic of the whole arc,
and it is folded into the headroom-recursion skill ledger as entries A18–A20.

---

### 10. Artifact 9 — the m-curve and the slope law

Metered FLOPs are not the whole cost. The graded quantity is
`C = analytical + 1e11 × residual_seconds`, so any schedule that trades arithmetic
for dispatch can win on paper and lose on the board.

**The slope law.** The corpus's only case of a large FLOP saving dying is the V5-d3
static replay, and it died on **per-call slope** — `5.509e-4` s/call, integrated
`k ≈ 1.05` — not on arithmetic **[insight 145]**. That makes call slope, not
operation count, the predicted failure mode of every new schedule, and it is why
every splice in §4 carries a verification gate requiring inlined or batched
dispatch with no per-frame native-call structure.

**Doubly witnessed, independently of us [insight 167].** Codex's 2026-08-14
proof-carrying verification measured the fringe route at compute ratio `0.9493` and
**wall-time ratio `1.3749`** on Linux: the adopted champion route's compute win did
not produce a wall win. Independently, public Discourse topic 18184
(`bin_yong_bong`, no organizer reply) measured Strassen–Winograd depth against
residual wall time at width 256 and reported that depth-5 "saves 24,000 metered
FLOPs per sample and spends 432,000 residual ones — an 18:1 loss" **[R]**.

**A correction to our own slope law, from that same public table.** 18184's data
also show depth-**2** at a total of 104,169 per sample against 130,958 direct — an
11:1 *win* where depth-5 is the 18:1 loss. Our slope wall had been drawn at depth 5
and over-generalized to the family. The corrected statement: deep recursive
schedules pay in residual time and shallow ones do not, so under a surviving
`λ = 1e11` the deployed optimum is shallow, and under a dropped or generously capped
residual channel our metered floor stands as measured **[R, sweep 2026-08-18 ~16:0x
UTC]**.

**The m-curve.** Fold the certified floor and banked splices into the deployed
route and the post-fold compute bill is
`max C_post = 126.7e9 + 18.815e9 × m`, where `m` is the residual-wall multiplier the
deeper route realises against the deployed `0.1606` s/net. The increment
`r_inc = 0.18815` s is exact. Every score ratio and break-even below is taken against
the incumbent's own Public100 receipt, `C = 222.405B` **[R, channel 2026-08-18 ~18:1x
UTC]**; that denominator is what makes `m* = (222.405 − 126.7)/18.815 = 5.09` and the
`C ≥ 200B` falsifier line `m ≥ 3.896`.

**Carrier, stated where it bites.** The measured half of this curve is on the deployed
`row_blocked` (Haar) lineage: the fold's candidate source is a fork of
`row_blocked_production/candidate_source/fold3_estimator.py` **[O, file header read this
session]**, so the `flops_ratio` of 0.712–0.726 and every residual second below are
deployed-carrier measurements. The analytical constant `126.7e9` inherits §9's transfer
question, since it folds banked splices whose Kerdock-carrier share the A/B/C partition
bounds at `2.37e9` non-transferring. Discounting that share in full moves `C_post` to
`129.07e9 + 18.815e9·m`, which moves the break-even from `m* = 5.09` to `4.96` and the
falsifier line from `m ≥ 3.896` to `m ≥ 3.77` **[D, recomputed this session]** — both
still far above the measured band below, so the conclusion is insensitive to the whole
open transfer question even at its worst.

Four derivations of the same curve, arrived at separately:

1. **Graph adjudicator** — applied the ladder's `0.69` route constant to total `C`:
   predicted `C = 153.5B`, score `1.4640e-7`, a 31.0% cut in `C` against the 222.405B
   receipt **[R, wf a06c25c8-7ab]**. The 31.0% is the compute reduction, not a
   score-versus-`1.83e-7` comparison; the adjudicator's absolute score figure carries
   its own MSE baseline and is quoted, not re-derived.
2. **Judge pre-registration**, filed before the locator agent reported, deriving from
   receipts instead: `C ≈ 156.5B`, score `1.493e-7`, with a pre-registered band
   `C ∈ [150B, 165B]`, `score ∈ [1.45e-7, 1.53e-7]` **[D, channel 2026-08-18 ~18:2x
   UTC]**. Its route identification was subsequently **falsified**: the deployed
   route is `owned_batched` at `471,711,744`/call
   (`experiments/v31_guards/package_source/row_blocked_winograd.py:88`; the constant
   re-derived this session from `cost_model.owned_batched_candidate_bill(4096,256,256)`
   in that package and asserted at `depth6_winograd.py:680`), not the 418M-class route the
   pre-registration inferred, and the 210.79-versus-222.4 gap it computed was
   coincidence. Per the pre-registration's own commitment the number was re-derived
   from itemized receipts rather than patched.
3. **The headroom-recursion (TRM) engine**, run independently and halting at its
   cheapest tier with no escalation: `r_inc = 0.18815` exact, break-even
   `m* = 5.085` against the judge's `5.087`, score ratios `0.6542 / 0.7387 / 0.8232`
   at `m = 1/2/3` **[O, engine run 2026-08-18 ~20:5x UTC]**.
4. **Measurement.** Hostile verification of the implemented fold measured, on probe
   networks at the shipped depth 4, `flops_ratio` 0.712–0.726 — and this is where
   the honest band widens.

**The measured `m`, reported at its real spread — three runs, not two.** The first
hostile-verify pass reported residual ratio 1.86–2.03 and effective-C ratio
0.811–0.829 **[R, channel 2026-08-18 ~21:2x UTC]**. The committed revision of
`experiments/fold_floor_splice/full.json` gives, for the depth-4 arm,
`residual_ratio` 1.967 / 2.260 and `effective_C_ratio` 0.806 / 0.837. The
working-tree revision of that same file, regenerated at 23:11 on 2026-08-18 and
**not committed as of this draft**, gives `residual_ratio` **2.406 / 2.637** and
`effective_C_ratio` 0.834 / 0.866 **[O, both revisions read this session:
`git show HEAD:…/full.json` against the file on disk]**. `flops_ratio` holds at
0.7121 / 0.7253 committed and 0.7120 / 0.7257 in the working tree, so the metered
half reproduces across all three runs and only the residual channel moves.
Residual seconds are machine-load dependent and the three runs disagree. **We state
the union: `m` measured in `[1.86, 2.64]` across three hostile-verify runs.** From
committed evidence alone the band is `[1.86, 2.26]`; we carry the union because the
wider band is the conservative one against the falsifier and because the third run is a
real measurement that happens not to be committed yet. Committing that regeneration
before any filing is an open item, and it is the only way the narrower band becomes the
honest one. At
`m = 2` the predicted score ratio is `0.7389`; at `m = 2.64` it is `0.7930`
**[D, recomputed this session]**. Both sit under the falsifier line, which trips at
`C ≥ 200B`, i.e. `m ≥ 3.896`, and well under the break-even against the incumbent at
`m* = 5.09`.

**Why the naive transcription would have failed.** Public 18184's data imply a
geometric residual growth of `q = 5.455` per unit of depth
**[D, recomputed this session: 432,000/2,662 = 162.3 over the three levels from
depth 2 to depth 5, so `162.3^(1/3) = 5.455`]**, so a naive depth-6
transcription lands at roughly `5.455⁴ = 885x` the depth-2 residual — catastrophically
above `m*`. The implementation law that follows is not optional: batch and
restructure the recursion. The implementer applied exactly that discipline (depth
cap plus batched leaf dispatch), which is why the measured `m` is near 2 rather than
near 885.

---

### 11. Artifact 10 — the carrier discovery, and the A_4 reconciliation as a live prediction

**The discovery [O, verified in source 2026-08-18 ~22:3x UTC].** The deployed
`row_blocked` carrier **does not run the Kerdock design**. `orthogonal_fold3.setup`
builds Haar-random orthonormal frames. For random frames the degree-4 design defect
is `A_4 = 3.136387e-05`; for the Kerdock 126-frame design the design document's
exact-rational census gives `A_4 = 7.350908201315546e-07`. The deployed carrier is
therefore sitting at **42.67x** the Kerdock degree-4 defect
**[D, recomputed this session: 3.136387e-05 / 7.350908201315546e-07 = 42.6667]**,
which is to say at full iid degree-4 strength — the `2/N = 3.1002e-05` line for
`N = 64,512` antipodal points, plus 1.2%.

Everything the corpus wrote about design completion — including §3b2 of the Phase-1
v13 long draft (`core/PHASE1_WRITEUP_DRAFT_20260808.md`), condensed into §4 of the
filed short form: "completion buys 0.4497% against a 2.33% break-even" — was
measured or derived for
the *Kerdock* carrier and over-generalized to the deployed one. The m81/s11
break-even does not bind the deployed carrier
[`m81_full129_pareto`, `s11_full129_reopen_measured_breakeven`, both killed].

**Theorem — the A_4 law in closed form, and the derivation the first draft did not have
[D, exact rational arithmetic].** v1 of this document flagged an unexplained identity:
the certificate's degree-4 penalty line `R_4(k) = (129−k)/3` equals `128/3` at `k = 1`,
the Haar-to-Kerdock degree-4 defect ratio is also `128/3`, and no argument connected an
adjusted-score ratio to a ratio of design defects. The settling check named there — an
exact-rational `A_4(k)` sweep over `k = 1 … 129` — has since been written and run
(`papers/a4_ratio_settling_check.py`, committed `89d44cb`). It closes the item, and what
it returns is stronger than what was asked for.

For a union of `k` orthonormal frames in `R^256`, antipodally doubled, with `Q_4` the
degree-4 Gegenbauer normalized to `Q_4(1) = 1`, and with every cross-block inner product
equal to `±1/16` in the MUB case:

```
Q_4(0) = 1/21845                Q_4(1/16) = −65/2105344            (exact)
A_4,haar(k) = [1 + 255·Q_4(0)] / (256 k)
A_4,mub(k)  = A_4,haar(k) + (k−1)·Q_4(1/16)/k  =  |Q_4(1/16)| · (129 − k) / k
```

The closed form on the right follows in three lines: `k·A_4,mub(k)` is affine in `k` with
slope `Q_4(1/16)`, so its root is `1 − A_4,haar(1)/Q_4(1/16) = 1 + 128 = 129`
**[D, re-derived by hand this session and independently in `Fraction` arithmetic]**.

**One asymmetry between the two lines, stated before the consequences that rest on it.**
The MUB line is exact per instance: every cross-block inner product *is* `±1/16`, so
`A_4,mub(k)` is a property of the design and not of a draw. The Haar line is an
expectation over the frame draw — cross-frame zonal terms have mean zero rather than
being identically zero, which is what makes `A_4,haar` the iid-strength reference in the
first place. Consequences 1 and 3 below are therefore per-instance exact; consequence 2
is an exact identity between the *expected* iid defect and the exact design defect, which
is the sense in which the carrier discovery's `42.67x` was always meant and measured.

Three consequences, all exact rather than numerical, in the two senses just
distinguished:

1. **`A_4,mub(129) = 0` identically.** The completion annihilates degree 4 as an
   algebraic fact. It had been a measured zero; it is now a proved one.
2. **`A_4,haar(126) / A_4,mub(126) = 128/3` exactly.** The `42.67x` of the carrier
   discovery is a rational identity, not a seven-digit near-match — which also disposes
   of the obvious rival reply, that a rounded `3.136387e-05` was compared against `128/3`
   and the agreement called striking.
3. **The certificate's payoff line is the design defect, scaled by compute.** For every
   `k = 1 … 129`, `A_4,mub(k) / A_4,mub(126) = R_4(k) · 126/k` holds **identically** in
   exact rationals **[O, all 129 values checked this session; zero failures]**.
   Equivalently `R_4(k) = (k/126) · A_4,mub(k) / A_4,mub(126)`, where `k/126` is exactly
   the "compute proportional to block count" premise Theorems 3–5 are stated under. At
   `k = 1` a single block has no cross-block terms, so `A_4,mub(1) = A_4,haar(1) =
   126·A_4,haar(126)`; the compute factor cancels the `1/k` scaling of the iid part; and
   `R_4(1)` collapses to `A_4,haar(126)/A_4,mub(126) = 128/3`. That is the connecting
   argument. The two quantities were never two objects.

**Four independent anchors, none of them fitted.** `A_4,haar(126) = 3.136387499227966e-5`
against the source-read `3.136387e-05` of the discovery above; `A_4,mub(126) =
7.350908201315546e-7` against the design document's exact-rational census;
`A_4,mub(128) = 2.4120167535566633e-7` against m191's measured value; and
`A_4,mub(1) = 3.951848e-3` against the `base1` design defect `0.0039518` measured by the
k32 instrument of §3 **[O, `cells/k32_base_sensitivity_v3/report.json`,
`metrics.second_signal_design_defects.base1.A4`]**. Four measurements taken for four
unrelated purposes land on one closed form with no fitted parameters in it — `Q_4(0)` and
`Q_4(1/16)` are both forced by the dimension and the design's inner-product set.

**What the theorem buys, and what it does not.** It settles the design-defect side of the
completion question as mathematics, and it confirms that the sealed cell's exactness
assertion is correct rather than approximate (`runner_fc129.py` docstring, "a factor of
exactly 128/3"; `spec.json` second-signal (a), which makes a departure a protocol kill
rather than a result). It does **not** settle the MSE gain. `A_4` is a property of the
design; the gain is a property of how much of a given carrier's estimator error lives at
degree 4, and that is precisely the quantity the amendment below says is unreconciled and
the 129 cell measures. Promoting the theorem into a gain prediction is the one move this
section refuses to make.

**The pre-registered law [H1, filed 2026-08-19 ~01:0x UTC, BEFORE the cell runs; its
A_4 leg is now [D] closed form by the theorem above, its gain leg still unmeasured].**
The Puffi-19% / ely2sh-0.9% / ours-0.45% discrepancy is not a contradiction. It is
two regimes of one quantitative law:

```
completion gain  ~  (degree-4 error share at iid strength) × (1 − A4_after / A4_before)
```

Kerdock-regime carriers (`A_4 ≈ 7.35e-7`) see sub-1% gains — that is ely2sh, and
that is our own m81/s11 breakeven. iid-regime carriers (`A_4 ≈ 3.14e-5`, 42.7x) see
19%-class gains — that is Puffi. Our deployed carrier is in the iid regime.

**The prediction, its amendment, and the falsifier.** On our carrier, the 126-Haar →
129-MUB swap yields an MSE ratio in the band **[0.78, 0.93]** — 19%-class — and **not**
the 0.995-class the Kerdock-regime numbers implied. The band was pre-registered at
`[0.78, 0.86]` at ~01:0x UTC and **widened to `[0.78, 0.93]` at ~02:1x UTC, still before
the cell ran**, when the regime audit found three unreconciled quantifications of the
Kerdock-versus-iid degree-4 suppression: m191 measured degree-4 error at 0.098–0.107 of
iid (~9.1x); `m81_full129_pareto` records `A_4 = 0.047` (~21x); and the A_4 law uses the
defect ratio `128/3` (42.7x), now exact by the theorem above. Those may measure three
different objects — a design defect, an MSE suppression, and a per-block `A_4` — and
which of them governs MSE gain sets the magnitude. What survives all three is the
direction: our carrier sits in the strong-gain regime. This document prints the amended
band, and the reconciliation is required reading for the verdict when the cell lands
**[R, channel 2026-08-19 ~02:1x UTC, committed as `0486668`, whose message reads "band
widened honestly"]**.

**A corpus inconsistency, recorded rather than smoothed over [O, read this session].**
The channel entry filing that amendment ends "The seal-time spec carries this amendment
verbatim." It does not:
`experiments/frame_completion_129/spec.json` still carries the 0.78-to-0.86 band and no
amendment text. The cell is sealed but unrun, so the repair is free and belongs before
predeclaration; until it lands, the amended band lives in the channel entry and the spec
is behind it. We print the wider band because it is the one that was filed with a
timestamp before any data existed, which is the only property that makes a
pre-registration worth anything.

A second arm (H2) adds Kerdock-126
as a third condition from the shipped `kerdock_phases.npz`, and predicts that most
of the gain comes from design *quality* (Haar → structured), with the 126→129
completion increment small. That would reconcile the dual-witness certificate —
126 optimal *inside* the structured game — with Puffi's measurement, by locating the
gain in **entering** the game rather than in completing it. **Falsifier, filed:** an
MSE ratio above 0.95 on our carrier kills H1 and reopens the discrepancy.

**This is a prediction and not a result.** The cell is designed, its margin is 5% set
by measured bootstrap power, its metric is studentized so that noise drives
INCONCLUSIVE and cannot counterfeit a powered null, MSE provenance is verified at
`scoring.py:851` of the installed WHestBench 0.14.0 harness (a package file, not a
path in this repository), the identity frame is placed last to avoid a pilot confound,
radial-conditioning transfer is proven exact, and five ledger numeric collisions were
found and avoided proactively. Memory is **not** discharged: the completion adds
2.25 MiB, above m81's fatal margin, and is routed to a separate build stage on PASS.
Harness runs are held behind the fold measurement so that CPU contention does not
pollute either run's residual seconds. Nothing here is a score claim.

**The tension is the point.** The certificate says 126 is optimal inside the Kerdock
game. The carrier discovery says the deployed estimator is not playing that game.
One powered run adjudicates between a theorem and a measurement in open
disagreement — and it is write-up material whichever way it lands, because a theorem
that survives contact with a measurement outside its stated scope, and a theorem
whose scope statement turns out to have been the load-bearing sentence, are both
results.

---

### 12. Sidebar — independent corroborations from the public record

Every number in this sidebar is **[R]**: reported by other participants, read from
the public forum, never re-run by us. They are here because four of them corroborate
a load-bearing claim of ours from outside our own machinery, which is the only kind
of corroboration that carries weight.

- **kaileh57 — the degree-≥6 ceiling, certified.** An Arb-certified linear program
  over the same design family reports `R² = 0.2351%` at 4.05% cost for degree-≥6
  controls, and degree-≤5 controls pathwise **zero**. That is an independent
  confirmation of our §5–§6 ceiling by a different method: we measured
  0.19–0.63% own-axis capture; their LP bounds the achievable `R²` at the same
  order.
- **trim_qewas — the flat-budget theorem, organizer-reproduced.** Dropping to the
  compute floor is exactly neutral on adjusted score. This validates our C/B
  posture: compute-side wins are real score wins only above the floor, and our entire
  compute programme is priced against that.
- **qi_zhang5 — control-variate gains collapse under QMC.** Measured CV gain falls
  from 1.42x to 1.04x once the base sampler is quasi-Monte-Carlo. That is our
  §2 law in a different family: a control that pays against iid noise has almost
  nothing left to subtract once the base design already removes the structured part.
- **omer_kiraz — antithetic mirrors on lattices make it worse.** A direct external
  replication of a kill class we recorded internally, on a design family we did not
  test.
- **Withdrawn from this list:** "butterbaugh's 340x closure gap." That is our own
  handle and our own post at Discourse topic 18147 (§2). It is a second *statement*
  of our result, not a second *witness* to it.

**Standing position, stated because a contribution document that hides it is not
credible.** On publicly declared adjusted scores we are approximately 7th, not
leading: ednacob 1.845e-8, Puffi 9.10e-8, ely2sh 1.196e-7, pranay212 1.23e-7,
mliston 1.334e-7, baltsat 1.439e-7, SOX 1.551e-7, us 1.83e-7 **[R, sweep of 34
write-ups, 2026-08-18 ~16:0x UTC]**. Our `1.83e-7` carries a lineage qualifier like
everything else here: it is submission #326094, which is the **`kerdock_v3`** lineage,
while the compute programme of §9–§10 is priced and measured on **`row_blocked`**, whose
local adjusted score is `2.1218e-7` against `kerdock_v3`'s local `1.619e-7` **[R,
`core/KILL_CONTEXT_INDEX_20260819.md`, ledger ids `row_blocked_winograd_production` and
`t4_kerdock_v3_descriptive_rescore`]**. Local and hosted scores are different
instruments and are not comparable across that boundary, so no regression should be read
into the pair; what the pair does say is that the host fork of §0 is unresolved inside
our own standing line. The structural read is that every declared gain
ahead of us is prediction-preserving arithmetic — a compute multiplier — rather than
accuracy. That is consistent with this document's thesis, and it is also the reading
most favourable to us, which is why we state it as a reading rather than a finding.
One anomaly is on the record: ednacob's 1.845e-8 sits below what kaileh57's
Arb-certified LP permits any fixed nonnegative rule at that support, so it is either
genuinely non-fixed or an accounting artifact. We do not resolve it and we do not
build on it.

---

### 13. Pre-registered predictions, with their filed falsifiers

Neither of these is a result. Both were filed before the measurement that would
settle them, both name the carrier lineage they are filed against, and P2's band was
amended once — before its cell ran — in the direction that makes it harder to claim a
hit. The amendment is in the table, not in a footnote.

| # | prediction | filed | falsifier |
|---|---|---|---|
| P1 | Public100 re-measurement of the folded floor **on the deployed `row_blocked` (Haar) carrier** lands at `C ∈ [150B, 165B]`, score `∈ [1.45e-7, 1.53e-7]`; equivalently `C_post = 126.7e9 + 18.815e9·m` with measured `m ∈ [1.86, 2.64]` (committed evidence alone: `[1.86, 2.26]`) | 2026-08-18 ~18:2x UTC (judge), ~19:0x UTC (revised law) | `C ≥ 200B` (i.e. `m ≥ 3.896`) kills the thesis; wall multiplier `≥ 7.58` under a surviving λ holds deployment; per-net `\|MSE ratio − 1\| > 5e-4` or aggregate `> 1e-4` breaks exactness |
| P2 | The 126-Haar → 129-MUB swap on the deployed `row_blocked` (Haar) carrier yields MSE ratio in **`[0.78, 0.93]`** — filed at `[0.78, 0.86]` and **widened before the run** when three quantifications of the degree-4 suppression (m191 ~9.1x, `m81_full129_pareto` ~21x, the exact defect ratio `128/3` = 42.7x) proved unreconciled; the Kerdock-126 third arm shows most of the gain in Haar→structured, with the 126→129 increment small | 2026-08-19 ~01:0x UTC, amended ~02:1x UTC (commit `0486668`, "band widened honestly") | MSE ratio above `0.95` on our carrier kills H1 and reopens the 20x discrepancy — unchanged by the amendment |

The A_4 leg that puts our carrier in the strong-gain regime is no longer a modelling
assumption: §11 proves it in closed form, and the theorem holds for the design defect on
every block count from 1 to 129. What the amendment concerns is only the **magnitude** of
the MSE gain that defect buys, which no theorem in this corpus fixes and the cell
measures. The sealed spec still carries the pre-amendment band, which §11 records as an
open repair.

A third item is designed and unrun, and is listed so that it is not mistaken for a
finding later: the mub129 **powered rerun**. The existing 126→129 kill on our own
carrier had 5% power against a 0.45% effect, and sixteen fresh networks returned a
score ratio of `1.00087` at `p = 0.92` **[R]**. That is an underpowered null, not a
measured zero, and P2's cell is the powered instrument that replaces it.

---

### 14. What this document does not claim

- **No score.** Nothing here has been measured on the private suite, and the two
  live items in §13 have not been measured at all.
- **No minimax optimality of the estimator.** The dual-witness certificate is a
  minimax statement about *block mixtures inside one game*. It is not a lower bound
  on estimation of this target, and the S17 floor remains what it was — a gated
  lower-bound attempt, indistinguishable from the champion at the resolution
  available (`gm_s17_reuse`: distinct-direction ratio 1.0044, CI [0.8450, 1.1639]) —
  which is item 5 of §3e in the Phase-1 v13 long draft
  (`core/PHASE1_WRITEUP_DRAFT_20260808.md`) and erratum E5 of the filed short form.
- **No universal information floor.** §1's law is supported by two independent
  campaigns, Phase-1's twelve predeclared kills, and the Phase-2 cells above. It is
  not a theorem, no method space was enumerated, and a shared blind spot would
  produce the same evidence.
- **No claim that the accuracy frontier cannot move.** What is measured is that
  every mechanism *this campaign constructed* died, that the two survivor classes
  (subtract-side exact structure, and compute) behave as the law predicts, and that
  the doors that remain have named keys.
- **No transfer of the k32 or DGFL kills outside their measured regimes.** Both are
  regime-indexed per §1, and the axis changes that would make them topical are
  recorded on their records.
- **No carrier-free compute claim.** The suite floor of §9 and the splice pair of §4
  are priced on a phased-Hadamard (Kerdock) carrier and our own shipped code disables
  the CReLU split on the deployed Haar lineage; the per-call floor of §9 is
  carrier-free; the m-curve of §10 is measured on the deployed Haar carrier with an
  analytical component that inherits the Kerdock question. The transfer between the two
  lineages is bounded by a committed A/B/C partition at 1.55% non-transferring and is
  **not** itself a measurement in this document. Under the worst reading of that gap the
  §10 conclusion is unchanged, which is stated in §10 with the arithmetic.
- **No claim that the A_4 theorem predicts an MSE gain.** §11 proves a design-defect
  law. The step from a defect to a score is exactly what P2 measures, and the three
  unreconciled suppression quantifications are why its band was widened rather than
  narrowed.
- **The exact-control spine's closure is f64-specific.** The mixed-precision exit was
  closed by argument, not measurement (§7, [GAP]).

---

### 15. Reproduction and provenance

The estimator source, predeclarations, kill gates, cells, adversarial audits, frozen
manifests, and the 276-record fold ledger are in the campaign branch
`agent/compression-survivor-corpus` of `github.com/gmrmk/recursive-estimator-folding`.
The repository was made public on 2026-08-17 at ~21:25 UTC. Phase-1's filing pins
commit `f225be4e4e4872dc2bef06711525cf00e73a332b`; readers should use a pinned path
rather than the repository root, whose default branch is a 2026-08-06 snapshot
carrying 43 ledger records rather than 276.

Independently re-executed while writing this draft **[O, this session]**:

```
python corpus/whestbench/headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py
    -> total: 303096592   (strategy winograd_l6_inplaceleaf; direct 535822336)
python corpus/whestbench/headroom/compute_lineage/suite_00_incumbent.py
    -> uniform_t7_suite 152760682368
python corpus/whestbench/headroom/compute_lineage/suite_19_the_odd_channels_scalar_is_already_on_layer_ones_matrix.py
    -> TOTAL (per net) 144867083088
python corpus/whestbench/papers/a4_ratio_settling_check.py
    -> Q4(0) = 1/21845 ; Q4(1/16) = -65/2105344 ; ratio exact = 128/3 ; IDENTICAL: True
    -> A4_mub(129) = 0.000000000e+00   (exact zero in Fraction arithmetic)
```

The A_4 theorem of §11 was additionally re-derived twice against that script: by hand
from the affine form of `k·A_4,mub(k)`, and by an independent `Fraction` sweep over all
`k = 1 … 129` checking `A_4,mub(k)/A_4,mub(126) = R_4(k)·126/k`, which returned zero
failures **[O, this session]**.

Cell artifacts read directly: `cells/{ajpre1_w0_wi_precondition,
clone_l2fringe_flop_recompute_v2, k32_base_sensitivity_v1, k32_base_sensitivity_v3,
m207_reachability_v1, m207b_semantics_v1, deg6_own_axis_zonal_capture_v1,
deg_ladder_own_axis_capture_v2}/{predeclaration,report,verdict}.json`, plus
`experiments/fold_floor_splice/full.json` and
`headroom/FWHT_SPLICE_STAGED_20260818.md`.

**The harness is part of the contribution.** `scripts/fold_search.py` (21 contract
tests) enforces the sequence: predeclare with a schema, four-axis confidence, an
evidence firewall, and kill-finality checked both by id and by numeric token →
one-shot gate consumed before execution → sealed run with frozen-input rehash, a
fail-closed wall budget, and malformed metrics treated as a canonical kill →
mechanical verdict where the gray zone can never promote → append-only ledger write.
`scripts/fold_waves.py` (9 further tests) runs topological waves with cycle,
unknown-dependency, and same-wave write-overlap refusal, serialized ledger verdicts,
and a graph export of the live search DAG. Terminal-role cells structurally cannot
reach the ledger. Memory-cap enforcement is a declared **[GAP]** with a named upgrade
path (wire the clone's job-object wrapper as runner argv).

The harness earned its keep three times in the window this document covers: it
protocol-killed `k32_base_sensitivity_v1` on a metric-name mismatch, caught
`v2` as a bit-identical deterministic rerun carrying no independent weight and gained
a structural seed-agreement check as a result, and refused to mint a floor
certificate from twelve consecutive API failures. Two of the three catches were
against our own work, which is the only evidence that a gate is real.

**LLM involvement.** Unchanged from §5 of the filed Phase-1 short form (§4b of the
v13 long draft) and restated because it is unusual
enough that silence would misrepresent it: this campaign was conducted end to end by
large language models operating as agents under human direction. The estimator, the
experiments, the cells, the ladders, the certificates, this document, and the six
companion papers were written by LLMs. Every verdict in this document was produced
by a predeclared gate sealed in git before the value existed, every cell carries a
report hash, and the corrections in §2, §3, §5, §6, and §10 were found by our own
machinery pointed at ourselves while assembling this draft.

**What the hostile review changed, listed so the diff is not silent.** v1 of this
document was returned NEEDS_WORK. Thirteen defects were repaired in place by the
reviewer — numeric slips, dangling cross-references to Phase-1 sections that exist only
in the unfiled v13 long draft, an agreement claim in §5 stated one level above its
per-seed support, and the provenance mislabel on §10's residual band. Four survived for
this editorial round and are closed here: the missing carrier qualifiers on §4, §9 and
§10 (the document banked a saving its own shipped code disables on the deployed
lineage); the missing denominator behind §4's three percentages; the pre-registration
amendment of §11 and §13, which v1 omitted and which is the one item that would have
read as bad faith rather than as error; and the absent lineage statements on the eight
cells, which is the asymmetry of applying §1's own doctrine to competitors and not to
ourselves. Two further inconsistencies were found while making those repairs and are
recorded at their sites rather than fixed quietly: the sealed 129 spec disagrees with the
channel entry that claims it carries the amendment verbatim (§11), and our declared
standing line reports a `kerdock_v3` submission while the compute programme is measured
on `row_blocked` (§12).
