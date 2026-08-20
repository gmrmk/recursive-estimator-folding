# Compression score calculus

## Answer

Compression improves WHestBench performance only when it removes more cost
than estimator efficiency.  For one matched network in the active
(non-floor) score regime,

```text
score = MSE * C/B,
```

so a compressed child with cost ratio `r_C=C_child/C_parent` and raw-MSE
ratio `r_V=MSE_child/MSE_parent` has

```text
score_child / score_parent = r_C * r_V.
```

The strict promotion condition is therefore

```text
r_C * r_V < 1.
```

This is the only compression claim that matters.  File size, parameter count,
nominal precision, or state rank are not objectives unless they reduce billed
work or residual time without a compensating loss of statistical efficiency.
For the aggregate benchmark this product must be evaluated per network and
score-weighted: the ratio of aggregate MSEs times the ratio of aggregate costs
is not generally the aggregate score ratio.

## Concrete thresholds

| cost retained `r_C` | largest tolerable MSE ratio `r_V` | interpretation |
|---:|---:|---|
| 0.90 | 1.1111 | a 10% cost cut may spend at most 11.11% extra MSE |
| 0.75 | 1.3333 | a 25% cost cut may spend at most 33.33% extra MSE |
| 0.50 | 2.0000 | halving cost may at most double MSE; equality is neutral |
| 0.25 | 4.0000 | quarter cost may at most quadruple MSE; equality is neutral |

If cost is reduced solely by taking fewer Monte Carlo paths, the usual
`MSE proportional to 1/N` law gives `r_V approximately 1/r_C`, hence
`r_C*r_V approximately 1`: no first-order score gain.  Spending the saved
cost on more paths gives the same conclusion.  A winning compression must
reduce **cost per unit residual variance**, not merely sample count.

With a hard multiplier floor, the exact ratio is

```text
score_child/score_parent
  = r_V * max(0.1, r_C*C_parent/B)
          / max(0.1, C_parent/B).
```

The current promoted random32,256 sampler has raw MSE
`3.089512726e-7`, adjusted score `2.257079776e-7`, and mean multiplier
`0.7436830511`.  An impossible ideal exact compression all the way to the
`0.1` floor, with identical predictions, would score
`3.089512726e-8`, a `7.3056x` improvement from the observed aggregate adjusted
score.  The mean multiplier divided by `0.1` would give `7.4368x`, but that is
not the aggregate ratio because per-network MSE and multiplier are correlated.
Reducing sample count to reach that floor would surrender almost exactly the
same factor in raw MSE and would therefore be approximately neutral.

## Compression types

### 1. Exact arithmetic compression -- immediately useful

This preserves the estimator and changes only how its matrix products and
buffers are represented.

- The deployed child already folds dead, always-on, and kink neurons across
  its last three layers.  This is real compression: it omits provably dead
  work and composes provably linear work while retaining sampled kink paths.
- One or two levels of fused Strassen can reduce billed matrix multiplication
  from fewer/smaller operand-shape calls while leaving the mathematical
  product unchanged apart from floating-point association.  The open issue is
  residual wall-time and allocation/call overhead on ragged active widths.
- Hoisting reshape/copy/allocation work to setup and fusing calls can reduce
  residual-time charging.  These gains are smaller but nearly accuracy-free.

The already-recorded public-100 breakdown makes the bottleneck unambiguous:

| deployed random32,256 quantity | mean/result |
|---|---:|
| total billed arithmetic | `185.4069B` |
| matrix-multiply arithmetic | `184.8217B` |
| matrix-multiply share | `99.6844%` |
| matrix-multiply calls | `215.41` (range 215--216) |
| residual wall time | `0.16875s` mean, `0.23531s` p95 |

Thus buffer-only optimization cannot be the main win.  The first exact child
must reduce the billed geometry of those matrix multiplies while keeping the
number of temporary-producing calls low.

An exact child is promoted by measured billed/residual cost plus numerical
parity; no statistical oracle is needed.

The first whole-row rectangular Strassen child is now also locally falsified,
but it exposes a narrower engineering mutation.  Its full-product L2 hybrid
reduces the visible bill from `8.4392B` to `6.7128B` (`r_C=0.795427`) and is
numerically stable through a fresh depth-32 ReLU chain (`4.10e-6` relative
error; 5 gate changes in 4,194,304 activations).  The Python allocation graph
erases the saving: effective proxies are `8.444B` direct, `9.144B` L1
sequential, `9.602B` L1 fused, and `12.205B` L2 hybrid.  This kills the current
implementation, not the algebra.  A preallocated `out=` or changed Winograd
reconstruction may reopen L1 only if it cuts full-product residual below about
`0.00987s`; retuning the same tile/allocation schedule cannot help.

