# Falsification at machine speed

## An append-only kill ledger, optimality by adversarial attack, and graveyard re-measurement for AI-agent research campaigns

**Internal methods paper, draft 1. 2026-08-10.** Audience: successor sessions on this campaign; secondarily, an external methods write-up. Case study: the WHestBench recursive-estimator-folding campaign, 2026-08-02 to 2026-08-10.

## 0. Provenance and deviations (read first)

Evidence levels are tagged throughout. **[E]** = observed by this author reading a committed artifact or running a command this session. **[R]** = reported by a campaign document whose measurement I did not re-run. **[D]** = derived by arithmetic shown here.

- **D1.** The brief named `~/.claude` skill documentation unreadable. The fold discipline in §2 is reconstructed from the repository's own `SKILL.md` and `scripts/fold_ledger.py`, which are the operative artifacts anyway. No external skill text was consulted.
- **D2.** No `m245_*` artifact was read. The Gen-6 exact-control lane appears only where a cited document names it.
- **D3.** No git command was run. Claims about record chronology rest on file content, not commit order — a real limit, discussed in §5.4.
- **D4.** Two population figures in the source documents do not reproduce against the ledger JSON. Both are reported in §5.3 rather than quietly corrected, because surfacing that class of error is the point of the method.

## 1. Abstract and setting

An AI-agent campaign generates and discards candidate mechanisms far faster than a human team can adjudicate them. The bottleneck moves from having ideas to disposing of ideas honestly. The campaign's object here was a white-box estimator for a fixed d=256, L=32 network-output task under a hard compute meter, but its governing constraint was epistemic: fleets could propose and implement mechanisms in minutes, so a campaign that accepted its own summaries would accumulate false structure at the rate it accumulated results. Three practices answer that, stated below as transferable procedures.

**(1) An append-only falsification ledger.** Each candidate is a JSON record carrying a mechanism, a bias class, a predicted signature, and a kill condition, all written before implementation code exists. Kills are final. Records are dispositioned, never deleted, and dispositions may be compound. The ledger holds 258 records under 87 distinct status strings and passes its own machine auditor [E]. Its headline structural claim — that hundreds of independent failures collapse to seven root-cause families, each of which doubles as a proof that a champion property is optimal — is legible only because failures were recorded at mechanism resolution instead of summarized. [R]

**(2) Optimality by adversarial attack.** Near-optimality is not established by a certificate the claimant wrote. It is established by agent fleets mandated to break the claim, measuring against seeded deterministic gates the defender predeclared, with separate judges refereeing. Twenty such agents across three fleets returned five named obstructions, one genuine untested candidate, and four corrections to the defenders' own over-claims [R]. Worked example: the SVD-V rotation construction, the one lane the convergence certificate left open, predicted a win by its attacker and measured a clean null at paired t = +0.19, better on exactly 50 of 100 networks [E, ledger 242].

**(3) Graveyard re-measurement.** Dispositions decay. Premises true when a record was killed can be refuted later, and some records were never measured at all. A record-level sweep found three "kills" that had never been run (`status: proposed`, no `result` field) [E], twenty-nine dispositions closed by wording rather than evidence [R], and six records killed on a residual-cost convention of "roughly 5x" that fresh graded data observes at k ≈ 1.0 [R,E]. Sixteen revival falsifiers were then predeclared and run: four screened, ten kills confirmed by measurement instead of assumption, two blocked [E].

§5 reports what the method caught in its own authors; §6 costs; §7 what adversarial closure does not prove.

## 2. Practice 1 — the append-only falsification ledger

### 2.1 The record schema

One JSON document: `schema_version`, an `invariants` block, a `candidates` array. Verified against `corpus/whestbench/headroom/fold_ledger.json`, 258 records [E]:

| field | present in | role |
|---|---|---|
| `id` | 258/258 | stable name; auditor rejects duplicates |
| `status` | 258/258 | disposition (§2.3) |
| `mechanism` | 258/258 | one causal operator in ordinary mathematics |
| `bias_class` | 258/258 | exact / unbiased / asymptotically unbiased / deliberately biased |
| `prediction` | 258/258 | signature expected if the mechanism works |
| `kill_condition` | 258/258 | the observation that ends it, fixed in advance |
| `result` | 254/258 | what was measured |
| `status_note` | 33 | disposition commentary |
| `artifact_hash` | 26 | reproducibility anchor |
| `matched_units`, `primary_effect`, `ci_upper`, `failures` | 16 each | promotion evidence |
| `holdout_used_for_generation` | 3 | firewall affirmation |
| `sensitivity` | 3 | secondary-analysis note |

