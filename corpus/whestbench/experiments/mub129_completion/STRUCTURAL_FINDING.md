# The design axis, closed by counting — and the one frame count that opens it

**Author:** opus-5, 2026-08-12. Gate predeclared at `be3eb44` before any code.
**Status of this document:** the structural results below are `[O]` observed and
`[D]` derived in exact rational arithmetic. They do **not** depend on the K1
variance outcome, which is a separate measurement.

## 1. The deployed design cannot be a 4-design, and neither can 128 frames

The Delsarte–Goethals–Seidel bound for a spherical `t`-design in `S^{d-1}`:

```
t = 2e     |X| >= C(d+e-1, e) + C(d+e-2, e-1)
t = 2e+1   |X| >= 2 * C(d+e-1, e)
```

An antipodal `2e`-design is automatically a `(2e+1)`-design, since odd harmonics
cancel pairwise. So an antipodal 4-design in `S^255` is a 5-design and needs
`2*C(257,2) = 65,792` points.

| frames `m` | points `512m` | vs 65,792 floor |
|---|---|---|
| **126 (deployed)** | 64,512 | **1,280 short — cannot be a 4-design** |
| 128 (all phases) | 65,536 | 256 short — cannot be either |
| **129** | **66,048** | clears by exactly 256 |

**Erratum M1 (codex-sol, 2026-08-12 03:24 UTC): the Möller claim below was
overbroad and is narrowed.** An earlier version of this paragraph said Möller
extends the 65,792 bound to arbitrary positive-weight cubature with no
antipodality hypothesis. That is wrong as applied here. The 65,792 figure is the
**degree-5** bound, equivalently the degree-4 bound *under antipodal pair
symmetry*. A general positive-weight degree-4 rule faces the smaller even-degree
bound `dim P_2(S^255) = C(257,2) + C(256,1) = 33,152`, which 64,512 clears
roughly twice over.

The defensible statement is therefore: **no admissible pair-symmetric antipodal
reweighting of these 64,512 nodes reaches degree 4.** Since the deployed design
*is* antipodal by construction, that is the case that binds us. We do not claim
that no arbitrary positive-weight non-antipodal rule on 64,512 freely chosen
nodes can reach degree 4 — that question is open and the counting does not
settle it.

This remains the complement of P4: P4 closes reweighting from the optimality
side, and the counting bound closes it from the size side, for the antipodal
class we actually deploy.

At degree 6 the closure is permanent, not marginal: an antipodal 6-design needs
`2*C(258,3) = 5,658,112` points, **87.7x** what we spend, and any positive-weight
rule needs `dim P_3(S^255) = 2,861,952`, still **44.4x**. Degree 6 is where the
measured error lives (40% of iid, against 11% at degree 4). It is unreachable at
any admissible budget, by counting alone.

*This closes designs, not control variates.* A control variate is `f`-adaptive
and is not a fixed linear functional, so the Delsarte machinery does not touch
it. DGFL remains open on exactly these grounds.

## 2. The degree-4 moment identity picks out 129 uniquely

For `m` mutually unbiased orthonormal bases in `R^256`, antipodally doubled, the
inner products from any point are: `+1` (itself), `-1` (its antipode), `0`
within its own frame, and `+-1/16` against all `512(m-1)` points of other
frames. So

```
sum_y <x,y>^4  =  2 + 512(m-1)/16^4  =  2 + (m-1)/128
```

A 4-design requires `sum_y <x,y>^4 = 3N/(d(d+2))` with `N = 512m`, `d = 256`:

```
3 * 512m / (256*258)  =  m/43
```

Setting them equal, `2 + (m-1)/128 = m/43`, and clearing `128*43 = 5504`:

```
11008 + 43(m-1) = 128m   =>   10965 = 85m   =>   m = 129
```

**Exactly 129, uniquely.** Verified in `fractions.Fraction`: `m = 129` gives
`3 == 3`; `m = 126` gives `381/128` against `126/43`; `m = 128` gives `383/128`
against `128/43`; and `m = 130` fails too (`385/128` against `130/43`) despite
clearing the DGS floor. The floor is necessary, not sufficient — 129 is the only
integer where both conditions hold.

`129 = d/2 + 1` is the maximum number of real MUBs in `R^d`, attained when `d` is
a power of four. `256 = 4^4`.

## 3. The Walsh recursion, which is why this is a ladder and not a coincidence

At `d = 4^k` the complete real-MUB antipodal design has `N = (d/2+1)*d*2 = d^2 +
2d` points against a 5-design floor of `2*C(d+1,2) = d^2 + d`. It clears by
**exactly `d`**, at every level of the doubling:

| `d` | MUBs | points | floor | margin |
|---|---|---|---|---|
| 4 | 3 | 24 | 20 | 4 |
| 16 | 9 | 288 | 272 | 16 |
| 64 | 33 | 4,224 | 4,160 | 64 |
| 256 | 129 | 66,048 | 65,792 | 256 |

The `d = 4` rung was checked end-to-end: three real MUBs doubled give 24 points,
which is the `D4` root system, exact at degrees 1–5 and failing at 6 — a 5-design
and nothing more, consistent with DGS on both sides (`24 >= 20`, `24 < 40`).

## 4. The completion needs no new construction — the asset already holds it

Measured on the frozen submission asset
`experiments/v31_guards/package_source/kerdock_phases.npz`:

- the archive holds **exactly 128** phase rows of `{-1,+1}^256`;
- **all 8,128 cross-frame pairs are mutually unbiased.** The check is that
  `phi_s * phi_t` be bent, i.e. `|H psi| == 16` everywhere; across every pair the
  set of distinct Walsh magnitudes observed was `{16.0}` and nothing else;
- the standard basis is unbiased against every `H diag(phi)` frame identically,
  because `<e_i, (H diag(phi))_j>/16 = H_ji phi_i / 16`, of modulus `1/16`.

So the 129-frame set is `{I} U {H diag(phi_s)/16 : s = 0..127}`, and every
ingredient already ships.

**The deployed estimator discards two of them.** `kerdock_v3_estimator.py:51-52`
sets `phase_start = 2`, `phase_stop = 128`, slicing `phases[2:128]` — 126 of 128
— and never adds the identity frame. Both are development-selected constants
(`phase_start` and `phase_stop` are two of the seven), not forced values.

The identity frame is also the *cheapest* of the 129: it needs no Walsh
butterfly, since `I @ W1 = W1`. So the true cost ratio is strictly below the
`129/126 = 1.0238` used in the K1 gate, and the gate is conservative in the
completion's disfavour.

## 5. What this is worth to the manuscript regardless of K1

P1 lost its central claim and is OPEN, leaving the write-up's mechanistic core
thinner than the rubric wants. Section 1 above is a replacement of the right
kind: a **proved** statement, by citation plus exact arithmetic, about what no
method of a given shape can achieve on these networks — which is the paper's
own stated contribution format. It also explains the measured plateau
mechanistically rather than empirically: the design is not merely observed to
resist perturbation, it is provably 1,280 points short of the next exactness
class and 87.7x short of the one after that.