Preallocation repaired that failed link.  A seven-product Winograd L1 screen
reduced the effective full-call proxy to `0.8821x` direct with negligible
residual time, but seven separate half-width BLAS calls missed the frozen
whole-call wall gate at `1.5587x` direct.  Batching those seven products into
one visible matmul then reduced the billed/effective proxies to
`0.880151/0.885099x`, with float32 relative Frobenius error `6.04e-7` and
`480.94 MiB` conservative peak memory.  Its remaining failure is narrow:
total wall is `1.54559x` direct versus the declared `1.5x` ceiling.  The score
algebra passes while the packed-memory/BLAS throughput does not yet pass; the
next mutation changes only operand packing and layout.

That packing mutation has now failed: its effective proxy still passes at
`0.886148x`, but total wall worsens to `1.70148x`.  Across all three
preallocated variants, depth-32 relative error stays below `2.96e-6`, gate
changes stay at most `2/4,194,304`, residual is only `0.263-0.527 ms`, and
conservative peak memory stays below `481 MiB`.  The branch is therefore
localized and closed at the current mechanism.  Allocation/reconstruction is
repaired; the remaining obstacle is one-core half-width BLAS throughput plus
Winograd memory traffic.  Mutation B's `0.885099x` score-side operator is
preserved, but no whole-entry or champion gain is claimed.

An independent whole-entry upper-envelope calculation makes that qualifier
quantitative. Mean effective cost is `202.281790B`, of which `184.821668B`
is billed matmul work. Even granting Mutation B's `0.885099x` effective ratio
to every matmul gives

```text
C_optimistic = 202.281790 - (1 - 0.885099) * 184.821668
             = 181.045546B = 0.8950165x parent.
```

Thus current evidence supports `0%` validated gain and at most about `10.5%`
optimistic whole-entry upside before MSE changes. The actual eligible fraction
is smaller, ragged products dispatch direct, and integrated memory, residual,
and prediction parity remain unmeasured.

A source audit subsequently established that the frozen `1.5x` relative-wall
test is campaign policy, not a scoring rule. FlopScope attributes counted
NumPy/BLAS time to backend time and excludes it from charged residual; total
wall binds through absolute local limits (`30 s` host response and `60 s`
in-context), not comparison with the parent. This does not make Mutation B a
winner. It authorizes a new full-entry synthetic descendant with absolute
setup/predict, effective-cost, memory-liveness, and prediction-parity gates.

That full-entry descendant has now run at the actual `n_base=32256` geometry.
It compresses 16 of 29 hooks and `57.42%` of their direct bill, reducing
analytical work from `170.531B` to `159.493B` and effective compute from
`186.485B` to `175.521B` (`r_C=0.941206`). Whole-prediction parity is
`4.56e-8` relative and predict wall is `4.43s`. The one failure is physical
memory: transient peak working set is `667.328MiB` versus `<512MiB`, although
the end set is `478.883MiB`. The next exact mutation row-blocks Winograd with
a frozen8192-row scratch; row-linearity preserves the bill while planning
workspace falls from `283.94MiB` to about `91.44MiB`.

The fixed-8192-row mutation has now repaired that link. On the same full
synthetic geometry it preserves the exact `11.037909953B` FLOP saving, reduces
measured peak working set to `474.301MiB`, and yields
`C_child/C_parent=0.931714`. Whole-prediction relative drift is `4.28e-8` and
the depth-32 drift is `2.49e-6` with one gate change in `4,194,304`. In the
linear score regime the paired cost ratio permits a raw-MSE ratio below
`1/0.931714 = 1.07329`. That is an engineering tolerance, not evidence the MSE
will rise or that the current champion is already improved. A production port
and paired permitted-development score are the remaining promotion gates.

Those gates now pass in the immutable production port. On the already-touched
public0..99 units, raw MSE is effectively invariant (`r_MSE=0.999982962`) while
mean effective compute falls to `r_C=0.938554853`. Because the score is paired
per network, the observed mean-score ratio is `0.940047616`, not the product of
aggregate ratios. The child scores `2.121762464e-7` versus `2.257079776e-7`,
wins all100 networks, has zero failures and maximum C `222.405B`. A frozen
one-million network bootstrap gives ratio95% CI `[0.936501,0.943476]`.
This is the first validated exact-compression promotion; it remains an
unsubmitted local champion, not a guarantee about the private suite.

