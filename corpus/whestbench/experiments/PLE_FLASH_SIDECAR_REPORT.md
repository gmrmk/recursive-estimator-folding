# Clean-room PLE response sidecar: result

## Outcome

The compressed sidecar is a **screened survivor, not a WHestBench promotion**.
It stores two analytic primitives, `Phi(alpha)` and `phi(alpha)`, in a read-only
atlas and reconstructs six ReLU/Price response quantities on CPU. The exact
layer-invariant part compresses from 2,097,536 bytes to 65,672 bytes
(0.03131x, about 31.9x smaller). Exact per-layer cyclic row schedules remain
in 320-byte descriptors. The complete factorized package is 66,632 bytes.

The key operational answer to “put the calculations in flash” is narrower:
**flash stores cold immutable tables; it does not perform the calculations.**
A memory map lets the operating system page those files from storage, but
touched pages are used from RAM/page cache and interpolation/reconstruction
runs on the CPU. For the hot path, the best design is to keep the 66 KB package
on flash and preload the 65.5 KB atlas during `setup()`. Querying physical flash
for every neuron would add latency, not remove it.

## What was borrowed, and what was not

Google's official Gemma 4 material says the E2B/E4B models use per-layer
embeddings: each decoder layer gets a small embedding for every token, allowing
parameter capacity to sit in quick lookup tables. The technical report
identifies PLE as the source of the small models' extra embedder parameters.
[Gemma 4 model overview](https://ai.google.dev/gemma/docs/core),
[Gemma 4 Technical Report](https://arxiv.org/html/2607.02770v2).

That inspired only the storage pattern. This sidecar used no Gemma weights,
hidden states, outputs, downloads, or API calls. Its values are independently
derived closed forms for a standardized Gaussian preactivation:

```text
p  = Phi(alpha)
m  = alpha Phi(alpha) + phi(alpha)
a1 = Phi(alpha)
a2 = phi(alpha)/2
a3 = -alpha phi(alpha)/6
a4 = (alpha^2 - 1) phi(alpha)/24
```

The official LiteRT-LM discussion is also a useful warning: it describes
keeping PLEs out of active memory to reduce footprint. Storage placement and
hot arithmetic are different design problems.
[LiteRT-LM memory discussion](https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/).

## Recursive fold

The frozen v1 deliberately materialized `[layer, alpha, primitive]`. Its layer
symmetry defect measured exactly zero, exposing a redundant causal link:

```text
T[layer, alpha, primitive] = S[alpha, primitive].
```

The changed mutation factored this exact gauge into:

- one shared `[8193,2]` response atlas;
- 32 layer descriptors `(cyclic_shift, active_width, row_block)`;
- one exact eight-block schedule per layer for width 256.

This retains layer-specific routing while avoiding 32 identical coefficient
copies. It is a mathematical compression, not lossy parameter quantization.

## Frozen measurements

All eight unit tests pass. The fixed 4096-query audit used nine timing repeats
after three warmups. Five additional fresh Python subprocesses passed every
frozen gate.

| Quantity | Result |
|---|---:|
| Maximum expanded-response interpolation error | `1.99419e-7` |
| Layer symmetry error | `0` |
| Row-schedule gauge error | `0` |
| V1 coefficient file | `2,097,536 B` |
| Factorized coefficient file | `65,672 B` |
| Factorized package including descriptors/schedule | `66,632 B` |
| Factorized preload array | `65,544 B` |
| Factorized/parent warm-latency ratio, 5-run median | `0.7631` |
| Factorized/parent ratio, worst fresh run | `0.7985` |
| Factorized/direct ratio, 5-run median | `0.2810` |
| Factorized/direct ratio, worst fresh run | `0.2937` |

The timings show a stable cache/locality win in this Python/NumPy premise
workload. They do **not** establish the same speedup in the contest runner: the
direct reference uses dependency-free scalar `math.erf`, while an evaluator's
native vectorized special function may have very different wall time.

The audit reports mmap open, first-touch, and preload setup times, but the
first-touch number is intentionally not called physical-flash latency. This
process cannot force safe operating-system cache eviction, and storage-media
inspection was unavailable without elevated system access.

## Conservative accounting

Using the campaign's stated `gather = 4/element`, `copy = 1/element` convention:

| Path | Proxy operations/query |
|---|---:|
| Interpolated lookup and reconstruction | `41` |
| Known float64-promoted direct path | `56` |
| Hypothetical native-float32 analytic lower bound | `28` |

The factorized preload setup copy is 16,482 element operations, versus 524,352
for the duplicated v1 table. Lookup therefore beats the known float64-promotion
path in this proxy, but it does not beat an ideal native-float32 analytic path.
This unresolved accounting link is why the branch is not folded into the
deployed champion.

## Salvage and next mutation

Preserve:

- the 66 KB immutable package and hashes;
- exact response formulas and interpolation accuracy;
- exact layer descriptors and cyclic scheduling;
- mmap for cold packaging;
- setup preload for the hot path;
- the correctness, symmetry, storage, and stability harnesses.

Localize rather than dismiss:

- “flash executes math” is a killed interpretation;
- true cold-flash latency is unmeasured, not assumed;
- native-float32 accounting is unresolved;
- whole-estimator benefit is untested.

The next legal mutation should fuse alpha quantization and atlas lookup into an
already-existing per-layer moment pass, amortizing index arithmetic and output
materialization. Only then should it face a whole-estimator billed-cost and
residual-wall gate. No leaderboard or holdout claim follows from this screen.
