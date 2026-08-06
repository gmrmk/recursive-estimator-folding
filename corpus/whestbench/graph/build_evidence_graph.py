"""Build the auditable WHestBench relationship graph.

The local Graphify/Ollama semantic pass was intentionally treated as a noisy
proposal generator.  This graph is the human/model-audited replacement: every
edge has a relation, confidence class, and evidence source.  NetworkX is used
for topology; Graphify consumes the resulting node-link JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
OUT = HERE / "graphify-out"
GRAPH_PATH = OUT / "graph.json"
INSIGHTS_PATH = HERE / "DETERMINISTIC_INSIGHTS.md"


NODES = {
    "target": ("Winning legal adjusted score", "objective", "target", "Minimize private-suite adjusted MSE without failures."),
    "budget": ("272B combined-budget law", "constraint", "proved", "Billed FLOPs plus residual wall-time proxy; over-budget outputs are zeroed."),
    "fresh_private": ("Fresh-private generalization", "constraint", "rule", "A solution must generalize to newly generated MLPs rather than memorize public instances."),
    "symmetry_quotient": ("Permutation + gauge + O(256) quotient", "constraint", "proved", "Model features must respect hidden permutations, positive ReLU gauge, and Gaussian-input rotations."),
    "radial_sphere": ("Exact radial spherical reduction", "structure", "proved", "Positive homogeneity removes radial variance exactly."),
    "high_degree_residual": ("Even spherical residual degree >=6", "phenomenon", "measured", "Antipodal design removes odd and low-degree content; surviving error is high degree."),
    "finite_width_vertex": ("Connected finite-width four-point vertex", "phenomenon", "proved+measured", "The missing non-Gaussian dependence shared by analytic closure failures."),
    "sign_changing_control": ("Network-specific sign-changing control", "phenomenon", "measured", "Per-network oracle blend coefficients vary from -3.74 to +3.56."),
    "scramble_noise": ("Sampler-scramble noise", "phenomenon", "measured", "Fresh randomized probes introduce error signs not determined by weights alone."),
    "random32256": ("Random 32,256 sampler", "estimator", "promoted", "Official100: zero failures, max C 250.489B, adjusted 2.25708e-7."),
    "fold39936": ("Recursive-fold 39,936 parent", "estimator", "demoted", "Official100: five combined-budget failures, max C 294.999B."),
    "kerdock": ("Kerdock/MUB cubature", "estimator", "rejected", "Excellent low-degree cubature, but structured activations caused nonlinear cost excess."),
    "fullcov": ("Full-covariance Gaussian closure", "estimator", "rejected_parent", "Cheap and stable but raw MSE 5.43e-5 because every layer re-Gaussianizes."),
    "terminal_oracle": ("True terminal k3/k4 oracle", "oracle", "oracle", "Shows 4.7e-8 is possible if fixed-instance k3/k4 are available cheaply."),
    "terminal_analytic": ("One-shot analytic terminal cumulants", "estimator", "rejected", "Only 0.493% improvement."),
    "cavity_tap": ("Cavity/Dyson/TAP resummation", "estimator", "rejected", "Feed-forward DAG has zero Onsager self-reaction; generic vertex state is too large."),
    "copula": ("Copula/two-Gaussian closure", "estimator", "rejected", "Available moments do not identify dependence; generic propagation is too costly."),
    "scalar_hybrid": ("Global sampler/analytic blend", "estimator", "rejected", "Worsened raw MSE by 0.765%; oracle coefficients are instance-specific."),
    "h1_equivariant": ("H1 equivariant learned residual closure", "candidate", "rejected", "Hard-killed: 70 symmetry-safe features reach OOF R2 0.6627 versus the 0.965 gate."),
    "h2_coefficient": ("H2 weight-conditioned blend coefficient", "candidate", "blocked", "Weight-only sign transfer fails across sampler seeds; only seed-averaged magnitude remains plausible."),
    "h3_k4_rank5": ("H3 rank-5 k4 tensor sketch", "candidate", "rejected", "Hard-killed: even the optimal rank-5 ceiling has sign-unstable downstream corrections."),
    "h4_sample_count": ("H4 sample-count mutation", "candidate", "promoted", "Reduce points to buy safety and adjusted-score headroom."),
    "r2_gate": ("Grouped-CV residual R2 > 0.965", "falsifier", "predeclared", "Minimum premise gate for H1 before inference cost; championship scale is about 0.974."),
    "rank5_gate": ("Rank-5 optimistic k4 ceiling", "falsifier", "predeclared", "Require <=30% k4 error, stable signs, and <=50B projected cost."),
    "cross_seed_gate": ("Independent-scramble transfer", "falsifier", "measured", "All six current cross-seed oracle-transfer tests fail; ICC is 0.129."),
    "failure_gate": ("Zero failures and Cmax < 258.4B", "falsifier", "predeclared", "Candidate deployment safety gate."),
    "mediant": ("Mediant dilution law", "no_go", "proved", "A mixture of independent families cannot beat its more efficient component."),
    "approx_mean": ("Approximate-mean theorem", "no_go", "proved", "A noisy external control mean must already beat the sampler error to help."),
    "frame_annihilation": ("Frame/design annihilation", "no_go", "proved", "Low-degree polynomial controls vanish on exact frames/designs."),
    "dense_k4_cost": ("Dense k4 O(n^4)/O(n^5) wall", "no_go", "proved", "Generic storage and transport exceed the contest envelope."),
    "rank_cost": ("8.187B per retained k4 pair rank", "cost", "derived", "Rank5=40.936B; rank6=49.124B before recompression; rank7 impossible."),
    "retina": ("Retinal predictive-coding translation", "analogy", "mechanized", "Use a multiscale residual pyramid, not literal quantum vision."),
    "morphogenesis": ("Morphogenesis translation", "analogy", "mechanized", "Shared local update plus global normalization becomes equivariant message passing."),
    "memristic": ("Memristic translation", "analogy", "mechanized", "Compressed depth-history features encode hysteresis-like path dependence."),
    "fractal_tau": ("Fractal/tau translation", "analogy", "mechanized", "Dyadic depth scales and telescoping are retained only after covariance-cost tests."),
    "quantum": ("Quantum-superposition translation", "analogy", "exhausted", "Classically realized as signed orthogonal, antithetic, WHT, and MUB probes."),
    "tensor_network": ("Tensor-network translation", "analogy", "mechanized", "Low-rank vertex state is useful only if rank stays closed under every layer."),
    "renormalization": ("Renormalization translation", "analogy", "mechanized", "Learn weight-conditioned scale-dependent couplings rather than fixed scalar acceleration."),
    "depth_memory": ("Dyadic depth-memory features", "feature_family", "proposed", "Layer 1,2,4,8,16,32 innovations plus signed/absolute cancellation."),
    "hermite_defects": ("Layerwise Hermite defect sources", "feature_family", "proposed", "Non-Gaussian source proxies derived around the full-covariance state."),
    "gauge_edges": ("Gauge-fixed contraction edges", "feature_family", "proposed", "Adjacent-layer invariant contractions for unseen-network message passing."),
    "strong_on_scale": ("Strongly-on multiplicative bias mode", "phenomenon", "measured", "Alpha>2 outputs carry 91.36% of fullcov error; a shared scale explains most currently observable bias."),
    "signed_transport": ("Coordinatewise signed cumulant transport", "requirement", "derived", "The surviving challenge is preserving correction direction through rotating ReLU gates."),
    "k3_horizon": ("Finite-horizon factorized k3", "candidate", "rejected", "Hard-killed: safe and algebraically correct, but the best horizon is 583.1x worse adjusted than champion."),
    "adjoint_cumulant": ("Goal-oriented adjoint cumulant", "candidate", "rejected_component_preserved", "Terminal source projections are exact and cheap, but full covariance adjoints become generic full rank and promotion is killed."),
    "latent_factor": ("Weight-identified latent-factor closure", "candidate", "screened_live", "q3,r2 passed the exact synthetic premise by carrying weight-derived covariance factors through a capped Gaussian mixture."),
    "k3_horizon_gate": ("Finite-horizon k3 premise gate", "falsifier", "predeclared", "Require algebraic parity, finite safe cost, material raw improvement, and a route to champion score."),
    "adjoint_gate": ("Adjoint contraction factorization gate", "falsifier", "predeclared", "Require exact small-n parity, stable sign, and O(Ln3) all-output cost."),
    "latent_gate": ("Latent-factor closure gate", "falsifier", "predeclared", "Reject scale collapse, broken invariance, mixture explosion, or no small-n improvement over fullcov."),
}


# source, target, relation, confidence class, confidence score, evidence
EDGES = [
    ("budget", "target", "constrains", "PROVED", 1.0, "installed scorer"),
    ("fresh_private", "target", "constrains", "RULE", 1.0, "competition rules"),
    ("symmetry_quotient", "fresh_private", "protects", "PROVED", 0.95, "feature-graph derivation"),
    ("radial_sphere", "high_degree_residual", "reduces_problem_to", "PROVED", 1.0, "homogeneity"),
    ("high_degree_residual", "kerdock", "motivates", "MEASURED", 0.9, "harmonic ledger"),
    ("budget", "kerdock", "kills", "MEASURED", 1.0, "official cost tests"),
    ("frame_annihilation", "kerdock", "limits_controls_on", "PROVED", 1.0, "design exactness"),
    ("mediant", "scalar_hybrid", "limits", "PROVED", 0.95, "cost-variance law"),
    ("approx_mean", "scalar_hybrid", "limits", "PROVED", 0.95, "control theorem"),
    ("sign_changing_control", "scalar_hybrid", "explains_failure_of", "MEASURED", 0.9, "20-network hybrid screen"),
    ("fullcov", "finite_width_vertex", "leaves_unmodeled", "MEASURED", 0.9, "fullcov campaign"),
    ("terminal_oracle", "finite_width_vertex", "reveals_value_of", "ORACLE", 0.95, "terminal k3/k4 oracle"),
    ("terminal_analytic", "finite_width_vertex", "fails_to_recover", "MEASURED", 0.9, "0.493% gain"),
    ("cavity_tap", "finite_width_vertex", "requires", "PROVED", 0.9, "closure counterexample"),
    ("dense_k4_cost", "cavity_tap", "kills_generic_form", "PROVED", 1.0, "complexity accounting"),
    ("copula", "finite_width_vertex", "fails_to_identify", "PROVED", 0.9, "mixture closure report"),
    ("finite_width_vertex", "h1_equivariant", "target_effect_for", "HYPOTHESIS", 0.55, "feature-graph proposal"),
    ("finite_width_vertex", "h3_k4_rank5", "compressed_by", "HYPOTHESIS", 0.45, "tensor-sketch derivation"),
    ("dense_k4_cost", "h3_k4_rank5", "forces_compression_of", "PROVED", 1.0, "rank accounting"),
    ("rank_cost", "h3_k4_rank5", "constrains", "DERIVED", 1.0, "8.187B/rank"),
    ("rank5_gate", "h3_k4_rank5", "falsifies", "PREDECLARED", 1.0, "premise protocol"),
    ("fullcov", "h1_equivariant", "provides_baseline_for", "MEASURED", 0.85, "analytic state"),
    ("symmetry_quotient", "h1_equivariant", "required_by", "PROVED", 1.0, "network invariances"),
    ("r2_gate", "h1_equivariant", "falsifies", "PREDECLARED", 1.0, "required score contraction"),
    ("retina", "depth_memory", "maps_to", "TRANSLATION", 0.8, "residual pyramid"),
    ("memristic", "depth_memory", "maps_to", "TRANSLATION", 0.8, "path memory"),
    ("fractal_tau", "depth_memory", "maps_to", "TRANSLATION", 0.75, "dyadic scales"),
    ("morphogenesis", "h1_equivariant", "maps_to", "TRANSLATION", 0.8, "shared message passing"),
    ("renormalization", "h1_equivariant", "maps_to", "TRANSLATION", 0.75, "state-dependent coupling"),
    ("tensor_network", "h3_k4_rank5", "maps_to", "TRANSLATION", 0.85, "low-rank vertex"),
    ("quantum", "kerdock", "maps_to_existing_mechanism", "TRANSLATION", 0.9, "orthogonal signed probes"),
    ("quantum", "fold39936", "maps_to_existing_mechanism", "TRANSLATION", 0.9, "antithetic folds"),
    ("depth_memory", "h1_equivariant", "supplies_features", "HYPOTHESIS", 0.65, "feature graph"),
    ("hermite_defects", "h1_equivariant", "supplies_features", "HYPOTHESIS", 0.7, "feature graph"),
    ("gauge_edges", "h1_equivariant", "supplies_edges", "PROVED+HYPOTHESIS", 0.75, "feature graph"),
    ("scramble_noise", "h2_coefficient", "blocks_sign_prediction", "MEASURED", 0.95, "cross-seed tests"),
    ("cross_seed_gate", "h2_coefficient", "rejects_current_form", "MEASURED", 1.0, "six transfer failures"),
    ("sign_changing_control", "h2_coefficient", "originally_motivates", "ORACLE", 0.7, "oracle blend"),
    ("h4_sample_count", "random32256", "instantiates", "MEASURED", 1.0, "official100"),
    ("failure_gate", "random32256", "passed_by", "MEASURED", 1.0, "0 failures; Cmax250.489B"),
    ("failure_gate", "fold39936", "failed_by", "MEASURED", 1.0, "5 failures; Cmax294.999B"),
    ("random32256", "target", "current_best_path_to", "MEASURED", 0.9, "paired official100"),
    ("h1_equivariant", "target", "rejected_path_to", "MEASURED", 1.0, "grouped-CV R2 gate failed"),
    ("h3_k4_rank5", "target", "rejected_path_to", "MEASURED", 1.0, "rank-5 stability gate failed"),
    ("fold39936", "target", "unsafe_path_to", "MEASURED", 0.1, "budget failures"),
    ("h1_equivariant", "strong_on_scale", "reveals", "MEASURED", 1.0, "H1 diagnostics"),
    ("strong_on_scale", "fullcov", "dominates_error_of", "MEASURED", 0.95, "alpha-stratified SSE"),
    ("finite_width_vertex", "signed_transport", "requires", "DERIVED", 0.8, "cross-branch sign failures"),
    ("h3_k4_rank5", "signed_transport", "fails", "MEASURED", 1.0, "negative downstream cosine"),
    ("h2_coefficient", "signed_transport", "fails", "MEASURED", 1.0, "cross-seed sign failure"),
    ("terminal_oracle", "signed_transport", "motivates", "ORACLE", 0.9, "true k3/k4 correction"),
    ("signed_transport", "k3_horizon", "attempted_by", "HYPOTHESIS", 0.45, "factorized finite memory"),
    ("signed_transport", "adjoint_cumulant", "partially_preserved_by", "MEASURED", 0.8, "small-n k3/k4 correction cosines 0.951/0.762"),
    ("k3_horizon_gate", "k3_horizon", "falsifies", "PREDECLARED", 1.0, "recursion packet"),
    ("adjoint_gate", "adjoint_cumulant", "falsifies_promotion_of", "PREDECLARED+MEASURED", 1.0, "full covariance pullback rank1-to-rank8 and public0..4 2.12% gain"),
    ("k3_horizon", "target", "rejected_path_to", "MEASURED", 1.0, "official index0 premise failed"),
    ("adjoint_cumulant", "target", "rejected_path_to", "MEASURED", 1.0, "terminal fold insufficient; full dual O(Ln4)"),
    ("terminal_analytic", "adjoint_cumulant", "generator_repaired_by", "MEASURED", 0.9, "mean absolute skew restored from 0.0317 to 0.3867"),
    ("dense_k4_cost", "adjoint_cumulant", "reappears_in", "PROVED", 1.0, "generic full-rank covariance adjoint slices"),
    ("fullcov", "latent_factor", "extended_by", "MEASURED", 0.85, "synthetic summed-MSE ratio 0.04738"),
    ("copula", "latent_factor", "underidentification_avoided_by", "DERIVED+MEASURED", 0.75, "weight-derived factors define the ansatz without fitting a generic copula"),
    ("symmetry_quotient", "latent_factor", "required_by", "PROVED", 0.9, "equivariant factor selection"),
    ("latent_gate", "latent_factor", "passed_by", "PREDECLARED+MEASURED", 1.0, "q3,r2 wins 6/7 with exact invariance and bounded growth"),
    ("latent_factor", "target", "screened_path_to", "MEASURED+HYPOTHESIS", 0.45, "synthetic premise passed; legal target-shape cost/accuracy pending"),
    ("strong_on_scale", "latent_factor", "refined_beyond_scalar_by", "MEASURED", 0.8, "component means affine-rank2; scalar-fit residuals 0.407-0.814"),
]


def build() -> nx.Graph:
    graph = nx.Graph()
    for node_id, (label, kind, status, description) in NODES.items():
        graph.add_node(
            node_id,
            label=label,
            norm_label=label.lower(),
            type=kind,
            status=status,
            description=description,
            file_type="document",
            source_file="CORPUS.md",
            source_location=None,
            source_url=None,
            captured_at="2026-08-06",
            author="WHestBench campaign",
            contributor="Codex + user",
        )
    for source, target, relation, evidence_class, score, evidence in EDGES:
        graphify_confidence = (
            "INFERRED"
            if evidence_class in {"HYPOTHESIS", "TRANSLATION", "ORACLE"}
            else "EXTRACTED"
        )
        graph.add_edge(
            source,
            target,
            relation=relation,
            confidence=graphify_confidence,
            confidence_score=score,
            evidence_class=evidence_class,
            evidence=evidence,
            source_file="CORPUS.md",
        )
    return graph


def save_graph(graph: nx.Graph) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = nx.node_link_data(graph, edges="links")
    GRAPH_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def path_labels(graph: nx.Graph, source: str, target: str) -> str:
    path = nx.shortest_path(graph, source, target)
    return " -> ".join(graph.nodes[node]["label"] for node in path)


def write_insights(graph: nx.Graph) -> None:
    degree = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph)
    articulation = sorted(nx.articulation_points(graph), key=lambda n: (-betweenness[n], n))
    top_bridge = sorted(graph.nodes, key=lambda n: (-betweenness[n], -degree[n], n))[:10]
    communities = list(nx.community.greedy_modularity_communities(graph))

    lines = [
        "# Deterministic graph analysis",
        "",
        f"Nodes: {graph.number_of_nodes()}; edges: {graph.number_of_edges()}; communities: {len(communities)}.",
        "",
        "The metrics describe topology, not truth. Edge confidence and the original reports remain authoritative.",
        "",
        "## Highest-betweenness bridge nodes",
        "",
        "| node | status | betweenness | degree centrality |",
        "|---|---|---:|---:|",
    ]
    for node in top_bridge:
        lines.append(
            f"| {graph.nodes[node]['label']} | {graph.nodes[node]['status']} | "
            f"{betweenness[node]:.4f} | {degree[node]:.4f} |"
        )

    lines.extend(["", "## Articulation points", ""])
    lines.extend(f"- {graph.nodes[node]['label']}" for node in articulation)

    lines.extend(
        [
            "",
            "## Audited shortest paths to the target",
            "",
            f"- Current deployed path: {path_labels(graph, 'h4_sample_count', 'target')}",
            f"- Learned-closure path: {path_labels(graph, 'hermite_defects', 'target')}",
            f"- Tensor path: {path_labels(graph, 'tensor_network', 'target')}",
            f"- Retinal translation path: {path_labels(graph, 'retina', 'target')}",
            "",
            "## Decision insights",
            "",
            "1. The current entry improves through the budget/failure path, not through better raw integration.",
            "2. The connected four-point vertex is the shared bottleneck linking full-covariance failure, the terminal oracle gap, cavity/TAP failure, copula non-identifiability, and tensor rank growth.",
            "3. H1 and H3 were complementary attacks on that bottleneck, but both are now hard-killed: H3 loses downstream sign stability and H1 reaches only OOF R2 0.6627 versus 0.965.",
            "4. H2 is not a live sign-prediction method because sampler-scramble noise is not weight-identifiable. A seed-averaged magnitude model is a different, narrower hypothesis.",
            "5. The useful cross-domain translations converge on one architecture: multiscale residual sources, depth memory, invariant contractions, and shared local-to-global message passing.",
            "6. Both graph-prioritized mechanisms failed their cheap gates. The deployable frontier remains random32,256 while new coordinatewise signed-transport mechanisms are derived.",
        ]
    )
    INSIGHTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    evidence_graph = build()
    save_graph(evidence_graph)
    write_insights(evidence_graph)
    print(f"wrote {GRAPH_PATH}: {evidence_graph.number_of_nodes()} nodes, {evidence_graph.number_of_edges()} edges")
    print(f"wrote {INSIGHTS_PATH}")
