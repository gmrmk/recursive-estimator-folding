# DGFL-1 deterministic synthetic F0 notes

**Status:** `PASS_SYNTHETIC_MATH_ONLY`<br>
**Manifest:** `85CA3CCF5F6BE7E1E3DBF7F417E5CF1138F55B737F22B5A3F47BA9F5E7F4821B`<br>
**Source:** `2D8DE711FAF66C986F6C087A052BC828EDA4DFB0D81D994C6A217D7822CA0939`<br>
**Tests:** `0A05C5D22AF38F0E77528F1191F47EBE363CA7C99F9DB2C71441C9706EECFBDE`

## Outcome

The exact manifest-bound command passed 20 of 20 deterministic tests under
Python 3.12.13 and NumPy 2.3.5. It produced no bytecode cache and spawned no
workers. The shard cases are schedule simulations only. The verbatim combined
[test transcript](F0_TEST_TRANSCRIPT.txt), including the reported 0.186-second
duration, has SHA-256
`B3D9DB8DA851C5D92FA7A4D22D42F392C76D422EDB1348BD8D8892B2C13DB7D0`;
the process exit code was zero and the duration supports no performance claim.

The result verifies the small mathematical kernel used by the companion paper:
the rank-two skew geometry, shared JVP, dipole and Fourier product rules,
physical radius, WHest row-weight and absorbed-rotation convention, fusion,
antipodal parity, weak centering on a hand CPWL network, and canonical reduction.

## Test-driven chronology

The hostile additions first failed because malformed dipole geometry was not
rejected and adversarial shard completion order was absent. After those
contracts were implemented, an independent math audit found that the bank path
still propagated `u, Ju` rather than the physical `radius*u, J@(radius*u)`.
New radius and row-weight/absorbed-`Q` tests failed before the corresponding
source seams were added. The final sealed replay is the 20-test result above;
earlier development runs receive no evidence credit.

## Boundary

This is not a provider, production-source, generated-network, multiprocessing,
cost, variance, score, or contest result. It does not authorize the F1 network
panel. The next lawful gate is a source-only contract that binds how the exact
production rotation is retained, how selected rows are replayed, how all guard
branches remain total, and how complete serial costs and lifetimes are billed.