The `invariants` block carries seven required keys enforced by `scripts/fold_ledger.py`: `objective`, `score_formula`, `legality_boundary`, `resource_ceiling`, `development_split`, `holdout_split`, `champion_hash` [E]. These pin the scoring formula, legality boundary, resource ceiling with safety margin, split firewall, and the frozen champion's hash, so no record can be measured against a moved goalpost.

### 2.2 The predeclare-before-code rule

The four content fields are written before implementation code exists. The rule is visible in the artifacts: every `gm_*` experiment directory opens its `PREDECLARATION.md` asserting the ordering, e.g. `Written BEFORE any experiment code` [E, `experiments/gm_residual_k1/PREDECLARATION.md`].

A predeclaration here contains more than a hypothesis. The `gm_residual_k1` document is representative: a numbered deviations section up front; the exact quantity under test with its formula; the arms, one explicitly marked non-binding and unable to open a gate; the predicted outcome with numeric values on record; the exact kill inequality; the two-signal verification plan; a firewall statement; and a compute envelope with declared overrun behavior — report BLOCKED with measured wall time rather than silently scale down [E].

Two consequences transfer. First, the prediction is on record before the measurement, so a null is informative rather than deniable; in the SVD-V case (§3.3) the ledger preserves the attacker's prediction of a win next to the null. Second, the kill condition is an inequality on a named statistic, not a judgment call. `gm_residual_k1` predeclared "KILLED if, in ARM A, `max_i C_k1(i) >= 258.4e9`", and further: "No retuning past a failed gate. If ARM A kills, I report KILL_CONFIRMED and stop; I do not soften the pin, change seeds, or fall back to the unpinned configuration" [E].

### 2.3 Kills are final; dispositions are not deletions

The repository states the rule: `killed` is a disposition of one fully specified implementation at one gate, never a dismissal of an idea family [E, `SKILL.md`]. Each failed branch is split into passed components, the failed link, untested claims, and reusable operators. Passed components go to a salvage bank; the failed link becomes a constraint on the next mutation. Reimplementation is permitted only by changing the failed mechanism or exposing a new observable — parameter drift and post-hoc coefficient tuning do not count.

This produces compound dispositions, and the ledger shows them: **87 distinct status strings** across 258 records [E].

| bin | count |
|---|---|
| `killed*` | 171 |
| `screened*` | 42 |
| composite legacy dispositions (one-off strings) | 23 |
| `repair_*` / `preserved_*` / `passed_*` | 11 |
| `blocked` | 5 |
| `proposed` | 4 |
| `promoted` | 2 |

Sum 258 [D]. Examples of the one-off strings: `rankone_pass_generic_provider_killed`, `killed_closures_theorem_preserved_numerics_unverified`, `resource_killed_identity_preserved`. Each encodes what survived alongside what died — exactly the information a boolean `failed` flag destroys.

A related device is the one-shot authorization token: a mechanism granted a development authorization consumes it on use, and a protocol failure consumes the token and forbids retry of that implementation while preserving the mechanism as an unresolved-family component. The M143 postmortem records the outcome in full: run terminated at 49.2 seconds, no result file, "no replacement authorization, seed retry, family deletion, or rerun of the same implementation is permissible" [E].

### 2.4 Mechanical enforcement

`scripts/fold_ledger.py` audits: required invariants present; ids present and unique; the four content fields non-empty on every record; `validated`/`promoted` records carrying artifact hash, matched units, primary effect, CI upper bound and failure count; and three hard promotion gates — zero resource failures, paired `ci_upper < 0`, `holdout_used_for_generation` false. Legacy compound statuses are admitted under an explicit prefix namespace and barred from inheriting `validated`/`promoted` rules [E]. Run this session:

```
$ python scripts/fold_ledger.py audit corpus/whestbench/headroom/fold_ledger.json
ledger is valid
$ python -m pytest tests/test_fold_ledger.py -q
5 passed
```

