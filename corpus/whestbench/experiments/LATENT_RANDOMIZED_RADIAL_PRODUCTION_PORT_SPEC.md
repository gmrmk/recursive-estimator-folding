# FlopScope production-port and quantization specification

Status: design only. The n=128 width-scaling candidate survived, but this document authorizes neither official-data access nor a public-row run.

## 1. Estimator contract

Implement a `BaseEstimator` subclass with:

```python
def setup(self, ctx): ...
def predict(self, mlp, budget): ...
```

`predict` must return `fnp.stack(layer_means, axis=0)` with shape `(L, n)`; for the target task this is `(32, 256)`. The offline screening closure returned only the last layer, so production parity must explicitly test every layer before any official run.

Use one component initially:

- mixture weights `(1,)`, value 1;
- means `(1, n)`, all zero;
- covariances `(1, n, n)`, identity.

After the first compression and thereafter, q=3:

- mixture weights `(3,)`, exactly `1/3` up to float error;
- means `(3, n)`;
- symmetric covariances `(3, n, n)`.

All inference arrays and constants must be `float32`, unless FlopScope requires an integer type for indices. Accidental float64 promotion is a rejection condition for the port because it changes memory, time, and possibly billing.

## 2. Frozen n=256 radial rule

Store these constants as float32 in `setup`:

```text
radii  = [15.29310401749476, 16.706972273688994]
weights = [0.5110727989792762, 0.48892720102072385]
```

They are the positive two-node quadrature for the chi distribution in 256 dimensions, matching radial moments zero through three. Each radial node is paired with both signs and every frame column, with conditional weight `radial_weight / (2*n)`.

## 3. Randomness and no-best-pick policy

The validation bank is permanently frozen at:

```text
104729, 130363, 155921, 196613
```

The production estimator may pay for only one Haar draw per layer. Averaging four full estimator predictions would exceed the 80B target and is prohibited. Selecting the best observed seed is also prohibited.

Use a preregistered, seed-blind selection policy: map the task-provided MLP seed through a fixed 64-bit SplitMix transform and take the low two bits as the index into the frozen four-seed bank. If no stable MLP seed is exposed by the interface, use `ctx.seed` in the same mapping. This distributes rows over all four frozen modes without consulting weights, labels, predictions, or scores. Record the input seed, selected slot, and master seed in local diagnostics.

Within a prediction, initialize exactly one FlopScope RNG from the selected master seed and draw one `(n,n)` standard-normal matrix per layer in order. Obtain the Haar frame with:

```python
raw = rng.standard_normal((n, n), dtype=fnp.float32)
Q, R = fnp.linalg.qr(raw)
sign = fnp.where(fnp.diag(R) < 0, -1.0, 1.0)
Q = Q * sign[None, :]
```

Use the same `Q` for every q component at that layer. Generate it inside the billed prediction path; moving QR into unbilled setup would create an accounting ambiguity. NumPy/Philox and FlopScope RNGs need not emit identical frames, but pre-public parity must establish distributional equivalence over all four frozen master seeds.

## 4. Exact per-layer tensor plan

Let `W` be `(n,n)`, component means `(q,n)`, component covariances `(q,n,n)`, and q<=3.

1. Linear propagation:

   ```python
   pre_mean = means @ W                                  # (q,n)
   temp = covariances @ W                               # (q,n,n)
   pre_cov = fnp.swapaxes(W, 0, 1) @ temp               # (q,n,n)
   pre_cov = flops.as_symmetric(pre_cov, symmetry=(1,2))
   ```

2. Symmetric square root:

   ```python
   evals, evecs = fnp.linalg.eigh(pre_cov)               # (q,n), (q,n,n)
   evals = fnp.maximum(evals, 0.0)
   root = (evecs * fnp.sqrt(evals)[:, None, :]) @ fnp.swapaxes(evecs, 1, 2)
                                                               # (q,n,n)
   ```

3. Shared Haar orientation and cubature:

   ```python
   oriented = root @ Q[None, :, :]                      # (q,n,n)
   directions = fnp.swapaxes(oriented, 1, 2)            # (q,j,n)
   delta = radii[None, :, None, None] * directions[:, None, :, :]
                                                               # (q,2,j,n)
   plus  = fnp.maximum(pre_mean[:,None,None,:] + delta, 0.0)
   minus = fnp.maximum(pre_mean[:,None,None,:] - delta, 0.0)
   child_means = fnp.stack((plus, minus), axis=2).reshape((-1,n))
                                                               # (4*q*n,n)
   child_weights = (...).reshape((-1,))                # (4*q*n,)
   ```

   At steady state and n=256, `M=4*q*n=3072` child points. Do not allocate child covariance matrices: every child is a deterministic point.

