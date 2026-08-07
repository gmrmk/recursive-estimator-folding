# M143 one-shot development failure — 2026-08-07

## Disposition

`KILLED IMPLEMENTATION — PROTOCOL FAILURE; NO RETRY`

The independently audited, single-use development authorization was consumed
before response construction, as required.  The frozen run then terminated
after 49.2 seconds without writing a development result.  No confirmation was
opened and no contest, leaderboard, submission, designation, or champion state
was touched.

This is not an efficacy result.  It is a failed executable premise screen.
The output-aware suffix-energy mechanism remains unresolved and may be reused
only in a genuinely changed descendant that addresses the failed
certification mechanism under a new frozen protocol.

## Bound evidence

- Manifest SHA-256: `6338584fdf89813c6e6f0c2c46bc72ccbcb22b5d600a6766ba8d6bf319bce215`
- Runner SHA-256: `1f0d31ec7e28d98cd84fc64fac3bc3a67293f6060d14f085f8f0005c92a9a81c`
- Authorization SHA-256: `be1f33d5d354001d59f7b9e5eed2003950ac85e713c2da9ad8922e5099b43ec1`
- Consumed receipt SHA-256: `f2c7251bf80ea895d0a0e9cbbf19870e7888da0918099064a1c6debce454fdab`
- Hostile PASS report SHA-256: `7710dfcf3068748285093341b8027efe7b3f13c555bd81aa54439dd5f5f50fb0`
- Authorized output: `M143_DEVELOPMENT_RESULT_20260807.json`
- Output exists after failure: `false`
- Confirmation authorization/result: absent

The consumed receipt records status `consumed-before-response` for nonce
`m143-development-20260807-root-01-6338584fdf89813c` and authorization ID
`m143-e5f00a9fe790c445690cddf7c8b6eb35b957cf7e4283b1820e173736731601e1`.

## Failure boundary

The exception path was:

```text
run_split
  -> build_cell
  -> build_state_frechet
  -> m122_nonzero_bridge.build_state
  -> NonzeroBridgeFailClosed(
       "small state has a pair too close to a Gaussian endpoint")
```

`NonzeroBridgeFailClosed` subclasses `RuntimeError`.  The frozen per-cell
protocol recorder caught only `(ArithmeticError, ValueError)`, so the
certificate refusal escaped instead of being recorded as a target-
extrapolation failure.  Catching it mechanically would not make the frozen
cell pass: the manifest already requires any family certification failure to
fail the screen with no seed retry or family removal.

## Salvage map

Preserve:

- the exact sign-scrambled suffix-energy recurrence;
- the physical-scale-only causal attribution arm;
- the pooled and per-family IID-He/diagonal gates;
- the one-shot authorization/receipt firewall; and
- the protected proposal cost crosswalk.

Failed link:

- endpoint-safe construction/certification of the generated Gaussian bridge
  state used by the exact response oracle.

A descendant must change that link mathematically—for example, an audited
endpoint-limit/asymptotic bridge evaluator or a new predeclared state family
whose exact oracle certifies—rather than changing seeds, deleting the IID-He
family, loosening the gate, or issuing another M143 token.
