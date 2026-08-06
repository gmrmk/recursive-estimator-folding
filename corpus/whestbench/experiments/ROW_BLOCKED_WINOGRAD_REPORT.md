# 8192-row streaming Winograd full-entry audit

Date: 2026-08-06

## Decision

**All frozen synthetic engineering gates pass.**  This exact-arithmetic child
is a screened survivor eligible for a separately frozen development-score
evaluation.  It is not yet a promoted competition champion: this branch never
opened a WHestBench row, target, scorer, API, saved official result, or
submission path, and it did not measure MSE.

The causally changed mechanism did what it was designed to do.  Replacing the
full-height seven-left/seven-product workspace with fixed 8192-row streaming
reduced the operator workspace from `283.9375 MiB` to `91.4375 MiB`.  The
measured child peak working set fell from the failed predecessor's
`667.328 MiB` to `474.301 MiB`, passing the frozen `<512 MiB` gate by
`37.699 MiB`.  The observed `193.027 MiB` peak reduction is within about half
a MiB of the predeclared `192.5 MiB` workspace reduction.

The price is kernel fragmentation: the child made 144 visible hook matmul
calls rather than 29, and whole-predict/backend wall time was about 1.35x
direct.  The scorer model excludes backend time except through its absolute
timeout, so this remains inside the predeclared `<20 s` predict gate, but the
single synthetic timing is not a stability certificate.

## Frozen full-entry result

Both estimators used identical fresh synthetic width-256/depth-32 He weights,
setup frames, `n_base=32256`, and all 64512 antipodal sample paths, in
independent one-thread processes.

| measurement | direct parent | row-blocked child | child/parent |
|---|---:|---:|---:|
| setup wall | `0.798181 s` | `0.621151 s` | `0.7782` |
| whole-predict wall | `3.291410 s` | `4.448758 s` | `1.3516` |
| analytical FLOPs | `170.530655499B` | `159.492745546B` | `0.935273` |
| backend wall | `2.912047 s` | `3.944791 s` | `1.3546` |
| FlopScope overhead | `0.196406 s` | `0.339576 s` | `1.7289` |
| residual wall | `0.182886 s` | `0.164329 s` | `0.8985` |
| effective compute `C` | `188.819284722B` | `175.925616214B` | `0.931714` |
| process peak working set | `414.543 MiB` | `474.301 MiB` | `1.1442` |
| end working set | `196.086 MiB` | `288.188 MiB` | `1.4697` |

The exact arithmetic saving is `11.037909953B` FLOPs.  In this paired run,
the child also had `0.01856 s` less measured residual, producing a
`12.893668507B` effective-compute saving.  Residual measurements can vary, so
the durable claim is the exact FLOP saving; the frozen `C` gate nevertheless
passes on the complete paired measurement.  The observed `C` ratio would
tolerate an MSE ratio below `1.07329` in the linear score regime.  This branch
did not use that tolerance to weaken any parity gate.

## Bill-preserving row proof

Let even row blocks have sizes `m_r`, with `sum_r m_r = m`; define
`h_r=m_r/2`, `h_k=k/2`, and `h_n=n_core/2`.  The streamed core bill is

```text
sum_r 7*h_r*h_n*(2*h_k-1)       leaf products
+ sum_r 7*h_r*h_k                left-stack fills
+       7*h_k*h_n                right-stack fill, exactly once
+ sum_r 7*h_r*h_n                reconstruction adds.
```

Every row-dependent term is linear in `h_r`, so this equals the unsplit
Batched-B core bill exactly.  An odd output tail remains one full-row direct
matmul; an odd contracted width remains direct.  Independent expansion found
zero mismatches across:

- all 131,072 triples with `m in {32256,64512}` and `k,n in [1,256]`;
- 96,768 canonical/even/ragged checks covering every even `m` from 2 through
  64,512;
- every actual hook and every explicit probe.

The static dispatcher selected Winograd on 62,648 shapes and direct on 68,424
shapes, with zero worse-than-direct selections.  The actual 29-hook trace
matched the parent shape for shape: 16 selected Winograd, representing
57.4164% of the direct hook bill.  Its exact hook totals remained:

```text
direct hook bill:   161.964214272B
selected hook bill: 150.926304319B
saved:               11.037909953B
```

The 16 selected calls expanded to 124 row-core calls plus seven odd-output
tail calls; together with 13 direct shapes, the hook used 144 matmul calls.
Every actual count matched `ceil(m/8192)` plus the declared tail rule.

## Numerical gates

Whole-estimator parity:

```text
relative Frobenius: 4.28216e-8        gate <=2e-5
maximum absolute:   1.49812e-6
finite:             yes
```

Independent 32-layer propagation:

```text
relative final error: 2.48581e-6      gate <=2e-5
ReLU gate mismatches: 1 / 4,194,304
mismatch fraction:    2.38419e-7      gate <=2e-4
finite:               yes
```

Eight explicit probes covered small full/even/direct/ragged products, the
8192 boundary, a two-row remainder, two blocks plus two rows, and the full
64512-row odd-output case.  Every measured bill equaled both the selected and
independently expanded bill; every call count matched; all outputs were
finite.  Relative errors ranged from zero to `6.04725e-7`, below `3e-6`.

## Memory accounting

The setup allocation is exactly:

```text
full output          63.0000 MiB
7 left blocks        14.0000 MiB
7 product blocks     14.0000 MiB
packed right blocks   0.4375 MiB
total                91.4375 MiB
```

After setup, the child working set was `192.484 MiB`; the process-wide peak
already reflected setup QR work at `412.949 MiB`.  Prediction touched the
bounded workspace while live activations existed, raising the final peak only
to `474.301 MiB`.  End working set was `288.188 MiB`, and peak pagefile usage
was `476.980 MiB`.  This passes the process-wide gate, not merely a static
array estimate.

## Gate ledger

| gate | result |
|---|---|
| setup `<4 s` | pass |
| predict `<20 s`, no failure, finite | pass |
| `C_child/C_parent <=0.98` | pass (`0.931714`) |
| whole prediction relative `<=2e-5` | pass |
| depth relative and gate mismatch | pass |
| process peak working set `<512 MiB` | pass (`474.301 MiB`) |
| static/actual bill and partition identity | pass |
| explicit and ragged probes | pass |
| fixed workspace/block contract | pass |

## Recursive-fold disposition

- **Preserved components:** exact one-level Winograd algebra; shape-only
  never-worse dispatcher; one-time right packing; float32 numerical parity;
  complete random32,256 fold3 path geometry; exact 11.038B-FLOP reduction.
- **Solved failed link:** transient full-height operand/product liveness.
- **New exposed cost:** 115 extra visible matmul calls and ~35% greater backend
  wall time.  This is acceptable in the present synthetic screen but remains a
  runtime-stability risk, not evidence that call fragmentation is universally
  harmless.
- **Next legal step:** first create an immutable production port of this exact
  8192-row implementation, then predeclare and run a separately frozen matched
  score on permitted development rows.  Do not retune the block height from
  this result, and do not claim a current champion promotion.
