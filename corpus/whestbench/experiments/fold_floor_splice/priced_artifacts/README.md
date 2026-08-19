# Priced but undeployed artifacts of the fold-floor splice

Modules kept for their verified price and their negative evidence, deliberately
outside `candidate_source/` so the shipped package contains only modules the
deployed path imports.

- `phased_wht.py` — the crowned phased-Walsh-Hadamard butterfly schedule for
  the first-layer product, ported and self-checked (`_selfcheck`), with its
  `butterfly_ops` price table. Nothing in `candidate_source/` imports it, and
  it must not be wired in on this lineage: the module's own
  `PHASED_DESIGN_IS_PARITY_PRESERVING = False` records that the butterfly
  computes `mean_chi * H diag(phase_s) M / 16`, which substitutes the sample
  design and therefore changes MSE — a class-B move against the per-net parity
  law, not a reassociation. It is priced here so the campaign can cost the
  substitution without re-porting it.
  `verify_fold_floor.py` still runs its `_selfcheck` and its price table from
  this directory, so the module stays covered while staying undeployed.
