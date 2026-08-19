# Phase-2 Algorithmic Contribution writeup — draft v1.2

Status: DRAFT v1.2, 2026-08-19. **Theorem integration and governance disposition.**
This revision does three things and changes the document's centre of mass while doing
them.

**What v1.2 adds.** (i) The ultramath slate's theorems, which close the design axis:
the degree-6 dyadic tax `A_l,mub(k)/A_l,haar(k) = 1 + (k−1)·X_l/S_l` with
`X_4/S_4 = −1/128` and `X_6/S_6 = +1/4096` exactly — of which §11's `A_4` theorem is
the degree-4 corollary — the unconditional carrier-optimality theorem, the Delsarte
floor, and a fourth external anchor at the k32 instrument that reproduces both closed
forms to five digits through an unrelated code path (§11b). (ii) The governance
disposition of the fold lineage: the round-4 fix completed, the gate retired green,
and the owner's re-plan ruling then **halted** the lineage under the three-red-loops
pipeline law (§10). Prediction P1 of §13 was **withdrawn by governance before
measurement** — never run, therefore never falsified, and recorded as such rather than
erased. (iii) The cross-references that the repricing swarm's artifacts now make
mandatory: the local↔hosted divergence map into §12, the `row_blocked` frozen-scalars
disclosure into §15, and the policy-v2 supersession of §10's projected designation
numbers.

**The centre of mass has moved, and this front matter moves with it.** v1.1 led with a
compute programme whose largest item was a pre-registered prediction. That prediction
no longer exists. What leads now is what is **proved and measured**: the exact `A_4`
and `A_6` theory with its four independent anchors, the unconditional carrier-optimality
theorem, the carrier-free per-call floor `303,096,592`, the metered operator-level FLOP
win, and the kill-ledger methodology that produced all of it. One prediction remains
live — P2, the 129-frame completion cell — and it is **running** as this draft is
written; §13 says so in those words rather than describing it as queued.

**Status of the v1.1 record, retained verbatim below because corrections here are
append-only.**

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

**Correction to the paragraph above [v1.2].** One of those two items no longer exists
as a live prediction. The Public100 re-measurement of the folded compute floor —
prediction P1 of §13 — was **withdrawn by governance before measurement** on
2026-08-19 (owner re-plan ruling, channel `2026-08-19T08:41:38Z`). It was never run and
is therefore **never falsified**; it is neither a result nor a failure, and §10 and §13
state that in those words. The 129-frame completion cell (P2) stands as the one live
pre-registered prediction and is running. The final sentence is unchanged and is the
one that matters: **nothing in this document claims a score.**

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

**What to read first, and why the order changed [v1.2].** A reader with limited time
should read the **proved and measured** spine, which is now the document's weight:

1. **§11b — the exact `A_4`/`A_6` design theory.** Two closed forms in exact rational
   arithmetic, four independent anchors, and one of those anchors is a cell built for
   an unrelated purpose whose measured value reproduces the closed form to all five of
   its printed digits. No fitted parameter appears anywhere in it.
2. **§11b — the carrier-optimality theorem.** Mutual unbiasedness is the unique
   degree-4 minimizer over every union of orthonormal bases, unconditionally, and the
   global minimizer of the weighted objective under a margin measured at 28x.
3. **§9 — the carrier-free per-call floor `303,096,592`**, re-executed this session,
   proved to be a floor by three adjudicated dry tiers, and the one large compute
   number in this document that carries no carrier qualifier at all.
4. **§1–§7 — the kill-ledger methodology**: twelve predeclared kills, the gates that
   protocol-killed our own cells twice, and the corollary of §3 that pre-kills an
   entire competitor family.

Everything above is closed. What is **open** is confined to one place: §13's prediction
P2, the 129-frame completion cell, which is running as this draft is written. §13's
other prediction, P1, was withdrawn by governance before it ran (§10). This ordering is
a change from v1.1, which led with the compute programme and its predictions; the
evidence moved, so the emphasis moved with it.

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

**Both payoff lines are design defects, not just the degree-4 one [D, v1.2; exact
`Fraction` sweep over `k = 1 … 129`, zero failures, this session].** The paragraph
above records that §11 turned `R_4` into the degree-4 defect scaled by compute. The
degree-6 line is the same object at the next degree, and the check is the same one:

```
R_6(k) = (k/126) · A_6,mub(k) / A_6,mub(126) = (4095 + k)/4221     for every k = 1 … 129
```

It follows in one line from the degree-6 dyadic tax of §11b, `X_6/S_6 = +1/4096`:
`k·A_6,mub(k) = S_6 + (k−1)X_6`, so the ratio is `[1+(k−1)/4096] / [1+125/4096] =
(4095+k)/4221`, which is the certificate's printed line. **Neither of the certificate's
two payoff lines was ever a payoff convention.** Both are the per-degree design defects
of the carrier, and the convention supplies only the compute factor `k/126` and the
normalization at `k = 126`. The opposite slopes that make the minimax value 1 are the
opposite signs of `X_4/S_4` and `X_6/S_6`, and the 32:1 ratio of those slopes (§11b) is
why degree 4 dominates the trade everywhere except in the last three blocks.

**The certificate's own margin is the degree-6 tax, read in its own units [D, this
session].** `R_6(129) = 1408/1407` exactly — the same `1408/1407`, `0.0711%`, that the
dependency paragraph above computes as the gap between the break-even ratio
`2881/2816` and the cheapest completion ratio `129/126`. The certificate's tightest
number and the degree-6 penalty for completing the design are one quantity reached from
two directions. Stated carefully, because the two nearby ratios are different objects:
`1408/1407` is the completion's degree-6 penalty **in the payoff normalization**,
relative to `k = 126` and carrying the compute factor, whereas the `33/32` of §11b is
the completed design's degree-6 defect against the **iid reference at the same block
count**. Both are exact; they are not the same ratio and neither may be substituted for
the other.

