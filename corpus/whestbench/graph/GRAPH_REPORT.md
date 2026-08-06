# Graph Report - work\scorefloor_generation\hyperconnection_graph  (2026-08-06)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 49 nodes · 65 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.74)
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
- [[_COMMUNITY_Community 9|Community 9]]

## God Nodes (most connected - your core abstractions)
1. `H1 equivariant learned residual closure` - 11 edges
2. `Winning legal adjusted score` - 9 edges
3. `Connected finite-width four-point vertex` - 8 edges
4. `H3 rank-5 k4 tensor sketch` - 7 edges
5. `Coordinatewise signed cumulant transport` - 6 edges
6. `Weight-identified latent-factor closure` - 6 edges
7. `Goal-oriented adjoint cumulant` - 5 edges
8. `Kerdock/MUB cubature` - 4 edges
9. `Full-covariance Gaussian closure` - 4 edges
10. `H2 weight-conditioned blend coefficient` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Connected finite-width four-point vertex` --target_effect_for--> `H1 equivariant learned residual closure`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 0 → community 2_
- `Kerdock/MUB cubature` --maps_to_existing_mechanism--> `Quantum-superposition translation`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 5 → community 9_
- `H1 equivariant learned residual closure` --supplies_features--> `Dyadic depth-memory features`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 2 → community 6_
- `Coordinatewise signed cumulant transport` --attempted_by--> `Finite-horizon factorized k3`  [INFERRED]
  CORPUS.md → CORPUS.md  _Bridges community 0 → community 4_
- `Winning legal adjusted score` --constrains--> `Fresh-private generalization`  [EXTRACTED]
  CORPUS.md → CORPUS.md  _Bridges community 4 → community 8_

## Communities (10 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.24
Nodes (12): Goal-oriented adjoint cumulant, Adjoint contraction factorization gate, Cavity/Dyson/TAP resummation, Dense k4 O(n^4)/O(n^5) wall, Connected finite-width four-point vertex, H3 rank-5 k4 tensor sketch, Rank-5 optimistic k4 ceiling, 8.187B per retained k4 pair rank (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (7): Approximate-mean theorem, Independent-scramble transfer, H2 weight-conditioned blend coefficient, Mediant dilution law, Global sampler/analytic blend, Sampler-scramble noise, Network-specific sign-changing control

### Community 2 - "Community 2"
Cohesion: 0.33
Nodes (6): Gauge-fixed contraction edges, H1 equivariant learned residual closure, Layerwise Hermite defect sources, Morphogenesis translation, Grouped-CV residual R2 > 0.965, Renormalization translation

### Community 3 - "Community 3"
Cohesion: 0.5
Nodes (5): Copula/two-Gaussian closure, Full-covariance Gaussian closure, Weight-identified latent-factor closure, Latent-factor closure gate, Strongly-on multiplicative bias mode

### Community 4 - "Community 4"
Cohesion: 0.5
Nodes (4): 272B combined-budget law, Finite-horizon factorized k3, Finite-horizon k3 premise gate, Winning legal adjusted score

### Community 5 - "Community 5"
Cohesion: 0.5
Nodes (4): Frame/design annihilation, Even spherical residual degree >=6, Kerdock/MUB cubature, Exact radial spherical reduction

### Community 6 - "Community 6"
Cohesion: 0.5
Nodes (4): Dyadic depth-memory features, Fractal/tau translation, Memristic translation, Retinal predictive-coding translation

### Community 7 - "Community 7"
Cohesion: 0.67
Nodes (3): Zero failures and Cmax < 258.4B, H4 sample-count mutation, Random 32,256 sampler

## Knowledge Gaps
- **21 isolated node(s):** `Exact radial spherical reduction`, `Sampler-scramble noise`, `H4 sample-count mutation`, `Grouped-CV residual R2 > 0.965`, `Rank-5 optimistic k4 ceiling` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Winning legal adjusted score` connect `Community 4` to `Community 0`, `Community 2`, `Community 3`, `Community 7`, `Community 8`, `Community 9`?**
  _High betweenness centrality (0.486) - this node is a cross-community bridge._
- **Why does `H1 equivariant learned residual closure` connect `Community 2` to `Community 0`, `Community 3`, `Community 4`, `Community 6`, `Community 8`?**
  _High betweenness centrality (0.387) - this node is a cross-community bridge._
- **Why does `Coordinatewise signed cumulant transport` connect `Community 0` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.283) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `H1 equivariant learned residual closure` (e.g. with `Connected finite-width four-point vertex` and `Morphogenesis translation`) actually correct?**
  _`H1 equivariant learned residual closure` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Connected finite-width four-point vertex` (e.g. with `True terminal k3/k4 oracle` and `H1 equivariant learned residual closure`) actually correct?**
  _`Connected finite-width four-point vertex` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `H3 rank-5 k4 tensor sketch` (e.g. with `Connected finite-width four-point vertex` and `Tensor-network translation`) actually correct?**
  _`H3 rank-5 k4 tensor sketch` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Coordinatewise signed cumulant transport` (e.g. with `True terminal k3/k4 oracle` and `Finite-horizon factorized k3`) actually correct?**
  _`Coordinatewise signed cumulant transport` has 2 INFERRED edges - model-reasoned connections that need verification._