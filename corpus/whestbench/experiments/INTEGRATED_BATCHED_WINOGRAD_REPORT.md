# Integrated batched-Winograd full-entry audit

Date: 2026-08-06

## Decision

**Do not promote this implementation.**  The actual random32,256 fold3 path
geometry completed successfully and seven of eight frozen gates passed, but
the child reached a measured process peak working set of `667.328 MiB`, above
the predeclared `<512 MiB` limit.

The failure is localized to peak live-set geometry.  It is not a timeout,
score-side, numerical, dispatcher, or leak failure.  The child finishes with
a `478.883 MiB` working set and `480.855 MiB` private allocation; its transient
peak occurs while the `283.938 MiB` seven-product workspace overlaps live
network activations.  The exact batched-Winograd operator and all seven passing
integration results remain preserved for a causally new, lower-live-set
mutation.

No WHestBench row, truth, scorer, API, official result, or submission path was
opened.  Both runs used fresh synthetic width-256/depth-32 He weights.

## Full-entry result

The audit ran the real `n_base=32256` estimator geometry in independent,
one-thread parent and child processes.  No reduced-path extrapolation was
needed.

| measurement | direct parent | batched child | child/parent |
|---|---:|---:|---:|
| setup wall | `0.633567 s` | `0.646361 s` | `1.0202` |
| whole-predict wall | `2.727470 s` | `4.427377 s` | `1.6233` |
| analytical FLOPs | `170.530655499B` | `159.492745546B` | `0.935273` |
| backend wall | `2.407884 s` | `4.055268 s` | `1.6841` |
| FlopScope overhead | `0.160008 s` | `0.211794 s` | `1.3236` |
| residual wall | `0.159546 s` | `0.160284 s` | `1.00462` |
| effective compute | `186.485295448B` | `175.521105660B` | `0.941206` |
| peak working set | `414.566 MiB` | `667.328 MiB` | `1.6097` |
| end working set | `195.055 MiB` | `478.883 MiB` | `2.4551` |

The child saves `11.037909953B` analytical FLOPs.  Its residual penalty is
only `0.0007372 s`, or about `0.07372B` effective-compute units, leaving a net
effective saving of `10.964189788B`.  Under the score calculus
`score_child/score_parent = r_C*r_MSE`, the measured `r_C=0.941206` would
tolerate a raw-MSE ratio below about `1.06247`.  This is an engineering screen,
not an MSE measurement or a deployment claim.

Both predicts are comfortably below the frozen absolute `20 s` limit, and
both setups are below `4 s`.  The old relative-wall comparison is deliberately
not a gate because the installed scorer charges residual rather than backend
wall; the absolute timeout remains enforced.

## Trace coverage and eligibility

Parent and child followed exactly the same 29 hook shapes.  The child selected
Winograd on 16 calls (`55.1724%`).  Those eligible calls represented
`57.4164%` of the direct hook bill.  Across the trace:

```text
direct hook bill:   161.964214272B
selected hook bill: 150.926304319B
saved:               11.037909953B
```

The trace naturally exercised full, shrinking-active, even, odd-contracted,
and odd-output shapes.  Thirteen odd-contracted shapes correctly dispatched
direct; eligible odd-output shapes used one batched core plus one tail call.
Every selected bill was no worse than direct.

An independent exhaustive enumeration checked all `131072` triples with
`m in {32256,64512}` and `k,n in [1,256]`: zero worse-than-direct selections,
`62648` Winograd selections, `68424` direct selections, and at most two
matmul calls.

## Numerical gates

Whole-prediction parent/child parity passed:

```text
relative Frobenius: 4.56348e-8
maximum absolute:   1.63122e-6
finite:             yes
```

The independent 32-layer propagation check also passed:

```text
relative final error: 2.48581e-6       (gate <=2e-5)
ReLU gate mismatches: 1 / 4,194,304
mismatch fraction:    2.38419e-7       (gate <=2e-4)
finite:               yes
```

Explicit full, active-even, odd-contracted/direct, and odd-output/ragged
probes all matched their analytical bills, were finite, and had relative
errors between zero and `6.01349e-7`, well inside the `3e-6` gate.

## Memory failure localization

The child's workspace is exactly `297,730,048` bytes (`283.9375 MiB`):

```text
output                    63.0000 MiB
seven left operands      110.2500 MiB
seven right operands       0.4375 MiB
seven products           110.2500 MiB
```

After setup, the fresh child had a `192.922 MiB` working set, although its
reserved/private allocation was already `479.164 MiB`; untouched `empty`
pages were not yet resident.  Prediction touched the operand and product
stacks while full network activations were live, producing a measured
`667.328 MiB` peak working set and `670.598 MiB` peak pagefile usage.  The end
working set fell to `478.883 MiB`.  This pattern identifies transient
workspace/activation overlap, not accumulation across MLPs.

Passing `<512 MiB` requires at least `155.328 MiB` less peak residence on this
trace.  The best changed mechanism is **row-blocked preallocated Winograd**,
because every large-row term in the leaf, left-pack, reconstruction, and
output bill is linear in `m`.  Allocate one full `64512x256` output, pack the
small right-hand Winograd operands once per hook, then process even row blocks
through a much smaller left/product workspace directly into output slices.
With a frozen row block of `8192`, the large live workspace is approximately

```text
full output          63.0000 MiB
7 left blocks        14.0000 MiB
7 product blocks     14.0000 MiB
packed right blocks   0.4375 MiB
total                91.4375 MiB
```

That is `192.5 MiB` below the current workspace, giving a planning-only peak
of about `474.8 MiB` by subtraction from this measured trace.  If the right
pack is reused across all row blocks and reconstruction writes directly into
the final slices, the analytical bill is unchanged: sums of the row-linear
terms equal the full-row bill.  The trade is more visible matmul calls and
possibly more residual/backend wall.  A sequential minimal-scratch Winograd
inside each row block is the lower-memory fallback if batched block liveness
still misses the limit.  Both require a new liveness proof, frozen absolute
time/residual gates, and a fresh full-entry audit; neither is silently
promoted here.

## Frozen gates

| gate | result |
|---|---|
| setups `<4 s` | pass |
| predicts `<20 s`, no failure, finite | pass |
| `C_child/C_parent <=0.98` | pass (`0.941206`) |
| full prediction relative `<=2e-5` | pass |
| depth relative and gate mismatch | pass |
| child peak working set `<512 MiB` | **fail (`667.328 MiB`)** |
| dispatcher never worse | pass |
| explicit branch probes | pass |

## Reproducibility note

The first process launch stopped before prediction because the Windows memory
probe had not declared the pseudo-handle's 64-bit return type.  Only that
audit-infrastructure declaration was corrected; seeds, mechanism, geometry,
and gates remained frozen.  `audit.json` is the subsequent complete run.