**Correction to the framing of the paragraph above, found by the audit pass on this
draft [v1.2].** Only one half of it is new. The equality of the certificate's margin
with its own degree-6 line was already established, executed and stored by the
certificate itself: `dual_witness_certificate.json` carries
`game.worst_case_margin = 1408/1407`, `game.degree6_penalty_above_126["129"] =
1408/1407`, and `game.worst_case_ratio_by_k["129"] = {1408/1407, binding_degree 6}`,
and the check list contains one named **"Worst-case margin equals the degree-6 penalty
1408/1407 exactly"**; the companion markdown prints the same equality in its
worst-case-by-`k` table and in its margin line **[O, both files read this session]**.
What is new here is the other side of the identity — that `R_6` *is* the degree-6
design defect scaled by compute — and that is new because the certificate contains no
`A_l` quantity at any degree: the symbols `A_4` and `A_6` and the constant `4096` occur
zero times in either file, and the only `A6` in the markdown is an objection label in
its own §7 **[O, grepped this session]**. So the margin's equality with `R_6(129)` is
the certificate's own result and is credited to it; the margin's *reading* as the
completion's degree-6 design tax is this integration's. The distinction matters for the
same reason §2's withdrawal of "butterbaugh's 340x" mattered: a result of ours restated
in new words is not a second result.

**What this does and does not do to §5.1's boundary.** It does not widen it. The
narrowed claim above still speaks only about mixtures over the 129 canonical blocks
under the stated payoff. What §11b's carrier-optimality theorem adds — separately, and
by a different argument — is an unconditional statement over the strictly larger class
of **all unions of orthonormal bases**, which is the class the certificate explicitly
declined to bound. The two results are complementary rather than nested, and §11b
states its own boundary.

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

#### 10b. Governance disposition of the fold lineage [v1.2] — the gate went green and the lineage halted anyway

Everything above this subsection was written while the fold was a live candidate whose
Public100 measurement was pending. It is not one any more. Both halves of that sentence
are recorded here, in order, because only one of them is the kind of ending a document
like this usually reports.

**The round-4 fix completed, and the gate retired green [R, channel
`2026-08-19T08:41:38Z`, workflow `wf_27e7a983-7fa`].** The two blocking findings from
round 3 were closed: `D-A3a` (cost-model static-versus-metered divergence on the
fallback branch) was priced — fallback total = frozen bill + `m·n`, with 42 shapes
metered, **0 delta and 0 above direct** — and `D-A3b` (selected-above-direct across
18,290 swept shapes) was closed structurally, the plain product now seeding the search
and the unreachable `direct_owned` class removed. The load-bearing verification result
is the negative one: **production bills are unchanged byte-for-byte, with 35 operator
products traced and 0 reroutes at production geometry.** The defect was real and
sweep-visible, and it never touched a shipped product. Parity is unchanged at worst
Frobenius `1.462611e-05` against a `2e-5` bar. The verifier returned
**`APPROVED_PENDING_CEILING`**; the ceiling item `D-A6` was discharged by the owner's
**1-GiB memory ruling** of `2026-08-19T06:12:13Z` (channel entry plus the
`FOLD_FLOOR_SPLICE_PRODUCTION_GATE.md` addendum), against a measured peak of 615.87 MiB
median and 616.27 MiB max with the instrument validated at +0.89% on the incumbent's
own receipt **[R, channel `2026-08-19T08:41:38Z`; the peak figures are round-4's, and
they are not the pair the ruling itself was written against — the `06:12:13Z` entry and
the gate addendum both record 616.02 MiB median / 616.95 MiB max, the round-3
measurement. The two readings differ by 0.1–0.7 MiB, both sit at roughly 60% of the
1-GiB bar, and the discharge does not turn on which is used; the citation is corrected
here rather than the number]**. The remaining finding `D-M1` is administrative: the gate manifest still
names the round-3 `depth6_winograd` bytes `6ee49e57…` against on-disk round-4 bytes
`88f8b787…`, and a re-freeze is required only if an archive is ever cut. **The fold
therefore retires GATE-GREEN.**

**And then the owner halted the lineage [R, same channel entry, ruling 2].** Under the
three-red-loops pipeline law the ruling was `RE-PLAN NOW`: the fold lineage **HALTS**,
the designation pivots to unfolded `kerdock_v3` against incumbent `row_blocked`, and
the compute effort moves to this manuscript. The measurement M1 — the fold Public100 —
is **CANCELLED**.

