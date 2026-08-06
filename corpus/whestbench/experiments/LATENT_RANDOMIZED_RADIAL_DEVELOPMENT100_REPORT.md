# Frozen development-index-100 verdict

## Decision

**Kill the direct replacement claim; preserve the validated FP32 component.**

The frozen estimator was executed exactly once on the predeclared development
split `full`, index `100`. No other new row was accessed. The estimator and
gate hashes matched before the start marker was written.

| quantity | value |
|---|---:|
| final-layer raw MSE | `8.381168580e-5` |
| billed FLOPs | `59,278,060,569` |
| residual-adjusted effective compute | `70,406,900,303` |
| score multiplier | `0.2588488982` |
| adjusted score estimate | `2.169456252e-5` |
| deployed sampler champion | `2.257079776e-7` |
| ratio to champion | **`96.11784x`** |

The output was finite, nonnegative, FP32, and shaped `(32,256)`. The production
and cost mechanism worked; the analytic accuracy route did not. This is a
clean falsification of the claim that the randomized-radial q3 closure can
directly replace the deployed sampler.

The local failure is not a reason to discard its passing parts. Preserve:

- the one-seed Haar angular de-aliasing operator;
- positive two-node chi radial moments;
- the guarded cumulative-overlap q3 compressor;
- the deterministic FP32 FlopScope implementation and its exact call audit.

Do not tune q, radii, rotation seed, dtype, or compressor from index 100. A
future descendant must put these parts in a different causal role and return
to cleanroom tests. This result authorizes neither a wider official screen nor
submission, and the locked/prohibited firewall remains unchanged.

## Provenance

- estimator SHA-256: `0681179273a21d8a5eae98010927186fce1d48397e497c635179c2441c4b656e`
- gate SHA-256: `939995422552C2A887436BDEE5D5FFBB1512B8513F06C7CFBF7C6803B0D3351F`
- runner SHA-256: `9DE365DDE2068512C4785188DB17BC8229C92B64F197B76BA801A1D091F892B9`
- start-marker SHA-256: `C683758727C5899A3D2AC9F71503AE6D8A6C003ECF44D65C7EA97191EA25556A`
- result SHA-256: `7E8685F2288749CDAD638D52DF045AB52C6B5E0AB3327F0C2407D0E161D6F829`
