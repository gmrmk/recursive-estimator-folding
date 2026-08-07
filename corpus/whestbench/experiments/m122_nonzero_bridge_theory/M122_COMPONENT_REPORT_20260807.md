# M122 nonzero-mean bridge component report -- 2026-08-07

## Verdict: REPAIR

The missing M121 nonzero-mean source is now specified and has a generated
small-width reference implementation.  Preserve it as the source-algebra
repair.  Do **not** promote it to an estimator component or run an efficacy
grid: the generic dense-bridge `k4` alternating-path `iijj` contraction still
has the M121 Khatri--Rao `n^4` obstruction.  Only its fixed-rank projected
form is presently cost-shaped.

## What passed

The generated-only identity suite completed six tests:

```
passed 6
```

It covers exact local normal-ordered coefficients, signed bivariate bridge
against both deterministic quadrature and the independent M120 Plackett
implementation, exact repeated central-cumulant strata `[2,1]`, `[2,2]`, and
`[2,1,1]`, a three-node normal-ordered raw moment, positive-diagonal gauge
and permutation covariance, and low-rank tree projection against direct
small dense contraction.

The finite Gauss--Hermite comparisons are explicitly coarse because a ReLU
kink is not polynomial; the exact checks are the Hermite and set-partition
identities.  No contest/public/private model, scorer, outcome, submission, or
target-width run was read or generated.

## Artifacts

| file | SHA-256 |
|---|---|
| `M122_NONZERO_BRIDGE_THEORY_20260807.md` | `5086c2108c84adb25c73555cbffd73177e1932efb3d6bfd4b42ce61dd8c4904f` |
| `m122_nonzero_bridge.py` | `c765fe24818f4ec8928a879e217a530077edff98f729555739202c1f7286f927` |
| `test_m122_nonzero_bridge.py` | `c0866e53e892ead8419f9c030803802ec9fb8e9c4f91ec2f235199bb4ffb0195` |

## Integration gate

An M121 successor may use this only after all of the following are supplied:

1. a frozen, independently audited fixed-rank M120 adjoint pairing;
2. an endpoint-stable pair bridge replacing the reference's `|rho|<=0.8`
   series domain, with no clipping;
3. an exact collision correction in that projected representation;
4. an all-in non-overlapping FlopScope/memory ledger; and
5. a fresh independent algebra/manifest audit before any generated outcome
   protocol.

M122 owns the source definition.  It does not license a union with terminal
Born terms; the M121 LLQ/LLLC/LLQQ ownership/subtraction gate remains in
force.