**What informed the halt, stated as arithmetic rather than as judgement.** The
ultrareview merge's rank-1 finding recomputed the fold's **paired** effective-`C` ratio
from `full.json` at `0.83879 / 0.84470`, against the `0.739` the designation policy had
been pricing **[R, channel `2026-08-19T07:07:56Z`, "CONFIRMED by merge recomputation";
this ratio is a paired statistic and is not the `effective_C_ratio` 0.806/0.837 quoted
from the same file above, which is the depth-4 arm's unpaired pair]**. Folding the
deployed carrier at that ratio projects
`2.1218e-7 × 0.8388 = 1.780e-7` **[D, recomputed this session: 1.77977e-7]**, against
the unfolded `kerdock_v3` score of `1.6190838e-7` that the campaign **already holds**
**[O, `headroom/fold_ledger.json` id `t4_kerdock_v3_descriptive_rescore`, recomputed
from `kerdock_v3_official100.json` in the divergence map to 1.4e-11 relative. Cited by
stable id per §0's own erratum: the divergence map cites it as "record 183", and
counting the 276-record ledger the way §0 counts it puts `t4_kerdock_v3_descriptive_rescore`
at position 184, with 183 landing on the unrelated `t3_fold3_deterministic_cap`
**[O, ledger read this session]**. The value is in the record either way; the pointer
is what drifted, exactly as §0 warns]**. The folded
route is therefore **9.9% worse** than the unfolded artifact already in hand
**[D, recomputed this session: 1.780/1.6190838 = 1.0994]**. A lineage that passes its
own gate and still loses to what you already have is a lineage that has finished, and
that is the reading the ruling took. The `[R*]` caveat of the divergence map applies to
the `0.8388` as it does to every `full.json`-derived number — it is pending the
round-4 bill repair re-run — and the direction of the finding does not depend on the
repair, because the gap to be closed is 9.9% and the repair moved production bills by
zero.

**Prediction P1's disposition, stated exactly and not as a failure.** Prediction P1 of
§13 — the Public100 re-measurement of the folded compute floor on the deployed
`row_blocked` carrier — is **WITHDRAWN BY GOVERNANCE BEFORE MEASUREMENT**. It was
**never run** and is therefore **never falsified**. It is not a failed prediction, it is
not a quiet deletion, and it is not evidence about the folded route's compute either
way. A pre-registration that is cancelled before its measurement carries exactly one
piece of information — that it was cancelled, by whom, and when — and this document
records that rather than either claiming the prediction or erasing it. §13 carries the
same disposition in its table.

**What survives the halt as contribution artifacts.** Four things, none of which
depended on M1:

1. **The metered operator-level FLOP win**, measured at the operator rather than
   projected at the estimator: **`0.6524`** at `4096 × 256 × 256` and **`0.7145`** at
   `256 × 256 × 256` **[R, channel `2026-08-19T08:41:38Z`]**. This is a statement about
   a matmul schedule and it is untouched by the estimator-level verdict.
2. **The carrier-free per-call floor `303,096,592`** of §9, re-executed this session,
   which was never a fold quantity at all.
3. **The m-curve methodology critique** — the scale-mix lesson, below.
4. **The `D1` aliasing find and fix** as an engineering-rigor exhibit, below.

**The scale-mix lesson, which is a critique of this section's own arithmetic [R,
channel `2026-08-19T07:07:56Z`; recorded here rather than repaired].** The merge found
that the headline this section is built on **mixed two scales**: the `126.7e9`
analytical anchor is a **local-scale** quantity, while `222.405B` is the **record
max-`C` net** from the incumbent's Public100 receipt. Dividing one by the other is not
the like-for-like comparison the `m*` derivation presents it as, and the `0.739`
that the designation policy carried is where that mix surfaced as a decision number.
The four independent derivations in the list above agreed with each other because
**they all inherited the same denominator**, which is precisely the failure mode that
independent-derivation agreement is supposed to exclude and does not: four routes to
one number are one signal when they share an input. We do not repair `m* = 5.09` here,
because repairing it would require the measurement that governance cancelled. We record
that **every score projection in this section is conditioned on a denominator the merge
has since called mis-scaled**, and that the conclusion those projections supported —
that `m` sits far below the falsifier line — is no longer load-bearing for anything,
since the route it defended is halted. The transferable lesson is the one worth
keeping: *an anchor and a receipt are not interchangeable just because they are
denominated in the same units, and agreement among derivations that share a
denominator measures the derivations, not the number.*

**Supersession of this section's designation numbers [R, channel
`2026-08-19T08:41:38Z`, repricing swarm `wf_b325115d-acd`, verifier APPROVED].** The
projected scores quoted in the four derivations above — the graph adjudicator's
`C = 153.5B` / `1.4640e-7`, the judge pre-registration's `C ≈ 156.5B` / `1.493e-7` and
its band, and the TRM engine's ratios — are **superseded** as designation inputs by
`core/DESIGNATION_POLICY_20260819.md` **v2**, which reprices on the measured basis
(v1 is retained byte-intact under a supersession banner, 907 lines), and by
`core/designation_repricing.py`, which parameterizes `(lambda_mode, floor, B,
residual_constant, suite_size, host, C_ratio)` behind a 4-check selfcheck. The decision
number that replaced them is `r*` (fold + 129 against unfolded `kerdock_v3`) `=
0.8886 / 0.8823 / 0.8799` across bases. They are retained above as the record of what
was derived and pre-registered at the time, which is what a pre-registration is for;
they are not to be quoted forward as designation numbers.

**The `D1` aliasing find and fix, kept as an engineering-rigor exhibit [R, channel
`2026-08-19T06:12:13Z`, round-3 disposition `wf_d6440c2b-55a`].** Round 3 found an
aliasing defect at the operator and fixed it **with a discriminating regression
selfcheck that fails on the reverted build** — which is the property that separates a
regression test from a green checkmark, and the reason this is worth reporting after
the lineage it was found in has been halted. The same round restored the `D5` OFF-branch
to incumbent shape and re-priced the hoist at `7,438,002` FLOPs, gated `D6` buffer
retention, and purged stray bytecode. That last item produced a protocol finding of
general application: an **external process wrote `.pyc` into custody trees mid-run**,
so every agent running Python against a repository tree must use `-B` /
`PYTHONDONTWRITEBYTECODE=1`, and `verify_fold_floor.py` now hard-fails on stray
bytecode. Round 3's gate verdict was `REJECTED` and `measured = false` was **correctly
held** — the harness declined to measure behind a rejected gate, which is the same
fail-closed behaviour §9 reports on the suite ladder.

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

**Resolved, and the resolution observed rather than assumed [v1.2, O,
`experiments/frame_completion_129/spec.json` re-read at the close of this session].**
The repair landed under the owner's ruling 1 of `2026-08-19T08:41:38Z`, **before**
predeclaration and therefore inside the free window. The spec now carries the amended
`[0.78, 0.93]` band with the amendment text, the unsupported "12% of C" prose is gone
(zero occurrences), and the single surviving mention of `0.86` is the amendment's own
history — "the originally filed 0.78 to 0.86 band" — which is the correct way for a
widened pre-registration to record what it widened from. **The spec and the channel
entry now agree**, and the discrepancy recorded in the paragraph above is closed. The
paragraph stays because it is the record of a real finding at the time it was made, and
because a document that deletes its own caught errors gives a reader no way to judge how
well it catches them.

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

### 11b. Addendum to Artifact 10 [v1.2] — the design axis, closed by theorem

Source: `core/ULTRAMATH_SLATE_20260819.md` (five lanes × two rounds, synthesized
2026-08-19 08:18:59 UTC) and the channel entry of `2026-08-19T08:41:38Z`. **Every
load-bearing identity below was re-derived independently in this session** from the
Gegenbauer recurrence in exact `Fraction` arithmetic under `python -B`, in a scratchpad
script that shares no code with the slate's lanes and no code with
`papers/a4_ratio_settling_check.py`. Where a claim was *not* re-derived here it is
tagged `[R]` and says so.

