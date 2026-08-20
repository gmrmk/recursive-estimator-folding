# M112 independent frozen-manifest judgment — 2026-08-07

## Verdict: `PASS_TO_EXECUTE`

Frozen manifest SHA-256:
`00cdfe590f9f7af40f972ce94ad29bca1bf14df1f88637d2ab51d4f87d1f808c`.

This is a source-and-binding-only pre-execution judgment. I did **not** run
`analyze_m112_one_shot.py`, import that module, deserialize any NPZ member, or
touch a champion. The M111 archive was hashed as opaque bytes only.

## Exact analyzer contract

Static inspection of `analyze_m112_one_shot.py` shows that the manifest gate
requires the passing status, exactly the nine-file source surface, the fixed
theory and re-audit releases, a complete equality-checked runtime fingerprint,
the fixed schedule plus four W1 and four frame-block hash entries, the exact
M111 archive path and whole-file hash, and the exact pre-outcome cost schema.
It permits deserialization of only `raw_outputs` and `provenance` after these
checks. The manifest conforms to that contract.

## Recomputed bindings

All SHA-256 values below equal the values in the manifest.

| Bound item | SHA-256 |
|---|---|
| `ANALYSIS_CONFIG.json` | `e8087ec583157c213c1e35d09d2d4b5d5b810965a1fe85e6106886af33d30b57` |
| `COST_CALIBRATION.md` | `46f44a02948804cb6c0dc3eecc9bd410c9112873f4b4afd4e78ef4ab4c19233a` |
| `INVENTORY.md` | `fd9a1c5ed6f3e92977f3c43b8a5a02a9a6b4440857db05028246f28e9714ec9c` |
| `REFERENCE_AND_PROTOCOL.md` | `f049a26b3b33592ef0c961041175365e81e97457cd68c6160d32e79a18f12ee6` |
| `analyze_m112_one_shot.py` | `ef72d28d2d91bd8c84a2c8b97baf5ff66f57e82c5c461eaf3c26dcb26fa19fe9` |
| `m112_connected_gate_kernel.py` | `a0a9c053f9b96167be5f051056a66c71c59c4d5ef2bd523bf59e2f7de1782545` |
| `run_target_free_tests.py` | `73afac282dd921fbe402a82ff5b93a6e209617395f656a6a27dc0d7709eee9c4` |
| `test_m112_analyzer.py` | `d18c1b893f4263d2787aeddfac7c43f7dd792f6a3971f387c0b532d193c42878` |
| `test_m112_core.py` | `2245d50971fda00f5c3db1ba1085614d91a5f58eb7a598cba065224ebafad664` |
| repaired theory release | `5f8e5f12de65d3c910ed82ab18a05b9fb5f4994a1bd44bfaba61f52d422240c0` |
| independent re-audit release | `d4507b0f3012c2cad0c556de20c5ace9e7852777436bedb701c37f8089cd6f1f` |
| opaque M111 archive | `4f82e547901ecba643ee648c74656818c429ca38a9d9290fa907c8db26fd752e` |

The theory path resolves to
`work/scorefloor_generation/research_excursions/M112_CONNECTED_GATE_KERNEL_THEORY_20260807.md`;
the audit and cost-report paths resolve to their required files in
`work/scorefloor_generation/m112_connected_gate_kernel_draft`; and the input
path resolves exactly to
`work/scorefloor_generation/m111_coherent_gate_interferometer_draft/m111_evidence_frozen_run_20260807/m111_raw_frames.npz`.
The cost schema is exact, its report/config hashes equal the frozen source
hashes, its factor is `1.15`, and it declares no official flopscope.

The declared runtime was separately observed as CPython `3.12.13`, NumPy
`2.4.4`, and little-endian at the declared executable and NumPy paths. Its
executable and NumPy-init hashes respectively recompute to
`e850bfe7e4ca64d4b1a10a34fd8ab4f74108c75a559c200700655df9eaad905f` and
`b16a4f347c6583c878e1973a208564e01686b79cc70911ad0157e05d8eecda37`.

Independent deterministic regeneration (W1/frame generation only; no M111
archive access) reproduced the schedule hash
`5905d437506fb73ad097ac88d19067d72b814877cc85bbf82516b40b40d97210` and all
eight association hashes:

| Weight seed | W1 hash | 50-frame block hash |
|---:|---|---|
| 111001 | `549dd69033ab83f8e44d69ff14cf34cefb3c1463523ea68ff80ce0d5f0999b45` | `83677119a86b8c23d764755b15296f50105a536340d708e70f7134781af6029a` |
| 111002 | `800ddec2eed07c25ef99b8f9e2f90edd62fb2d8322cb8d0933ce2a0e854dba6b` | `d01ec2e58c440970559af065d7f335ee4f7a83d9f3dd839668397de9aeae360b` |
| 111003 | `b9410b1e7864f5974acd8ae5ee1ebe413e1d2436b95616524094f0b68b236e10` | `a642ce4c6b4b535b06c755f6cd33bec25e567134e5dbb6adf7b62fedd97c0685` |
| 111004 | `04e84389a02527c11d5b3858f432e6c1ba291474a51146aca277fe83a2edef04` | `9a6638b9873bdfc7e5da9884858c59ff63be664d6f42a397137b1995c38a0279` |

## Release ordering, lifecycle, and limitations

The complete independent source audit (`f7eea52de3100cbe04454cf0f2b17a69aa83350be2c2505289fe9f30f026a991`)
and its local release predate the manifest, and the release hashes exactly bind
the final nine-file surface. File times also support the ordering: final source
changes finished by `06:07:12 -05:00`, full audit at `06:10:38`, audit release
at `06:12:55`, then manifest at `06:14:02`.

The only canonical output path,
`m112_reuse_diagnostic_one_shot_output`, is absent. Recursive inspection of
the M112 draft found no `ONE_SHOT_CONSUMED.json`, result, failure, or kernel
artifact. Thus no prior one-shot claim or output exists.

This authorization remains strictly narrow: the fixed hash-derived M111 bank
is an association diagnostic only, with no conditional-zero or
conditional-unbiasedness claim. A favorable result cannot promote a champion,
access contest material, or authorize an estimator; it can only require a
separately specified and frozen M112b with frame roots statistically
independent of every weight root.
