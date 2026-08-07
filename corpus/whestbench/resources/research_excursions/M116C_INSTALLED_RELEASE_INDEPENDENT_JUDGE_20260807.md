# M116c installed-release independent judge — 2026-08-07

## Verdict: PASS_TO_EXECUTE

This is a source-only, installed-release decision. It did **not** invoke the
campaign runner and did **not** create the canonical root. `PASS_TO_EXECUTE`
is authorization for the one bound future invocation below; it is not evidence
that any numerical gate has passed.

## Exact installed release

| Binding | Verified SHA-256 / value |
|---|---|
| execution release, raw bytes | `ec1431ac6669c9ede19486a13eec139bd9598e1535dbca4f9dc5c83b5c584a6d` |
| runner, raw bytes (after the permitted release-literal patch) | `27f3d59b24f7d21918a2b3a85a0ec879a0d89bb80b9d3fbbe021dbd66efe8d4a` |
| runner, normalized source | `66bbda5c7d5fe69551dc897e730e3ee4fc3e2dd677d314888387a27181737c2c` |
| contract | `f289cd0ca1e81273cd45398e3b6d827d946197db989a8db638318665ede09ebf` |
| worker | `bdc6d2a6666c65a370d68f43a743458e8a811ac8cd0ec57a3a3f7704571e6d56` |
| cost model | `ee1d0dc3f9f15239cc7561c6437545c5c316f8148d9b70060217488428c6a2e3` |
| in-place L3 operator | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| protocol identity | `c2fa4f35bacf4b8f37f9755d62b0eb927eb2d7aa09eaa76f5082d6f8bfff1246` |
| runtime identity | `c7ee40a1ea4556b3dfc8617a91dbc176955bd03b9abcb9b4216e9533495214f7` |
| authorization audit | `6a3cec283c61d1d9f8f83b4c507e2b66e496027077c3281672d48cd0021ed896` |

The raw release file hashes to the sealed release hash; JSON parsing of those
same raw bytes yields exactly the payload verified by the runner. The payload
is schema 1, status `INDEPENDENT_EXECUTION_RELEASE`, run ID
`M116C_B4096_GENERATED_20260807`, and binds the contract, normalized runner,
the three source files, protocol, runtime, and the authorization audit above.
The audit filename is
`M116C_B4096_EXECUTION_AUTHORIZATION_AUDIT_20260807.md` and its verdict is
`PASS_TO_EXECUTE`.

The release declares `retry_allowed: false` and binds this fixed canonical
root:

```text
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation\m116c_inplace_l3_b4096_draft\M116C_B4096_GENERATED_CAMPAIGN
```

The runner's embedded release hash is present exactly once in the raw source,
matches the release raw hash, and its normalized hash matches the contract.
All fixed lexical paths used for this check (runner directory, contract,
release, audit, and canonical root) were direct paths rather than symlinks.
The canonical root was absent before and after the audit.

## Static and source-only checks

- `py_compile` passed for the runner, worker, cost model, in-place operator,
  and both test modules.
- The full source test command found 30 tests: 29 passed. The sole failure was
  the installed release making the pre-release assertion
  `assertFalse(EXECUTION_RELEASE_PATH.exists())` false. It occurs before the
  mocked campaign call and is expected once the release has been installed; it
  neither calls the campaign nor creates the canonical root.
- The 29 source/static/unit tests that do not make that pre-release-only claim
  were then run explicitly: 29 passed, with no errors or failures.

## M116b preservation

Every file in M116b's frozen manifest still hashes to its manifest value. The
three consumed terminal artifacts also equal the prior independent-result
judge's recorded hashes:

| Artifact | SHA-256 |
|---|---|
| `M116B_B2048_CLAIM.json` | `dc28bcccd71822e8760bb2168aac9340bcf4b04bceea48071232077e9c5436b1` |
| `M116B_B2048_FAILURE.json` | `a299f73e8880ae5b52d71d5403b97618aedaed76a988416b4bd4c5e7dc858e3b` |
| `M116B_B2048_TERMINAL.json` | `e7fa2cbc9d5b74a4cae1d748c87ddc7ea4857a8cd1095ad8046e10b1f1267fb1` |

No M116b artifact was changed by this audit.

## One authorized future invocation

Under the pinned `whest-v014` interpreter and the four one-thread environment
variables (`OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, and
`NUMEXPR_NUM_THREADS`, each `1`), the exact and only authorized call is:

```python
run_authorized_generated_campaign()
```

No argument, alternate root, substitute runtime, or retry is authorized.

## Gates intentionally still unobserved

No generated campaign was run. Therefore the complete B=4096/depth-32
numerical evidence remains unobserved, including the parent and child peak
budget (`<= 464`), prediction wall-time (`< 20 s`), residual threshold
(`<= 0.170`), all campaign protocol/aggregation checks, and the final
pass/fail terminal result. The release's one-shot and no-retry controls do not
turn these unobserved outcomes into passes.
