# M152: generated-only noise2noise cross-risk analytic weight student

Status: **KILLED BEFORE EXECUTION.** This is a frozen source-only mathematical protocol. It authorizes no reference generation, target inspection, fitting, score calculation, submission, or champion change.

## One mechanism

M152 is exactly the existing 50-column target-free analytic message bank in `equivariant_weight_student/model_core.py`, followed by one universal ridge readout. It is not a new GNN, feature search, response/Jacobian model, ensemble, per-MLP fit, or adaptive sampler.

For a generated width-256 depth-32 bias-free ReLU MLP W, let a(W) be the full-covariance Gaussian anchor, s(W)>0 its terminal preactivation scale, and

```text
phi(W,o) = [1, a_o/s_o, local_1:16(W,o), h_1:32(W,o)] in R^50
q_beta(W,o) = s_o phi(W,o)^T beta
G_beta(W,o) = a_o + q_beta(W,o).
```

local and h are the frozen target-free code: h is a fixed-seed 32-channel recurrence over signed, absolute, and squared messages of the gauge-normalized edge matrix. One 50-vector and a train-fold normalizer are shared over all MLPs and outputs. This is strictly weaker than the prior per-MLP least-squares oracle.

## f32 estimand and independent references

The estimand is explicitly the f32 fixed-radius spherical program, not silently the ideal Gaussian integral:

```text
T_f32(W) = E_U [F32(rho_256 U;W) + F32(-rho_256 U;W)] / 2,
U ~ Unif(S^255), rho_256 = 15.984382666608527.
```

F32 is direct 32-layer `flopscope.numpy.float32` matmul/ReLU arithmetic with the reduction semantics specified by `m145_direct_f32_reference.py`. Finite precision is not asserted to preserve real-arithmetic radial homogeneity, so this protocol makes no continuous-Gaussian claim.

For 32,256 Kerdock lines D and an independently sign-corrected Haar matrix Q_b:

```text
R_b(W) = mean_{d in D} [F32(rho_256 Q_b d;W) + F32(-rho_256 Q_b d;W)] / 2.
```

Every fixed d has Q_b d uniformly distributed on the sphere. Hence E[R_b|W]=T_f32(W), although points within a rotated design are dependent. R1 and R2 require distinct PCG64 streams, QR draws, buffers, reductions, and process state; none may be shared with network generation, feature extraction, fitting, or evaluation. Q may be made in f64 only; points are scaled then cast to f32 before direct forward evaluation.

## Unbiased noise2noise loss

Let r=T_f32-a and Y_b=R_b-a=r+e_b. Conditional on W, require E[e_b|W]=0, e1 independent of e2, and both independent of beta and training randomness. For K pairs:

```text
L_cross(beta) = 1/(N_train K 256) sum_i sum_k
  <q_beta(W_i)-Y_i,k,1, q_beta(W_i)-Y_i,k,2>
  + lambda ||beta_nonconstant||^2.
```

With delta=q_beta-r, E[<delta-e1,delta-e2>/256 | W,beta]=||delta||^2/256. The exact identity

```text
<q-Y1,q-Y2> = ||q-(Y1+Y2)/2||^2 - ||(Y1-Y2)/2||^2
```

shows that its gradient is precisely the weighted ridge gradient on the pair mean; the last term is beta-independent. The inference program is always a+s phi^T beta and never consumes a reference.

For Sigma=Cov(R_b|W),

```text
Var(L_pair|W,beta) = [2 delta^T Sigma delta + tr(Sigma^2)] / 256^2
Cov(grad_q L_pair|W,beta) = 2 Sigma / 256^2.
```

The tr(Sigma^2) term remains near a good fit. It cancels exactly from a common-reference candidate-minus-anchor risk difference. Negative finite cross-risk values are retained without clipping or replacement.

## Frozen generated split

No M152 data exist. If separately unlocked, generate 32 f32 Gaussian-He MLPs: 32 matrices of shape 256x256 with N(0,2/256) entries, PCG64 seed 152000000+i for i=0..31.

```text
train: 0..15       development: 16..23       test: 24..31.
```

All outputs of an MLP remain in its group. Each MLP receives four independent R1/R2 pairs: pairs 0--1 fit the train/capacity oracle and pairs 2--3 independently evaluate it. The canonical UTF-8 table uses

```text
i|split|k|152100000+100*i+2*k|152100000+100*i+2*k+1\n
```

in i,k order including its final newline. It is 3,832 bytes and its SHA-256 is `e481000cc0d500d34186f0e489d59c12270c55a137fc4d0afe233e324a53a215`. Development selects lambda only from {1e-6,1e-4,1e-2,1,100}; all normalizers are train-only and test is one-shot after hashes are sealed.

## Noise, capacity, and rejection gates

For D_k=R_k,1-R_k,2, the label variance for the mean of all 2K references has estimator

```text
V_label = (1/(4 K^2 256)) sum_k ||D_k||^2,
E[V_label|W] = tr(Sigma)/(2K*256).
```

The held-out anchor cross-risk is L_anchor=(1/(K*256)) sum <a-R1,a-R2>. Every split aggregate must be finite with positive L_anchor, and each label-noise estimate must be <=0.005 L_anchor. No replicate increase after label inspection is allowed.

The non-deployable capacity oracle receives a separate 50-vector per MLP, fit only on pairs 0--1; it therefore upper-bounds the universal ridge. To pass to a training premise it would have to pass every condition:

1. Oracle held-out cross-risk / anchor cross-risk <=0.05 on both development and test, with whole-MLP bootstrap upper-90 <=0.08.
2. At least 28/32 MLPs have positive held-out paired gain; none is removed or refit.
3. Universal grouped ridge has test ratio <=0.10 and upper-90 <=0.15.
4. Semantic, independence, replay, finite, source-hash, symmetry, cost, and resource gates all pass. A nonpositive bootstrap anchor denominator is ambiguous and fails.

The 5% oracle screen is deliberately much weaker than a competition claim. It would only justify a new generated premise, never public-label or deployment work.

## Symmetry and gauge contract

All non-scale phi coordinates must be invariant to input O(256) change and positive hidden gauge, and equivariant to hidden/output permutations. Audit a fixed arbitrary beta without labels:

- W0 -> Q W0: prediction unchanged.
- W0 -> W0 P0 and Wl -> P(l-1)^T Wl Pl: final output permutes by P31.
- W0 -> W0 D0, Wl -> D(l-1)^(-1) Wl Dl, final W31 -> D30^(-1) W31: prediction unchanged.
- Final W31 -> W31 Dout: prediction co-scales by Dout.

Every transform must have maximum absolute error <=2e-8 and normalized RMS <=1e-6 using max(RMS(expected),1e-8). No near-zero relative-error loophole is permitted.

## KILL disposition

**KILL M152; do not generate the 256 references.** The unchanged 50-column representation already had generated-only cleanroom evidence with a stronger per-MLP target oracle: MSE 1.126683597e-5 versus the cited strict reference 1.544730044e-7, 72.9x too large. Its universal ridge was 2.144424096e-5. Relative to its generated anchor, the oracle retained about 17.8% of error, missing this protocol's permissive 5% capacity gate.

The prior independent antithetic spherical-MC target was not an M152 f32 result and cannot establish f32 equality at 1e-7. It does establish that a new cross-reference campaign would add label variance without adding weight information or capacity to the same weaker mechanism. The f32 semantic fixture is also unresolved. This is a conservative pre-execution kill of this exact mechanism, not a claim about richer equivariant models.

No public truth/labels, leaderboard feedback, private data, scorer, API, reference vector, target MSE, submission, or champion state was opened or changed for M152.

