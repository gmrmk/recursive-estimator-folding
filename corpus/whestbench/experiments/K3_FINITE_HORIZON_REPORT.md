# Factorized K=3 FlopScope adaptation

Status: **killed at the official index-0 premise; not promoted**.

## Frozen mutation verdict (2026-08-06)

The frozen Headroom packet tested one mechanism only: biased finite-memory
BASE K=3 with predeclared horizons `H={2,4,8,12,16}`.  The algebra is correct
and every horizon is legal on public index 0, but accuracy is decisively worse
than both the analytic baseline and the promoted sampler.  No public index
above 0, no locked index, and no private data was read for this screen.

| H | raw final MSE | adjusted | billed F | effective C | residual s | failures |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1.101030e-3 | 1.316207e-4 | 26.522B | 32.516B | 0.05994 | 0 |
| 4 | 1.134838e-3 | 2.451832e-4 | 49.136B | 58.766B | 0.09630 | 0 |
| 8 | 1.243088e-3 | 4.712252e-4 | 89.516B | 103.109B | 0.13592 | 0 |
| 12 | 1.275102e-3 | 6.697348e-4 | 123.436B | 142.865B | 0.19429 | 0 |
| 16 | 1.305302e-3 | 8.311419e-4 | 150.894B | 173.194B | 0.22300 | 0 |

All effective-compute values clear the packet's 258.4B safety ceiling.  H=2
is the best rung, but it is still:

- 14.51x worse in raw MSE than full-covariance Gaussian closure on the same
  public network (`7.5865e-5`);
- 583.1x worse in adjusted score than the promoted random-32,256 champion's
  official-100 score (`2.25708e-7`);
- 488x too inaccurate even under the unattainably favorable assumption that
  its score multiplier could be reduced all the way to the hard 0.1 floor.

Consequently the prespecified `no raw improvement / no plausible adjusted
route` kill condition fired.  A matched 0..4 expansion would only spend more
development data after a >500x premise loss, so it was not run.

## Algebra, dtype, and rank audits

`audit_parity.py` compares the hand-specialized formulas against the
independently generated NumPy port of ARC's
`factored_nonlin_kprop_k3(base=True,use_pK=False)`:

- one-step mean/covariance/factor maximum error: `3.997e-15`;
- complete depth-3/4 state-threading maximum error: `5.190e-15`;
- all five horizon rank sequences exactly match
  `2*n*min(layer,H)`;
- the scored Wick path remains float32 at every order.

The dtype check found and repaired a material accounting bug before scoring:
FlopScope's normal CDF returns float64 even for float32 input.  Without an
explicit cast, every factor state upcast and the dominant matmuls were billed
at 2x.  `estimator.py` now casts the CDF back to `mean.dtype`; float64 parity
tests therefore remain float64 while the scored path remains float32.

The static two-term factor lower bounds also match the official bill closely:
measured-F / lower-bound ratios fall from 1.098 at H=2 to 1.018 at H=16.  The
remaining bill is full-covariance transport, Wick algebra, concatenation, and
reductions.

## Mechanistic diagnostic (non-promotional)

On public index 0 only, the best H=2 displacement from the full-covariance
closure points mostly toward that closure's required correction:

```text
cos(H2 - fullcov, truth - fullcov) = 0.89972
coordinate sign agreement          = 0.58203
oracle scalar coefficient          = 0.19207
oracle scalar fused raw MSE         = 1.44523e-5
```

Thus the connected third-order direction contains signal, but BASE/no-pK
over-amplifies it by roughly `0.89972/0.19207 = 4.68x`.  This explains the
otherwise interesting pattern that shorter memory is best: forgetting damps
an unstable closure expansion.  This is not a win hiding behind engineering;
even the index-0 oracle scalar fusion, granted the truth, has a raw MSE 6.4x
above the maximum raw error permitted by the competition's 0.1 multiplier
floor to beat the champion.  Scaling or hybridization would be a new mutation
and was not silently added to this frozen finite-horizon test.

Auditable artifacts:

- `audit_parity.py`: independent small-shape and chain parity tests;
- `run_smoke.py`, `smoke_metadata.json`: sequential official harness and
  hashes;
- `h{2,4,8,12,16}_official1.json`: full official outputs;
- `analyze_smoke.py`, `smoke_analysis.json`: summary and correction diagnostic.

Key SHA-256 values after the screen:

