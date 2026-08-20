from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import replace
from pathlib import Path
import sys
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for directory in (
    HERE,
    EXPERIMENTS / "m124_shared_k3_projector",
    EXPERIMENTS / "m125_source_batched_forward_tangent",
    EXPERIMENTS / "m178_certified_phi2_owent",
    EXPERIMENTS / "m179_background_archive_producer",
    EXPERIMENTS / "m167_collision_owner_unification",
    EXPERIMENTS / "m172_selective_22_owner_fusion",
):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import m124_shared_projector as m124  # noqa: E402
import m179_jacobian_archive as m179  # noqa: E402
from m125_forward_tangent import TangentState  # noqa: E402
from m167_collision_owner_unification import PhysicalFourthOwners  # noqa: E402
from m198_source211_delay_one_adapter import (  # noqa: E402
    DelayOneContext,
    LabelledSource211,
    LabelledTangent,
    M163_M172_OWNER,
    OwnershipConservationWitness,
    Source211Slots,
    SourceOwnerPolicy,
    add_sources,
    build_extended_background,
    build_labelled_carrier_maps,
    labelled_explicit_source_superposition,
    labelled_inhomogeneous_source_recurrence,
    make_context_provenance,
    issue_m172_source,
    reference_source211_delay_one,
    relu_gaussian_mean,
    scale_source,
    slots_from_dense_t4,
    source211_delay_one,
)


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def symmetric_t4(n: int, rng: np.random.Generator) -> np.ndarray:
    tensor = np.zeros((n, n, n, n), dtype=np.float64)
    for multiset in itertools.combinations_with_replacement(range(n), 4):
        value = float(rng.normal(scale=0.05))
        for permutation in set(itertools.permutations(multiset)):
            tensor[permutation] = value
    return tensor


def make_context(
    mean: np.ndarray,
    covariance: np.ndarray,
    *,
    layer: int = 2,
    epoch: int = 17,
    network_digest: str | None = None,
    weight_trace_digest: str | None = None,
) -> DelayOneContext:
    network = network_digest or digest(f"generated-network-{layer}-{epoch}")
    weight_trace = weight_trace_digest or digest(f"generated-trace-{layer}-{epoch}")
    provenance = make_context_provenance(
        mean,
        covariance,
        network_digest=network,
        weight_trace_digest=weight_trace,
        relu_layer=layer,
        producer_epoch=epoch,
    )
    return DelayOneContext(
        provenance=provenance,
        pre_mean=mean,
        pre_covariance=covariance,
        post_mean=relu_gaussian_mean(mean, covariance),
    )


def context(n: int, seed: int, layer: int = 2, epoch: int = 17) -> DelayOneContext:
    rng = np.random.default_rng(seed)
    factor = rng.normal(size=(n, n))
    covariance = factor @ factor.T / n + np.eye(n) * 0.75
    covariance = 0.5 * (covariance + covariance.T)
    mean = rng.normal(scale=0.35, size=n)
    return make_context(mean, covariance, layer=layer, epoch=epoch)


def source_from_dense(dense4: np.ndarray, ctx: DelayOneContext) -> LabelledSource211:
    return slots_from_dense_t4(dense4, ctx.provenance)


def generated_m172_source(entry, seed: int) -> LabelledSource211:
    rng = np.random.default_rng(seed)
    n = entry.mu.size
    weight = rng.normal(scale=0.22, size=(n, n))
    distinct = rng.normal(scale=0.03, size=(n, n, n))
    distinct = 0.5 * (distinct + distinct.swapaxes(1, 2))
    k4 = rng.normal(scale=0.02, size=n)
    k31 = rng.normal(scale=0.02, size=(n, n))
    np.fill_diagonal(k31, 0.0)
    k22 = rng.normal(scale=0.02, size=(n, n))
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k22, 0.0)
    factor = rng.normal(size=(n, n))
    covariance = factor @ factor.T / n + np.eye(n) * 0.8
    covariance = 0.5 * (covariance + covariance.T)
    return issue_m172_source(
        provenance=entry.provenance,
        weight=weight,
        distinct_211=distinct,
        owners=PhysicalFourthOwners(k4, k31, k22),
        covariance=covariance,
    )


