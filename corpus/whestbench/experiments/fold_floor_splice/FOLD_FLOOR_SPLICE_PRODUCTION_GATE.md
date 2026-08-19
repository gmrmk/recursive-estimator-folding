# Frozen gate: production fold-floor splice descendant

Date frozen: 2026-08-19, authored as the successor to
`ROW_BLOCKED_WINOGRAD_PRODUCTION_GATE.md` after the second hostile REJECT
established that the incumbent gate cannot adjudicate this child: it freezes
incumbent-specific constants (operator workspace `91.4375 MiB`, a seven-module
manifest, `fold3_estimator.py` byte-identical to the parent) that a depth-swept
descendant does not satisfy by construction.  Every clause of that gate which
measures *quality* is retained here verbatim.  Every clause that measured the
incumbent's *envelope* is restated at this candidate's declared envelope, with
its provenance named rather than inherited.

This is a `recursive-estimator-folding` mutation of the promoted
`random32256_rowwinograd8192` package (the incumbent).  Sampling geometry,
randomization, analytic closure, pruning, pilot rules, tangent, seeds, float32
path and output contract remain fixed.

## Invariants and firewall

- Objective: reduce the official mean score while preserving the parent
  estimate, with per-network score
  `MSE * max(0.1, C / 272000000000)` and
  `C = billed_FLOPs + 1e11 * residual_wall_seconds`.
- Bias class: exact arithmetic rearrangement apart from ordinary float32
  reassociation, bounded by prespecified parity tests.
- Incumbent of record: `experiments/row_blocked_production/candidate_source/`,
  seven modules, hashes in the custody clause below.
- Runtime: Python 3.14.4, NumPy 2.4.6, WHestBench 0.14.0, FlopScope
  0.10.0+np2.4.6, from the frozen environment `work/whest-v014`
  (`Scripts/python.exe`).
- Budget: 272B per network; safety gate is maximum child `C < 258.4B`
  (95% of budget), zero failures, setup under 4 s, prediction under 20 s.
- Development data, if earned: only the already-touched public full-split rows
  0..99, seed 0.  Rows 600..799 are locked and forbidden; rows >=800 are
  prohibited.  No API, login, submission, private evaluation, or external
  service is authorized.
- No score observation may change block size, depth cap, workspace, dispatch,
  thresholds, sample count, coefficients, or any source byte.  Any
  implementation change after the score run creates a new child and invalidates
  these results.

## Frozen paths and source contract

- Work directory: `experiments/fold_floor_splice`.
- Production source: `candidate_source/` — the eight runtime modules named in
  the manifest clause, and nothing else.
- Priced but undeployed: `priced_artifacts/phased_wht.py`, deliberately outside
  the package.  No module in `candidate_source/` imports it; it is named only
  in one `fold3_estimator` docstring.
- Harness: `verify_fold_floor.py`, `peak_probe.py`.
- Candidate archive (only if every gate passes):
  `submission_random32256_foldfloor_l4_20260819.tar.gz` in this directory.

### Manifest: the eight runtime modules

The package is exactly these files.  Any addition, removal, or byte change
creates a different child.

```text
base_estimator.py        f4b45d515d24f8b32e55338523f7ec51c34fa9b006d4d51a774ea2e4a29dabe3
cost_model.py            c3c72c649b3ab9b037010e9277dfc381909743ba8b3025e160300867f506865d
depth6_winograd.py       6ee49e574bb598b53ea30171c3f5525b0307acd112c5e13dd47f88526252fc44
estimator.py             713ed302ca430dd101f27bac44e4dd29ff4ac4ba31129d59dc1046306f09db76
fold_estimator.py        11f27f00d14ed467fcc4af07866964e26375205b77c771854527f3f0412fa8c5
fold3_estimator.py       f91811e676e7f81b77d7501ec46bf4490a7d42bcceda4e7d0bc4446af9a6f74c
orthogonal_fold3.py      fa4705ded8daffe8bf7e73a557d1e9be0995beedccf4bf3e20c55c2cd52ff646
row_blocked_winograd.py  ef21dc4c79b7bfca1e3c29fceab933cc8afababdcd2d9af958f0708b000f29e1
```

Four of the eight are byte-identical to the incumbent's own copies
(`base_estimator.py`, `fold_estimator.py`, `orthogonal_fold3.py`,
`row_blocked_winograd.py`); three differ (`cost_model.py`,
`fold3_estimator.py`, `estimator.py`); one is new (`depth6_winograd.py`).
`n_base` remains `126*256 = 32256`.