4. Append the global post-ReLU mean for this layer before compression:

   ```python
   layer_mean = child_weights @ child_means             # (n,)
   ```

5. Compress to q=3 using the q3 rule in section 5.

Only after all layers return `fnp.stack(layer_means, axis=0)`.

## 5. Vectorized q3 compressor

The compressor must contain no Python progress loop. Its fixed tensor shapes at target width are child weights `(3072,)`, child means `(3072,256)`, allocation `(3,3072)`, output means `(3,256)`, and output covariances `(3,256,256)`.

Compute global moments without materializing an `(M,n,n)` tensor:

```python
mu = child_weights @ child_means                         # (n,)
raw2 = fnp.einsum("m,mi,mj->ij", child_weights, child_means, child_means)
cov = raw2 - mu[:,None] * mu[None,:]                    # (n,n)
evals, evecs = fnp.linalg.eigh(flops.as_symmetric(cov, symmetry=(0,1)))
direction = evecs[:, -1]                                # (n,)
score = (child_means - mu[None,:]) @ direction          # (M,)
order = fnp.argsort(score)
```

Apply a deterministic eigenvector gauge (largest-absolute coordinate positive). If the leading eigengap or score spread is smaller than a relative tolerance times its own spectral/score scale, replace scores with a constant so sorting falls back to original point order. Do not use an absolute `max(scale, 1)` threshold; it breaks positive-scale equivariance.

After sorting, use cumulative mass to construct a vectorized three-bin fractional allocation matrix `(3,M)` at boundaries `1/3` and `2/3`. This permits a boundary point to split fractionally across adjacent bins and guarantees exact bin mass. Assert in eager/unit-test execution that all three masses exceed the relative tolerance. The production graph must have a safe denominator even if that assertion cannot be represented symbolically.

Then compute:

```python
bin_w = allocation * sorted_weights[None,:]              # (3,M)
mass = fnp.sum(bin_w, axis=1)                            # (3,)
new_mean = (bin_w @ sorted_means) / mass[:,None]         # (3,n)
new_raw2 = fnp.einsum("bm,mi,mj->bij", bin_w, sorted_means, sorted_means)
new_raw2 = new_raw2 / mass[:,None,None]                  # (3,n,n)
new_cov = new_raw2 - new_mean[:,:,None] * new_mean[:,None,:]
new_cov = flops.as_symmetric(new_cov, symmetry=(1,2))
new_weights = fnp.full((3,), 1.0/3.0, dtype=fnp.float32)
```

This is the production equivalent of the tested zero-progress guard: allocation is finite and noniterative, so a zero-weight last point cannot trap the reducer.

## 6. FlopScope call inventory

The target call graph per layer is:

- one `(q,n) @ (n,n)` mean propagation;
- two batched covariance sandwich matmuls over `(q,n,n)`;
- one batched `fnp.linalg.eigh` on `(q,n,n)` and one batched root reconstruction matmul;
- one RNG draw `(n,n)`, one `fnp.linalg.qr` on `(n,n)`, one `fnp.diag`, one sign correction;
- one batched `(q,n,n) @ (n,n)` orientation matmul;
- elementwise formation and ReLU of `(q,2,2,n,n)` before flattening to `(M,n)`;
- one weighted-mean matmul and one `fnp.einsum("m,mi,mj->ij", ...)`;
- one `fnp.linalg.eigh` on `(n,n)`, one `(M,n) @ (n,)` projection, `fnp.argsort`, gather, and cumulative-mass allocation;
- one `(3,M) @ (M,n)` bin-mean matmul and one `fnp.einsum("bm,mi,mj->bij", ...)`;
- constant-size normalizations and covariance centering.

Mark every covariance result with `flops.as_symmetric` immediately after construction. Losing symmetry metadata can change both the chosen kernel and billed work.

## 7. Cost envelope

The preregistered conservative arithmetic model for q=3, n=256, L=32 is:

| Term | Operations |
|---|---:|
| covariance sandwiches | 6,442,450,944 |
| symmetric square roots | 14,495,514,624 |
| shared Haar QR | 4,831,838,208 |
| compressor eigensolver | 4,831,838,208 |
| child moment passes | 25,769,803,776 |
| node formation | 100,663,296 |
| **Subtotal** | **56,472,109,056** |
| **With 25% contingency** | **70,590,136,320** |