### 2. Numeric compression -- mostly useless under this biller

FlopScope charges float16, int8, and float32 at the same arithmetic rate.
Therefore FP16/int8 do not buy a billed-FLOP reduction by themselves.  They
may reduce physical wall time, but can also move ReLU gates and accumulate
depth-dependent error.  FP32 is already the sensible numerical floor unless a
lower precision enables a structurally smaller operator.

### 3. Weight/Jacobian low-rank compression -- wrong target

The fixed Gaussian weight matrices are not low rank.  Truncating them changes
gate patterns at every subsequent layer.  JSpace input-Gram top, bottom, and
complement subspaces all had near-zero correlation with the integration
error; low pointwise Jacobian rank does not imply low rank of the spherical
integration residual.  This compression loses task-relevant directions much
faster than it saves cost.

### 4. Cumulant-state compression -- highest mathematical headroom

The final ReLU mean needs only certain signed contractions of third and fourth
cumulants, not a dense `n^3`/`n^4` tensor.  The strongest cleanroom evidence is:

- a fixed at-most-12-dimensional covariance algebra plus rank 4 retains
  `0.972741` combined standardized fidelity, `0.988152` correction fidelity,
  and `97/97` material correction signs;
- the unrestricted signed rank-4 representation retains `0.986618` combined
  fidelity and `0.995497` correction fidelity;
- a degree-4 conditional response-Gram forms a signed rank-at-most-4
  covariance correction from univariate responses with `95.0349%`
  off-diagonal reconstruction and a conservative `0.5103B` arithmetic target.

These results establish that the **representation** is compressible.  They do
not yet establish a winning estimator because the signed coefficients must be
formed from weights/current state and propagated through all 32 ReLU layers
without constructing the dense tensors or using truth.

The current conservative incremental envelope for the compressed signed
cumulant transport is `8.622B` FLOPs.  Atop the `59.276B` analytic port it
must reduce matched MSE by more than `12.698%` merely to repay its own cost.
Atop random32,256 it needs more than `3.327%` matched MSE reduction on the
maximum-cost planning calculation. At the reported mean effective cost the
analogous scalar threshold is `4.088%`; neither scalar replaces paired
per-network scoring. Mean-cost arithmetic is not the binding constraint there:
adding it unchanged
would exceed the predeclared `258.4B` maximum-compute safety line by `0.710B`
on the worst recorded network.  It must first replace existing work or be
compressed further; it cannot simply be appended.

The first frozen production attempt was therefore:

```text
conditional state per cell:
    mean m
    diagonal residual d
    covariance factors U[0:4]
    <= 7 linear directions
    <= 12 symmetric matrix directions
    rank <= 4 signed k3/k4 cores

formation:
    matrix-free orthogonal/Hadamard probes
    -> small 7x12 and 12x12 cores
    -> PSD/symmetry/gauge-preserving ReLU recurrence
    -> output contractions only
```

It must clear three independent gates:

1. `r_C*r_V < 1` against the deployed sampler at matched total cost;
2. no dense pair-space or cumulant tensor is ever materialized;
3. coefficient formation is weights-only, symmetry-covariant, and stable on
   fresh synthetic networks before any permitted development row.

That first attempt is now locally falsified.  With exact scalar responses
given free by an oracle, 128 constant-modulus probes per cell still retain
`0.926273` combined fidelity, `0.983525` correction fidelity, and `94/94`
material signs.  Yet their design is not identifiable: the minimum recovered
k3/k4 core-rank fractions are only `0.3611/0.2051`.  Every Rademacher or
Hadamard direction has `v_i^2=1/n`, so it is exactly blind to the trace-free
diagonal algebra coordinate.  Antipodal pairing adds zero rank.

More fundamentally, the preserved mean/covariance state does not supply the
directional k3/k4 values on the right-hand side.  The inverse is cheap if those
responses are free (`12.3398B` total), but orthogonal probes do not create the
missing information.  Directly sampling the responses under the 80B envelope
allows at most 10,719 paths, about 670 per conditional cell, with idealized
skewness/excess-kurtosis standard errors around `0.095/0.189`.

Disposition: kill constant-modulus coefficient formation, preserve the
`<=12D` representation.  The next legitimate child must change both links:
use nonconstant-amplitude probes to remove the nullspace **and** derive a
weights-only Price/Hermite higher-moment response recurrence before another
accuracy screen.