The auditor passes on the live ledger and its own unit tests pass, including negative cases rejecting a promotion with a resource failure and a promotion with holdout leakage [E].

### 2.5 What the ledger bought: the 238-to-7 compression

The campaign's structural result is that its kills do not fail in as many ways as there are kills. `FAILURE_MODE_GRAPH_20260810.md` places every record in one of seven root-cause families, each with a single causal boundary [R]:

| # | family | representative kills | causal boundary | positive dual |
|---|---|---|---|---|
| 1 | DISPERSION | M191, S5, S15 | residual spreads over ~1.8e8 degree-4 dims; low-dim probes are blind | design is harmonically complete |
| 2 | FIDELITY | S10, S13, m36 | output fingerprints the exact early-layer weights; cheap copies decorrelate | estimator is exact-weight-faithful |
| 3 | CLOSURE | M181, N5, T2 | non-Gaussianity accrues with depth; exact closure 9.6e-5 vs sampling 2.5e-7 | sampling is the right regime |
| 4 | SYMMETRY / OPTIMALITY | M180, kriging/BLUE | design is a group orbit, so LP-optimal weights are uniform | design is provably optimal |
| 5 | INFORMATION-GATING | S2/P2/P2b, A1b | quality signal in no cheap observable (best proxy rho 0.12–0.17) | variance is irreducible sampling noise |
| 6 | COST / CLOCK | N8b, M183, M184 | meter bills FLOPs not wall-time; FLOP count already minimal | billed-compute lever exhausted |
| 7 | EXACT-CONTROL / ABI | M243, M120–M179 | mathematics correct, dies at cost or byte-ownership gates | the frontier is real |

The fourth column is the transferable observation. A kill recorded with its causal boundary is a two-sided measurement: it says a mechanism failed, and it says which property of the incumbent made it fail. Failure and optimality are the same measurement read twice. That inversion is unavailable to a campaign that records only that things did not work.

**Procedure (transferable).** (1) One JSON ledger per campaign with an invariants block pinning objective, score formula, legality boundary, resource ceiling, split firewall, champion hash. (2) Per candidate write mechanism, bias class, predicted signature, kill condition **before** implementation code exists; store the predeclaration next to the run artifacts. (3) Append only — never delete a record, never edit a kill into a pass. (4) Allow compound dispositions; require every kill to name its causal boundary and its preserved components. (5) Write a machine auditor for schema and promotion gates plus unit tests for the auditor, and run both on every append. (6) Periodically cluster kills by causal boundary and read each cluster's positive dual.

## 3. Practice 2 — optimality by adversarial attack

### 3.1 The mandate, the fleets, the gates, the judges

Before Gen-7 the near-optimality claim had the status of a self-assessment plus a convergence certificate written by the champion's own author. That is one signal. The Gen-7 protocol replaces it. Owner mandate on record: "actually try, dammit". Twenty agents across three fleets, attacker and judge roles held by different agents, every measurement seeded [R, `GEN7_ADVERSARIAL_CLOSURE_20260810.md`]. Fleet 1 broke the champion with six attack lenses; Fleet 2 re-litigated the seven family boundaries under changed premises; Fleet 3 attacked six load-bearing claims from the campaign's own write-up.

An attacker's claim is adjudicated on gates the defender predeclared, under common random numbers, a fixed seed, and a bit-identical repeat requirement. In the SVD-V measurement the noise floor was exactly 0.0 and both arms reproduced bitwise across two runs [E]. This is not ceremony: an attacker fleet is a multiple-comparisons machine, and without a fixed gate and a determinism check twenty agents will surface noise as a finding.

Attack agents did not adjudicate themselves. In Gen-7 attackers were Opus-5 and the judge Fable-5; in the later graveyard run both workers and judges were Opus-5, with the judge drafting the ledger append [R]. The judge's product is a verdict document plus a proposed record, so the disposition entering the permanent record is written by someone other than the agent who wants the result. The role is load-bearing in both directions — see §4.4, where a worker's own arm failed, the worker reported it plainly, and a diagnostic then moved the verdict to INCONCLUSIVE rather than to a pass.

### 3.2 Named obstructions are the earned result

Five of Fleet 1's six lenses returned no candidate. "No candidate" is worthless unless it names why, so each closed with a measured obstruction [R]:

