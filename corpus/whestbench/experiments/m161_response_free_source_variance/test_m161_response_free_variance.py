from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m161_response_free_variance import (  # noqa: E402
    ORDERED_OWNER,
    TARGET_COLLISION_MASS,
    _finite_population_metrics,
    _source_vector,
    certified_target_table,
    frozen_cells,
    frozen_probability,
    proxy_metrics,
    symmetry_audit,
)
from m156_extended_domain_star_control import (  # noqa: E402
    collision_count,
    collision_strata,
    distinct_target_extension,
    extended_star_table,
    residual_table,
)


class TestM161ResponseFreeSourceVariance(unittest.TestCase):
    def test_frozen_q0_has_full_support_and_target_collision_mass(self) -> None:
        for width in (4, 5, 6):
            total = 0.0
            collision = 0.0
            for i in range(width):
                for j in range(width):
                    for k in range(width):
                        probability = frozen_probability(width, (i, j, k))
                        self.assertGreater(probability, 0.0)
                        total += probability
                        if len({i, j, k}) < 3:
                            collision += probability
            self.assertAlmostEqual(total, 1.0, places=14)
            self.assertAlmostEqual(collision, TARGET_COLLISION_MASS, places=14)

    def test_complete_domain_residual_is_negative_control_on_collisions(self) -> None:
        rng = np.random.default_rng(16111)
        width = 5
        target = rng.normal(size=(width, width, width))
        target = 0.5 * (target + target.swapaxes(1, 2))
        target = distinct_target_extension(target)
        factor = rng.normal(size=(width, width))
        control = extended_star_table(factor @ factor.T)
        residual = residual_table(target, control)
        for unit in collision_strata(width):
            self.assertEqual(target[unit], 0.0)
            self.assertEqual(residual[unit], -control[unit])

    def test_source_proxy_keeps_coefficient_proxy_separate(self) -> None:
        rng = np.random.default_rng(16112)
        width = 4
        target = np.zeros((width, width, width))
        target[0, 1, 2] = target[0, 2, 1] = 0.7
        covariance = np.eye(width)
        covariance[0, 1] = covariance[1, 0] = 0.2
        covariance[0, 2] = covariance[2, 0] = -0.1
        control = extended_star_table(covariance)
        cell = next(cell for cell in frozen_cells() if cell.width == width)
        coefficient, source = proxy_metrics(target, control, cell)
        self.assertTrue(np.isfinite(coefficient.residual_to_raw))
        self.assertTrue(np.isfinite(source.residual_to_raw))
        self.assertGreaterEqual(source.collision_residual_second_fraction, 0.0)

    def test_certified_provider_is_symmetric_and_endpoint_excluded(self) -> None:
        cell = next(cell for cell in frozen_cells() if cell.name == "isotropic_w4")
        target, certificate = certified_target_table(cell)
        self.assertLessEqual(certificate["provider_max_value_disagreement"], 2.0e-8)
        self.assertLessEqual(certificate["provider_max_tangent_disagreement"], 2.0e-7)
        self.assertTrue(np.allclose(target, target.swapaxes(1, 2), atol=0.0, rtol=0.0))
        for i in range(cell.width):
            self.assertTrue(np.all(target[i, i, :] == 0.0))
            self.assertTrue(np.all(target[i, :, i] == 0.0))
            self.assertTrue(np.all(target[:, i, i] == 0.0))

    def test_actual_provider_control_and_source_proxy_obey_permutation_and_gauge(self) -> None:
        audit = symmetry_audit(next(cell for cell in frozen_cells() if cell.name == "isotropic_w4"))
        physical = (
            "permutation_target_max_abs",
            "permutation_control_max_abs",
            "permutation_source_variance_relative",
            "permutation_residual_variance_relative",
            "gauge_target_relative",
            "gauge_control_relative",
            "gauge_source_variance_relative",
            "gauge_residual_variance_relative",
        )
        for name in physical:
            value = audit[name]
            self.assertLess(value, 2.0e-8, name)
        # A bare coefficient has physical ReLU-scale units.  Unlike the full
        # source feature, it is not gauge invariant; keeping it separate is a
        # required diagnostic, not a failed source symmetry.
        self.assertGreater(audit["gauge_coefficient_variance_relative"], 1.0e-8)


if __name__ == "__main__":
    unittest.main()
