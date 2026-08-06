# Compression score calculus

## Answer

Compression improves WHestBench performance only when it removes more cost
than estimator efficiency.  In the active (non-floor) score regime,

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
`3.089512726e-8`, a `7.4368x` improvement.  Reducing sample count to reach
that floor would surrender almost exactly the same factor in raw MSE and
would therefore be approximately neutral.

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
Atop random32,256 it needs more than `3.327%` matched MSE reduction, but the
mean-cost arithmetic is not the binding constraint there: adding it unchanged
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
