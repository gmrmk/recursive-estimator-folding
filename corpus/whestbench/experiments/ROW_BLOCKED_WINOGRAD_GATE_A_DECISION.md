# Gate A decision: PASS

Date: 2026-08-06

The immutable production source passed the complete no-truth gate and is
eligible for the separately frozen public-100 score run.

## Production measurements

- inherited parent modules: byte-identical 4/4;
- declared runtime modules: exactly 7;
- static shape checks: 131,072, zero bill mismatches, zero worse-than-direct;
- even row partitions: 96,768, zero mismatches;
- full prediction relative Frobenius: `4.282157660967493e-8`;
- maximum absolute prediction delta: `1.4981191647223113e-6`;
- depth-32 relative error: `2.485805510973982e-6`;
- depth-32 gate mismatches: `1/4,194,304`;
- parent/child synthetic effective compute:
  `186.895735127B / 175.189095496B`, ratio `0.9373627246`;
- child analytical FLOPs: `159.492745546B`;
- child peak working set: `474.859375 MiB`;
- operator workspace: `95,879,168 bytes = 91.4375 MiB`;
- setup/predict: `0.631762 s / 4.197633 s`;
- WHest estimator validation: passed, output `(2,4)`;
- row-block unit tests: passed 5/5.

The first staging package localized a packaging-call failure: pointing the
folder packager at one file produced only that file.  No estimator source or
score was changed.  The corrected directory package contains exactly the
seven runtime modules plus `manifest.json`; `validate-package` reports `ok`
with no issues.  This is the permitted failure-driven reimplementation in
`PACKAGING_FAILURE_1.md`.

Corrected staging archive SHA-256:
`bc2ec39558c76a67b12b587ca4ee70bb1e8921489643d83707e052d086e8ae36`.

Frozen production module SHA-256 values:

```text
b64376e09279e520465d63c4c0b2933a8edb0ec8eae9d6086c16c1830e7ece4e  base_estimator.py
21b077a7bcdf244b9480e891a8b63ecee05427d2725ea30ef5d2fc016bc03023  cost_model.py
d32de9fb7fa8f953fc873eec91a39e66778215f8607fb03bebbbe1292ca5d432  estimator.py
6952abc0a617e1fb32c64a4483f1539b79933c049f9190984460266bf357e116  fold3_estimator.py
0c6187e19cf567d7f7b5658902dc00a123f6219c815e2ea6711589e0a4e9159d  fold_estimator.py
24f2eebb1adf37f6be1392de57611c52cbaac7b04e319ff771533da54257796a  orthogonal_fold3.py
876ac0f042239c88bb48205585d7175da1f956ed0c4b96d8d6f95f5be5ea74b5  row_blocked_winograd.py
```

No WHestBench row, target, or scorer was opened by Gate A.  The next action is
the single unchanged child run on already-touched public rows 0..99.