- **exact-identity:** all four closed-form conditional expectations already consumed.
- **control-variate:** the 2-design absorbs every degree-≤2 statistic exactly; degree-≥4 content is ~1e-5 R².
- **biased-hybrid:** baseline measures unbiased, so the MSE-optimal shrinkage weight is ~0; every realizable form measured worse, -5.7% to -38%.
- **cost-remap:** ~99% of the bill is irreducible float32 matmul at floor rate; f64 share 0.033% max.
- **design-alternative:** the DGS bound needs N ≥ 33,152 for a 4-design and ~44x rows for degree-6 nulling; Var·C invariant on the flat speckle.

Each is a reusable constraint on future proposals. A campaign recording only "attack failed" has to re-derive them.

Fleet 2 returned 7/7 boundaries held, and one hold produced new work: the dispersion boundary named the record's single un-probed crack — non-smooth cell-membership covariates — and S18 killed it the same day. Best gated out-of-sample incremental R² 2.371e-5 against a predeclared 2.63e-5 bar, inside its own permutation null of |5.3e-5|. Structural mechanism: all 64,512 directions occupy 64,512 distinct first-layer cells, so cell identity is a per-point unique label incapable of out-of-sample generalization. Two-signal: split-sample plus permutation null, with instrument sanity confirmed by reproducing S15's Base-B values exactly [E, ledger 241].

### 3.3 Worked example: the SVD-V null

The sixth lens found the one candidate the convergence certificate left untested. Full record, ledger 242, `gen7_svdv_rotation_construction` [E]:

- **Mechanism.** Seed-side rotation *construction*, not selection: replace the champion's grader-seed Haar input rotation with the deterministic V from W0 = U S Vᵀ, coupling the rotation to the possessed weights' singular basis. Distinct from the S2/P2/P2b selection kills because it needs no observable.
- **Prediction, on record before measurement.** The attacker predicted a win, citing a 24-rotation oracle spread of 5.8e-8 to 6.8e-7 with the champion at the mean. The campaign's gating results predicted a null.
- **Kill condition, predeclared.** Paired per-net t ≥ 3 on the committed public 0..99 basis at seed 0 under common random numbers, twice-run bit-identical determinism, no cost regression.
- **Result.** Clean null. Paired t = **+0.19**. Variant better on **exactly 50/100** networks. Bootstrap CI on mean delta **[-3.19e-8, +2.61e-8]**, symmetric about zero. Drop-top-5 sign flip confirms the sign is an artifact. Determinism bit-identical in both arms; noise floor exactly 0.0. Cost **+3.6e8 billed FLOPs** (C/B +0.0014) with no compensating MSE reduction.
- **Named obstruction.** V is marginally Haar, and coupling it to W0's singular basis buys no systematic alignment with the fixed cubature frame.
- **Scope.** The seed-side rotation lane closes at the point-evaluation level. Deeper seed-side structure is explicitly left open.

The 50/100 split is the detail worth transferring: it is the strongest available evidence for a null in a paired design, and it exists only because per-network paired outcomes were retained rather than aggregated to a mean.

**Procedure (transferable).** (1) Never let a claim's author be the sole source of its optimality evidence — mandate agents to break it. (2) Fix the gates first: seed, common random numbers, a paired statistic, a numeric threshold, a bit-identical repeat; report the noise floor. (3) Require the attacker's prediction on record before measurement. (4) Separate attacker and judge; the judge drafts the permanent record. (5) Require every null to close with a measured, named obstruction. (6) Retain per-unit paired outcomes — a 50/50 win split is a result, a mean difference alone is not.

## 4. Practice 3 — graveyard re-measurement

### 4.1 Record-level premise re-reads

Kills are final as dispositions of an implementation at a gate. They are not final as facts, because the premises they were measured under can be refuted later. The graveyard mine was a record-level sweep: six miners read approximately 307 records one at a time — the mechanism ledger plus the uncertainty dispositions — with a judge scoring every proposal against the record's own evidence. Output: 12 revivals judged falsifier-worthy, 31 salvage items, 29 framing-closes flagged, 4 stays-dead [R]. "Record-level" is the operative constraint: a summary-level re-read reproduces the summary, and each finding below is invisible above record resolution.

### 4.2 Framing-close detection: the U1 pattern