**Provenance gap, named before the theorems that rest on it [GAP].** The slate's own
lane scripts (`lane1/`, `lane2/`, `lane3r2/`, `lane4r2/`, `lane5r2/`) live in a session
scratchpad and are **not committed to this repository**. The committed artifact for the
degree-4 case is `papers/a4_ratio_settling_check.py` (commit `89d44cb`), which covers
consequence 1–3 of §11 and nothing at degree 6. The settling check is to commit a
degree-6 companion script; until that lands, the degree-6 identities below rest on this
session's re-derivation plus the slate's five agreeing code paths, and not on a
committed artifact. This is the same debt class as §3's missing `F075_RESULTS.json`,
recorded the same way.

**The convention from §11 carries forward unchanged.** `A_l,mub(k)` is **exact per
instance** — every cross-block inner product *is* `±1/16`, so it is a property of the
design and not of a draw. `A_l,haar(k)` is an **expectation over the frame draw**:
cross-frame zonal terms have mean zero rather than being identically zero. Every ratio
below is therefore an exact design quantity over an expected iid reference, which is
the sense in which §11's `42.67x` was always meant and measured. No statement below
upgrades that.

#### The degree-6 dyadic tax — the master law of which §11's `A_4` theorem is a corollary

For a union of `k` orthonormal frames in `R^256`, antipodally doubled, with the MUB
cross-block inner products at `±1/16`:

```
A_l,mub(k) / A_l,haar(k)  =  1 + (k − 1) · X_l / S_l          (exact, every even l)

    S_l = A_l,haar(1) = [1 + 255·Q_l(0)] / 256      X_l = Q_l(1/16)

    X_4 / S_4 = − 1/128          X_6 / S_6 = + 1/4096          (both exact)
```

**[D, re-derived this session in exact `Fraction` arithmetic from the dimension-256
Gegenbauer recurrence: `Q_4(0) = 1/21845`, `Q_4(1/16) = −65/2105344`,
`Q_6(0) = −1/1131571`, `Q_6(1/16) = 16637/17449091072`. The first two reproduce the
values §11 already prints; the second two are new here.]**

The two signs are the whole design game. **Degree 4 is the gain and degree 6 is the
tax**, and they are dyadic rationals differing by exactly `2^5`:

| quantity | value | what it is |
|---|---:|---|
| `X_4/S_4` | `−1/128` | degree-4 slope: completion **removes** defect |
| `X_6/S_6` | `+1/4096` | degree-6 slope: completion **adds** defect |
| **gain/tax slope ratio** | **exactly `32`** | why degree 4 dominates the trade |
| `A_4,mub(126)/A_4,haar(126)` | `3/128` | the `128/3` of §11, inverted |
| `A_4,mub(129)/A_4,haar(129)` | `0` | §11's consequence 1, now a special case |
| `A_6,mub(126)/A_6,haar(126)` | `4221/4096` | Kerdock **3.0518% worse** than Haar at degree 6 |
| `A_6,mub(129)/A_6,haar(129)` | **`33/32`** | the tax at the completion, exactly |

**§11's `A_4` theorem is the degree-4 corollary.** Setting `l = 4` gives
`1 + (k−1)(−1/128)`, whose root is `k = 129` — which is §11's completion index, reached
there through the affine form of `k·A_4,mub(k)` and reached here as one instance of a
per-degree law. Setting `k = 126` gives `3/128`, whose reciprocal is the `128/3` that
v1 of this document flagged as an unexplained coincidence, v1.1 upgraded to a theorem,
and v1.2 now exhibits as one row of a table.

**The countervailing fact, stated plainly because it cuts against the completion.** At
degree 6 the structured family is **worse** than iid, by 3.05% at `k = 126` and by
exactly `33/32` at the completion. Completing the design does not improve the carrier
at every degree; it zeroes degree 4 and pays `1/32` at degree 6. Whether that trade is
net-positive is an MSE question about where a given carrier's error lives, which no
theorem here settles and which P2 measures — the same boundary §11 draws, drawn again
one degree up. The 129 cell's pre-registered band already brackets the net **[R,
channel `2026-08-19T08:41:38Z`]**.

#### The carrier-optimality theorem — unconditional, over a class the certificate declined to bound

**Claim [R for the absolute-monotonicity mechanism, D for the moment identity].** For
**any** union of orthonormal bases in `R^d`, the second moment of the inner product is
pinned: `E[t²] = 1/d` exactly, by Parseval on each frame **[D, one line: for an
orthonormal basis `{e_i}` scaled to fixed radius, `Σ_i (u·e_i)² = |u|²` is constant in
`u`, so averaging over the `d` directions of each frame gives `1/d` regardless of which
bases were chosen]**. The design freedom at degree `l` therefore collapses to a
**single moment**, `⟨Q_l⟩`. The rectifier arc-cosine kernel is absolutely monotone —
closed-form nonnegative coefficients, derived three independent ways in the slate — and
absolute monotonicity survives composition, so the depth-composed even kernel is convex
in the squared inner product. Jensen against the pinned Parseval constraint then places
the **flat cross-Gram at the exact minimum**, making mutual unbiasedness the **unique
degree-4 minimizer** over frame unions at every depth, with no energy-ratio hypothesis
**[R, `ULTRAMATH_SLATE_20260819.md` entries 5 and 6; lanes L2 K3/K4, L1 ATK1, L4 ATK5;
depth-32 numeric convexity, minimum second difference `+7.5e-10`]**.

**Where a condition does enter, and the size of its margin.** Global optimality on the
*weighted* objective — degree 4 and degree 6 together, with the degree-6 tax priced in
— holds **iff `E6/E4 < 19.71`**, against a measured implied ratio of `0.6975`
**[both figures R, channel `2026-08-19T08:41:38Z`; neither the threshold nor the energy
ratio was re-derived here, and neither figure is in the slate in this form — see the
disagreement recorded below]**. The margin is therefore **28x** **[D, the only part recomputed this session: 19.71/0.6975 = 28.26]**,
and the adversarial floor — computed on the assumption that *all* degree-≥6 energy sat
at degree 6 — still leaves **3.9x** **[R]**. A condition that survives its own worst
case by a factor of four is reported as a condition, with both numbers, rather than
dropped. It is also the one leg of §11b that is **not** exact rational arithmetic: it
depends on a measured energy ratio, and the settling check is the per-degree energy
table that entry 2 of the slate identifies as a zero-cost artifact read.

