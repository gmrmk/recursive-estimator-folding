# M239 predeclaration -- write-ahead receipt for frozen M238 G0A

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_RUNNER_AND_EXECUTION`.

M239 changes exactly one mechanism: durable evidence transport for one replay
of M238's unchanged six G0A tests. It does not edit M238's module, test,
predeclarations, inputs, formulas, thresholds, or gate order. It cannot run the
seventh G0B method, native G0C, variance, response, scorer, truth, challenge
weights, or integration.

Frozen parent artifacts:

```text
M238 module SHA256
  25A44983642BAD7136C3486DF71BE9A3476EB76A28D2F9BA656EAB446241C603
M238 test SHA256
  618D1EF92917166325458FA2D51CC7B2402DB0261589D013A601F1D4A6617C7A
M238 disposition SHA256
  842EE3E6AB58D1622CC8AD2D4F6CA4159C40609D9162A51D9E9A06A69BC959F0
M237 durable helper SHA256
  774CEF483C33B149524121144A4C5EDE9141F094AA6FE5037414E31BDDAC873C
```

The interpreter is frozen to:

```text
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\whest-starterkit\.venv\Scripts\python.exe
```

The working directory is M238's experiment folder. The exact ordered unittest
targets are:

```text
M238AlgebraAndInterfaceTests.test_production_source_has_no_generated_oracle_import
M238AlgebraAndInterfaceTests.test_dependency_free_nine_monomial_census
M238AlgebraAndInterfaceTests.test_all_twenty_columns_tree_and_m224_parity_on_frozen_grid
M238AlgebraAndInterfaceTests.test_positive_gauge_action_matches_every_frozen_column_degree
M238AlgebraAndInterfaceTests.test_co_permutation_changes_only_coordinate_names
M238AlgebraAndInterfaceTests.test_hostile_binders_domain_zero_write_and_one_use_lifetime
```

Each name is prefixed by `test_m238_live_m179_event_packer.` and passed to
`python -m unittest ... -v`. The target-digest/static-FlopScope G0B method is
not present in the command.

## Durable protocol

Before starting the child, the runner must:

1. verify every frozen hash and exact absence of the final result;
2. use M237's already-validated exclusive-create/fsync/canonical-JSON and
   no-overwrite hard-link publication primitives; and
3. publish `M239_G0A_LAUNCH_INTENT_20260809.json` containing the exact command,
   cwd, hashes, and forbidden-test list.

The runner then starts exactly one subprocess with a 120-second timeout,
captures complete stdout and stderr, records return code/duration and all six
per-test names, re-verifies parent hashes, and publishes pass or fail to
`M239_G0A_RESULT_20260809.json` through a same-directory temporary hard link.
The result must survive loss of the outer tool's stdout. Existing intent or
result paths fail closed; there is no rerun.

M239 passes only if the durable protocol itself succeeds. The six test outcomes
remain evidence about frozen M238 and cannot promote M239. After publication,
execution stops regardless of pass/fail; no G0B/G0C action is authorized.