A framing-close is a disposition closed by wording rather than evidence. The canonical instance is U1, the question of whether Phase-2 duplicate nomination was allowed. Its disposition reads `OVERTAKEN-BY-RULE 2026-08-10`: nominations turned out to be Phase-1-only, so the question was moot [E, `UNCERTAINTY_RECURSION_20260810.md`]. That close is correct about the decision and silent about the substance. The mine found the same shape in U3, U5, U13 and Gen-3-U14 [R]. The taxonomy of the 29 framing-closes is itself the transferable artifact [R]:

1. **Overtaken closes** that kill the question's context but not its substance.
2. **Status labels stronger than their gates** — S8 marked "screened" after a 3/3 PASS-gate failure; S12 marked "PARTIAL" while below its predeclared bar.
3. **Thresholds inherited rather than derived** — S2's rho gate taken from P2b's observed failure level rather than from a cost calculation.
4. **Population accounting** — headline record counts that do not reproduce (§5.3).
5. **Provenance mislabels** — S1b's sole validation target labeled "hosted" when it is a local synthetic checkpoint (§5.2).

### 4.3 Never-run "kills"

Three records carried a disposition without ever having been measured. Directly checkable in the JSON: `status` is `proposed` and no `result` field exists [E].

| ledger # | id | status | `result` present |
|---|---|---|---|
| 12 | `latent_sparse_radial_cubature` | proposed | no |
| 34 | `flatworm_response_ladder` | proposed | no |
| 36 | `ecn_exact_jspace_psi_streaming` | proposed | no |

The mine's judgment: inaction is not a disposition [R]. All three got cheap frozen-state falsifiers and all three came back killed [E, ledger 249, 252, 247]. That the assumed dispositions happened to be right is not an argument for leaving them assumed — the ECN case returned a *stronger* verdict than the record predicted. The exact chain-rule-correct observable-Jacobian was implemented, validated against central differences to 6.5e-10 against a 1e-6 threshold over 9,216 points, and measured worse than the surrogate on 32 of 32 units [E].

### 4.4 The x5-convention case

The mine's headline find. Six records — m145, m153, m157, m160, m163, m164 — were killed on a hostile-residual cost formula `C = billed + 1e11 · k · residual_s` with **k = 5**. Every structural, numerical, ordering, replay, restoration, early-pruning and RSS gate had PASSED in five fresh CPython-3.11 workers. The sole binding failure was the multiplier, whose stated provenance was a reported-level legacy convention — "prior official-runner measurements showed roughly 5x local residual time for call-heavy candidates" — never re-measured [E, `experiments/gm_residual_k1/PREDECLARATION.md`].

**Changed premise.** Hosted grading of submission #326094 on 2026-08-08, four days after the residual-safeguard update and with the participant core pin and lambda already priced in, returned C/B 0.650, giving hosted mean effective compute 176.8e9 against a local metered mean of **178.5e9 at k=1**. Agreement 1.0%. A k=5 charge would have projected 198–219e9, that is 12–24% high. The multiplier is observed at **k ≈ 1.0** [E].

**Step 0, cached arithmetic, zero compute.** The five frozen workers recomputed at k=1 against the locked 258.4e9 gate [E]:

| worker | billed (B) | residual (s) | C at k=1 (B) | C at k=5 (B) | break-even k | k=1 | k=5 |
|---|---|---|---|---|---|---|---|
| 1 | 181.112 | 0.155486 | 196.660 | 258.855 | 4.971 | PASS | FAIL |
| 2 | 193.372 | 0.169803 | **210.352** | 278.273 | **3.830** | PASS | FAIL |
| 3 | 176.451 | 0.133213 | 189.773 | 243.058 | 6.152 | PASS | PASS |
| 4 | 167.601 | 0.139817 | 181.583 | 237.510 | 6.494 | PASS | PASS |
| 5 | 165.309 | 0.143669 | 179.676 | 237.143 | 6.480 | PASS | PASS |

At k=1, 5/5 pass with 18.60% worst-case margin. At k=5, 3/5 pass with worst case 278.273B, which reproduces the ledger's recorded "maximum 278.273084846B, 2/5 exceed" exactly — a recomputation cross-check against the frozen record.

**And then the arm failed.** The predeclared binding arm, a fresh five-worker re-run under a one-physical-core pin, produced max C_k1 = 282.530B against the 258.4e9 gate. The kill condition fired [E].

