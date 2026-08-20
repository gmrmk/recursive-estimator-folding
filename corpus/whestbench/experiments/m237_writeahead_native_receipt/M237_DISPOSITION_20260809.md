# M237 disposition -- 2026-08-09

## Decision

`KILLED_FROZEN_NATIVE_GATE`

M237 is not promoted. Its sole authorized official-worker A -> B -> A native
falsifier completed and durably published an authoritative receipt, but every
prediction exceeded the frozen conservative combined-residual cap of
3.227021568 ms. The native aggregate and G0 remain closed. No rerun, retune,
or post-result code change is credited to M237.

## Authoritative evidence

- Launch intent: `M237_LAUNCH_INTENT_20260809.json`
  - SHA256: `73092A3F7924BA3E862008A9672D7275B3130AD2F6DF7F3F335B907D0E72CEC8`
- Durable result: `M237_NATIVE_ONE_PROCESS_RESULT_20260809.json`
  - SHA256: `07CF60ABCBA857F7A38D06F72C8C54F32430DB27EBC62DA0829FB8812DB1619E`
- Frozen sequence: setup seed 0; sources A=`227700001`, B=`227710001`;
  predictions A -> B -> A in one official worker.
- Worker PID `35148`; launcher PID `11624`; same-worker transport confirmed.
- Official start response: 2.023054300 s, below the frozen 4.0 s gate.
- Setup component time: 0.007436700 s; setup bill 32,768; 18 setup empty
  calls.

## Binding native failure

| Prediction | Combined residual (ms) | M212 residual (ms) | M235 residual (ms) | Peak RSS (MiB) |
|---|---:|---:|---:|---:|
| A1 | 5.162300105 | 3.133900114 | 1.242100057 | 388.81640625 |
| B  | 6.849999714 | 4.253499850 | 1.516299846 | 467.66015625 |
| A2 | 4.368399648 | 2.642899897 | 1.003999787 | 470.93750000 |

All three combined residuals exceed both the conservative cap
3.227021568 ms and the lawful cap 3.227087104 ms. All three M235 component
times pass its 2.025121700 ms cap. The observed split therefore localizes this
M237 failure to the retained M212/four-block dispatch side of the combined
topology, not to the M235 row-sketch component. This localization is evidence
about M237 only; no alternative block size or execution topology was tested.

Memory passes: maximum observed worker RSS was 470.9375 MiB, below the frozen
496 MiB gate. The frozen numeric allocation ledger also passes at 61,812,736
bytes (58.94921875 MiB): 32,569,344 global-source bytes, 19,218,432 B8 M212
bytes, 9,437,184 B8 M235 bytes, 63,488 rank bytes, and a 524,288-byte selected
gather.

## Exact accounting preserved

Every prediction reported the frozen exact bills:

- M212: 1,249,253,376
- M235: 864,960,512
- Combined: 2,114,213,888

Every prediction reported the frozen call dictionaries:

- M212: `add=12`, `copyto=100`, `diagonal=8`, `matmul=16`,
  `multiply=44`, `reshape=16`, `stack=8`, `sum=4`, `swapaxes=32`,
  `transpose=32`.
- M235: `add=36`, `copyto=4`, `matmul=8`, `multiply=64`, `sum=4`,
  `take_along_axis=4`.

## Passed components retained as evidence

- Durable write-ahead publication and launch-intent/result exclusivity passed.
- Endpoint replay passed bitwise: A1 and A2 output hash
  `e9d0f4dcef7859079581e624d0b154c88dc45805e4c71a9640e828537418f4d9`.
- Receipt law and stability passed; receipt hash
  `2200ac5f0e594c2eaa1231c9ccf01e291eaf1edc8318d4445590b7638c4f92b4`.
- Source arrays were finite, symmetric, and had the frozen full f64 shapes:
  `aaaa=(31,256)`, `aaab=(31,256,256)`, `aabb=(31,256,256)`.
- Returned response had shape `(32,256)`, dtype f32, and was finite.
- Exact source-byte replay, identity stability, workspace replay, slot clearing,
  global coverage, owner pointers, exact alias shapes/strides/spans, and gapped
  receipt-view checks all passed.
- All runtime hashes matched the launch intent. The executed runner SHA256 was
  `7D2298A703CA8CF7ECD2ACF80B1518EEE1E1D88D61271C5594E40E147925BDFF`;
  the probe SHA256 was
  `0DB0471755F12E8806C45B4E0C798E58B6A63080273C3EFACF7D6D9F597002A4`.

These passing parts remain reusable evidence for a separately predeclared
child. They do not rescue M237's failed combined native wall gate and confer no
promotion, budget retirement, aggregate, or G0 credit.

## Closed work

- Native ten-process aggregate: not opened.
- G0: not opened.
- Post-result rerun: not performed.
- Post-result retune or topology change: not performed.
- Contest truth, scorer, or challenge weights: not used.