**The two sources disagree about whether this condition exists at all, and the
disagreement is recorded rather than resolved [O, both sources read this session].**
The slate does not carry `19.71` or `0.6975`. It carries the same threshold in exact
form as Lane 1's `w* = 178192/9039 = 19.7137`, and it files that threshold in its
*dropped* register — "arithmetic confirmed, theorem vacuous … Superseded by entry 5" —
on the grounds that a two-degree truncation is never a realizable absolutely monotone
kernel and that explicit realizable kernels with ratios up to `~2261` still have the
flat optimum. Its §0 backbone states the optimality result "with no energy-ratio
hypothesis", and its disagreement ledger records "Carrier optimality: **Lane 2 over
Lane 1** (unconditional theorem beats the vacuous threshold; Lane 1 broke its own 'iff'
and said so)". The channel entry, written 23 minutes later, states the condition as
live. We print the condition because it is the weaker of the two claims and because
carrying the channel's ruling is this integration's task, and we print the slate's
retirement because the slate adjudicated it and was the earlier, more detailed word on
that specific point. **Neither reading changes any conclusion**: the measured `0.6975`
sits below `19.71` and below `2261` alike. The settling check is one line — restate the
weighted objective against a realizable absolutely monotone kernel and see whether the
threshold binds at all. This is the same shape of disagreement as the Delsarte one
below, and it is recorded the same way.

**What this adds to §8.** The dual-witness certificate deliberately bounded only
mixtures over the 129 canonical MUB blocks and said so in its §5.1 boundary. This
theorem speaks about the strictly larger class of **all unions of orthonormal bases**,
which is the class the certificate declined to enter. It does not inherit the
certificate's payoff convention and it does not bound estimators outside the
frame-union class either — a carrier built from something other than orthonormal frames
is outside both results.

#### The Delsarte floor — nothing cheaper exists, and the completion is nearly tight

**Degree-6 exactness is out of budget by two orders of magnitude [R].** Achieving an
exact degree-6 design requires at least **2,861,696 directions**, which the channel
entry prices at **88.7x** the deployed carrier's direction count. And the completion is
close to the best that degree-4 exactness permits: the 129-block completion is a
**near-tight antipodal 4-design, sitting 0.389% above the absolute degree-4 floor**
**[R, channel `2026-08-19T08:41:38Z`]**. Nothing cheaper exists at any block count, and
the corollary for the campaign is that the degree-6 lane is closed on two independent
axes — the carrier route by this floor, and the control route by the measured
0.0019–0.0038 own-axis capture of §5–§6.

**A corpus inconsistency in this number, recorded rather than resolved [O, both
sources read this session].** The two sources disagree, and they disagree in a way that
is worth stating because a reader will otherwise hit it:
`ULTRAMATH_SLATE_20260819.md` §0 gives **2,861,952 points, "~44x the deployed count —
points-vs-lines corrected from the ~88x on file"**, and its entry 5 adjudicates
"Lane 4's degree-SIX points-vs-lines correction STANDS (~44x short, not ~88x)". The
channel entry, written 23 minutes later, gives **2,861,696 directions, 88.7x**. The
arithmetic says the disagreement is a **denominator convention plus 256 directions**:
`2,861,696 / 32,256 = 88.72` against the base direction count, while
`2,861,952 / 64,512 = 44.36` against the antipodally doubled point count — a factor of
exactly 2, which is the antipodal doubling **[D, both recomputed this session]**. The
two counts themselves differ by exactly 256, one frame. We print the channel's figure
because the task of this integration is to carry the channel's ruling, and we print the
slate's because the slate adjudicated the opposite convention and was the later word on
that specific point. **Neither reading changes any conclusion**: 44x and 88x are both
far outside a budget that would need to grow by more than an order of magnitude, and no
decision in this corpus turns on which. The settling check is one line of the Delsarte
LP restated in a single declared convention.

#### The k32 external anchor — a fourth anchor, from a cell built for something else

This is the strongest evidence in §11b and it costs nothing to check. The closed forms
above, evaluated at a **single frame** (`k = 1`, where there are no cross-block terms
and the MUB and Haar lines coincide), predict:

```
A_4,haar(1) = 65/16448      = 0.003951848…        [D, exact Fraction, this session]
A_6,haar(1) = 16637/4260032 = 0.003905370…        [D, exact Fraction, this session]
```

The k32 base-sensitivity instrument of §3 — a cell built to test **coefficient
transport across bases**, by a different agent, for an unrelated purpose, through a
different code path — measured its `base1` design defects at:

```
base1.A4 = 0.0039518        base1.A6 = 0.0039054        (base1.A2 = 0.0)
[O, cells/k32_base_sensitivity_v3/report.json,
    metrics.second_signal_design_defects.base1, read this session]
```

**All five printed digits agree, at both degrees.** §11 already claimed the degree-4
half of this as its fourth anchor; the degree-6 half is new in v1.2 and it is the
better of the two, because `A_6` was never used to design or check anything in the k32
cell and had no route by which it could have been tuned to match. The `A_2 = 0.0`
column is the instrument's own null and it holds exactly, which is what says the
measurement is of the object the closed form describes.

**What §11b claims, and what it refuses to claim.** It claims that the design axis is
closed as **mathematics**: the per-degree carrier dependence is a single exact rational
at each degree, degree 4 and degree 6 are the only two that matter, the structured
carrier is the unique degree-4 minimizer over frame unions, and nothing cheaper than
the completion exists. It claims **nothing about MSE**. `A_l` is a property of the
design; the gain is a property of how much of a given carrier's estimator error lives
at degree `l`, and the three unreconciled quantifications of that suppression recorded
in §11 (m191 ~9.1x, `m81_full129_pareto` ~21x, the exact defect ratio `128/3` = 42.7x)
are exactly why P2's band was widened rather than narrowed. Promoting a defect law into
a score prediction is the move §11 refuses and §11b refuses it again, one degree up.

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

**Scope correction to the sentence that opens this sidebar [v1.2].** "Every number in
this sidebar is [R] … reported by other participants, read from the public forum, never
re-run by us" describes the bullet list above and no longer describes the section. The
two paragraphs that follow report **our own** numbers — the standing line's local scores
and the local↔hosted map — and each carries its own tag and source at its own site. The
bullets are unaffected.

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

