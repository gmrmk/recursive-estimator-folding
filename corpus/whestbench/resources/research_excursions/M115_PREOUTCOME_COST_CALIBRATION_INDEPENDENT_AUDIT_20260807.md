# M115 pre-outcome cost calibration: independent audit

Date: 2026-08-07

Verdict: **PASS_TO_MANIFEST** for the frozen M115 runner's explicitly declared
`wall_proxy` accounting contract.  This is a pass for a conservative,
reproducible primitive-timing proxy, not a claim that the numbers are a newly
measured integrated contest-run wall time.  The manifest must retain that
scope and must not describe the proxy as a direct end-to-end wall-clock
measurement.

This audit was evidence-only.  It did not generate a contest output, invoke a
screen, create `EXTERNAL_FROZEN_M115_MANIFEST.json`, or create the canonical
one-shot root.

## Frozen artifacts and absence checks

The calibration file is present and hashes to:

```text
82e927d8a54f2a61fcfe48e542a624038b3ba0cb50f2dde592be28f21d21ebb1
```

The evidence directory contains exactly these 14 files, with the hashes
committed by the calibration:

```text
base_0.json       9deec66dbc7b29afecc7678d3cd1fc39e06742f2e427f756f9f40aec0fa15696
base_1.json       dd406537147b9e5ab1d13ceb13f5177b56d9f63a7e09c115c0cc415f150aaa02
base_2.json       93b9fcf3f89ecad233d2ab9046a17de3c3c53f94cfe174f9baa957d9806d6499
base_3.json       8606f3d46416398010a3e6901ae21dc3d881720c05ca7b31055d7f428dee59ca
candidate_0.json  1c5977d356024d46ee8a6b3cd0ac2ff38932e68db0b12cb545fea2f9230b303d
candidate_1.json  2674fbb9493ebe350246ef34e2c6dde172eac16deca5cecc60fbe8c9c2f4bd0f
candidate_2.json  cf189481414a88eee2aeebe0a3f85cf33b4f5e203f55a7994f4a5a5646c6dd84
candidate_3.json  1b86b90e7edbce526be536d5b29de89a0f00c7048b0b0b65b5ac45e29e21bfad
equal_0.json      8a9db11c4143a3d3fc854f4960b626178475e9d04a4a731f4e96c26aa1f7e1b0
equal_1.json      10415f87d4ef968aedb6eb190bee2d77cb7fac5096b1d4feddd63e7fcf3f54fe
equal_2.json      69c0992205969328624016aa3fe142a22fc763c9bcf50a9ab6f1bcd63090a60a
equal_3.json      d5ab8ecee94d9ea3a2e87baed7c3485697ce47627dc433ac499f91f1125c6ec6
failure_lifecycle.json 70481c9f090ccdd52b84804e1fe2d4d1907e547a8f49ad8bb6264bfd86d4dc7a
success_lifecycle.json 898f5b2cfa3615c2c965af5e266236f88b76044efd85b1547f9c498a4650e0bc
```

The forbidden final artifacts are absent after the audit:

```text
work/scorefloor_generation/m115_projective_arc_nystrom_draft/EXTERNAL_FROZEN_M115_MANIFEST.json
work/scorefloor_generation/m115_projective_arc_nystrom_one_shot_20260807/
```

## Preservation and provenance

Both earlier evidence archives remain present and unchanged at audit time:

```text
attempt1/base_0.json                 c42e1af255909164d538baf480f8d40aa6126397d536a2d1098bfe93f9e944a8
attempt1/candidate_0.json            fe0bf5e6adb1988ef22883ac82f135d23830d164a023b63e32819d26296fedcd
attempt1/equal_0.json                44996b0b5257cfa81847b820bd170acf14463cf2eea2ccc85fb301523198d4ce
attempt1/failure_lifecycle.json      ac924aa5482f730cde5fbf76e9994ab7c45064079978649cdd7f78a2c2bdaf73
attempt1/success_lifecycle.json      644f00ae46c3d9d4c193a5d0b64b38f7b6b2f9b4ed8e8d10505b9442ad133fe0
attempt2-partial/failure_lifecycle.json 25f7c74a08f62f9eadcd4c88a74cc7869a0bfc2d172a48ea5f047ef2cb532dbc
attempt2-partial/success_lifecycle.json 20848eeaeeabf60113d91a7a6dd389d707156a193bf9cada3499f2238cf5b614
```

