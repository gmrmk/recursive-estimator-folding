# Gemma 4 PLE to WHestBench: clean-room translation

Date: 2026-08-06

## Source-backed premise

Google's official Gemma 4 documentation and technical report describe the E2B
and E4B variants as using per-layer embeddings (PLE): static embedding capacity
is supplied to decoder layers while the active model remains smaller. The
technical report separates the embedder/PLE parameter counts from active
einsum parameters. Sources:

- https://ai.google.dev/gemma/docs/core/model_card_4
- https://arxiv.org/abs/2607.02770
- https://github.com/google-deepmind/gemma

No Gemma checkpoint is installed locally and no Gemma weights, activations,
outputs, downloads, or API calls were used. This campaign borrowed only the
architectural separation between cold static tables and hot active arithmetic.

## Clean-room mathematical translation

For standardized Gaussian preactivation alpha, the sidecar stores the two
layer-invariant primitives `Phi(alpha)` and `phi(alpha)` and reconstructs:

```text
p  = Phi(alpha)
m  = alpha*Phi(alpha) + phi(alpha)
a1 = Phi(alpha)
a2 = phi(alpha)/2
a3 = -alpha*phi(alpha)/6
a4 = (alpha^2 - 1)*phi(alpha)/24
```

The exact gauge is

```text
T[layer, alpha, primitive] = S[alpha, primitive].
```

Thus one shared atlas plus tiny per-layer routing descriptors replaces 32
duplicated copies. The resulting package is 66,632 bytes, its shared atlas is
65,672 bytes, and maximum expanded-response error is 1.994e-7.

## Flash placement rule

Flash is persistent storage, not an arithmetic device. A memory map still
serves touched pages through the operating-system page cache, and CPU/RAM runs
the interpolation. The low-latency arrangement is therefore:

```text
flash: immutable package + hashes
setup: preload 65.5 KiB shared atlas
predict: RAM lookup + CPU reconstruction
```

Per-neuron physical-flash reads would add page-fault latency. The branch is a
screened storage/locality operator only until fused into a whole-estimator
moment pass and tested under the true billed/residual score law.
