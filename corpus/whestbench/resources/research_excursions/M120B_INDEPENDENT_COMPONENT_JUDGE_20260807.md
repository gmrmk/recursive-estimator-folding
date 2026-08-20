# M120B independent component judge — 2026-08-07

## Verdict: REPAIR

The corrected local `(mu,C)` Jacobian and its shared-CP `E=0` realization are
valid component atoms, but the submitted generated falsifier is not the
theory-frozen falsifier. Its large `E=0` error is adverse evidence, not a
protocol-valid component kill. Do not promote M120B, form a source, or run a
correction experiment until the frozen target-free falsifier is restored.

## Scope, identity, and permitted execution

I inspected the requested component implementation/tests and implementation
report. `run_corrected_cp_falsifier.py` and
`corrected_cp_falsifier_results.json` are absent. The replacement
`run_corrected_cp_generated.py` prints deterministic generated-only output;
it creates no result file and has no target, contest, public outcome, scorer,
champion, correction-source, or target-shape path.

I ran only the target-free test and replacement runner:

```text
work\whest-v014\Scripts\python.exe test_corrected_cp_jacobian.py
6 tests, 0.174 s, OK

work\whest-v014\Scripts\python.exe run_corrected_cp_generated.py --aggregate-only
```

The interpreter was Python 3.14.4. I hashed the local import closure before
execution. The executable has no pinned runtime/source-hash guard or persisted
hashed result, and—more decisively—does not implement the frozen protocol.

## Algebra that survives — PASS

For `Z ~ N(mu,v)`, at `mu=0,v=1`, `m=1/sqrt(2*pi)`, `dq/dv=1/2`, and
`dm/dv=1/(2*sqrt(2*pi))`. Therefore

```text
d Var(ReLU(Z))/dv = 1/2 - 2*m*dm/dv
                    = 1/2 - 1/(2*pi)
                    = 0.3408450569081046... .
```

The implementation correctly uses central covariance rather than the raw
second-moment value `1/2`.

With symmetric covariance adjoints and Frobenius pairing, the complete local
cross blocks are correctly

```text
c_i^x = 2 sum_j A_ij H^x_ij - A_ii H^x_ii,   x in {mu,v}.
```

The factor two represents the independent symmetric off-diagonal coordinate.
The dense finite-difference oracle perturbs that coordinate symmetrically and
splits it equally back into `(i,j)` and `(j,i)`. The local reverse uses
`b^z=p*b^h+c^mu` and overwrites the covariance diagonal with
`delta=r*b^h+c^v`, as required.

For the sealed base `K_base=p p^T`, the CP reset is also correct:

```text
U_pp = diag(p) U
G_reset[output,i] = delta[i,output] - p[i]^2 diag(A)[i,output].
```

It is signed and represented by identity atoms. The rank ledger therefore
grows additively as `n,2n,...,depth*n`, not multiplicatively. The six passing
tests cover the `E=0` all-output dense/CP equality, finite differences, rank,
positive gauge, and permutation. They do not cover simultaneous gauge plus
permutation or the required degenerate/near-zero-variance cases.

## Cost reconstruction — PASS as a lower-bound arithmetic check

Using `M(a,b,c)=2abc-ac`, `n=O=256`, incoming ranks `R_t=256t`, and 31
reverse ReLU maps:

| Work | Calls | Flops |
|---|---:|---:|
| diagonal `G @ (U*U).T` | 31 | 16,640,966,656 |
| one `L` cross block | 62 | 33,251,459,072 |
| two cross blocks | 124 | 66,502,918,144 |
| affine inherited `U_pp` | 30 | 15,572,336,640 |
| affine mean adjoint | 30 | 1,004,666,880 |
| **complete reverse** | **215** | **99,720,888,320** |

Thus `99.72088832B` is correct. Adding the theory's existing Gaussian
background input, `6,189,000,000`, gives `105,909,888,320 = 105.90988832B`.
It remains a lower bound before CDF/derivative, pointwise, copy,
concatenation, source, and native-trace work.

## Reproduced replacement-run result — adverse evidence only

I regenerated the arrays directly and recomputed the result. There are 12
cases and 48 equally weighted terminal-output cells: 12 at width 3, 16 at
width 4, and 20 at width 5. The reported aggregate is an output-cell mean,
not an accidental width/case mean.

