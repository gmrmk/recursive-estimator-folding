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

---

# ADDENDUM: CReLU-antipodal channel splice (owner-prompted, judge arithmetic ~04:3x UTC)

IDENTITY: for each antipodal design pair (+u, -u), layer-1 activations satisfy
relu(z) - relu(-z) = z (odd channel, exactly linear) and relu(z) + relu(-z) = |z|
(even channel, nonlinear). Layer-2 preactivations for the pair are therefore
  z2(+/-) = ( W2|z| +/- (W2 W1) u ) / 2
and the odd channel (W2 W1) u rides the SAME Hadamard frame algebra as layer 1:
precompute W2W1 once per net (2n^3 = 3.4e7), then per frame ((W2W1)D_j)H^T via FWHT.
Layer 2's paid work collapses to the even channel alone: HALF the rows at full price.

ARITHMETIC [D, judge op-count]:
- layer-2 direct (fringe-priced): 6.587e9/net; CReLU route: 3.402e9/net
- saving 3.186e9/net = 1.511% of the champion suite bill
- COMBINED with the FWHT layer-1 splice: ratio 0.953989 (4.601% off the champion),
  stacked 0.845845 vs the parent route; IF tier-1's depth-swept-winograd composes,
  0.766244 vs the fringe champion (conditional on composed verification).

WHY IT DOES NOT RECURSE (the honest boundary): at layer >= 3 the pair difference
relu(a+b) - relu(a-b) is no longer globally linear (the even channel mixed in), and
the generic per-layer even/odd split relu(z) = z/2 + |z|/2 costs TWO matmuls
(telescoped linear chain + even channel) where direct costs one. CReLU pays exactly
once, at the design boundary, where the first nonlinearity's odd channel is still
linear in Hadamard-structured inputs.

RELU-VARIANT FAMILY SWEEP (doors with keys, not corpses):
- smooth variants (softplus/GELU) as propagation surrogates: the M181 smoothing kill
  (bias 4-6x); KEY: an exact computable smoothing-bias correction (none known).
- max-plus/tropical (relu as tropical algebra): the Crofton/facet door; KEY unchanged
  (m202 ESS + m86 ownership + m168 certificate simultaneously).
- leaky/parametric mixes (relu = (LReLU - alpha z)/(1-alpha)): elementwise identities
  only; the bill is matmul-dominated, elementwise choice moves nothing. No door.
- per-layer even/odd (CReLU everywhere): costs more than it saves (above). No door.

VERIFICATION GATES (same protocol as FWHT, ride the ladder verify): (i) double-count
check -- confirm the incumbent 64,512-row accounting does not already share antipodal
work at layer 2; (ii) composition audit with tier-1 depth-swept-winograd (its
per-layer pricing changes the layer-2 base); (iii) FlopScope pricing of the
precompute + FWHT adds, conservative count included.
