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
    "latent_factor": ("Weight-identified latent-factor closure", "candidate", "rejected_fixed_rank_components_preserved", "q3,r2 is honest and strong at small width but fails n64 because fixed-r trace capture vanishes with width."),
    "trace_collapse": ("Fixed-r covariance trace collapse", "failure_mechanism", "measured", "Top-two trace share falls from 88.4% at n4 to 3.02% at n256, reversing q3,r2 by n64."),
    "latent_rank3": ("Latent q3,r3 mutation", "candidate", "rejected", "One-factor increase is 27.22% worse than r2 under unchanged tensor quadrature and compression."),
    "latent_sparse": ("Adaptive fixed-trace radial latent closure", "candidate", "premise_running", "Use 2r signed cubature nodes over enough factors to capture a fixed trace fraction."),
    "sparse_harness": ("Sparse-radial measurement harness", "implementation", "rejected_candidate_pending", "Last-bin zero-progress loop caused 24.6/13.8GB workers; streaming truth itself stayed small."),
    "latent_random_radial": ("Randomized two-radius sigma closure", "candidate", "survived_n64", "Haar+chi2 ratio .6316,7/8 wins, every rotation<.8,70.590B,37MB."),
    "latent_random_radial_n128": ("Randomized-radial n128 scaling", "candidate", "survived", "Fresh ratio .634997,4/4 wins,every rotation<1,242MB, all guards."),
    "latent_random_radial_flopscope": ("Randomized-radial FlopScope port", "candidate", "component_preserved", "FP32 target port passes engineering, but its one-shot external accuracy is not competitive."),
    "latent_random_radial_dev100": ("Randomized-radial development100", "candidate", "rejected_accuracy", "Raw8.381e-5 and adjusted2.169e-5:96.118x worse than the deployed sampler champion."),
    "residual_r2_9896": ("Same-multiplier residual R2 .989596", "falsifier", "derived_caveated", "Severity threshold from a one-row/aggregate 96.1178x comparison; not an exact population bound without matched units."),
    "latent_full_sigma": ("Full-covariance sigma latent closure", "candidate", "rejected_component_preserved", "Covariance-exact 2n points pass symmetry/cost but fail n64 because low-degree axes alias ReLU gate crossings."),
    "latent_gate_split": ("Gate-aligned truncated projection mixture", "candidate", "rejected_direction_preserved", "Stable 8/8 improvement signs but only 0.2498% effect after generic recompression."),
    "latent_gate_memory": ("Gate-label path-memory recompression", "candidate", "rejected_constraint_preserved", "Local labels change meaning across layers; label aggregation erases 84% of the parent gain."),
    "latent_gate_rb": ("Rao-Blackwellized gate marginals", "candidate", "rejected_integrals_preserved", "Exact conditional marginals pass every audit and improve 8/8, but change the parent ratio by only 6.08e-8."),
    "scalar_dilution": ("Scalar gate-statistic O(1/n) dilution", "failure_mechanism", "measured", "One gate statistic explains about 1.0303e-4 of each n64 coordinate variance, making marginal corrections inert."),
    "pair_repeated": ("Repeated-index k3/k4 premise", "candidate", "rejected_orientation_preserved", "Preserves 94/97 signs but misses magnitude catastrophically because all-distinct entries cancel repeated sectors."),
    "all_distinct_cancel": ("All-distinct cumulant cancellation", "failure_mechanism", "measured", "Deleting all-distinct entries gives aggregate k3/k4 fidelities -249/-3578 by depth four."),
    "conditional_corr": ("Conditional-correlation spectrum", "candidate", "survived_compression_only", "Rank four retains 99.3533% energy and 99.1170% signs, but dense exact discovery costs 1.855T."),
    "response_gram": ("Conditional response-Gram factors", "candidate", "survived_formation", "Degree-four rank-four proxy recovers 95.03% energy and 95.92% signs for 0.510B."),
    "response_gram_recursion": ("q3 response-Gram recursion", "candidate", "rejected_operator_preserved", "Correction survives q3 reduction but one-scalar source is tiny; ratio 0.997502340 at 71.494B."),
    "multidirection_gate": ("Multi-direction gate response", "candidate", "rejected_directions_preserved", "Factor-only amplification was a cancellation false positive; complete k1 has PSD failures and k2+ is over budget."),
    "radial_susceptibility": ("Randomized-radial susceptibility compressor", "candidate", "rejected_pullback_preserved", "Passes structure/cost and layer0, but ratio .9753 and 11/24; mid/late covariance worsens."),
    "radial_dual_observable": ("Randomized-radial dual-observable compressor", "candidate", "rejected_lanes_preserved", "Scalar fusion passes structure/cost but reaches only .965944 and 17/24; gate and active lanes separate late."),
    "total_cumulance": ("Conditional total-cumulance factors", "candidate", "rejected_identity_preserved", "Exact identity and rank-four covariance survive; Gaussian cells omit residual k3/k4 and score 0.7872 combined."),
    "residual_cumulant": ("Conditional residual-cumulant spectrum", "candidate", "survived_representation", "Rank4 combined fidelity .9866 and 97/97 signs; exact factor formation is 129GiB for B16."),
    "residual_cov_algebra": ("Residual covariance-algebra factors", "candidate", "survived_algebra", "Fixed algebra retains .9727 combined fidelity and all signs; stable probe formation and recurrence remain."),
    "physarum_router": ("Physarum-attention MoE router", "candidate", "rejected_graph_preserved", "The fixed router collapses to fullcov and reaches .866761; preserve invariant query and flow graph for a complementary bank."),
    "flatworm_ladder": ("Flatworm two-lane attenuation", "candidate", "rejected_topology_preserved", "Fatigue balances routing load but worsens loss/cost; preserve paired longitudinal/commissural topology for distinct response lanes."),
    "ecn_jacobian_maxent": ("ECN-Jacobian MaxEnt compressor", "candidate", "rejected_components_preserved", "The .91147 no-ladder signal reproduces, but psi is a surrogate and target dense transport is 89.925B plus 38.65GB."),
    "ecn_exact_psi": ("Exact-psi streaming entropic compressor", "candidate", "proposed", "Replace only psi by exact ReLU derivatives in (alpha,log sigma), generalize phi, fix iterations, and resolve K=4qn streaming cost."),
    "weight_distillation": ("Exact-mean weight distillation", "candidate", "rejected_harness_preserved", "Layer1 ReLU and degree-{6,8} Gegenbauer students fail design-surviving cost-adjusted variance; preserve exact-mean cross-fit machinery."),
    "jspace_lens": ("JSpace fused Jacobian lens", "research_operator", "energy_gram_survived", "E[J] retains .1028 median energy; K4 E[D^T D] error .0857 and top8 overlap .9957 for 2.813B."),
    "jacobian_response_atoms": ("Jacobian-response control atoms", "feature_family", "rejected_top_modes", "Top terminal E[J^T J] directions yield4.758x raw and21.09x adjusted variance with0/16 wins."),
    "jspace_signed_pursuit": ("Signed Jacobian pursuit", "candidate", "rejected", "Only 8.66% terminal-residual and 1.91-point success improvement over nonnegative pursuit, below the frozen gate."),
    "jspace_inverse_complement": ("Bottom/complement JSpace control", "candidate", "rejected", "Bottom/complement improve over top modes but still score4.246x/4.563x raw,0/16,and near-zero correlation."),
    "analytic_residual_collapse": ("Constant analytic-residual collapse", "no_go", "proved", "a+mean(f-a)=mean(f); a constant analytic baseline cannot reduce sampling variance."),
    "failure_inversion": ("Failure inversion calculus", "operator", "mechanized", "Invert only a failed causal link; sign flips and basis changes within the same fitted span are equivalent."),
    "compression_score_law": ("Compression cost-times-variance law", "constraint", "proved", "Above the multiplier floor a child wins iff its cost ratio times raw-MSE ratio is below one."),
    "constant_modulus_blindness": ("Constant-modulus probe nullspace", "failure_mechanism", "proved+measured", "Hadamard/Rademacher probes are exactly blind to trace-free diagonal algebra and do not supply higher-moment responses."),
    "compressed_cumulant_transport": ("Compressed residual-cumulant transport", "candidate", "rejected_formation_preserved", "Oracle geometry stays strong, but constant-modulus cores are rank-deficient and the second-order state supplies no k3/k4 right-hand side."),
    "exact_sampler_strassen": ("Whole-row rectangular Strassen", "candidate", "rejected_algebra_preserved", "Full bill ratio .795427 and depth32 parity pass; allocation residual makes effective compute 8-45% worse."),
    "allocation_wall": ("Allocation/reconstruction residual wall", "failure_mechanism", "measured", "Python temporaries erase exact Strassen savings; L1 residual must fall below .00987s for parity."),
    "k3_horizon_gate": ("Finite-horizon k3 premise gate", "falsifier", "predeclared", "Require algebraic parity, finite safe cost, material raw improvement, and a route to champion score."),
    "adjoint_gate": ("Adjoint contraction factorization gate", "falsifier", "predeclared", "Require exact small-n parity, stable sign, and O(Ln3) all-output cost."),
    "latent_gate": ("Latent-factor closure gate", "falsifier", "expanded", "Require n64 width-law accuracy, exact relative-tolerance invariance, and conservative target cost after the small-width gate."),
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
    ("fullcov", "latent_factor", "extended_by_at_small_width", "MEASURED", 0.75, "small-width summed-MSE ratio 0.04738"),
    ("copula", "latent_factor", "underidentification_avoided_by", "DERIVED+MEASURED", 0.75, "weight-derived factors define the ansatz without fitting a generic copula"),
    ("symmetry_quotient", "latent_factor", "required_by", "PROVED", 0.9, "equivariant factor selection"),
    ("latent_gate", "latent_factor", "falsifies_fixed_rank_form", "PREDECLARED+MEASURED", 1.0, "n64 loses 8/8 after original small-width pass"),
    ("latent_factor", "target", "rejected_fixed_rank_path_to", "MEASURED", 1.0, "width law fails before target"),
    ("strong_on_scale", "latent_factor", "refined_beyond_scalar_by", "MEASURED", 0.8, "component means affine-rank2; scalar-fit residuals 0.407-0.814"),
    ("latent_factor", "trace_collapse", "fails_due_to", "MEASURED", 1.0, "trace fractions and n64 sweep"),
    ("trace_collapse", "latent_rank3", "not_repaired_by", "MEASURED", 1.0, "r3 ratio 0.0603 and unchanged compression"),
    ("latent_factor", "latent_rank3", "one_knob_child", "MEASURED", 1.0, "r2 to r3 only"),
    ("trace_collapse", "latent_sparse", "repaired_by_design_of", "HYPOTHESIS", 0.8, "fixed trace fraction with O(r) nodes"),
    ("trace_collapse", "latent_full_sigma", "eliminated_by_design_of", "PROVED+HYPOTHESIS", 0.9, "full covariance matched by 2n sigma points"),
    ("latent_factor", "latent_sparse", "preserved_components_reimplemented_in", "DERIVED", 0.9, "mixture and recompression retained"),
    ("sparse_harness", "latent_sparse", "fails_to_measure_not_falsify", "MEASURED", 1.0, "infinite zero-weight append; candidate remains pending"),
    ("latent_gate", "sparse_harness", "falsifies_resource_implementation", "PREDECLARED+MEASURED", 1.0, "workers exceed 2GB and do not complete"),
    ("latent_full_sigma", "latent_random_radial", "preserved_covariance_reimplemented_in", "DERIVED", 0.95, "change only angular orientation and radial order"),
    ("latent_full_sigma", "latent_random_radial", "axis_alias_targeted_by", "RESEARCH+HYPOTHESIS", 0.8, "seeded Haar frame"),
    ("radial_sphere", "latent_random_radial", "radial_moments_used_by", "PROVED+HYPOTHESIS", 0.85, "two-node chi quadrature matches moments through degree three"),
    ("latent_factor", "latent_full_sigma", "preserved_components_reimplemented_in", "DERIVED", 0.9, "mixture and recompression retained"),
    ("latent_gate", "latent_sparse", "falsifies", "PREDECLARED", 1.0, "n64 ratio/wins/invariance/cost gate"),
    ("latent_gate", "latent_full_sigma", "falsifies", "PREDECLARED+MEASURED", 1.0, "n64 ratio 8.8716; 1/8 wins"),
    ("latent_sparse", "target", "proposed_path_to", "HYPOTHESIS", 0.25, "premise running"),
    ("latent_gate", "latent_random_radial", "n64_gate_passed", "PREDECLARED+MEASURED", 1.0, "ratio .6316,7/8 wins, all rotations<.8,70.590B"),
    ("latent_random_radial", "latent_random_radial_n128", "frozen_operator_scaled_in", "DERIVED", 1.0, "fresh width law only"),
    ("latent_gate", "latent_random_radial_n128", "width_gate_passed", "PREDECLARED+MEASURED", 1.0, "ratio .634997,4/4,every rotation<1,all guards"),
    ("latent_random_radial_n128", "latent_random_radial_flopscope", "authorizes_port_of", "DERIVED", 1.0, "frozen production operator"),
    ("budget", "latent_random_radial_flopscope", "constrains", "RULE+MEASURED", 1.0, "actual charged calls and residual wall tail"),
    ("failure_gate", "latent_random_radial_flopscope", "synthetic_gate_passed", "PREDECLARED+MEASURED", 1.0, "six tests, 200 stage checks, finite, 71.423B adjusted, 210.6MB"),
    ("latent_random_radial", "target", "survived_component_toward", "MEASURED", 0.7, "strongest target-free estimator premise"),
    ("latent_random_radial_n128", "target", "survived_component_toward", "MEASURED", 0.8, "strong width-stable target-free premise"),
    ("latent_random_radial_flopscope", "latent_random_radial_dev100", "externally_falsified_by", "PREDECLARED+MEASURED", 1.0, "exactly one permitted development row"),
    ("latent_random_radial_dev100", "target", "rejected_path_to", "MEASURED", 1.0, "adjusted score96.1178x worse than champion"),
    ("latent_random_radial_dev100", "residual_r2_9896", "implies", "DERIVED", 1.0, "1-1/96.1178366555"),
    ("latent_random_radial_flopscope", "target", "component_only_not_path_to", "MEASURED", 1.0, "engineering passed but direct accuracy failed"),
    ("latent_full_sigma", "target", "rejected_path_to", "MEASURED", 1.0, "covariance exact but angular gate structure aliased"),
    ("latent_full_sigma", "finite_width_vertex", "fails_to_capture", "MEASURED", 0.95, "second moments do not determine gate crossings"),
    ("latent_factor", "latent_gate_split", "preserved_components_reimplemented_in", "DERIVED", 0.9, "forward mixture and recompression retained"),
    ("adjoint_cumulant", "latent_gate_split", "boundary_observable_informs", "DERIVED", 0.75, "goal-aligned rather than variance-aligned direction"),
    ("finite_width_vertex", "latent_gate_split", "targeted_by", "HYPOTHESIS", 0.55, "truncated conditional gate mixture"),
    ("latent_gate", "latent_gate_split", "falsifies_generic_compressor_form", "PREDECLARED+MEASURED", 1.0, "ratio 0.997502 despite 8/8 signs"),
    ("latent_gate_split", "target", "rejected_weak_path_to", "MEASURED", 1.0, "effect about 80x below gate"),
    ("latent_gate_split", "latent_gate_memory", "preserved_direction_reimplemented_in", "DERIVED", 0.95, "change compression only"),
    ("memristic", "latent_gate_memory", "maps_to", "TRANSLATION", 0.85, "persistent low/central/high state label"),
    ("latent_gate", "latent_gate_memory", "falsifies", "PREDECLARED+MEASURED", 1.0, "ratio 0.999603 and worse than parent 8/8"),
    ("latent_gate_memory", "target", "rejected_path_to", "MEASURED", 1.0, "ordinal labels are not coherent depth memory"),
    ("latent_gate_split", "latent_gate_rb", "conditional_skew_preserved_by", "DERIVED", 0.9, "replace Gaussianized marginals only"),
    ("latent_gate_memory", "latent_gate_rb", "generic_compressor_restored_in", "MEASURED+DERIVED", 0.85, "label compressor was uniformly worse"),
    ("latent_gate", "latent_gate_rb", "falsifies_marginal_only_form", "PREDECLARED+MEASURED", 1.0, "ratio 0.997502361; only 6.08e-8 better than parent"),
    ("latent_gate_rb", "scalar_dilution", "reveals", "MEASURED", 1.0, "T explains about 1.0303e-4 coordinate variance"),
    ("scalar_dilution", "latent_gate_rb", "explains_failure_of", "MEASURED+DERIVED", 0.98, "largest marginal correction 1.12e-7"),
    ("latent_gate_rb", "pair_repeated", "preserved_integrals_mutated_to_cross_neuron_state", "DERIVED", 0.8, "move from marginals to repeated-index cumulants"),
    ("latent_gate_rb", "conditional_corr", "preserved_conditioning_mutated_to_pairs", "DERIVED", 0.95, "integrate bivariate rather than univariate conditional moments"),
    ("finite_width_vertex", "pair_repeated", "compressed_by_hypothesis", "HYPOTHESIS", 0.45, "at-most-two-distinct-index slice"),
    ("finite_width_vertex", "conditional_corr", "compressed_by_hypothesis", "HYPOTHESIS", 0.5, "low-rank conditional covariance correction"),
    ("latent_gate", "pair_repeated", "falsifies_index_omission", "PREDECLARED+MEASURED", 1.0, "aggregate k3/k4 fidelity -249/-3578; only 3/9 energy passes"),
    ("pair_repeated", "all_distinct_cancel", "reveals", "MEASURED", 1.0, "94/97 signs but catastrophic magnitude"),
    ("all_distinct_cancel", "pair_repeated", "explains_failure_of", "MEASURED+DERIVED", 1.0, "missing harmonic sectors cancel repeated entries"),
    ("pair_repeated", "total_cumulance", "preserved_orientation_reimplemented_in", "DERIVED", 0.85, "replace index omission with implicit conditional factorization"),
    ("conditional_corr", "total_cumulance", "low_rank_state_informs", "MEASURED+HYPOTHESIS", 0.8, "rank-four conditional dependence may carry cancellation"),
    ("conditional_corr", "response_gram", "dense_discovery_reimplemented_in", "MEASURED+DERIVED", 1.0, "95.03 percent energy and 95.92 percent signs for 0.510B"),
    ("conditional_corr", "target", "survived_component_toward", "MEASURED", 0.45, "compression strong; formation unresolved"),
    ("latent_gate", "response_gram", "formation_gate_passed", "PREDECLARED+MEASURED", 1.0, "95.03 percent energy, 95.92 percent signs, 0.510B"),
    ("response_gram", "response_gram_recursion", "preserved_operator_inserted_in", "DERIVED", 1.0, "freeze degree, quadrature, rank, diagonal, and gain"),
    ("latent_gate_split", "response_gram_recursion", "parent_reimplemented_with", "DERIVED", 0.95, "change covariance correction only"),
    ("latent_gate", "response_gram_recursion", "falsifies_one_scalar_source", "PREDECLARED+MEASURED", 1.0, "ratio .997502340; source/cov median 9.64e-13"),
    ("scalar_dilution", "response_gram_recursion", "explains_failure_of", "MEASURED", 1.0, "q3 retains norm; source itself is tiny"),
    ("response_gram_recursion", "multidirection_gate", "preserved_operator_reimplemented_in", "DERIVED", 0.95, "expand direction bank only"),
    ("symmetry_quotient", "multidirection_gate", "constrains", "PROVED+HYPOTHESIS", 0.9, "invariant boundary-susceptibility Gram"),
    ("latent_gate", "multidirection_gate", "falsifies_gaussian_parent_form", "PREDECLARED+MEASURED", 1.0, "incomplete-source false positive; k1 PSD failures; k2+ over budget"),
    ("multidirection_gate", "radial_susceptibility", "preserved_direction_reimplemented_in", "DERIVED", 0.95, "apply only to non-Gaussian point cloud"),
    ("latent_random_radial", "radial_susceptibility", "parent_recompressed_by", "DERIVED", 0.9, "change q3 compressor only in clone"),
    ("latent_gate", "radial_susceptibility", "falsifies_single_geometry", "PREDECLARED+MEASURED", 1.0, "ratio .975251 and11/24 wins"),
    ("radial_susceptibility", "radial_dual_observable", "preserved_pullback_reimplemented_in", "DERIVED", 0.95, "add active covariance geometry only"),
    ("finite_width_vertex", "radial_dual_observable", "pair_covariance_targeted_by", "MEASURED+HYPOTHESIS", 0.75, "covariance is99.35 percent generic error"),
    ("latent_gate", "radial_dual_observable", "falsifies_scalar_fusion", "PREDECLARED+MEASURED", 1.0, "ratio .965944 and 17/24 wins despite structure/cost pass"),
    ("latent_gate", "total_cumulance", "falsifies_gaussian_cell_form", "PREDECLARED+MEASURED", 1.0, "k3/k4/combined fidelity .7560/.7966/.7872"),
    ("total_cumulance", "residual_cumulant", "preserved_identity_reimplemented_with", "DERIVED", 0.95, "add omitted within-cell k3/k4 factors only"),
    ("all_distinct_cancel", "residual_cumulant", "retained_by", "DERIVED", 0.9, "signed unfoldings retain every index sector"),
    ("latent_gate", "residual_cumulant", "representation_gate_passed", "PREDECLARED+MEASURED", 1.0, "rank4 combined .9866, correction .9955, 97/97 signs"),
    ("residual_cumulant", "residual_cov_algebra", "dense_formation_reimplemented_in", "DERIVED", 0.95, "reuse conditional covariance algebra"),
    ("conditional_corr", "residual_cov_algebra", "existing_factors_generate", "HYPOTHESIS", 0.65, "rank4 covariance products and diagonals"),
    ("latent_gate", "residual_cov_algebra", "algebra_gate_passed", "PREDECLARED+MEASURED", 1.0, "combined .9727 and 97/97 signs"),
    ("morphogenesis", "physarum_router", "maps_to", "PRIMARY_RESEARCH+DERIVED", 0.95, "adaptive conductance flow over expert graph"),
    ("memristic", "physarum_router", "conductance_memory_maps_to", "TRANSLATION", 0.8, "D retains path-dependent allocation"),
    ("symmetry_quotient", "physarum_router", "constrains_queries", "PROVED", 1.0, "alpha, boundary mass, covariance spectra, weight norms"),
    ("mediant", "physarum_router", "limits_unpredictable_mixing", "PROVED", 1.0, "routing needs predictable specialization"),
    ("cross_seed_gate", "physarum_router", "forbids_rotation_best_pick", "PROVED+MEASURED", 1.0, "route mechanisms not noisy Haar seeds"),
    ("latent_random_radial", "physarum_router", "strong_parent_expert_in", "MEASURED", 0.95, "Haar+chi2 reference expert"),
    ("latent_gate", "physarum_router", "falsifies_fixed_routing", "PREDECLARED+MEASURED", 1.0, "ratio .866761; all states select fullcov; bank oracle floor .829054"),
    ("physarum_router", "flatworm_ladder", "attenuated_by", "RESEARCH+DERIVED", 0.8, "two cords, commissures, and habituation recurrence"),
    ("latent_gate", "flatworm_ladder", "falsifies_router_attenuation", "PREDECLARED+MEASURED", 1.0, "loss 1.101064 and proxy cost 1.52484x"),
    ("radial_dual_observable", "flatworm_ladder", "preserved_lanes_reimplemented_in", "DERIVED", 0.85, "gate and active response lanes remain distinct"),
    ("radial_dual_observable", "ecn_jacobian_maxent", "response_features_inform_surrogate", "DERIVED+MEASURED", 0.8, "SPD response metric, not an exact observable Jacobian"),
    ("flatworm_ladder", "ecn_jacobian_maxent", "history_ablation_fails_in", "PREDECLARED+MEASURED", 1.0, "no-ladder .91147 versus ladder .93361"),
    ("symmetry_quotient", "ecn_jacobian_maxent", "constrains_transport", "PROVED+MEASURED", 0.95, "permutation and positive-gauge tests pass"),
    ("latent_gate", "ecn_jacobian_maxent", "falsifies_deployment", "PREDECLARED+MEASURED", 1.0, "ratio .91147 misses .8; K3072 dense cost 89.925B and 38.65GB"),
    ("ecn_jacobian_maxent", "ecn_exact_psi", "passed_transport_decoder_reimplemented_in", "DERIVED", 0.95, "preserve balanced transport and exact moment algebra only"),
    ("jspace_lens", "ecn_exact_psi", "exact_vjp_geometry_informs", "PRIMARY_RESEARCH+DERIVED", 0.8, "replace surrogate psi by chain-rule-correct Jacobian"),
    ("budget", "ecn_exact_psi", "requires_streaming_or_sparse_transport", "PROVED+DERIVED", 1.0, "dense K^2p form exceeds cost and memory"),
    ("frame_annihilation", "weight_distillation", "removes_low_degree_student_content", "PROVED+MEASURED", 1.0, "pointwise layer1 gain reverses on the 5-design"),
    ("high_degree_residual", "weight_distillation", "targeted_by", "HYPOTHESIS", 0.7, "even degree 6 and 8 exact-mean students"),
    ("latent_gate", "weight_distillation", "falsifies_generic_students", "PREDECLARED+MEASURED", 1.0, "Gegenbauer 174.995x cost-adjusted and 0/16 wins"),
    ("jspace_lens", "jacobian_response_atoms", "discovers_frozen_geometry_for", "PRIMARY_RESEARCH+HYPOTHESIS", 0.65, "fused VJP and sparse pursuit transfer"),
    ("jspace_lens", "jspace_signed_pursuit", "tested_by", "PREDECLARED+MEASURED", 1.0, "signed versus nonnegative 95-percent pursuit"),
    ("latent_gate", "jspace_signed_pursuit", "falsifies_materiality", "PREDECLARED+MEASURED", 1.0, "8.66 percent residual and 1.91 point success gains"),
    ("symmetry_quotient", "jspace_lens", "replaces_token_cone_in", "DERIVED", 0.9, "signed pursuit and energy Gram required for iid ReLU neurons"),
    ("finite_width_vertex", "jspace_lens", "gate_tumbling_tests", "HYPOTHESIS", 0.65, "compare E[D] cancellation against E[D^T D]"),
    ("weight_distillation", "jacobian_response_atoms", "failed_dictionary_reimplemented_with", "DERIVED", 0.9, "preserve exact-mean cross-fit machinery, replace generic harmonics"),
    ("latent_gate", "jacobian_response_atoms", "falsifies_top_modes", "PREDECLARED+MEASURED", 1.0, "Gram4.758x raw,21.09x adjusted,0/16,corr.0506"),
    ("jacobian_response_atoms", "target", "rejected_path_to", "MEASURED", 1.0, "terminal sensitivity is irrelevant to design residual"),
    ("jacobian_response_atoms", "jspace_inverse_complement", "failed_subspace_inverted_in", "DERIVED", 0.8, "bottom and top-orthogonal spaces on fresh seeds"),
    ("failure_inversion", "jspace_inverse_complement", "generates", "DERIVED", 0.9, "new subspace rather than sign flip"),
    ("failure_inversion", "analytic_residual_collapse", "certifies_no_go", "PROVED", 1.0, "sign/span and constant-baseline identities"),
    ("analytic_residual_collapse", "random32256", "reduces_to", "PROVED", 1.0, "sampling a constant residual is pure sampling"),
    ("residual_r2_9896", "failure_inversion", "constrains", "DERIVED", 1.0, "required grouped predictability before residual child"),
    ("latent_gate", "jspace_inverse_complement", "falsifies", "PREDECLARED+MEASURED", 1.0, "bottom4.246x/complement4.563x raw,0/16,corr near zero"),
    ("jspace_inverse_complement", "target", "rejected_path_to", "MEASURED", 1.0, "structural inversion reduces damage but never beats no control"),
    ("residual_cov_algebra", "compressed_cumulant_transport", "representation_reimplemented_by", "DERIVED", 0.95, "preserve12D algebra and97/97 signs; change formation only"),
    ("dense_k4_cost", "compressed_cumulant_transport", "avoided_by", "MEASURED+DERIVED", 0.9, "oracle response route costs12.340B without dense tensors"),
    ("budget", "compressed_cumulant_transport", "constrains", "PREDECLARED", 1.0, "complete analytic estimator below80B"),
    ("constant_modulus_blindness", "compressed_cumulant_transport", "kills_current_formation", "PROVED+MEASURED", 1.0, "min k3/k4 rank fractions .3611/.2051 and no observable RHS"),
    ("compressed_cumulant_transport", "target", "rejected_current_path_to", "MEASURED", 1.0, "representation survives but coefficient formation is unobservable"),
    ("compression_score_law", "compressed_cumulant_transport", "constrains", "PROVED", 1.0, "added correction must repay its complete cost"),
    ("random32256", "exact_sampler_strassen", "implementation_compressed_by", "DERIVED", 1.0, "change matrix products only"),
    ("compression_score_law", "exact_sampler_strassen", "falsifies_effective_cost", "PROVED+MEASURED", 1.0, "bill savings erased by residual charge"),
    ("allocation_wall", "exact_sampler_strassen", "kills_current_schedule", "MEASURED", 1.0, "direct8.444B versus L19.144B and L212.205B"),
    ("exact_sampler_strassen", "target", "rejected_current_path_to", "MEASURED", 1.0, "exact algebra preserved for a new allocation schedule"),
    ("ecn_exact_psi", "target", "proposed_path_to", "HYPOTHESIS", 0.3, "exact geometry and streaming cost must pass before accuracy"),
    ("response_gram", "target", "survived_component_toward", "MEASURED", 0.55, "affordable factor formation; recursion unresolved"),
    ("response_gram_recursion", "target", "rejected_weak_path_to", "MEASURED", 1.0, "factor survives but one-scalar effect is inert"),
    ("multidirection_gate", "target", "rejected_path_to", "MEASURED", 1.0, "exact Gaussian partition is no-op"),
    ("radial_susceptibility", "target", "rejected_weak_path_to", "MEASURED", 1.0, "mean geometry misses pair covariance"),
    ("radial_dual_observable", "target", "rejected_weak_path_to", "MEASURED", 1.0, "scalar fusion misses materiality; two lanes preserved"),
    ("total_cumulance", "target", "rejected_weak_path_to", "MEASURED", 1.0, "exact identity but Gaussian conditional residual is insufficient"),
    ("residual_cumulant", "target", "survived_component_toward", "MEASURED", 0.6, "representation strong; formation/recurrence unresolved"),
    ("residual_cov_algebra", "target", "survived_component_toward", "MEASURED", 0.55, "algebra strong; probes and recurrence unresolved"),
    ("physarum_router", "target", "rejected_weak_path_to", "MEASURED", 1.0, "router cannot beat the frozen expert-bank floor"),
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
            "6. Fixed-r latent mixtures are real small-width mechanisms but fail the width law because captured trace vanishes; increasing r from two to three does not repair the unchanged compressor.",
            "7. Matching the entire covariance with a 2n sigma rule still fails badly, proving that ReLU angular gate crossings are not determined by second moments.",
            "8. The deployed frontier remains random32,256. The randomized Haar plus chi-radial q3 closure passed internal scaling and engineering, then failed its one permitted development row by96.118x; retain its components, not its direct-estimator claim.",
            "9. JSpace terminal sensitivity is now exhausted as an integration control: top, bottom, and complement subspaces all have near-zero error correlation and lose every fresh case. Preserve G0 only as an offline diagnostic.",
            "10. Compression is now localized to two surviving components, not a deployable child: exact whole-row rectangular multiplication and a <=12D signed cumulant contraction. Their failed links are respectively allocation residual and weights-only higher-moment observability.",
            "11. Constant-modulus orthogonal probes cannot form the cumulant core: they are exactly blind to trace-free diagonal state, and the second-order conditional state contains no directional k3/k4 right-hand side.",
            "12. The next exact sampler mutation must preallocate reconstruction or change the Winograd schedule; the next analytic mutation must derive a Price/Hermite response recurrence before choosing nonconstant-amplitude probes.",
        ]
    )
    INSIGHTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    evidence_graph = build()
    save_graph(evidence_graph)
    write_insights(evidence_graph)
    print(f"wrote {GRAPH_PATH}: {evidence_graph.number_of_nodes()} nodes, {evidence_graph.number_of_edges()} edges")
    print(f"wrote {INSIGHTS_PATH}")