| Metric | Recomputed value |
|---|---:|
| max CP/base covariance relative error | 3.0881991885682878e-15 |
| max CP/base mean relative error | 7.075473474798217e-15 |
| mean base/exact covariance relative error | 0.37061361630706724 |
| max base/exact covariance relative error | 3.2006329269785545 |
| mean base/exact covariance cosine | 0.9137589534537535 |
| minimum base/exact covariance cosine | -0.47005886080185544 |
| negative covariance-direction cells | 1 / 48 |
| mean base/exact mean relative error | 0.3668628115469852 |
| minimum base/exact mean cosine | -0.2696303736079096 |
| negative mean-direction cells | 2 / 48 |

Case-equal covariance averaging is worse, `0.38298507004299687`. The
replacement probe honestly shows a severe `E=0` miss. Its cosine checks,
however, compare base and exact adjoints; they are not the frozen signed
`(delta mu,delta C)` contraction tests.

## R1 — binding frozen-falsifier mismatch

The M120 theory freezes widths `{8,12,16}`, depths `{2,3,4}`, three **Philox**
networks per cell, and all outputs. It requires global standardized-adjoint
error `<=.05`, every-cell worst-output error `<=.10`, the same limits for
predeclared signed `(delta mu,delta C)` directional contractions, and
simultaneous permutation, positive-gauge, degenerate, and near-zero-variance
tests to `1e-10`.

The executable instead uses widths `{3,4,5}`, depths `{3,4}`, two replicas,
and NumPy `default_rng` (PCG64), not Philox. It reports an unstandardized mean
of final per-output covariance-relative errors and a global maximum; it has no
frozen direction table/contraction gate, per-cell standardized aggregation,
simultaneous representation test, or degenerate/near-zero-variance test.

This replaces the predeclared falsifier after the fact. The `0.3706` mean and
`3.2006` maximum strongly predict failure but cannot be relabeled as the
frozen verdict. **REPAIR**, rather than empirical KILL, is mandatory.

### Required repair

Restore a sealed generated-only falsifier with the theory grid, three Philox
instances/cell, a frozen seed table, all-output/cell weighting, standardized
adjoint definitions, and signed direction vectors. Bind the runner, closure
dependencies, runtime, seed table, and JSON result by SHA-256. Add the
simultaneous gauge/permutation and degenerate/near-zero-variance gates. Only a
failure of that restored `.05/.10` protocol can issue a component KILL.

## M121 consequence

M121 is **blocked as currently specified**: it needs the cheap M120 all-output
adjoint propagated from a next-ReLU `(delta m,delta V)` source to terminal,
and that `E=0` carrier has not passed its binding component gate. The surviving
central-Jacobian/symmetric-slot/signed-reset atoms may support only a *new*
local-only derivation that immediately contracts a declared source without
later `E=0` propagation. That is not the registered M121 carrier and does not
authorize M121 implementation or a correction experiment.

## Hashes

| File | SHA-256 |
|---|---|
| `m120_price_normal_ordered_adjoint/corrected_cp_jacobian.py` | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| `m120_price_normal_ordered_adjoint/test_corrected_cp_jacobian.py` | `8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d` |
| `m120_price_normal_ordered_adjoint/run_corrected_cp_generated.py` | `c252be62fc18c3a879cfd26bffd42d43ba05eed37a0200f36825517f3978d99d` |
| `m120_price_normal_ordered_adjoint/EXPLORATORY_FINDINGS.md` | `98df30a45b6d9bf2f933a4ca19864bf1da3f77d3e11c5584dbb189650de1a932` |
| `m120_price_normal_ordered_adjoint/probe_price_split.py` | `25a16322bac8ab736e17e6a8d0b1b84acdb790fd62ce343cfea920e0857f0a4e` |
| `m120_price_normal_ordered_adjoint/probe_repeated_pullback.py` | `be0e8040bf5949f7870221ad59467f3585b98a1ee3646f6f88a9aa2f59d75b5b` |
| `m120_price_normal_ordered_adjoint/SOURCES.md` | `164b65bf0c063489e85d8548900f9c10b26411ee16c64b2f2630ab1220db0996` |
| `research_excursions/M120B_CORRECTED_CP_JACOBIAN_IMPLEMENTATION_20260807.md` | `54faffbd6920e232825053aaf4e79960fe232899477919390dba2b132d6fbd2c` |
| `research_excursions/M120_NORMAL_ORDERED_PRICE_ADJOINT_THEORY_20260807.md` | `ec681ad77d518054b6ae08164ca390f58caa18f92be37083a54519d1b1566dd4` |
| `fullcov_gaussian_mm/fullcov.py` | `091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6` |
| `adjoint_cumulant/adjoint_born.py` | `f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd` |
| `m121_bridge_source_normal_adjoint/PRETHEORY.md` | `2d20dd013666cf90fb0d320b98755924c237d75fff56dff3ab323d77e776bd75` |

