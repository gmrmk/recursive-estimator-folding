# Frozen gate: production row-blocked Winograd descendant

Date frozen: 2026-08-06, before creating this production descendant or
opening any scorer output for it.

This is a `recursive-estimator-folding` mutation of the immutable promoted
`random32256` package.  It changes exactly one mechanism: the two sample-path
matrix-multiplication hooks use the already-screened, exact 8192-row streaming
Batched-B Winograd operator.  Sampling geometry, randomization, analytic
closure, pruning, pilot rules, tangent, output contract, and all other parent
code remain fixed.

## Invariants and firewall

- Objective: reduce the official mean score while preserving the parent
  estimate, with per-network score
  `MSE * max(0.1, C / 272000000000)` and
  `C = billed_FLOPs + 1e11 * residual_wall_seconds`.
- Bias class: exact arithmetic rearrangement apart from ordinary float32
  reassociation, bounded by prespecified parity tests.
- Parent package: `submission_random32256_20260806.tar.gz`, SHA-256
  `1874f9cac4be962dbd4f919bffc38dedf23b428ea6cbd7847a813c87d7ba7333`.
- Parent official artifact: `work/scorefloor_generation/random32256_paired100/
  candidate_random32256_official100.json`, SHA-256
  `b7dbd03e498773f45ed873b3f10cae1e93b99bdfb2d87bb506a891ae29dcf88b`.
- Runtime: Python 3.14.4, NumPy 2.4.6, WHestBench 0.14.0, FlopScope 0.10.0.
  `work/whest-v014/Scripts/whest.exe` SHA-256
  `888a44d9c886df88cf8933398c154e113f530f3dc2705282170820a101dd674a`.
- Budget: 272B per network; safety gate is maximum child `C < 258.4B`
  (95% of budget), zero failures, setup under 4 s, prediction under 20 s.
- Memory gate: process peak working set `<512 MiB`; fixed block rows are 8192.
- Development data, if earned: only the already-touched public full-split rows
  0..99, seed 0.  Rows 600..799 are locked and forbidden; rows >=800 are
  prohibited.  No new row outside 0..99 may be opened.  No API, login,
  submission, private evaluation, or external service is authorized.
- The cached parent result is the frozen paired comparator.  It will not be
  rerun or altered.  The child is one new sequential official CLI run.
- No score observation may change block size, dispatch, thresholds, sample
  count, coefficients, or any source byte.  Any implementation change after
  the score run creates a new child and invalidates these results.

## Frozen paths and source contract

- Work directory: `work/scorefloor_generation/row_blocked_production`.
- Parent extraction: `parent_source/`, extracted from the immutable tar.
- Production source: `candidate_source/`.
- Candidate archive (only if every gate passes):
  `submission_random32256_rowwinograd8192_20260806.tar.gz` in this directory.
- Score output: `candidate_official100.json`; stderr:
  `candidate_official100.stderr.log`; analysis: `paired100_results.json`.

The following four inherited modules must remain byte-identical to the parent
tar manifest:

```text
base_estimator.py   b64376e09279e520465d63c4c0b2933a8edb0ec8eae9d6086c16c1830e7ece4e
fold_estimator.py   0c6187e19cf567d7f7b5658902dc00a123f6219c815e2ea6711589e0a4e9159d
fold3_estimator.py  6952abc0a617e1fb32c64a4483f1539b79933c049f9190984460266bf357e116
orthogonal_fold3.py 24f2eebb1adf37f6be1392de57611c52cbaac7b04e319ff771533da54257796a
```

The parent `estimator.py` (SHA-256
`f2257a988b0df4cdc42cd3ceb21d6f2c7f5f96f4afa278f25c59f090dcc94d87`)
is preserved in `parent_source/`; the candidate entrypoint may only subclass
the same random-frame estimator, keep `n_base=126*256`, allocate the operator
in `setup`, and override `_first_sample_matmul` and `_sample_matmul`.
`row_blocked_winograd.py` and its self-contained shape-only `cost_model.py`
are the only new runtime modules.

## Mechanism and predicted signature

For even `(m,k)` and an even output core `n_c`, the child packs seven right
operands once, streams consecutive even row blocks of at most 8192 through
seven left/product buffers, and writes reconstruction directly into one full
output.  Odd `k` dispatches direct and an odd output has one direct tail.
The shape-only dispatcher selects the child only when its explicit bill is
strictly below direct.

The row-dependent terms are linear in block row count, so splitting preserves
the unsplit Batched-B bill.  The engineering audit predicts, at full geometry:

```text
parent analytical FLOPs     170.530655499B
child analytical FLOPs      159.492745546B
exact saving                 11.037909953B
child/parent effective C     approximately 0.9317 in the frozen synthetic run
operator workspace           exactly 91.4375 MiB
process peak                 474.301 MiB in the frozen synthetic run
```

The score signature should therefore be a lower cost multiplier on nearly
unchanged predictions.  In the linear multiplier regime the per-network
identity is
`score_child/score_parent = (MSE_child/MSE_parent) * (C_child/C_parent)`;
ratios are computed from paired per-network records, never by multiplying
unpaired aggregate ratios.

## Gate A: no-truth production/package screen

All must pass before the official child run:

1. parent tar and cached parent-report hashes equal the frozen values;
2. the four inherited candidate modules equal the parent-tar hashes byte for
   byte, and `n_base` remains 32256;
3. package import and WHest `validate`/`validate-package` pass without network;
4. static bill checks and row-partition identities reproduce the screened
   operator with zero mismatches, selected bill never above direct;
5. full synthetic parent/child prediction relative Frobenius `<=2e-5`,
   maximum absolute finite, depth-32 relative `<=2e-5`, and ReLU mismatch
   fraction `<=2e-4`;
6. full synthetic effective-compute ratio `<=0.98`, process peak `<512 MiB`,
   setup `<4 s`, predict `<20 s`, and fixed operator workspace `91.4375 MiB`;
7. candidate archive contains only the seven declared Python files plus its
   generated manifest, with no dataset, truth, cached result, credential,
   network, subprocess, or undeclared binary payload.

## Gate B: frozen paired public-100 score

Only after Gate A passes, run the unchanged candidate once on public rows
0..99 with the same dataset, split, seed, budget, subprocess runner, and full
detail as the cached parent.  All must pass:

1. exactly 100 child records with indices 0..99 and zero failures;
2. every output and score is finite; maximum child `C <258.4B`;
3. mean official adjusted child score is at most `0.98` times the cached
   parent's mean adjusted score;
4. a 1,000,000-resample paired network-cluster bootstrap (seed 20260806) of
   mean `score_child-score_parent` has a 95% percentile upper endpoint `<0`;
5. report the per-network true score ratio, `C` ratio, MSE ratio, failures,
   win count, tails, percentile summaries, and confidence interval.

The package may be retained as an **unsubmitted validated child** only when
both gates pass.  No leaderboard submission occurs in this branch.  If a gate
fails, preserve the exact algebra, bill proof, and any passing parity/memory
components; localize the failed production, runtime, or score link without
dismissing the operator family.