The port is rejected if FlopScope reports 80B or more. Prefer an engineering stop at 76B to retain at least 5% uncommitted headroom.

Cost-tail risks that must be measured before any official row:

- FlopScope may bill batched `eigh`, QR, `einsum`, sort, or gathers differently from the arithmetic model.
- A backend may materialize conceptual `(3,3072,256,256)` intermediates in a poorly fused child-second-moment contraction. Peak memory must be measured, not inferred.
- Float64 constants can silently double memory and alter kernels.
- Missing symmetric metadata may select general eigensolver/matmul paths.
- Generating four Haar banks or averaging four predictions is out of budget; exactly one frozen-bank slot is used per row.
- Moving random-frame construction to `setup` could look like unbilled computation even though it is weight-independent. Keep it in the billed path unless the competition rules explicitly say otherwise.
- RNG implementation differences can change finite-seed behavior. Validate all four modes; never choose one afterward.
- Tiny eigengaps, tied scores, negative roundoff eigenvalues, and fractional boundary mass are numerical tails that require adversarial tests.
- Official input width/depth assumptions must be asserted. Any fallback for other shapes must have an independently accounted cost.

## 8. Quantization ladder

Quantization is allowed only when it preserves the measured operator, not when it substitutes a new untested estimator.

Advance monotonically through these rungs; each rung must pass before the next begins:

1. **FP32 reference port.** All state, QR, eigensolvers, moments, and output in float32. Establish layer-by-layer NumPy/FlopScope parity on synthetic n<=16 cases for all four frozen seeds.
2. **FP16/BF16 point formation only.** Quantize `directions`, `delta`, and the pre-ReLU point tensor; immediately accumulate child means and all moments in FP32. This attacks the largest transient tensor without quantizing covariance state or spectral decisions.
3. **FP16/BF16 storage, FP32 spectral compute.** Store component means/covariances compressed, but upcast before covariance sandwiches, QR, `eigh`, score projection, bin moments, PSD clipping, and output. Accept only if the backend accounts the casts and the memory saving is real.
4. **Blocked covariance storage.** If FlopScope supports it honestly, store only the symmetric triangle or block-symmetric form while presenting the same mathematical covariance. Never claim a flop reduction unless the billed operator actually exploits it.
5. **Int8 is experimental and off by default.** Weight/covariance int8 introduces scale calibration and PSD failures, while QR/eigendecomposition still require floating point. It can be explored only on synthetic data as a new candidate with a separately frozen gate.

For each rung, require:

- maximum layer-mean relative L2 drift <= `2e-3` and maximum absolute drift <= `2e-4` against the FP32 port on scale-normalized synthetic tests;
- aggregate loss ratio versus FP32 <= `1.02` across the four frozen rotation modes and at least 3/4 per-network non-regressions on a newly frozen synthetic bank;
- covariance minimum eigenvalue >= `-2e-5 * max(trace(cov)/n, tiny)` after symmetrization;
- radial moment, permutation coupling, positive-scale gauge, sign-pair, and reducer mass/progress tests still pass;
- actual FlopScope cost and peak memory decrease or the rung is discarded.

Do not use per-layer, per-network, or per-row calibration obtained from truth. Quantization scales must be analytic from current tensors (for example max-absolute or RMS) or frozen from synthetic-only calibration before evaluation.

## 9. Required tests before authorization

1. Shape tests at n in `{1,2,3,8,16}` and varying depth, including returned `(L,n)` shape.
2. Exact component-weight and bin-mass checks; deliberate zero-weight tail and all-tied-score cases.
3. PSD/symmetry checks after every compression, including rank-deficient covariance.
4. Positive-scale tests at `1e-6`, `0.375`, and `1e6`.
5. Coupled coordinate-permutation tests using the correspondingly transformed Haar frame.
6. QR orthogonality and sign-gauge tests for all four master seeds.
7. Layer-by-layer NumPy/FlopScope parity in FP32, then drift tests for each quantization rung.
8. Target-shape cost-only and peak-memory run on synthetic weights, with no truth or scorer.
9. Freeze code, dependency versions, cost report, RNG policy, and hashes.
10. Stop and request parent authorization. Only then may any official/public row be evaluated.

## 10. Promotion boundary

Passing this spec would establish a reproducible, billed production candidate. It would still not establish a winning entry until an authorized, rule-compliant official evaluation confirms it. Failures must be reported locally—numerical, cost, memory, or accuracy—not relabeled as a win.