**The local↔hosted conversion, which the paragraph above declined to perform and which
now exists [v1.2; `core/LOCAL_VS_HOSTED_DIVERGENCE_MAP_20260819.md`, every number in it
re-derived from source artifacts in its own session].** The sentence above says local
and hosted scores are different instruments and refuses to compare them. That refusal
was correct and it is now replaceable by a measured map, with three consequences for
how this section's standing line should be read.

*First, a constant this corpus used for ten days is retired.* **`R = 1.65` is dead in
both directions.** It was never a suite-difficulty ratio: it was the **skew of a
22-net panel**, and the divergence map shows the tell — `mean/median = 1.65076` and
`mean/printed = 1.65167` agree to 0.0548%, which they do *because* the panel's median
equals the grader's printed reference. The "difficulty ratio" was numerically identical
to a pure skew statistic of a single sample. Nothing in this corpus may divide or
multiply a local score by 1.65 to reach a hosted one, and any earlier document of ours
that did is wrong at that step.

*Second, the honest map is `R ≈ 1` with a mildly adverse anchor.* Three independent
routes land at parity or slightly against us: the MC-lane median matches the grader's
printed MC reference to **+0.055%**; the single paired graded observation — the same
frozen artifact scored locally and graded hosted, submission #326094 — puts the
champion lane at **`R = 0.884`**, i.e. **hosted ~13% worse than local**; and the
campaign's own same-day post-mortem recorded that failure of an out-of-sample
projection before either statistic was computed. The 13% is **entirely raw MSE**: the
two score multipliers agree to 0.14%, so the transfer risk is suite difficulty and not
billing. The band that every position statement must now carry until a second paired
anchor exists is **`R ∈ [0.707, 1.105]` at 95%, point `0.884`**. The planning default
is `R = 1.0`, the conservative arm is `0.884`, and `R > 1` is never to be used — the
local anchor is burned-descriptive, which biases `R = local/hosted` downward, so the
one attack that would move the recommendation moves it toward parity.

*Third, and this is what it does to the standing line above.* Our declared `1.83e-7` is
a **hosted** number and the `1.6190838e-7` / `2.1218e-7` pair is **local**, so the
`kerdock_v3` row is self-consistent by construction: `1.6190838e-7 / 0.8840979 =
1.8313e-7` is the observed grade, which is the map's calibration check rather than a
prediction. The divisor is the map's unrounded anchor; the rounded `0.884` printed
everywhere else in this section returns `1.8315e-7`, and the difference is 0.01%
**[D, both recomputed this session]**.
Applying the same map to the deployed `row_blocked` local score of `2.1218e-7` projects
`2.40e-7` hosted at the anchor. **Approximately 7th is therefore not an artifact of
comparing instruments** — it survives the conversion, and at the adverse edge of the
band it gets worse rather than better. The map also prices what a front position would
actually cost: matching Puffi's `9.10e-8` needs a **local** score of `8.0e-8`–`9.1e-8`,
which is **1.66–1.87x more MSE reduction than the corpus had been budgeting for** under
the retired constant. We state that because the retired constant made the front look
reachable and it is not the kind of error to correct quietly.

The single highest-value check on all of this is named and cheap: **grade one more
already-locally-scored artifact.** The band is one-anchor-wide, the two suites share
**zero** of 150 net names so nothing cancels, and a second paired anchor is the only
thing that separates a true suite offset from sampling error.

---

### 13. Pre-registered predictions, with their filed falsifiers

Neither of these is a result. Both were filed before the measurement that would
settle them, both name the carrier lineage they are filed against, and P2's band was
amended once — before its cell ran — in the direction that makes it harder to claim a
hit. The amendment is in the table, not in a footnote.

**Disposition [v1.2], stated before the table rather than after it, because the table
is now a record of what was filed and not a list of what is pending.** The two
predictions have diverged:

| # | disposition as of 2026-08-19 08:41 UTC | what this means |
|---|---|---|
| **P1** | **WITHDRAWN BY GOVERNANCE BEFORE MEASUREMENT** | **Never run, therefore never falsified.** The owner's re-plan ruling halted the fold lineage under the three-red-loops pipeline law and cancelled M1, the Public100 measurement that would have settled it (§10b). This is **not** a failed prediction and **not** a silent deletion. No evidence about the folded route's Public100 compute exists, in either direction. |
| **P2** | **RUNNING** | The 129-frame completion cell is executing as this draft is written, under the owner's "repair + run" ruling: `spec.json`'s band repaired to the amended `[0.78, 0.93]` verbatim, the unsupported "12% of C" prose corrected in the same pass, re-hashed, arm-C Tier-1 pre-flight, then predeclare and one run. Its result is **not** in this document. |

**Why P1's wording matters more than its content.** A pre-registration exists so that a
later reader can tell what was claimed before the data arrived. That contract is broken
in two ways: by quietly removing a prediction that would have embarrassed you, and by
reporting a cancelled prediction as though the cancellation were evidence. P1 was
cancelled for a reason recorded in §10b — the folded route lost 9.9% to an artifact the
campaign already held, so the measurement stopped being worth its CPU — and that reason
is about the route's *value*, not about whether P1 would have hit. **We do not know
whether P1 would have hit.** The row below stays in the table exactly as filed.

**What P2's outcome will and will not decide [R, channel `2026-08-19T08:41:38Z`,
pre-stated so the verdict cannot be re-narrated afterwards].** On the unfolded host the
arithmetic is `r × 1.0238 × 2.121762464e-7` — the deployed **`row_blocked`** local
adjusted score, unfolded — which beats the held **`kerdock_v3`** `1.6190838e-7` only
at `r < 0.7453` — **below** P2's pre-registered PASS band. So whichever way P2 lands, it
is a **scientific** result (a test of the `A_4` theory, and evidence about the host
fork) and **not** an immediate designation flip. That is written here before the cell
reports.

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

