from __future__ import annotations

from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for sibling in (
    "m223_m179_fused_physical_owner_packet", "m179_background_archive_producer",
    "m220_certified_bivariate_high_moments", "m129_source_frechet_tangent",
):
    path = str(EXPERIMENTS / sibling)
    if path not in sys.path:
        sys.path.insert(0, path)

import m223_m179_fused_physical_owner_packet as m223
import m179_relu_pair_assembly as m179
import m220_certified_bivariate_high_moments as m220
import m129_source_frechet as m129


def _context(mu_x=0.37, mu_y=-0.41, sx=0.8, sy=1.3, rho=-0.63, *, layer=7, epoch=19):
    a = np.asarray((mu_x, mu_y), dtype=np.float64)
    C = np.asarray(((sx*sx, rho*sx*sy), (rho*sx*sy, sy*sy)), dtype=np.float64)
    return m223.LayerPrecontext(layer, epoch, a, C, "generated-m223-test")


class M223FusedPacketTests(unittest.TestCase):
    def test_one_call_identity_m179_and_m220_parity(self):
        context = _context()
        calls = []
        import m178_certified_phi2_owent as m178
        original = m178.evaluate
        def counted(a, b, rho):
            calls.append((a, b, rho))
            return original(a, b, rho)
        with patch.object(m178, "evaluate", side_effect=counted):
            packet = m223.fuse_next_pair(context, 0, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(packet.m178_calls, 1)
        self.assertEqual(packet.m179_jet_identity, packet.owner_jet_identity)
        self.assertEqual(packet.owner_boundary_identity, id(packet.boundaries))
        self.assertEqual(packet.endpoint_unary_calls, 4)
        self.assertEqual(packet.owner_special_function_calls, 0)
        old = m179.pair_moments(0.37, -0.41, 0.8, 1.3, -0.63)
        for name in old.__dataclass_fields__:
            self.assertAlmostEqual(getattr(packet.pair, name), getattr(old, name), places=7)
        reference = m220.evaluate(0.37, -0.41, 0.8**2, 1.3**2, -0.63*0.8*1.3)
        self.assertFalse(reference.refused, reference.reason)
        self.assertAlmostEqual(packet.owners.raw_m31_ij, reference.raw_m31, places=10)
        self.assertAlmostEqual(packet.owners.raw_m22, reference.raw_m22, places=10)
        self.assertAlmostEqual(packet.owners.k31_ij, reference.kappa31, places=9)
        self.assertAlmostEqual(packet.owners.k22_ij, reference.kappa22, places=9)
        self.assertIs(packet.consume(context), packet.owners)

    def test_m179_parity_on_frozen_hostile_spd_grid(self):
        cells = (
            (0.0, 0.0, 1.0, 1.0, 0.0),
            (1.2, -0.9, 0.5, 1.7, 0.72),
            (-2.0, 1.0, 0.7, 1.2, -0.74),
            (0.31, -0.28, 1.1, 0.8, 1.0 - 2.0**-45),
        )
        for mx, my, sx, sy, rho in cells:
            context = _context(mx, my, sx, sy, rho)
            packet = m223.fuse_next_pair(context, 0, 1)
            old = m179.pair_moments(mx, my, sx, sy, rho)
            for name in old.__dataclass_fields__:
                self.assertAlmostEqual(getattr(packet.pair, name), getattr(old, name), places=6)
            packet.consume(context)

    def test_m129_connected_owner_parity_on_random_spd_cells(self):
        rng = random.Random(22320260809)
        for _ in range(12):
            mx, my = rng.uniform(-1.3, 1.3), rng.uniform(-1.3, 1.3)
            sx, sy = rng.uniform(0.5, 1.5), rng.uniform(0.5, 1.5)
            rho = rng.uniform(-0.7, 0.7)
            context = _context(mx, my, sx, sy, rho)
            packet = m223.fuse_next_pair(context, 0, 1)
            mean = np.asarray((mx, my), dtype=np.float64)
            covariance = context.C
            tangent = m129.build_state_frechet(mean, covariance, np.zeros(2), np.zeros((2, 2)), pair_terms=96)
            k31, _ = m129.exact_collision_cumulant_dot(tangent, (0, 0, 0, 1), terms=96)
            k22, _ = m129.exact_collision_cumulant_dot(tangent, (0, 0, 1, 1), terms=96)
            k4, _ = m129.exact_collision_cumulant_dot(tangent, (0, 0, 0, 0), terms=96)
            self.assertAlmostEqual(packet.owners.k4_i, k4, places=8)
            self.assertAlmostEqual(packet.owners.k31_ij, k31, places=8)
            self.assertAlmostEqual(packet.owners.k22_ij, k22, places=8)
            packet.consume(context)

    def test_permutation_and_positive_gauge(self):
        first_ctx = _context()
        first = m223.fuse_next_pair(first_ctx, 0, 1)
        swapped_ctx = _context(-0.41, 0.37, 1.3, 0.8, -0.63)
        swapped = m223.fuse_next_pair(swapped_ctx, 0, 1)
        self.assertAlmostEqual(first.owners.k31_ij, swapped.owners.k31_ji, places=9)
        self.assertAlmostEqual(first.owners.k22_ij, swapped.owners.k22_ij, places=9)
        gx, gy = 1.7, 0.6
        scaled_ctx = _context(gx*.37, gy*-.41, gx*.8, gy*1.3, -0.63)
        scaled = m223.fuse_next_pair(scaled_ctx, 0, 1)
        self.assertAlmostEqual(scaled.owners.k4_i, gx**4*first.owners.k4_i, places=8)
        self.assertAlmostEqual(scaled.owners.k31_ij, gx**3*gy*first.owners.k31_ij, places=8)
        self.assertAlmostEqual(scaled.owners.k22_ij, gx**2*gy**2*first.owners.k22_ij, places=8)

    def test_hostile_substitutions_rank_refusal_and_retirement(self):
        context = _context()
        import m178_certified_phi2_owent as m178
        with self.assertRaisesRegex(m223.M223Refusal, "HOSTILE_JET_TYPE"):
            with patch.object(m178, "evaluate", return_value=object()):
                m223.fuse_next_pair(context, 0, 1)
        packet = m223.fuse_next_pair(context, 0, 1)
        foreign = _context(layer=8)
        with self.assertRaisesRegex(m223.M223Refusal, "FOREIGN_PRECONTEXT"):
            packet.consume(foreign)
        with self.assertRaisesRegex(m223.M223Refusal, "PREVIOUS_PACKET_NOT_RETIRED"):
            m223.fuse_next_pair(context, 0, 1)
        packet.consume(context)
        with self.assertRaisesRegex(m223.M223Refusal, "PACKET_ALREADY_RETIRED"):
            packet.consume(context)
        context.close()
        with self.assertRaisesRegex(m223.M223Refusal, "PRECONTEXT_CLOSED"):
            m223.fuse_next_pair(context, 0, 1)
        rank = _context(rho=1.0)
        with self.assertRaisesRegex(m223.M223Refusal, "NON_SPD_OR_RANK_ONE"):
            m223.fuse_next_pair(rank, 0, 1)

    def test_stream_binding_is_by_reference_and_cost_ceiling_is_incremental(self):
        context = _context()
        packet = m223.fuse_next_pair(context, 0, 1)
        self.assertEqual(packet.a_identity, id(context.a))
        self.assertEqual(packet.C_identity, id(context.C))
        self.assertEqual(m223.M178_CALLS_PER_SPD_PACKET, 1)
        self.assertEqual(packet.owner_special_function_calls, 0)
        self.assertEqual(m223.OWNER_INCREMENTAL_FLOP_CEILING_PER_PAIR, 512)
        self.assertEqual(m223.ALL_LAYER_OWNER_CEILING, 518062080)
        packet.consume(context)

    def test_owner_path_makes_no_unary_call_after_m179_cache(self):
        context = _context()
        original = m223._endpoint_unary
        calls = []
        def audited(mean, sigma):
            calls.append((mean, sigma))
            return original(mean, sigma)
        with patch.object(m223, "_endpoint_unary", side_effect=audited):
            packet = m223.fuse_next_pair(context, 0, 1)
        # endpoints plus M179's two conditional means; M223 owner recurrence
        # itself made no extra unary request.
        self.assertEqual(len(calls), 4)
        self.assertEqual(packet.owner_special_function_calls, 0)
        packet.consume(context)

    def test_frozen_selective_trace_emits_only_predeclared_events(self):
        context = _context()
        selection = m223.FrozenOwnerSelection.from_context(context, ((0, 1),), (0,))
        calls = []
        import m178_certified_phi2_owent as m178
        original = m178.evaluate
        def counted(a, b, rho):
            calls.append((a, b, rho))
            return original(a, b, rho)
        with patch.object(m178, "evaluate", side_effect=counted):
            self.assertIsNone(m223.maybe_fuse_selected_pair(selection, context, 1, 0))
            self.assertEqual(calls, [])
            packet = m223.maybe_fuse_selected_pair(selection, context, 0, 1)
        self.assertIsNotNone(packet)
        self.assertEqual(len(calls), 1)
        packet.consume(context)
        unary = m223._endpoint_unary(float(context.a[0]), float(np.sqrt(context.C[0, 0])))
        k4 = m223.emit_selected_k4(selection, context, 0, unary)
        self.assertIsNotNone(k4)
        self.assertEqual(k4.additional_special_function_calls, 0)
        self.assertIsNone(m223.emit_selected_k4(selection, context, 1, unary))
        with self.assertRaisesRegex(m223.M223Refusal, "SELECTION_PRECONTEXT"):
            selection.selects_pair(_context(layer=8), 0, 1)


if __name__ == "__main__":
    unittest.main()
