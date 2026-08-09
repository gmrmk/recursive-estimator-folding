# S3 verdict -- cross-net coupled rotations (ledger id: s3_cross_net_coupled_rotations)

Date: 2026-08-09. Compute-runner execution of the predeclared S3 gates.

## OVERALL: KILL (G0a PASS, G0b KILL)

G0a (legality/plumbing) passed: a coupled-ensemble rotation scheme is
implementable purely inside the package's lawful surface. G0b (effect)
failed: neither predeclared coupled construction reached the predeclared
>=10% suite-mean variance reduction (best: block-orthogonal, 4.43%, 95% CI
spanning zero reduction). Per the predeclared gates, the seed is killed at
G0b.

## Deviations from predeclaration

None in arms or gates. Recorded operationalizations (choices the
predeclaration left open, fixed before results were seen):

- K=12 nets (inside the predeclared 8-16), width 64, depth 8, He init.
- Plain fixed orthonormal frame (64 directions) at the champion's
  radial-conditioning radius mean-chi_64 = 7.96825, explicitly permitted
  ("plain random orthonormal frames if the Kerdock loader resists
  rescaling").
- "Per-net marginal variance unchanged (within noise)" operationalized as:
  >=11/12 per-net variance-ratio 95% bootstrap CIs covering 1.0.
- One harness bugfix between the first and final run, before any verdict was
  written: the bitwise-repeat cross-check initially regenerated 50 reps
  against a 250-rep batch; float32 matmul rounding depends on batch size, so
  the check was rewritten to replay the first full 250-rep block on the
  identical execution path. No statistic changed (same seeds, same arms);
  the final run's numbers match the first run's to reported precision.

## G0a -- legality/plumbing: PASS

Question: does OUR code derive the per-net rotation internally, such that a
coupled-ensemble seeding scheme is implementable inside the package -- or
does the grader force externally-supplied independent per-net seeds we
cannot couple?

Finding: the rotation is derived entirely inside participant code. The
grader passes predict only the net object and a budget; the seed->rotation
map is ours, and the setup lifecycle provides a lawful run-level shared
surface (one estimator instance, setup once with grader `ctx.seed`, then
predict for every MLP) on which a coupled bank can be built.

Evidence, quoted:

1. Frozen champion predict derives the rotation itself from `mlp.seed`
   (corpus\whestbench\experiments\v31_guards\package_source\
   kerdock_v3_estimator.py, lines 146-150):

   ```python
   def predict(self, mlp: MLP, budget):
       if mlp.width != 256:
           return super().predict(mlp, budget)
       rotation = self._haar_rotation(int(mlp.seed), mlp.width)
       first_weight = rotation.T @ mlp.weights[0]
   ```

   and the seed->rotation map is a participant-owned static method (same
   file, lines 138-144):

   ```python
   @staticmethod
   def _haar_rotation(seed: int, width: int):
       rng = fnp.random.default_rng(seed)
       raw = rng.standard_normal((width, width), dtype=fnp.float32)
       rotation, triangular = fnp.linalg.qr(raw)
       signs = fnp.where(fnp.diag(triangular) < 0.0, -1.0, 1.0)
       return rotation * signs[None, :]
   ```

2. Setup already lawfully consumes the run-level grader seed
   (corpus\whestbench\experiments\v31_guards\package_source\
   base_estimator.py, line 73): `rng = fnp.random.default_rng(ctx.seed)`.

3. The pinned starter-kit contract, as quoted in the frozen M235
   predeclaration (corpus\whestbench\experiments\
   m235_setup_shared_philox_row_receipt\M235_PREDECLARATION_20260809.md,
   lines 31-43): setup runs before predict, outside the per-predict FLOP
   budget, may perform one-time preparation independent of the particular
   MLP; `code-patterns.md` lines 90-130 "permits setup-time fixed random
   projections seeded from grader `ctx.seed` and forbids participant-chosen
   or time-based seeds"; `whestbench/sdk.py` "defines `SetupContext.seed` as
   one run-level seed shared by all MLPs"; "the pinned worker calls
   `estimator.setup` before constructing the predict BudgetContext". M235's
   entire mechanism ("issue one immutable SRSWOR receipt in the official
   setup lifecycle and reuse that same receipt for every MLP in the run",
   lines 16-18) is premised on one instance serving all nets, and passed its
   own legality review on that basis.

4. The worker replica shows the lifecycle concretely
   (corpus\whestbench\experiments\terra_m160_hostile_deploy\
   m160_cp311_worker.py): `estimator.setup(... seed=int(args.setup_seed)
   ...)` once (lines 298-308), then repeated
   `estimator.predict(mlp, 10**15)` on the same instance (lines 232,
   312-314). Predict receives only `(mlp, budget)` -- no net index, no suite
   size.

Constraints recorded (they shape any implementation but do not block it):

- Assignment of coupled-bank slots to nets must come either from an internal
  predict-call counter (mutable cross-predict state; conflicts with the
  replay bitwise-equality audit invariant at m160_cp311_worker.py lines
  336-337 if the harness ever replays a net) or from hashing `mlp.seed`
  (replay-safe, but slot collisions dilute the coupling).
- Any setup-time randomness must be rooted at grader `ctx.seed` (per the
  quoted code-patterns rule); a coupled bank built from `ctx.seed` complies.

Verdict G0a: coupling IS implementable inside the lawful surface -> proceed
to G0b.

## G0b -- effect: KILL

Harness: run_s3_g0b.py (this directory). 12 synthetic He nets (width 64,
depth 8, seeds 3000001-3000012), cached MC truth (200k samples/net,
cross-checked against a second independent 200k-sample stream, max gap
4.75e-4). Per-net estimate: fixed orthonormal 64-direction frame at radius
mean-chi_64, rotated per net, forward pass, mean over directions x neurons.
2000 replicate ensembles per arm. All arms have exactly Haar marginals by
construction; arms differ only in the joint rotation law.

Arms:
- indep: 12 iid Haar (sign-fixed QR).
- block_orth: one Haar Stiefel frame in V_64(R^768) sliced row-wise into 12
  blocks; each block's orthogonal polar factor is the net's rotation
  (two-sided orthogonal invariance => exact Haar marginals; joint repulsive,
  sum_k B_k^T B_k = I).
- antithetic: 6 iid Haar, pairs (R, -R) (-R is the maximally distant
  rotation, trace inner product -64; negation preserves Haar measure).

Suite-mean error variance (Var over 2000 ensembles of the across-net mean
error):

| arm        | suite var    | ratio vs indep | 95% CI           | reduction | per-net marginal CIs covering 1 |
|------------|--------------|----------------|------------------|-----------|--------------------------------|
| indep      | 2.2252e-05   | 1 (ref)        | --               | --        | --                             |
| block_orth | 2.1267e-05   | 0.9557         | [0.8762, 1.0428] | 4.43%     | 12/12                          |
| antithetic | 2.2314e-05   | 1.0028         | [0.9208, 1.0928] | -0.28%    | 10/12                          |

Gate: PASS requires >=10% suite-mean variance reduction with unchanged
per-net marginals. block_orth: 4.43% point reduction, CI includes 0%
reduction, split-half ratios 1.037 / 0.874 (inconsistent direction ->
consistent with noise). antithetic: null effect (split-half 1.009 / 0.997).
Per-net marginal variances unchanged as required (block_orth 12/12;
antithetic 10/12 -- within the expected multiple-testing miss rate for exact
marginals, and moot given the effect failure). Neither arm passes.

Verdict G0b: KILL.

## Cross-checks (two-signal discipline)

- Var(suite mean) recomputed via the covariance-matrix quadratic form
  (1/K^2) 1'Cov1: gap 0.0 / 6.8e-21 / 3.4e-21 vs the direct variance across
  the three arms (independent code path, same number).
- Bitwise repeat of the first 250-rep block of every arm from seeds:
  identical in all three arms.
- Truth re-derived from a second independent MC stream: max |t1-t2| =
  4.75e-4 across the 12 nets (truth values span 0.247-0.981; the gap is a
  constant per-net offset common to all arms and cannot affect variance
  ratios).
- Split-half variance ratios reported above.

## Limitations

- Reduced shape (width 64, depth 8, 12 nets, 64 directions), as the
  predeclaration permits; the coupling question is about the joint rotation
  law, but the null result is formally established at this shape, not at the
  hosted 256x32x~100 shape.
- Mechanism reading of the null: for He-random nets the first weight is
  rotation-invariant in law, so the ensemble-averaged estimator fluctuation
  as a function of R is constant -- there is no systematic error component
  shared across nets for a coupled ensemble to cancel; any across-net
  anticorrelation must come from realized-suite alignment, which is what the
  observed ~0-4% (noise-level) effects reflect.
- The hosted score, per the M235 predeclaration (lines 95-96), "averages
  per-MLP squared losses" -- even a genuine suite-mean signed-error variance
  reduction would reach the hosted score only through second-order
  covariance terms, a further headwind not tested here because G0b already
  killed on the predeclared metric.
- The per-net estimator is a reduced proxy (no pilot rescue, no tangent
  correction, fixed-radius frame bias common to all arms); marginal Haar-ness
  of every arm is exact by construction, so the arm comparison is unbiased.

## Artifacts

- run_s3_g0b.py -- harness (this directory)
- s3_results.json -- full numbers, config, seeds, cross-checks
- s3_errors.npz -- raw (2000 x 12) error matrices per arm + cached truths
- S3_VERDICT.md -- this file