**The open repair is closed [v1.2; ordered R, channel `2026-08-19T08:41:38Z` owner
ruling 1; landing O, spec re-read at the close of this session].** The repair was
ordered as part of P2's execution chain and **has landed**: `spec.json` now carries the
`[0.78, 0.93]` band with the commit `0486668` amendment text, the unsupported "12% of C"
prose is removed, and the spec was re-hashed — all **before** predeclaration, which is
the only window in which the repair is free rather than a protocol violation. §11's
record of the discrepancy stands as written, with the resolution appended at its site.
What matters about the direction of the fix: **the spec was brought up to the channel
entry, not the channel entry quietly read down to the spec.** The `A_4` leg referenced
above is also no longer only §11's degree-4 theorem: §11b generalizes it to the
per-degree dyadic tax and prices the countervailing degree-6 term at exactly `33/32`,
which the pre-registered band already brackets.

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

**Additions and one correction [v1.2].**

- **Correction to the first bullet.** "The two live items in §13 have not been measured
  at all" is superseded. There is now **one** live item: P2, which is running. P1 was
  **withdrawn by governance before measurement** — never run, never falsified (§10b,
  §13). The bullet's actual claim is unchanged and still holds: **no score.** Nothing in
  this document has been measured on the private suite.
- **No MSE claim from any theorem in §11b.** The dyadic tax, the carrier-optimality
  theorem and the Delsarte floor are statements about **design defects** and about which
  carriers minimize them. The step from a defect to a score is unmeasured, the three
  quantifications of degree-4 suppression remain unreconciled (§11), and the degree-6
  tax of `33/32` cuts against the completion in a direction no theorem here weighs
  against the degree-4 gain. P2 measures that trade; §11b does not predict it.
- **No claim that the design axis is closed outside the frame-union class.** The
  carrier-optimality theorem is unconditional **over unions of orthonormal bases**. A
  carrier built from anything else is outside it, as it is outside §8's certificate.
  Its weighted-objective leg additionally carries a stated condition, `E6/E4 < 19.71`,
  which is met by a measured 28x margin and by 3.9x under the adversarial floor —
  reported as a condition with both numbers rather than dropped. The slate retires the
  same threshold as vacuous while the channel states it as live; §11b records that
  disagreement and no conclusion turns on it.
- **The Delsarte figure is quoted under two conventions that disagree**, `2,861,696`
  directions at 88.7x and `2,861,952` points at ~44x, and §11b records the disagreement
  instead of picking a winner. No conclusion in this document depends on which is right.
- **The degree-6 identities rest on an uncommitted script [GAP].** The committed
  artifact `papers/a4_ratio_settling_check.py` covers degree 4 only; the slate's lanes
  live in a session scratchpad. The degree-6 half was re-derived independently in this
  session and by five agreeing lanes, and the settling check — commit a degree-6
  companion script — is named in §11b.
- **§10's score projections are superseded and its denominator is contested.** The
  m-curve's `m* = 5.09`, the `C ∈ [150B, 165B]` band and the four agreeing derivations
  all share one denominator that the ultrareview merge has since called a **scale mix**
  (local-scale analytical anchor against a record max-`C` receipt). Those numbers are
  retained as the record of what was pre-registered; they are **not** claimed forward,
  they are superseded as designation inputs by `DESIGNATION_POLICY_20260819.md` v2, and
  §10b states the methodology lesson rather than repairing arithmetic whose measurement
  was cancelled.
- **No hosted position claim without the transfer band.** §12 now carries the
  local↔hosted map. `R = 1.65` is retired in both directions; the honest map is
  `R ≈ 1` with a `0.884` anchor and a 95% band `[0.707, 1.105]` that is **one anchor
  wide**. Any sentence about where we would sit on the hosted board carries that band,
  and the settling check is one more paired grade.

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

**Additionally re-derived for v1.2 [O, this session, exact `Fraction` arithmetic under
`python -B`, zero harness runs and zero estimator compute].** The degree-6 half of §11b
was reconstructed from the dimension-256 Gegenbauer recurrence in a scratchpad script
sharing no code with the slate's lanes or with `a4_ratio_settling_check.py`:

```
Q_4(0) = 1/21845            Q_4(1/16) = -65/2105344          (both reproduce §11)
Q_6(0) = -1/1131571         Q_6(1/16) = 16637/17449091072    (new in v1.2)

X_4/S_4 = -1/128            X_6/S_6 = +1/4096                (exact)
A_4,mub(129)/A_4,haar(129) = 0            A_6,mub(129)/A_6,haar(129) = 33/32
A_4,mub(126)/A_4,haar(126) = 3/128        A_6,mub(126)/A_6,haar(126) = 4221/4096
A_4,haar(1) = 65/16448     = 0.003951848…   vs k32 base1.A4 measured 0.0039518
A_6,haar(1) = 16637/4260032 = 0.003905370…  vs k32 base1.A6 measured 0.0039054

R_4(k) = (k/126)·A_4,mub(k)/A_4,mub(126) = (129-k)/3     ] all k = 1…129,
R_6(k) = (k/126)·A_6,mub(k)/A_6,mub(126) = (4095+k)/4221 ] zero failures
R_6(129) = 1408/1407  = the certificate's own 0.0711% margin (§8)
```

The two measured k32 values were read this session from
`cells/k32_base_sensitivity_v3/report.json`,
`metrics.second_signal_design_defects.base1` (`A2 = 0.0`, `A4 = 0.0039518`,
`A6 = 0.0039054`). The `R_6` identity — that the certificate's degree-6 payoff line is
the degree-6 design defect scaled by compute — is a new result of this integration
rather than a restatement of the slate. The `1408/1407` equality with §8's margin is
**not** new: the certificate already carries it as `game.worst_case_margin`, as
`game.degree6_penalty_above_126["129"]` and as a named check, and §8 now credits it
there. What this integration adds to that number is only its reading as the
completion's degree-6 design tax.

**The criterion-(iii) artifact, named because it is the one a judge needs.** Rules v12
§6 criterion (iii) is "the ease of determining the actual performance impact of the
contribution from the code and writeup together," and for the deployed `row_blocked`
lineage that is answered in
`core/SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md`, with its mechanical
re-checker `core/verify_row_blocked_disclosure.py` (run it as
`python -B core/verify_row_blocked_disclosure.py` after any edit to that file or to
`experiments/row_blocked_production/candidate_source/`). Three things about it belong
in this document rather than only in that one:

