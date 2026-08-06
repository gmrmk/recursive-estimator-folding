# Localized packaging failure 1

The first Gate-A staging archive was built with `--estimator` pointing to the
single `candidate_source/estimator.py` file.  WHestBench correctly packaged
only that file plus its manifest.  `validate-package` checks manifest
integrity, not whether unresolved sibling imports will exist at grader import
time, so its success did not satisfy the stricter frozen seven-module content
gate.

This does not falsify the estimator or the row-blocked operator.  The passing
components remain the source import, synthetic prediction, bill identities,
numerical parity, compute, and process-memory gates.  The failed link is only
the packaging invocation target.

The parent package report documents the required mechanism: point WHestBench's
folder packager at the self-contained source directory.  The corrected v2
mutation changes only that packaging input path, does not alter any estimator
source byte, and occurs before any public score run.  The v1 archive is retained
as negative evidence and can never become the final candidate.