The raw timing provenance hashes to
`8e419a1d910b4a77407d399746109c674d8b52868e84222c761d9aabfb420f0b`.
The calibration builder hashes to
`378c469c35020b87773e87fdf8c00d3b360551b9cebe55f19765d774dfa70886`.
The frozen runner source audited here hashes to
`ce4d622b368dd928886b24c47dc9de8125dc46097f39fa07825ec04ae2c7bc5b`.

## Measurement-contract audit

The raw source records one unreported real warmup, then three
`perf_counter_ns` microbatch timings per primitive.  Every trace channel is
the maximum retained per-repetition rate multiplied by that operation's exact
frozen repetition count.  I recomputed this mapping from raw provenance for
all **209** evidence calls (**627** retained raw-rate values); every call
matched its source envelope and exact contracted repetitions.

The rate-book use was:

| Scope | Used primitive keys | Recorded primitive keys |
| --- | ---: | ---: |
| global lifecycle | 38 | 38 |
| network 0 | 19 | 20 |
| network 1 | 19 | 20 |
| network 2 | 19 | 20 |
| network 3 | 19 | 20 |

The one unused key in each network rate book is surplus provenance; it is not
referenced by a trace and therefore cannot lower a charged cost.  It is not a
failure, but should remain unused rather than being repurposed after this
pass.

Candidate, base-L1, and equal-cost-L1 traces for a given network are generated
from one common rate book.  For a shared primitive, the source envelope is the
same in all three traces; differences in displayed normalized floats are only
the final binary multiply/divide rounding at differing repetition counts.
There is no candidate-only favorable timing channel, selection of a smaller
sample, or free multiplier.  The maximum of the three channels is charged,
not a mean or minimum.

The runner independently recomputes billed FLOPs, byte charges, operation
contracts, aggregate totals, effective costs, and the static inventory hash.
It rejects any undocumented multiplier and treats the global lifecycle as
non-amortized: the maximum of success and dominating failure lifecycle cost is
charged once to every candidate.  The resulting charged amount is
`39195280468.00001` FLOPs-equivalent per candidate.  File write/read/flush,
hash, fsync, replace, and durability operations are all represented in their
respective exact trace contracts and subject to the runner's wall-safety
ceilings.

## Comparator and ratio audit

The frozen runner's fresh-process verification under Python 3.12.13 and
NumPy 2.3.5 (one BLAS/OpenMP/MKL thread) passed.  The recomputed ratios and
maximal whole-frame equal-cost comparators are:

| Network | Candidate cost incl. lifecycle | Base 50-frame cost | Equal frames | Equal cost | Next-frame cost | Ratio |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 771766148544.4998 | 303434691063.0000 | 127 | 767283377017.5000 | 773307385926.0000 | 2.5434341269 |
| 1 | 859939947919.4998 | 287179058563.0000 | 150 | 856619574413.0000 | 862313979571.5000 | 2.9944382164 |
| 2 | 796601725419.4999 | 290679019188.0000 | 137 | 792538995165.0000 | 798307500636.0000 | 2.7404858034 |
| 3 | 810300290419.4999 | 312761782938.0000 | 130 | 809447970618.0000 | 815656547964.0000 | 2.5907906101 |

Thus each stated equal frame count is the maximal affordable whole-frame
solution: `C(f) <= candidate_cost` and `C(f + 1) > candidate_cost` for all
four networks.  The independent builder test suite also passed (3 tests),
including a real temporary L1 trace accepted by the runner and affine frame
cost checks.

## Admissibility judgment

The proxy is honest and admissible **under this frozen runner** because its
semantics are explicit, pre-outcome, mechanically verifiable, conservative
within each primitive (maximum retained warmed sample), symmetric across the
three compared methods, and globally non-amortized.  It is not admissible for
the stronger and different assertion that it measures actual integrated
execution wall time in an external contest sandbox.  No such assertion is
needed by, or encoded in, the frozen runner.

Manifest gate: retain `accounting_flags.wall_proxy = true`, preserve all
listed hashes, forbid any regeneration, and carry the scope qualification
above verbatim or equivalently.  Any change to the builder, source contracts,
runtime identity, evidence corpus, or accounting semantics invalidates this
pass and requires a new pre-outcome audit.
