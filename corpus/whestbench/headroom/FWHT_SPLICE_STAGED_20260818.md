# STAGED SPLICE: FWHT design-algebra route (judge arithmetic, awaiting hostile verify)

The one exact structure the champion's own algebra has not spent: the design IS 126
phased-Hadamard frames, so the FIRST-LAYER evaluation of the whole design admits the
fast Walsh-Hadamard transform.

IDENTITY: frame j's rows are D_j h over Hadamard rows h, so the frame's layer-1
preactivation block is Z_j = (W1 D_j) H^T. Right-multiplication by H^T via FWHT costs
n log2 n adds per row (2048 at n=256) instead of n^2 mult-adds. The antipodal half of
the design is exact negations: free. Layers 2-32 are untouched (post-ReLU activations
carry no Hadamard structure) and keep the fringe grouped-l2 route.

ARITHMETIC [D, judge op-count 2026-08-18 ~04:4x UTC]:
- fringe-priced layer-1 bill per net: 15.75 tiles x 418,238,464 = 6.587e9
- FWHT price per net: 126 x (256^2 sign-mask + 256 rows x 2048 FWHT) = 7.43e7
- speedup on layer 1: 88.6x ; saving 6.513e9/net = 3.09% of the champion suite bill
- stacked ratio vs parent route: 0.8866 x 0.9691 = 0.8592 (total FLOP-only win 14.1%)

LAWFULNESS: schedule-class exact reschedule (same real arithmetic, reordered) - the
same class as the adopted Winograd fringe route; touches no ReLU commutation (the
monomial law is about weight-side rank reduction; this is design-side factorization).
Compliance gates to verify hostilely (the Delta branch): (i) NOT already exploited in
the incumbent's accounting (double-count check); (ii) the deployed pipeline actually
bills layer-1 design evaluation at the generic tile price; (iii) FlopScope prices
adds/sign-ops per the receipts convention (count conservative: sign-mask included);
(iv) rounding-order differences are accepted for reschedule-class routes (fringe
precedent).

DISPOSITION: goes up the ladder as a seeded splice tier through the standard
drafter+hostile-verifier protocol when wf_c77f69d3-66f lands (or as a one-round
follow-up if the ladder dry-stops first). Nothing is adopted on judge arithmetic
alone.