- **It exists because the committed disclosure described the wrong host.**
  `SECTION_ESTIMATOR_AND_CONSTANTS_20260812.md` enumerates the `kerdock_v3` MRO. Every
  number in it checks out against a real file and it was cited about the deployed
  entry, which is a cheaper mistake to make and a harder one to see than a false
  number. Neither document supersedes the other: **two promoted lineages, two
  disclosures**, and the older one gains a host banner rather than a rewrite.
- **The fitted surface on the deployed host is six scalars, one boolean switch and one
  structural integer**, all frozen before grading, confined to budget, threshold and
  correction coefficients, with nothing that could learn the target and no component
  fit to the evaluation suite. The count is six rather than five because **`n_base =
  126 * 256` is *forced* on `kerdock_v3` and *selected* here** — the same literal, a
  fact about a frozen design on one lineage and a number someone chose on the other,
  which is precisely the kind of claim that does not survive being copied between
  hosts.
- **It carries a fourth disclosure tier that the `kerdock_v3` section did not need:
  *present but unreachable*.** `radial_conditioning = True` strands a fitted-looking
  radial polynomial (`257.0`, `66563.0`, `2600.0/537689.0`, `3.0/537689.0`) in a live
  file, and the whole of `base_estimator.{setup,predict}` is dead on the deployed path.
  Declaring those lets the mechanical check distinguish "undeclared" from "unreachable"
  instead of reporting a false fitted surface. The carrier statement it lands on is the
  one §11 depends on: **126 Haar-orthonormal frames of 256 directions, redrawn per
  network from `ctx.seed`, degree-2 and degree-3 exact by construction, carrying the
  full i.i.d. degree-4 error.**

Its own standing caveat is inherited here: any performance number ever added to that
section — in particular anything derived from a `full.json` — must carry **"pending
round-4 bill repair re-run"**, because the cost model that produced those numbers was
wrong in both directions. No such number is present in it, and §10b is where this
document says the same thing about its own.

**Other v1.2 companion artifacts, read-only this session.**
`core/ULTRAMATH_SLATE_20260819.md` (the theorems of §11b);
`core/LOCAL_VS_HOSTED_DIVERGENCE_MAP_20260819.md` (the transfer map of §12, which
supersedes the scattered readings in `experiments/c1_local_mc_calibration/C1_REPORT.md`,
`experiments/gm_c1_bound/VERDICT.md`, `CODEX_HANDOFF_20260810.md` §4.1/§4.2 and
`SUBMISSION_RESULT_20260808.md` wherever those disagree);
`core/DESIGNATION_POLICY_20260819.md` **v2** with `core/designation_repricing.py` (which
supersede §10's projected designation numbers, v1 retained byte-intact under a
supersession banner).

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

**What v1.2 changed, in the same spirit.** Nothing in v1.1 was deleted; every edit is
an addition or a marked correction sitting next to the text it corrects.

1. **§0 and the front matter** — the centre of mass moved from the compute programme
   and its predictions to what is proved and measured, per the strategy ruling. A
   reading order was added; the "two of the ten items are not results" paragraph was
   corrected rather than replaced.
2. **§8** — the certificate's degree-6 payoff line `R_6(k)` is shown to be the degree-6
   design defect scaled by compute, exactly as §11 showed for `R_4`, and its own
   `1408/1407` margin is thereby read as the completion's degree-6 design tax. The
   first is a new result of this integration, verified over all 129 block counts with
   zero failures; the second is a **re-reading** of a number the certificate had
   already proved and stored, and the audit pass on this draft corrected the sentence
   that had called it new (§8, §15).
3. **§10b** — the fold lineage's governance disposition: gate retired **green**, then
   **halted** by owner ruling; P1 withdrawn before measurement; the four surviving
   artifacts named. Two self-critical items are recorded here rather than smoothed: the
   **scale-mix lesson**, which says four of this section's own agreeing derivations
   shared a contested denominator and therefore constituted one signal rather than
   four, and the **supersession** of its projected designation numbers by policy v2.
4. **§11b** — the ultramath theorems, with a **fourth external anchor** at degree 6
   that had no route to be tuned, and two items filed against ourselves: the
   uncommitted degree-6 script `[GAP]`, and the Delsarte points-versus-lines
   disagreement recorded unresolved because no conclusion turns on it.
5. **§12** — the local↔hosted map: `R = 1.65` retired in both directions as a panel
   skew statistic, `R ≈ 1` with a 13%-adverse anchor installed with its band, and the
   correction stated that the retired constant had made the front look 1.66–1.87x
   nearer than it is.
6. **§13, §14, §15** — P1's and P2's dispositions; the stale claim boundaries corrected
   and five new ones added; the criterion-(iii) `row_blocked` disclosure named with its
   mechanical verifier, including the disclosure's own finding that the previously
   committed estimator section described the wrong host.
7. **The hostile audit pass on this draft**, whose findings are repaired at their sites
   rather than in a separate note. It caught one **novelty overclaim** — the
   `1408/1407` equality was already a stored, executed check of the dual-witness
   certificate, so only its reading as a design tax is new (§8, §15); one **mis-cited
   source** — §10b's memory peaks are round-4's, not the pair the `06:12:13Z` ruling
   and the gate addendum were written against; one **positional ledger pointer** of the
   kind §0's own erratum forbids, since `record 183` lands on an unrelated record and
   the value is at `t4_kerdock_v3_descriptive_rescore`; one **unrecorded source
   disagreement** — the slate retires the `E6/E4 < 19.71` threshold as vacuous while
   the channel states it as live (§11b); a **rounded divisor** printed as an exact
   division in §12; a missing **carrier qualifier** on §13's unfolded-host arithmetic;
   and the **stale scope sentence** opening §12, which claimed the whole sidebar was
   other people's numbers after v1.2 filled it with ours. No conclusion moved under any
   of them, which is the only reason they are corrections rather than retractions.

The pattern worth naming: of the seven items above, **five are corrections to our own
work** — a shared denominator mistaken for independent agreement, a retired constant
that had been flattering us, a disclosure that described the wrong host, a prediction
whose withdrawal had to be stated so it could not later read as either a hit or a
failure, and a number this integration called new that its own certificate had already
proved. That ratio is the same one §15 reports for the harness, and it is the only
evidence available that the machinery is pointed at us as well as outward.