**The attack that landed.** The worker then ran its predeclared attack-the-conclusion step against its own result. Counter-hypothesis: the residual inflation is not the core pin but BLAS thread-pool oversubscription, because `os.cpu_count()` still reports 16 under the pin, so OpenBLAS sizes a 16-thread pool and spin-contends on 2 logical CPUs. Measured sgemm throughput [E]: unpinned with default pool, 244.4 GFLOP/s; **pinned with default pool, the arm as run, 1.7 GFLOP/s**; pinned with `OPENBLAS_NUM_THREADS=1`, 74.3 GFLOP/s. The arm inflicted a 142.36x slowdown; a faithful one-physical-core pin costs 3.29x; sizing the pool to the affinity at the *same* affinity recovers 43.30x. Worker-level corroboration: setup time inflated 116.4x to 191.6x, which a 3.29x hardware reduction cannot produce.

**Disposition: INCONCLUSIVE.** Arithmetic confirmed; instrument disqualified; nothing opens; the original kills stand. The worker explicitly declined to re-run under a corrected pool size on the grounds that doing so would be retuning past a failed gate, and instead predeclared that run for a future worker with its expected cost (~10 min) and the evidence level the claim currently sits at: "DERIVED-from-frozen-data, not OBSERVED-under-pin" [E]. This is the practice's hardest case and its best advertisement — the honest outcome was neither the kill the gate returned nor the revival the arithmetic suggested.

### 4.5 Outcome of the run-all

Sixteen falsifiers predeclared and adjudicated, each with `PREDECLARATION.md` + `VERDICT.md` + `results.json` [R, `GRAVEYARD_RUN_RESULTS_20260810.md`]. Verified against ledger records 243–258 [E]:

| judge verdict | prose doc | ledger status | count |
|---|---|---|---|
| REVIVED_SCREENED | 4 | `screened` | 4 |
| KILL_CONFIRMED | 10 | `killed` | 10 |
| BLOCKED_ESCALATE + INCONCLUSIVE_HOLD | 1 + 1 | `blocked` | 2 |

The tallies reconcile exactly. The ten confirmed kills are the quiet payoff: dispositions previously assumed are now measured. The one repricing that moved was `gm_rankone_bill`, which found three "over budget" verdicts priced under an undischarged f64 convention. Discharging f32 parity with three independent signals — an exact-rational reference at 2e-16, an alternative association order at 1.98e-15, and a bit-repeat — reprices the bills about 2x down, landing 34% under strict headroom. The judge recorded the residual risk: width-256-specific, not reusable at larger n without re-measurement [R].

**Procedure (transferable).** (1) Re-read the graveyard at record resolution, one record per pass, against the record's own evidence. (2) Flag every disposition whose binding failure rests on a reported-level constant, an inherited threshold, or an "overtaken" framing. (3) Check mechanically for records with a disposition and no result — inaction is not a disposition. (4) Order revivals cheapest-falsifier-first: cached arithmetic, then existing harnesses, then new builds. (5) Every revival gets a fresh predeclaration; kills stay final, and a revival produces a new record rather than an edit. (6) If the instrument turns out confounded, the honest label is INCONCLUSIVE — do not re-run under corrected conditions in the same session, predeclare it for the next one.

## 5. What the method caught in its own authors

Every finding below is an error by the campaign's own agents, caught and corrected the same day.

### 5.1 Level inflation

Fleet 3's first finding was against the campaign's own claim about selection default-safety. The judge's verdict: "my claim was level inflation" — the scores were not the default mechanism, and a one-versus-two slot conflict was unresolved. Corrected on the record the same day; explicit selection restored as REQUIRED [R]. Two further Fleet-3 items were also self-corrections: the write-up's floor language was de-escalated everywhere after S17 was found to self-label a lower-bound *attempt*, and a dispersion model with DIFF_RATIO 1.1x was refuted by the campaign's own committed data and re-measured. Four of six load-bearing claims returned REAL_ACT_NOW, all executed same-day.

### 5.2 Provenance mislabels

