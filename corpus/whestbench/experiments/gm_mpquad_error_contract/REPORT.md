# Falsifying the `mp.quad(error=True)` software-contract premise

**Status: the premise is FALSIFIED. The audit's predeclared falsifier does NOT
fire; a different mechanism does, and it is worse.**

Answers the M245 audit item:

> **mpmath Heuristic False PASS (OPEN)**: Provide a predeclared symbolic
> integrand `f(x) = sin(k x)` where `k` is specifically tuned to alias the exact
> spacing of the tanh-sinh final refinement level (`maxdegree=14`). If
> `error=True` returns 0 despite massive analytical error, the software-contract
> premise is falsified.

Rated *Probability: Medium, Consequence: High, Cost: Low. Required before shard
launch.* Environment: mpmath 1.4.1, `dps=80`, `mp.quad` default (tanh-sinh).
Falsified := reported error ≤ 1e-40 while true relative error ≥ 1e-6, against
closed-form references.

## 1. The predeclared falsifier does not fire

`∫₀¹ sin(kx) dx = (1−cos k)/k`. 26 frequencies (`k` up to 49152) × 9 maxdegrees
(3…14) = 234 probes.

| maxdegree | 3 | 4 | 5 | 6 | 7 | 8 | 10 | 12 | 14 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| wrong /26 | 22 | 18 | 16 | 13 | 11 | 9 | 5 | 1 | **0** |
| **false pass** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** |

Wrong answers are common on coarse grids and **every one carried a loud reported
error**. Worst case `k=49152, maxdegree=4`: true relative error `11006.9`,
reported error `1.0`. At M245's own `maxdegree=14` nothing was wrong at all.

**Oscillatory aliasing is the wrong attack.** The audit's stated mechanism —
integrand roots aliasing the node grid across two levels — is not supported.

## 2. The mechanism that does fire: interior features between nodes

tanh-sinh clusters nodes double-exponentially at the **endpoints**, so the
interior is sparse. A feature narrow enough to fall *between* interior nodes is
invisible; it stays invisible at the next level too, the levels agree, and the
reported error — their difference — collapses to a meaningless number while the
value is completely wrong.

Narrow Gaussian bump, `∫₀¹ exp(−((x−c)/w)²) dx`, exact in closed form:

| probe | centre | panels | result |
|---|---|---|---|
| A1 | `0.5` (a node) | none | wrong for `w ≤ 1e-5`, **all flagged** |
| A2 | `0.3141592…` | none | **FALSE PASS at every `w ≤ 1e-4`** |
| B1 | `0.5` | `[0, 0.25, 1]` | **FALSE PASS at every width, including `w=1e-3`** |
| B2 | `0.5` | `[0, 0.25, 0.5, 1]` | **all correct** |

15 false passes. Representative rows:

| probe | w | reported error | true rel err |
|---|---|---|---|
| A2 | `1e-4` | `2.63e-333` | **1.0** |
| A2 | `1e-15` | `1.02e-3318200587309268176495050` | **1.0** |
| B1 | `1e-3` | `3.48e-119` | **1.0** |

A reported error of `1e-3318200587309268176495050` is not convergence. It is two
refinement levels agreeing that they both saw nothing.

## 3. The decisive row: reported error carries no usable signal

Compare two runs of the **same integrand at the same width** `w = 1e-3`:

| configuration | reported error | true relative error |
|---|---|---|
| A1 — plain `[0,1]` | `1.0e-175` | `0.0` — **correct** |
| B1 — panels `[0, 0.25, 1]` | `3.48e-119` | `1.0` — **completely wrong** |

**The wrong answer reported an error 56 orders of magnitude LARGER than the
correct one.** Correct results here run down to `1e-175`; a total miss reports
`3.5e-119`. The two populations are interleaved.

Therefore **no threshold on the reported error separates correct from wrong**.
The heuristic cannot be repaired by tightening it, calibrating it, or rejecting
"absurdly small" values. It must be replaced by an independent check.

This converts the audit's proposed resolution — *"the heuristic `returned_error`
must be actively checked against the exact analytical `R_q` recurrences rather
than blindly trusted"* — from a precaution into a **requirement with evidence**.
The audit also flags that primary and replica both rely on `mp.quad`'s trap; §3
says that shared reliance is not merely correlated risk, it is unmonitorable.

## 4. Panel insertion is a measured risk multiplier — and the kink cut is right

B1 vs A1 at `w=1e-3` is the same integrand: **inserting the audit's fixed-panel
style at `0.25` converted a correct answer into a silent total miss.** This is
the audit's own concern — *"inserting arbitrary fixed panels interrupts the
exponential convergence mapping"* — measured, with a False PASS as the outcome
rather than merely deeper refinement.

B2 is the counterpart: putting a panel edge **on** the feature (`0.5`) is correct
at every width tested. So the audit's approval of the single positive kink cut at
`t = |α|` is validated; the exposure is the *other*, arbitrary panels.

## 5. Scope — what this does not establish

- **This is not a demonstration that M245's integrand is wrong.** M245 integrates
  `h_q(t)` against a piecewise-quadratic window — a piecewise polynomial against
  a Gaussian weight, with one kink. That shape has no narrow interior feature, so
  the trigger demonstrated here is not obviously present. **Someone must check
  the actual integrand**; this report deliberately does not assume it.
- What *is* established is the contract: `mp.quad`'s `error=True` can return an
  arbitrarily small number on a completely wrong value, and its magnitude does
  not rank correctness. Any gate that treats it as a pass condition is unsound
  regardless of integrand.
- Single library version (mpmath 1.4.1), single method (tanh-sinh), `dps=80`.
- The other two open falsifiers (transport clock merge, infinite-span
  completeness) are untouched here.

## 6. Recommended disposition

The audit's `REPAIR` verdict stands and this item hardens from *Medium
probability* to **observed**. Concretely, before shard launch:

1. Replace the pass condition. A panel result is admissible only when checked
   against the exact analytical `R_q` recurrences, or against a second method
   with different nodes (Gauss–Legendre on the same panel). `mp.quad`'s error may
   be logged; it may not gate.
2. Treat every fixed panel edge not tied to a feature as an exposure, and justify
   each one. Keep the kink cut at `t = |α|`.
3. Since primary and replica share the trap, an independent second method is
   required for genuine cross-engine independence — the current gate is
   common-mode by construction.

## Reproduction

```bash
pip install mpmath
python3 falsify_mpquad_error.py      # predeclared sin(kx) probe: NOT falsified
python3 falsify_mpquad_interior.py   # interior-feature probe: FALSIFIED, 15 cases
```

Pure mpmath; no corpus data, no truth, scorer, holdout, private data,
leaderboard, submission, or champion access. No estimator, variance, MSE, or
score claim.