The amplitude mutation has now separated those links.  With 128 normalized-
Gaussian sphere lines, the formerly blind diagonal response is material in
every nontrivial cell, condition numbers stay below `53`, exact physical cores
recover below `6e-15` relative error, and downstream combined/correction
fidelity reaches `0.980382/0.991939` with `97/98` signs.  The raw designs still
rank `64/84` and `58/78`, but the missing 20 coordinates are the exact kernels
of cubic/quartic symmetrization: they encode no distinct directional
polynomial.  The literal full-coordinate gate is killed; the amplitude
mechanism is preserved on the nonredundant `64D/58D` quotient.  Its
free-response total is `12.342916B`.  A deterministic quotient proof is the
next geometry rung; weights-only response formation remains the independent
blocking link.

That quotient proof now passes in all 144 cells.  Complete monomial
symmetrization rank, amplitude-design rank, and deterministic quotient rank
agree exactly; the nontrivial physical coordinate counts are `64` and `58`,
with maximum conditions `30.3514/52.5370`.  Response, core, and equivariance
errors stay below `1e-14`, and downstream fidelity/signs are unchanged.  This
certifies prospective coefficient reductions of `23.81%/25.64%`, but it is
not yet a runtime saving because the response-free SVD is still charged.

The first weights/state-only response attempt also isolates the remaining
information gap.  Degree-two Price--Hermite chaos evaluates its k3/k4 trace
identities without dense tensors for a conservative `61.286B` envelope.  It
improves transported-total combined/correction fidelity to
`0.90194/0.96478` with `60/61` signs, but direct conditional fidelity is only
`0.67069` for k3 and `0.16234` for k4.  Thus Q2 is a useful compressed
transport operator, not a faithful response source.  The next rung holds its
factor inversion and total-cumulance map fixed while adding exact Hermite
orders three and four through connected Wick contractions in the certified
quotient.

That Q4 rung is now measured. It improves isolated conditional combined
fidelity from `0.282335` to `0.673419` and k4 from `0.162341` to `0.655277`;
transported combined/correction fidelity reaches `0.931300/0.979659`. The
signal is real, but the child misses the direct `0.80` gate and its literal
connected-feature envelope is `35.115T`, `438.94x` over the `80B` ceiling.
The next changed mechanism conditions on the existing rank-four common
Gaussian factor, where coordinates are independent, then integrates exact
conditional cumulants over only four latent dimensions. This resums the
rectified-Gaussian response instead of increasing finite Hermite order.

The conditional resummation now validates that cost mechanism: a49-node
rank-four Smolyak rule reduces the conservative envelope to `74.427B`, about
`472x` below literal Q4, while transported combined/correction fidelity is
`0.935843/0.979747`. But isolated combined fidelity is only `0.56923`; the
201-node reference reaches `0.70341`, still below `0.80`. The49-node rule is
also insufficiently converged and changes by `0.19931` squared response energy
under an equivalent factor rotation. Thus low-dimensional integration is
preserved as compression, while the Gaussian-copula state is not a faithful
source of the missing conditional response.

Canonical factor-gauge normalization cleanly separates quadrature covariance
from prior fidelity. It reduces the equivalent-rotation defect from `.19931`
to `1.68e-26` and the 49/201 discrepancy from `.12403` to `.07386`, but
isolated combined fidelity is only `.66364` and the canonical 201-node result
is `.67573`. The grid is now stable; the moments-through-two copula prior is
still missing signed higher-order state.

### 5. Static analytic sidecar compression -- screened premise

A clean-room, Gemma-PLE-inspired storage pattern factors the exactly
layer-invariant rectified-Gaussian `Phi/phi` response atlas from small
layer-specific descriptors. The complete package is `66,632` bytes versus a
`2,097,536`-byte duplicated coefficient atlas, with maximum reconstructed
response error `1.994e-7`. Preloading the shared `65.5KiB` atlas during setup
is the correct hot-path arrangement: flash stores immutable data, while CPU
and RAM perform interpolation and reconstruction.

The conservative proxy is `41` operations/query versus `56` for the known
float64-promoted direct path, but a hypothetical native-float32 analytic path
is only `28`. Therefore this is a screened locality/storage operator, not a
whole-estimator score claim. It should be folded only if quantization and
lookup can be fused into an existing moment pass and complete billed plus
residual cost satisfies `r_C*r_MSE<1`.

## Operational conclusion

The answer is not "make the model smaller."  It is:

```text
compress the computation exactly where possible;
compress only the sufficient signed cumulant contractions statistically;
leave the full-rank weights and design geometry alone.
```

That combination can improve performance because it lowers cost per unit of
unexplained final-layer variance.  All other compression is neutral or loses
under the current score law.