The incumbent gate additionally froze four inherited modules against the parent
tar manifest.  Those four published hashes match no file on disk, with or
without line-ending normalization, so that clause is not inherited: it is not
dischargeable from this corpus.  See the custody clause for what replaces it
and the residual-risk section for what that costs.

### Custody: the incumbent tree is byte-identical, before and after

The incumbent is read-only evidence.  A verification run may import it and must
not write to it.  These are the on-disk bytes of record, all with 2026-08-07
mtimes:

```text
base_estimator.py        f4b45d515d24f8b32e55338523f7ec51c34fa9b006d4d51a774ea2e4a29dabe3
cost_model.py            8084c2241fa428b3ee47b860a4767229a92ce2ecde0d48e6701ba5a6c28729f6
estimator.py             e0eb3df97a7585eaed3d32505643f697ebcb0e6ac939cca381f56984abaf1ade
fold_estimator.py        11f27f00d14ed467fcc4af07866964e26375205b77c771854527f3f0412fa8c5
fold3_estimator.py       cb06ba68878d7afd21bd2858f5028f5425bef5333672472859e9c8ae3cb96f9c
orthogonal_fold3.py      fa4705ded8daffe8bf7e73a557d1e9be0995beedccf4bf3e20c55c2cd52ff646
row_blocked_winograd.py  ef21dc4c79b7bfca1e3c29fceab933cc8afababdcd2d9af958f0708b000f29e1
```

All seven hashes and all seven mtimes must be unchanged at the end of every
verification run, and the directory must contain exactly these seven files.

### Bytecode hygiene

`sys.dont_write_bytecode` must be set before the first import of any candidate
or incumbent module, and every entry point must be run under `-B` or
`PYTHONDONTWRITEBYTECODE=1`.  At the end of a run, no `__pycache__/*.pyc` may
exist in the experiment directory, `candidate_source/`, `priced_artifacts/`, or
the incumbent tree.  This is not housekeeping: a compiled artifact in the
incumbent tree is a write to protected evidence, and a compiled artifact in the
package is undeclared binary payload under the archive clause.  An earlier run
of this harness dropped both.

## Mechanism and predicted signature

**One mechanism: the estimator's full-height products are routed through the
depth-swept operator.**

The honest statement of granularity, because it is two source-level edits.
`estimator.py` builds `depth6_winograd.DepthWinograd` in `setup` where the
incumbent built `RowBlockedBatchedWinograd`; `fold3_estimator.py` sends the
terminal fold's own 64,512-row products (`x @ weight30`, `pre31`, `pre32`, the
three weighted means) through the same hook the sample path already used,
instead of leaving them on the direct `@`.  Neither edit is the mechanism
alone.  The operator swap without the routing changes which engine runs the
sample products and leaves the fold's products on `@`; the routing without the
swap sends the fold's products to the incumbent's engine.  What is under test
is the single proposition *one depth-swept operator carries every full-height
product in the estimator*, and it does not decompose: the two edits are the
operand set and the engine of one substitution, and separating them would gate
two children neither of which is the claim.

Nothing else moves.  Three further mechanisms are ported, priced and
default-off (`HOIST_FOLDED_WEIGHT_STACK`, `USE_CRELU_SPLIT`,
`USE_PRECOMPUTED_CM`); off must mean off, with no fragment of any of them
evaluated under a false flag.  Turning any one on creates a different child
that is gated separately.

Shipped constants: `USE_FLOOR = True`, `FLOOR_MAX_LEVELS = 4`,
`FLOOR_WORKSPACE_MIB = 192.0`.

The score signature is a lower cost multiplier on nearly unchanged predictions.
In the linear multiplier regime the per-network identity is
`score_child/score_parent = (MSE_child/MSE_parent) * (C_child/C_parent)`;
ratios are computed from paired per-network records, never by multiplying
unpaired aggregate ratios.

## Declared envelope, and where its bounds come from

Two numbers in the incumbent gate were the incumbent's own measurements
promoted to clauses.  They are restated here at this candidate's declared
envelope, each with its source named.