S1b's sole validation target was labeled "hosted". It is the local synthetic m185 stage-1 checkpoint, and m185's own firewall field proves it. Flagged against the same day's work and corrected in the same commit as the mine document [R]. Structurally identical second instance: the a1b/m185 tail-flag kill was filed under family F5 carrying P2b's *rotation* correlation numbers (0.12–0.17), when the battery's strongest correlate was `borderline_frac` at Spearman -0.563 against raw MSE — wrong numbers attached to the right kill [R]. The revival run then reproduced the frozen diagnostics exactly (all seven Spearmans to 1e-12, `borderline_frac` at -0.5627285513361463) and still confirmed the kill on its own predeclared gate [E].

### 5.3 Population accounting

Two headline figures do not reproduce against the ledger. Both are reported, not silently fixed. First, `FAILURE_MODE_GRAPH_20260810.md` is titled on **238 records** collapsing to 7 families; the ledger held 242 records at the Gen-7 close and holds **258** as of this reading [E]. The mine document itself lists "population accounting (the '238 records' figure vs actual)" among its framing-closes [R], so the campaign had already caught this — it is recorded here because the figure is still the one the graph paper carries. Second, `GRAVEYARD_MINE_20260810.md` writes "killed **five** records" in the x5 case and then lists six ids; all six resolve to distinct ledger records at 1-based positions 144, 152, 156, 159, 162, 163 [E], so the correct count is six. Neither error changes a scientific conclusion. Both would change a reader's arithmetic, which is why they belong in the paper.

### 5.4 Timestamp skew: chronology evidence has a ceiling

The predeclare-before-code rule is enforced socially and by file ordering, not cryptographically. The campaign's own judge states the limit: "File times are consistent with gate -> implementation manifest -> result -> report order. This is good provenance hygiene, though ordinary timestamps are not a cryptographic proof of chronology" [E, `experiments/ECN_JACOBIAN_MAXENT_JUDGE.md`]. This paper inherits the limit and adds to it: per deviation D3 no git command was run, so commit ordering was not checked either. A campaign wanting machine-checkable predeclaration ordering needs a hash chain or a signed commit per predeclaration; this one has neither. The claim "predeclared before code" therefore sits at **[R]** for historical records and at **[E]** only for artifacts whose predeclaration text I read this session.

### 5.5 Confounded instruments

§4.4 in full. The general lesson: an adversarial fleet's *measurement apparatus* deserves the same hostile treatment as its conclusion. The `gm_residual_k1` worker found a 43x artifact inside its own binding arm by asking one question — what else does the pin change? — and running a five-configuration throughput probe that took minutes.

## 6. Costs

The repository records agent counts. It records no LLM token counts or dollar figures anywhere I could find, so those are omitted rather than estimated. ("Token" in `M143_CONSUMED_TOKEN_POSTMORTEM_SALVAGE_20260807.md` denotes a one-shot development authorization, not an LLM token.)

| activity | agents | scope | product |
|---|---|---|---|
| Gen-7 adversarial closure | 20 across 3 fleets | 6 attack lenses, 7 family boundaries, 6 load-bearing claims | 5 named obstructions, 1 measured candidate, 4 same-day self-corrections [R] |
| Graveyard mine | 6 miners + 1 judge | ~307 records read one at a time | 12 revivals, 31 salvage items, 29 framing-closes, 4 stays-dead [R] |
| Graveyard run-all | 16 workers + judges | 16 predeclared falsifiers | 16 adjudicated: 4 screened, 10 kills confirmed, 2 blocked [E] |

Compute per falsifier was small and predeclared as an envelope. The queue was tiered by cost: Tier 0 arithmetic and grep on committed data (minutes), Tier 1 existing harnesses (~CPU-hour), Tier 2 new builds against frozen states [R]. Of the 16 adjudicated items the most expensive named envelope was ~90 minutes [E, `gm_residual_k1`]. Aggregate CPU-hours are not recorded and are omitted. Order of magnitude for transfer: on the order of 40 agent-tasks closed a campaign that had accumulated 258 mechanism records over nine days, and the dominant cost is reading rather than running — 6 agents reading ~307 records generated the queue that 16 short runs settled.

## 7. Limits — what adversarial closure does not prove

Stated plainly, because the campaign's own closing language was de-escalated once already for over-claiming (§5.1).

