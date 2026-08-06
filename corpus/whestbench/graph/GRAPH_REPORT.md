# Graph Report - work\scorefloor_generation\hyperconnection_graph  (2026-08-06)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 53 nodes · 76 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]

## God Nodes (most connected - your core abstractions)
1. `Winning legal adjusted score` - 11 edges
2. `H1 equivariant learned residual closure` - 11 edges
3. `Weight-identified latent-factor closure` - 10 edges
4. `Connected finite-width four-point vertex` - 8 edges
5. `H3 rank-5 k4 tensor sketch` - 7 edges
6. `Coordinatewise signed cumulant transport` - 6 edges
7. `Goal-oriented adjoint cumulant` - 5 edges
8. `Kerdock/MUB cubature` - 4 edges
9. `Full-covariance Gaussian closure` - 4 edges
10. `H2 weight-conditioned blend coefficient` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Connected finite-width four-point vertex` --target_effect_for--> `H1 equivariant learned residual closure`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 6 → community 2_
- `Connected finite-width four-point vertex` --compressed_by--> `H3 rank-5 k4 tensor sketch`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 6 → community 5_
- `H1 equivariant learned residual closure` --supplies_features--> `Dyadic depth-memory features`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 2 → community 7_
- `Coordinatewise signed cumulant transport` --attempted_by--> `Finite-horizon factorized k3`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 6 → community 8_
- `Winning legal adjusted score` --constrains--> `272B combined-budget law`  [EXTRACTED]
  CORPUS.md → CORPUS.md  _Bridges community 1 → community 0_

## Communities (9 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.2
Nodes (10): 272B combined-budget law, Zero failures and Cmax < 258.4B, Recursive-fold 39,936 parent, Frame/design annihilation, H4 sample-count mutation, Even spherical residual degree >=6, Kerdock/MUB cubature, Quantum-superposition translation (+2 more)

### Community 1 - "Community 1"
Cohesion: 0.44
Nodes (9): Fresh-private generalization, Weight-identified latent-factor closure, Full-covariance sigma latent closure, Latent-factor closure gate, Latent q3,r3 mutation, Adaptive fixed-trace radial latent closure, Permutation + gauge + O(256) quotient, Winning legal adjusted score (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.29
Nodes (8): Full-covariance Gaussian closure, Gauge-fixed contraction edges, H1 equivariant learned residual closure, Layerwise Hermite defect sources, Morphogenesis translation, Grouped-CV residual R2 > 0.965, Renormalization translation, Strongly-on multiplicative bias mode

### Community 3 - "Community 3"
Cohesion: 0.29
Nodes (7): Approximate-mean theorem, Independent-scramble transfer, H2 weight-conditioned blend coefficient, Mediant dilution law, Global sampler/analytic blend, Sampler-scramble noise, Network-specific sign-changing control

### Community 4 - "Community 4"
Cohesion: 0.4
Nodes (5): Goal-oriented adjoint cumulant, Adjoint contraction factorization gate, Cavity/Dyson/TAP resummation, Dense k4 O(n^4)/O(n^5) wall, One-shot analytic terminal cumulants

### Community 5 - "Community 5"
Cohesion: 0.5
Nodes (4): H3 rank-5 k4 tensor sketch, Rank-5 optimistic k4 ceiling, 8.187B per retained k4 pair rank, Tensor-network translation

### Community 6 - "Community 6"
Cohesion: 0.67
Nodes (4): Copula/two-Gaussian closure, Connected finite-width four-point vertex, Coordinatewise signed cumulant transport, True terminal k3/k4 oracle

### Community 7 - "Community 7"
Cohesion: 0.5
Nodes (4): Dyadic depth-memory features, Fractal/tau translation, Memristic translation, Retinal predictive-coding translation

## Knowledge Gaps
- **20 isolated node(s):** `Exact radial spherical reduction`, `Sampler-scramble noise`, `H4 sample-count mutation`, `Grouped-CV residual R2 > 0.965`, `Rank-5 optimistic k4 ceiling` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Winning legal adjusted score` connect `Community 1` to `Community 0`, `Community 2`, `Community 4`, `Community 5`, `Community 8`?**
  _High betweenness centrality (0.524) - this node is a cross-community bridge._
- **Why does `H1 equivariant learned residual closure` connect `Community 2` to `Community 1`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.358) - this node is a cross-community bridge._
- **Why does `Coordinatewise signed cumulant transport` connect `Community 6` to `Community 8`, `Community 3`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.263) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Winning legal adjusted score` (e.g. with `Adaptive fixed-trace radial latent closure` and `Full-covariance sigma latent closure`) actually correct?**
  _`Winning legal adjusted score` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `H1 equivariant learned residual closure` (e.g. with `Connected finite-width four-point vertex` and `Morphogenesis translation`) actually correct?**
  _`H1 equivariant learned residual closure` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Connected finite-width four-point vertex` (e.g. with `True terminal k3/k4 oracle` and `H1 equivariant learned residual closure`) actually correct?**
  _`Connected finite-width four-point vertex` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `H3 rank-5 k4 tensor sketch` (e.g. with `Connected finite-width four-point vertex` and `Tensor-network translation`) actually correct?**
  _`H3 rank-5 k4 tensor sketch` has 2 INFERRED edges - model-reasoned connections that need verification._