**Operator workspace: DECLARED 192.0 MiB.**  Self-declared by this candidate
(`FLOOR_WORKSPACE_MIB`), and it is a real bound rather than a report: the
operator sizes its row block from it, so the declaration determines the
allocation instead of describing it.  Measured high-water is 191.9745 MiB
(pooled scratch, at production geometry), which the gate must reproduce.  The
frozen fallback's 91.4375 MiB workspace is built lazily and must not be
constructed at all on a run the depth route never leaves.

**Process peak: bounded at `< 512 MiB` under method A.**  This is the tightest
bound that can be sourced, and the sourcing is the substance of the clause.
What the record actually establishes:

- **There is no competition memory ceiling in the record.**  The only
  competition-sourced memory figure is the advertised environment size, 64 GB
  (`sources/reviews/2026-08-12-contest-contract-audit.md`, runtime row,
  evidence state "Current official docs").  No official document in this corpus
  or in the Codex clone states a memory limit.
- **1 GiB is not a competition bound.**  The figure originates in Codex's own
  G1 lane, where `G1_SELECTED_PREDECLARATION.json` writes its own
  `static_resource` stop condition as "peak at or above 1073741824 bytes fails
  this gate", and `.codex-tmp/g1-static-resource-audit.json` fails a candidate
  against it.  The same lane says in plain words what the number is:
  "Candidate peak working set is `< 1024 MiB` in every process.  The official
  environment advertises 64 GB; 1 GiB remains a deliberately tight local
  engineering ceiling and replaces no contest rule."
  (`experiments/whest/research/CALL_FUSION_RESOURCE_PREDECLARATION.md`, gate 6.)
- **512 MiB is self-imposed too — and it is the campaign's standing gate, not
  the incumbent's self-declaration.**  It was in force before this lineage's
  incumbent existed, and it has killed candidates in other lineages.  It failed
  the full-height Batched-B operator at 667.328 MiB on 2026-08-06
  (`COMPRESSION_SCORE_CALCULUS_20260806.md`), and the V31-G4 lane calls it "the
  retained, self-imposed 512 MiB campaign gate, not the mechanically enforced
  contest limit", excluding `GROUP=8` against it and killing v7 by it
  (`CODEX_V31_G4_EXACT_CALL_FUSION_PROPOSAL_20260811.md`,
  `CODEX_V31_G4_V7_STATIC_KILL_20260811.md`).  It was explicitly *retained* on
  2026-08-11, three days after the 64 GB grader intel landed and called the
  memory worry moot (`HOSTED_INTEL_20260808.md`).

Both candidate ceilings are self-imposed engineering choices and neither is
law.  A gate must pick one, and a verifier does not get to pick the looser of
two self-imposed bounds because the tighter one is inconvenient for the
candidate in front of it.  The clause therefore binds at the tightest sourced
standing bound, 512 MiB.

**Named upgrade path.**  Re-declaring the campaign memory ceiling is an owner
decision, not a verifier's.  If the owner re-declares it — at 1 GiB, matching
the Codex lane, or at any figure justified against the 64 GB environment — this
clause moves with it and the candidate is re-adjudicated against the new
number without re-running anything else.  What a verifier can supply is the
measurement and the bound the record currently supports.

**Method A, the measurement instrument.**  The clause is measured exactly as
the incumbent's was: an isolated, single-thread process; one estimator; one
`setup` and one `predict` on fresh synthetic width-256 depth-32 He weights at
`n_base = 32256` (all 64,512 antipodal paths); process-wide `PeakWorkingSetSize`
via `K32GetProcessMemoryInfo`, read from inside the live process.  Single-thread
is part of the instrument and not a detail: the same probe with a default
16-thread BLAS pool reads about 68 MiB higher on every route, incumbent
included.  Before any candidate figure is quoted, the instrument must reproduce
the incumbent's published receipt (474.301 MiB,
`ROW_BLOCKED_WINOGRAD_REPORT.md`; 474.859375 MiB, `GATE_A_DECISION.md`) to
within 2%.

## Gate A: no-truth production/package screen

All must pass before any official child run.

1. **Custody and manifest.**  The incumbent tree matches the seven custody
   hashes and mtimes before and after the run; `candidate_source/` contains
   exactly the eight manifest modules at their declared hashes; the import
   closure of `estimator.py` is those eight and nothing else; `n_base` is
   32256.
2. **Package import and validation.**  Package import and WHest
   `validate`/`validate-package` pass without network.
