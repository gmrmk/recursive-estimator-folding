# Random-frame fold3 n=32,256 submission package

Date: 2026-08-06  
Decision source: `random32256_paired100/REPORT.md`  
Artifact: `submission_random32256_20260806.tar.gz`

## Status

This folder is a self-contained packaging of the unchanged promoted
random-frame fold3 estimator. `estimator.py` is intentionally a thin entrypoint;
all four modules it imports are vendored beside it. The scored path needs no
external asset, repository-relative import, network access, API key, or package
outside the WHestBench/FlopScope runtime.

The source behavior is preserved:

- `n_base = 126 * 256 = 32,256` base directions;
- 126 seeded Haar orthogonal frames, radially fixed at `E[chi_d]`;
- antipodal first-layer propagation, yielding 64,512 paths;
- pilot-rescued dead-unit pruning;
- exact dead/on/kink folding over the final three layers;
- development-frozen first-layer moment tangent.

The promoted public-100 result was raw MSE `3.089512726e-7`, adjusted score
`2.257079776e-7`, mean effective compute `202.281790B`, maximum effective
compute `250.488783B`, and zero failures. This package does not rerun or alter
that experiment.

## Verification

No official scorer was run during packaging. No public index other than 0 was
accessed, and no index at or above 100 was accessed.

1. `tests.py` passed 4/4 tests in 0.240 seconds:
   setup determinism; predict determinism/finite/shape; static rejection of
   direct NumPy/SciPy/Torch/JAX/CuPy imports in runtime modules; and exact output
   parity with the promoted source on a deterministic synthetic network.
2. `verify_public0.py` directly evaluated only public index 0. Packaged and
   promoted-source predictions were bit-identical with shape `(32, 256)`, all
   finite values, maximum absolute delta `0.0`, and common prediction SHA-256
   `f362d37510edc7abd0250e7ffe5e1173d800ce569e020cff9f4b3ff4a6ab90f4`.
3. `whest validate` passed with class `Estimator` and validator output shape
   `(2, 4)` under WHestBench `0.14.0`.
4. `whest validate-package` returned `ok: true` with no issues.

Estimator-dependent array arithmetic imports only `flopscope.numpy`; analytic
normal PDF/CDF calls use `flopscope.stats`. Python `math` is used only in
`setup()` for the scalar chi-radius constant.

## Archive contents

The official WHestBench folder packager includes exactly these six files:

| File | Purpose |
|---|---|
| `estimator.py` | Grader entrypoint and frozen sample count |
| `orthogonal_fold3.py` | Seeded orthogonal-frame construction |
| `fold3_estimator.py` | Scored three-layer folding path |
| `fold_estimator.py` | Regime/refinement helpers |
| `base_estimator.py` | Estimator contract and analytic moment helpers |
| `manifest.json` | WHestBench-generated API/file-integrity manifest |

The archive explicitly contains no `__pycache__` or `.pyc` file. The packager's
built-in ignore rules enforce this, and the archive listing was inspected after
creation.

## Working-folder contents

Every regular file in this working folder is listed here:

| File | Included in archive? |
|---|---:|
| `.whestignore` | No |
| `base_estimator.py` | Yes |
| `estimator.py` | Yes |
| `fold3_estimator.py` | Yes |
| `fold_estimator.py` | Yes |
| `orthogonal_fold3.py` | Yes |
| `tests.py` | No |
| `verify_public0.py` | No |
| `PACKAGE_REPORT.md` | No |
| `SHA256SUMS.txt` | No |

The last four non-runtime artifacts are excluded by `.whestignore`; the ignore
file itself is excluded by the official packager's built-in rules.

## Reproduction commands

From the workspace root:

```powershell
work\whest-v014\Scripts\python.exe work\scorefloor_generation\submission_random32256_20260806\tests.py

work\whest-v014\Scripts\python.exe work\scorefloor_generation\submission_random32256_20260806\verify_public0.py

work\whest-v014\Scripts\whest.exe package --estimator work\scorefloor_generation\submission_random32256_20260806 --output submission_random32256_20260806.tar.gz --yes --format json

work\whest-v014\Scripts\whest.exe validate-package submission_random32256_20260806.tar.gz --format json
```

No upload, login, or submission action was performed.
