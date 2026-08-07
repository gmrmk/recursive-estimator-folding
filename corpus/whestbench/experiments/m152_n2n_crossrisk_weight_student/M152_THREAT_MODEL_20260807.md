# M152 threat model and response-free checks

## Invalidity risks

| Threat | Consequence | Frozen mitigation or fail rule |
|---|---|---|
| f64 surrogate used for references | Cross-risk targets the wrong program | Direct f32 primitive must match an independent local official-semantics fixture. Failure kills. |
| Fixed-radius f32 target called Gaussian | Finite-precision radial bias becomes unbounded | Target is only T_f32. A Gaussian claim requires a new bound and protocol. |
| Shared R1/R2 RNG, QR, or buffer | e1^T e2 need not vanish | Separate seed streams, QR processes, buffers, reductions, and hash sealing. |
| Reference visible during fitting | Adaptive leakage | Train pairs and eval pairs are disjoint; test cannot be read before beta/source/prediction hashes are sealed. |
| Outputs treated as independent MLPs | Fake sample size / split leakage | Split, bootstrap, tuning, and all gates use whole MLPs. |
| Per-MLP oracle deployed | Target leakage | Oracle can only kill; inference has one universal 50-vector. |
| Feature/checkpoint edits after result | Multiple testing | Source and five-value ridge grid are frozen. A change needs a new protocol and fresh bank. |
| Negative cross-risk clipped | Selection bias | Every finite signed value is retained. Nonfinite values kill. |
| Index, hash, seed, or target feature | Memorization | Source scan and label-shuffle control; no such field may enter phi. |
| Symmetry defect | Coordinate-label shortcut | Four label-free transform audits must pass. |
| Label variance dominates | Capacity conclusion not identified | Enforce V_label <= .005 L_anchor without post-hoc replicate expansion. |

## Smallest response-free feasibility sequence

None is authorized under the kill. If an independent reviewer needs only plumbing evidence, the sequence is limited to:

1. An algebra unit test on fixed synthetic vectors for the cross-product and gradient identities and common-reference cancellation. No MLP evaluation.
2. An f32 semantic fixture on three generated synthetic MLPs x three frozen 256-row antipodal blocks, comparing independent direct f32 implementations. Retain pass/fail plus code/runtime digests only; do not form a reference average, label, risk, or fit.
3. One generated MLP with fixed rotation/permutation/gauge/output-scale transforms and a fixed arbitrary beta. Compare features and predictions only; use no reference.
4. One generated MLP and one complete 64,512-path streamed Kerdock pass, discarding the final vector. Record wall time, peak working set, call counts, and source hashes only. The hypothetical campaign fails local feasibility unless the 256-reference projection is below 8 wall-hours and the fixture stays below 20 GiB peak RAM.

These checks are neither capacity evidence nor accuracy evidence. They cannot reopen this killed M152 cell.