3. **Static bills.**  Static bill checks and row-partition identities reproduce
   the screened operator with zero mismatches, and **the selected bill is never
   above direct** — swept over every reachable shape, on the depth route and on
   the fallback it delegates to.  The static bill must equal the metered
   FlopScope bill on shapes spanning both routes.
4. **Exactness parity.**  Full synthetic parent/child prediction relative
   Frobenius `<= 2e-5`, maximum absolute finite, depth-32 relative `<= 2e-5`,
   and **ReLU mismatch fraction `<= 2e-4`**.
5. **Cost and time.**  Full synthetic effective-compute ratio `<= 0.98`,
   setup `< 4 s`, predict `< 20 s`.
6. **Envelope.**  Operator workspace high-water `<= 192.0 MiB` declared,
   measured across a whole predict rather than read at the end of one; the
   frozen fallback is never constructed on a depth-route run; process peak
   `< 512 MiB` under method A, with the instrument validated against the
   incumbent's published receipt in the same session.
7. **Fallback-route folded sums do not alias (the D1 regression).**  On every
   shape where the depth sweep declines *and* the frozen fallback selects its
   preallocated-output route, two and three products held live and summed must
   equal the float64 sum to `< 1e-5` relative, the results must not be bitwise
   equal, and they must not share a buffer address.  The regression must be
   demonstrated to fail against a mutant with the copy-out removed; a check
   that passes on both the shipped operator and that mutant does not discharge
   this clause.
8. **Archive.**  The candidate archive contains only the eight declared Python
   files plus its generated manifest, with no dataset, truth, cached result,
   credential, network, subprocess, or undeclared binary payload — and no
   compiled bytecode, per the hygiene clause.

## Gate B: frozen paired public-100 score

Only after Gate A passes, run the unchanged candidate once on public rows
0..99 with the same dataset, split, seed, budget, subprocess runner and full
detail as the cached parent.  All must pass:

1. exactly 100 child records with indices 0..99 and zero failures;
2. every output and score is finite; maximum child `C < 258.4B`;
3. per-network `|MSE ratio - 1| <= 5e-4` and aggregate `<= 1e-4`;
4. mean official adjusted child score is at most `0.98` times the cached
   parent's mean adjusted score;
5. a 1,000,000-resample paired network-cluster bootstrap (seed 20260819) of
   mean `score_child - score_parent` has a 95% percentile upper endpoint `< 0`;
6. report the per-network true score ratio, `C` ratio, MSE ratio, failures,
   win count, tails, percentile summaries, and confidence interval.

The package may be retained as an **unsubmitted validated child** only when
both gates pass.  No leaderboard submission occurs in this branch.  If a gate
fails, preserve the exact algebra, bill proof, and any passing parity/memory
components; localize the failed production, runtime, or score link without
dismissing the operator family.

## Residual risk this gate does not retire

- **Wall time, not compute.**  The C law excludes backend time, so effective
  compute improves while wall time per predict rises about 4.4x against the
  incumbent.  The contest-contract audit records "about 30 s import/setup per
  worker, 60 s per `predict`, 45 min submission total" from current official
  docs; at the measured single-thread per-net wall this candidate spends most
  of that 45-minute total on 100 networks.  Neither the 20 s clause nor the
  score sees this; a runner does.
- **The parent-of-record is unverifiable from this corpus.**  The incumbent
  gate's four frozen parent-tar hashes match nothing on disk.  Custody here is
  anchored to the on-disk incumbent bytes, which proves a verification run did
  not disturb the incumbent but does not prove the on-disk incumbent is the
  promoted tar.  Settling check: recover
  `submission_random32256_20260806.tar.gz` and compare.
- **`PeakWorkingSetSize` is a granted-working-set counter, not an allocation
  bound.**  It moves with host memory pressure and with BLAS pool size.  The
  single-thread condition and the incumbent-receipt validation exist to make it
  comparable; they do not make it exact.

---

## ADDENDUM 2026-08-19T06:12:13Z — owner ruling on the A.6 ceiling

The owner re-declared the campaign memory ceiling at 1 GiB (1,073,741,824 bytes) via
the upgrade path this gate names (see AGENT_CHANNEL.md 2026-08-19T06:12:13Z). Clause A.6 therefore
binds at 1 GiB: the candidate's measured 616.02 MiB median / 616.95 MiB max isolated
single-thread process peak PASSES. D-A6 is discharged by ruling. D-A3a and D-A3b
remain blocking pending the round-4 verdict.