1. **It does not prove global optimality.** It proves that a bounded set of attacks, by a bounded set of agents, in bounded time, against predeclared gates, produced no improvement. The strongest honest phrasing is the campaign's own: near-optimal *in its class*, where the class is named by the seven family boundaries.
2. **It does not close lanes the fleets did not enter.** Gen-7 says so itself: the seed-side rotation lane closes at the point-evaluation level, and whether non-rotation seed-side structure is extractable remains open by design.
3. **A null is not a proof of no effect.** The SVD-V CI is [-3.19e-8, +2.61e-8]. Effects inside that band are not excluded, only shown smaller than the interval at a measured cost of +3.6e8 FLOPs.
4. **The attacker population is correlated.** Twenty agents drawn from the same model family, primed from the same campaign record, share priors. They are not twenty independent researchers, and the effective number of independent attack directions is smaller than the head count. This is the method's largest unquantified weakness; nothing in the record bounds it.
5. **Judges share the attackers' context.** Separating roles removes the self-scoring incentive, not a blind spot in the framing both inherited. The 29 framing-closes are evidence that shared framing errors survive multiple passes.
6. **Kills are final as dispositions, not as facts.** That is why Practice 3 exists. Any claim resting on an old kill inherits that kill's premises, and the x5 case shows a refuted premise surviving across six records for days after fresh data had contradicted it.
7. **Predeclaration ordering is not cryptographically verified** (§5.4).
8. **Repricing results carry scope conditions.** `gm_rankone_bill` reprices at width 256 and its judge recorded that it is not reusable at larger n without re-measurement. A revival is not a general theorem.

## 8. Two-signal verification of this paper's own numbers

| claim | signal 1 | signal 2 |
|---|---|---|
| ledger schema and record count | JSON parse: 258 candidates, field-frequency table | `fold_ledger.py audit` returns "ledger is valid"; its 5 unit tests pass |
| status-bin table sums to the record total | per-prefix counter | 171+42+23+11+5+4+2 = 258, matching the parsed length |
| graveyard run-all tally | prose doc: 4 / 10 / 1+1 | ledger 243–258: 4 `screened`, 10 `killed`, 2 `blocked` |
| three never-run kills | mine document's claim | JSON: records 12, 34, 36 have `status: proposed` and no `result` key |
| the x5 case is six records, not five | mine document's own id list | each id resolves to a distinct record at positions 144/152/156/159/162/163 |
| k=5 reproduction | verdict table worst case 278.273084846B | matches the frozen ledger record's stated maximum exactly |

Not verified by this author, and therefore [R] throughout: every physical measurement in §2.5, §3.2 and §5.1, including the seven-family assignment, the obstruction numbers, and the Fleet-3 corrections. Settling check if a future session wants them at [E]: re-run the named experiment directories under their own predeclarations.

## Sources

Paths relative to `corpus/whestbench/` in the `recursive-estimator-folding` repository.

- `headroom/fold_ledger.json` — 258 records; the primary artifact [E]
- `../../scripts/fold_ledger.py`, `../../tests/test_fold_ledger.py` — auditor and tests [E]
- `../../SKILL.md` — the fold discipline as stated by the repository [E]
- `core/FAILURE_MODE_GRAPH_20260810.md` — 7-family compression, positive duals [R]
- `core/GEN7_ADVERSARIAL_CLOSURE_20260810.md` — three fleets, obstructions, self-corrections [R]
- `core/GRAVEYARD_MINE_20260810.md` — record-level sweep, framing-closes, the x5 find [R]
- `core/GRAVEYARD_RUN_RESULTS_20260810.md` — 16/16 adjudication tally [R]
- `core/UNCERTAINTY_RECURSION_20260810.md` — the ladder as a fold; the U1 disposition [E for U1 text]
- `core/GOD_NODE_SYNTHESIS_20260810.md`, `core/PASSES_AND_UNCERTAINTIES_GRAPH_20260810.md` — context [R]
- `experiments/gm_residual_k1/{PREDECLARATION,VERDICT}.md` — the x5 case in full [E]
- `experiments/gm_a1b_diffflag/VERDICT.md`, `experiments/gm_ecn_psi_opus5/VERDICT.md` — revival verdicts [E]
- `experiments/ECN_JACOBIAN_MAXENT_JUDGE.md` — the timestamp limitation [E]
- `resources/research_excursions/M143_CONSUMED_TOKEN_POSTMORTEM_SALVAGE_20260807.md` — one-shot authorization [E]