class M198Source211DelayOneTests(unittest.TestCase):
    def test_dense_m124_regression_widths_two_through_seven(self):
        """Regression only: the independent oracle is a separate frozen gate."""

        maximum = 0.0
        for n in range(2, 8):
            rng = np.random.default_rng(198000 + n)
            ctx = context(n, 198100 + n)
            dense4 = symmetric_t4(n, rng)
            source = source_from_dense(dense4, ctx)
            observed = reference_source211_delay_one(source, ctx)
            expected = m124.edgeworth_delay_one(
                ctx.pre_mean,
                ctx.pre_covariance,
                np.zeros((n, n, n), dtype=np.float64),
                dense4,
            )
            maximum = max(
                maximum,
                float(np.max(np.abs(observed.mean - expected.mean))),
                float(np.max(np.abs(observed.covariance - expected.covariance))),
            )
        self.assertLessEqual(maximum, 2.0e-10)

    def test_independent_high_precision_directional_derivative_fixture(self):
        fixture_path = HERE / "m198_independent_oracle_fixture.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(fixture["oracle"], "mpmath_100dps_rank1_d4_no_m124_m178_m179")
        self.assertIn("yields O(h^8)", fixture["finite_difference"])
        self.assertIn("correction proxy", fixture["correction_proxy_note"])
        self.assertEqual(
            [case["case_id"] for case in fixture["cases"]],
            ["rank1_n2_pos", "rank1_n3_neg", "rank1_n4_pos", "rank1_n5_neg"],
        )
        self.assertLessEqual(
            max(
                float(case["max_richardson_fine_correction_proxy"])
                for case in fixture["cases"]
            ),
            3.0e-10,
        )
        maximum = 0.0
        for case in fixture["cases"]:
            mean = np.asarray(case["mean"], dtype=np.float64)
            covariance = np.asarray(case["covariance"], dtype=np.float64)
            direction = np.asarray(case["direction"], dtype=np.float64)
            coefficient = float(case["coefficient"])
            dense4 = coefficient * np.einsum(
                "i,j,k,l->ijkl", direction, direction, direction, direction
            )
            ctx = make_context(
                mean,
                covariance,
                layer=int(case["layer"]),
                epoch=int(case["epoch"]),
                network_digest=digest(case["case_id"] + "-network"),
                weight_trace_digest=digest(case["case_id"] + "-trace"),
            )
            observed = reference_source211_delay_one(source_from_dense(dense4, ctx), ctx)
            expected_mean = np.asarray(case["expected_delta_mean"], dtype=np.float64)
            expected_covariance = np.asarray(
                case["expected_delta_covariance"], dtype=np.float64
            )
            maximum = max(
                maximum,
                float(np.max(np.abs(observed.mean - expected_mean))),
                float(np.max(np.abs(observed.covariance - expected_covariance))),
            )
        self.assertLessEqual(maximum, 2.0e-10)

    def test_context_provenance_rejects_same_labels_different_state(self):
        n = 4
        first = context(n, 198202)
        second_mean = np.array(first.pre_mean, copy=True)
        second_mean[0] = np.nextafter(second_mean[0], np.inf)
        second = make_context(
            second_mean,
            first.pre_covariance,
            layer=first.relu_layer,
            epoch=first.producer_epoch,
            network_digest=first.provenance.network_digest,
            weight_trace_digest=first.provenance.weight_trace_digest,
        )
        source = source_from_dense(
            symmetric_t4(n, np.random.default_rng(198201)), first
        )
        with self.assertRaisesRegex(ValueError, "not issued by m172_selective_22"):
            source211_delay_one(source, second)
        with self.assertRaisesRegex(ValueError, "provenance mismatch"):
            reference_source211_delay_one(source, second)
        with self.assertRaisesRegex(ValueError, "pre-state digest mismatch"):
            DelayOneContext(
                provenance=first.provenance,
                pre_mean=second_mean,
                pre_covariance=first.pre_covariance,
                post_mean=relu_gaussian_mean(second_mean, first.pre_covariance),
            )

    def test_all_public_arrays_are_immutable_snapshots(self):
        n = 3
        raw_aaaa = np.asarray([1.0, 2.0, 3.0])
        raw_aaab = np.arange(9, dtype=np.float64).reshape(3, 3)
        np.fill_diagonal(raw_aaab, raw_aaaa)
        raw_aabb = np.eye(3)
        slots = Source211Slots(raw_aaaa, raw_aaab, raw_aabb)
        snapshot = slots.aaab.copy()
        raw_aaab[0, 1] = 999.0
        self.assertTrue(np.array_equal(slots.aaab, snapshot))
        with self.assertRaises(ValueError):
            slots.aaab.setflags(write=True)
        with self.assertRaises(ValueError):
            slots.aaab[0, 1] = 7.0

        raw_mean = np.asarray([0.1, -0.2, 0.3])
        raw_covariance = np.eye(n)
        ctx = make_context(raw_mean, raw_covariance)
        snapshot_mean = ctx.pre_mean.copy()
        raw_mean[0] = 777.0
        raw_covariance[0, 0] = 888.0
        self.assertTrue(np.array_equal(ctx.pre_mean, snapshot_mean))
        self.assertEqual(ctx.pre_covariance[0, 0], 1.0)
        with self.assertRaises(ValueError):
            ctx.pre_mean.setflags(write=True)

    def test_ownership_conservation_and_adversarial_mutations(self):
        n = 4
        rng = np.random.default_rng(198802)
        weights = [rng.normal(scale=0.2, size=(n, n)) for _ in range(2)]
        entry = build_extended_background(weights, epoch=31)[0]
        source = generated_m172_source(entry, 198803)
        source211_delay_one(source, entry.delay_one_context)
        witness = source.ownership

        with self.assertRaisesRegex(ValueError, "physical-control=residual"):
            replace(
                witness,
                residual_ijj=np.zeros((n, n), dtype=np.float64),
            )

        nonzero_legacy = Source211Slots(np.ones(n), np.eye(n), np.eye(n))
        with self.assertRaisesRegex(ValueError, "not retired"):
            replace(
                witness,
                retired_legacy_k22_slots=nonzero_legacy,
            )

        changed_slots = Source211Slots(
            witness.retained_k4_source_slots.aaaa + 1.0e-3,
            witness.retained_k4_source_slots.aaab + np.eye(n) * 1.0e-3,
            witness.retained_k4_source_slots.aabb,
        )
        with self.assertRaisesRegex(ValueError, "omits or double-counts"):
            replace(
                witness,
                retained_k4_source_slots=changed_slots,
            )

        forged_witness = replace(witness, issuer_receipt="f" * 64)
        with self.assertRaisesRegex(ValueError, "forged.*ownership"):
            LabelledSource211(
                provenance=source.provenance,
                owner=M163_M172_OWNER,
                ownership=forged_witness,
                slots=source.slots,
                source_receipt=source.source_receipt,
            )
        other_source = generated_m172_source(entry, 198804)
        with self.assertRaisesRegex(ValueError, "not bound"):
            LabelledSource211(
                provenance=source.provenance,
                owner=M163_M172_OWNER,
                ownership=other_source.ownership,
                slots=source.slots,
                source_receipt=source.source_receipt,
            )
        with self.assertRaisesRegex(ValueError, "owner family"):
            SourceOwnerPolicy(family="self_certified_boolean_tag")

        # Frozen dataclasses are not treated as an integrity boundary: a
        # malicious object.__setattr__ mutation is detected by recomputation.
        object.__setattr__(source.slots, "aaaa", np.zeros(n))
        with self.assertRaises(ValueError):
            source211_delay_one(source, entry.delay_one_context)

    def test_production_m172_issue_widths_two_through_seven(self):
        maximum_conservation = 0.0
        for n in range(2, 8):
            rng = np.random.default_rng(198820 + n)
            weights = [rng.normal(scale=0.18, size=(n, n))]
            entry = build_extended_background(weights, epoch=37)[0]
            source = generated_m172_source(entry, 198830 + n)
            tangent = source211_delay_one(source, entry.delay_one_context)
            self.assertTrue(np.all(np.isfinite(tangent.state.mean)))
            self.assertTrue(np.all(np.isfinite(tangent.state.covariance)))
            witness = source.ownership
            maximum_conservation = max(
                maximum_conservation,
                float(
                    np.max(
                        np.abs(
                            witness.prior_owned_slots.aaaa
                            - witness.emitted_source_slots.aaaa
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            witness.prior_owned_slots.aaab
                            - witness.emitted_source_slots.aaab
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            witness.prior_owned_slots.aabb
                            - witness.emitted_source_slots.aabb
                        )
                    )
                ),
            )
        self.assertLessEqual(maximum_conservation, 5.0e-10)

    def test_linearity(self):
        n = 5
        rng = np.random.default_rng(198301)
        ctx = context(n, 198302)
        left = source_from_dense(symmetric_t4(n, rng), ctx)
        right = source_from_dense(symmetric_t4(n, rng), ctx)
        x, y = 1.75, -0.625
        combined = reference_source211_delay_one(
            add_sources(scale_source(left, x), scale_source(right, y)), ctx
        )
        a = reference_source211_delay_one(left, ctx)
        b = reference_source211_delay_one(right, ctx)
        self.assertLessEqual(
            np.max(np.abs(combined.mean - (x * a.mean + y * b.mean))), 2.0e-11
        )
        self.assertLessEqual(
            np.max(
                np.abs(combined.covariance - (x * a.covariance + y * b.covariance))
            ),
            2.0e-11,
        )

    def test_permutation_covariance(self):
        n = 6
        rng = np.random.default_rng(198401)
        ctx = context(n, 198402)
        dense4 = symmetric_t4(n, rng)
        reference = reference_source211_delay_one(source_from_dense(dense4, ctx), ctx)
        permutation = np.asarray([3, 0, 5, 1, 4, 2])
        permuted_mean = ctx.pre_mean[permutation]
        permuted_covariance = ctx.pre_covariance[np.ix_(permutation, permutation)]
        permuted_context = make_context(
            permuted_mean,
            permuted_covariance,
            layer=ctx.relu_layer,
            epoch=ctx.producer_epoch,
            network_digest=digest("permuted-network"),
            weight_trace_digest=digest("permuted-trace"),
        )
        permuted_dense = dense4[np.ix_(permutation, permutation, permutation, permutation)]
        observed = reference_source211_delay_one(
            source_from_dense(permuted_dense, permuted_context), permuted_context
        )
        self.assertLessEqual(
            np.max(np.abs(observed.mean - reference.mean[permutation])), 2.0e-11
        )
        self.assertLessEqual(
            np.max(
                np.abs(
                    observed.covariance
                    - reference.covariance[np.ix_(permutation, permutation)]
                )
            ),
            2.0e-11,
        )

    def test_positive_gauge_covariance(self):
        n = 5
        rng = np.random.default_rng(198501)
        ctx = context(n, 198502)
        dense4 = symmetric_t4(n, rng)
        reference = reference_source211_delay_one(source_from_dense(dense4, ctx), ctx)
        diagonal = np.asarray([0.5, 0.8, 1.1, 1.6, 2.0])
        gauged_context = make_context(
            ctx.pre_mean * diagonal,
            ctx.pre_covariance * diagonal[:, None] * diagonal[None, :],
            layer=ctx.relu_layer,
            epoch=ctx.producer_epoch,
            network_digest=digest("gauged-network"),
            weight_trace_digest=digest("gauged-trace"),
        )
        gauged_dense = (
            dense4
            * diagonal[:, None, None, None]
            * diagonal[None, :, None, None]
            * diagonal[None, None, :, None]
            * diagonal[None, None, None, :]
        )
        observed = reference_source211_delay_one(
            source_from_dense(gauged_dense, gauged_context), gauged_context
        )
        self.assertTrue(
            np.allclose(observed.mean, reference.mean * diagonal, rtol=2e-9, atol=2e-9)
        )
        self.assertTrue(
            np.allclose(
                observed.covariance,
                reference.covariance * diagonal[:, None] * diagonal[None, :],
                rtol=2e-9,
                atol=2e-9,
            )
        )

    def test_extended_archive_parity_and_frozen_maps(self):
        rng = np.random.default_rng(198601)
        weights = [rng.normal(scale=0.2, size=(4, 4)) for _ in range(3)]
        extended = build_extended_background(weights, epoch=19)
        reference = m179.build_archive(weights, epoch=19)
        self.assertEqual(len(extended), len(reference))
        for observed, expected in zip(extended, reference):
            self.assertEqual(observed.layer, expected.layer)
            self.assertTrue(np.array_equal(observed.mu, expected.mu))
            self.assertTrue(np.array_equal(observed.V, expected.V))
            for field in (
                "probability",
                "mean_variance_derivative",
                "price_kernel",
                "h_mu",
                "h_variance",
            ):
                self.assertTrue(
                    np.array_equal(
                        getattr(observed.jacobian, field), getattr(expected.jacobian, field)
                    )
                )
            with self.assertRaises(ValueError):
                observed.mu.setflags(write=True)
        maps = build_labelled_carrier_maps(extended, weights)
        with self.assertRaises(ValueError):
            maps[0].weight.setflags(write=True)
        before = maps[0].weight.copy()
        weights[1][0, 0] += 10.0
        self.assertTrue(np.array_equal(maps[0].weight, before))

    def test_labelled_carrier_identity_and_fail_closed_mutations(self):
        rng = np.random.default_rng(198701)
        weights = [rng.normal(scale=0.15, size=(4, 4)) for _ in range(4)]
        entries = build_extended_background(weights, epoch=23)
        sources = []
        for index, entry in enumerate(entries):
            source = generated_m172_source(entry, 198710 + index)
            sources.append(source211_delay_one(source, entry.delay_one_context))
        maps = build_labelled_carrier_maps(entries, weights)
        explicit = labelled_explicit_source_superposition(sources, maps)
        folded = labelled_inhomogeneous_source_recurrence(sources, maps)
        self.assertTrue(np.allclose(explicit.state.mean, folded.state.mean, atol=2e-12))
        self.assertTrue(
            np.allclose(explicit.state.covariance, folded.state.covariance, atol=2e-12)
        )
        self.assertEqual(len(folded.consumed_source_ids), len(sources))
        self.assertEqual(len(set(folded.consumed_source_ids)), len(sources))

        reordered = [sources[1], sources[0], *sources[2:]]
        with self.assertRaisesRegex(ValueError, "mismatch or reorder"):
            labelled_inhomogeneous_source_recurrence(reordered, maps)
        with self.assertRaisesRegex(ValueError, "indexing mismatch"):
            labelled_inhomogeneous_source_recurrence([*sources, sources[-1]], maps)
        duplicate = [sources[0], sources[1], sources[1], sources[3]]
        with self.assertRaisesRegex(ValueError, "duplicate source"):
            labelled_inhomogeneous_source_recurrence(duplicate, maps)
        with self.assertRaisesRegex(ValueError, "mismatch or reorder"):
            labelled_inhomogeneous_source_recurrence(sources, [maps[1], maps[0], maps[2]])

        arbitrary = TangentState(np.ones(4), np.eye(4))
        with self.assertRaisesRegex(ValueError, "does not match"):
            LabelledTangent(
                source=sources[0].source,
                context=sources[0].context,
                state=arbitrary,
                conversion_receipt="f" * 64,
            )

        object.__setattr__(maps[0], "weight", np.zeros_like(maps[0].weight))
        with self.assertRaisesRegex(ValueError, "tampered carrier-map"):
            labelled_inhomogeneous_source_recurrence(sources, maps)
        maps = build_labelled_carrier_maps(entries, weights)

        tampered = sources[-1]
        object.__setattr__(tampered, "state", arbitrary)
        with self.assertRaisesRegex(ValueError, "does not match"):
            labelled_inhomogeneous_source_recurrence(
                [*sources[:-1], tampered], maps
            )


if __name__ == "__main__":
    unittest.main()