```text
estimator.py                 ec54ecec8b14edf80826e7051b9eec0bf98fb109198341b1391d33ba6f64b0c5
audit_parity.py              6919eb1daa7305d5f862035c2601911d2ccd703536fae5b920146207e23214bd
smoke_analysis.json          06f5a644c099d09370e1be09eed204aaba942c2c92ae3a8c3ab1863fad6f57fb
smoke_metadata.json          c3103152dfad3e66efdb8c01c7b60d5df805c6311fbf7751a3db4f452baf5e53
packet_k3_finite_horizon.json 56edd0ae22550f34d110640f1181377efc9a38c45c7ea66b9bcc37b1fa5c38ac
```

## Decisive result

The repository's full factorized `SIMPLE`, K=3 algorithm does not fit the
WHestBench Phase-II accounting envelope at width 256 and depth 32.  Every ReLU
adds three width-column blocks to the symmetric CP representation of the third
cumulant.  Before lower-order work, the necessary factor transports cost about
149.787 GFLOP and reconstruction of the `(2,1)` third-cumulant slices costs
about 140.425 GFLOP.  Their 290.212 GFLOP sum already exceeds 272 GFLOP.

The repository's `BASE`, `use_pK=False`, factorized K=3 ablation is feasible.
It adds two width-column blocks per ReLU, tracks no fourth cumulant, and returns
before the power-cumulant-to-cumulant correction.  At the target shape its
corresponding two-term lower bound is approximately:

| Component | FLOPs |
|---|---:|
| Three CP factor transports | 99.858B |
| Required `(2,1)` slice GEMMs through layer 31 | 93.617B |
| Lower bound subtotal | 193.475B |
| Full-covariance linear propagation, conservative | 2.147B |

Elementwise Wick and connected-diagram work adds much less than the two CP
terms.  A first realistic expectation is roughly 196--202B FLOPs.  Because the
final ReLU needs only its mean and does not construct another state, the
largest resident rank is 15,872 and the three float32 factor matrices occupy
46.5 MiB.  These are
analytic predictions; the official FlopScope subprocess remains the authority.

## Exact reduced state and update

The port stores:

- mean `mu`, shape `(n,)`;
- ordinary covariance `C`, shape `(n,n)`;
- symmetric third cumulant
  `T = Sym(sum_r A[:,r] tensor B[:,r] tensor D[:,r])`, with three `(n,R)`
  float32 factor matrices.

For a WHestBench weight matrix `W` stored as `(input,output)`, the exact linear
update in this representation is

```text
mu <- mu W
C  <- W^T C W
(A,B,D) <- (W^T A, W^T B, W^T D).
```

The only nontrivial third-order slices required by the BASE nonlinear closure
are computed without an `n^3` tensor:

```text
T[i,i,i] = sum_r A[i,r] B[i,r] D[i,r]

T21 = ((A*B) D^T + (A*D) B^T + (B*D) A^T) / 3.
```

The ReLU Wick coefficients are evaluated directly from `mu`, `diag(C)`, the
normal density/CDF, and probabilists' Hermite polynomials.  In particular, the
post-ReLU mean is

```text
E[X] ~= w0 + Tiii*w3/6 + Tiii^2*w6/72,
```

where `wk = E[d^k ReLU(G)]` for the matching Gaussian `G`.  The covariance is
the nine connected-diagram `(1,1)` expansion, and the next third cumulant is
the old factorization contracted by `w1` plus two new width-column blocks.  The
source code hard-codes these generated expressions, so the grader needs no
partition library, torch, scipy, or network access.

## Bias class and cheapest falsifiers

This is not the paper's full SIMPLE K=3 estimator.  BASE/no-pK deliberately
omits its fourth-cumulant radial state and power-cumulant correction.  The
upstream repository labels BASE/use_pK=False an ablation and says it is not
expected to attain the main method's MSE.  It must therefore clear:

1. a width 8--16, depth 2--4 parity test against the original torch code;
2. a one-MLP FlopScope smoke test for shapes, finite values, FLOPs, and wall
   time;
3. the matched frozen premise gate against the current estimator, comparing
   raw MSE first and score second.

An optional finite-history variant retains only the newest `H` pairs of factor
blocks.  It is motivated by repeated ReLU `w1` attenuation but is additionally
biased.  Its factor-only lower bounds are approximately 24.2B (`H=2`), 46.7B
(`H=4`), 87.0B (`H=8`), 120.8B (`H=12`), and 148.2B (`H=16`).  These are
useful premise rungs; no horizon should be promoted without a matched gate.

## Files

- `estimator.py`: FlopScope-only BASE/no-pK K=3 port with optional horizon.
- `budget_model.py`: auditable static rank/FLOP/memory model.
