"""M179 G4: verify the inclusive FLOP ledger is metered, fixed/bounded, and
within budget, and that the B=8 liveness reproduces the M175 static facts.
Response-free.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m179_metering as met  # noqa: E402


class M179MeteringTests(unittest.TestCase):
    def test_matmul_is_metered_and_deterministic(self):
        billed = met.metered_layer_matmul_flops()
        # a real billed second signal (FlopScope's own matmul convention,
        # ~(2k-1) style per output). Dominated by the two 256-cubes ~8*256^3.
        self.assertGreater(billed, 0)
        self.assertAlmostEqual(billed / (8 * met.N ** 3), 1.0, places=4)
        self.assertEqual(billed, met.metered_layer_matmul_flops())  # deterministic

    def test_inclusive_ledger_within_budget_and_bounded(self):
        L = met.inclusive_ledger()
        # dominant term is the pair evaluations; all terms fixed (no data
        # dependence): the producer FLOP count is a static constant
        self.assertEqual(L["pairs_per_layer"], 256 * 255 // 2)
        self.assertLess(L["fraction_of_budget_B"], 0.05)     # << budget
        self.assertGreater(L["fraction_of_budget_B"], 0.01)  # non-trivial, not zeroed
        # no accounting bypass: the special-function work is charged at the
        # frozen F_M178, never zero
        self.assertEqual(met.F_M178, 4048)

    def test_b8_liveness_matches_m175_static_facts(self):
        lv = met.b8_liveness()
        self.assertEqual(lv["blocks"], [8, 8, 8, 7])
        self.assertEqual(lv["workspace_mib"], 85.52151489257812)
        self.assertEqual(lv["block_covariance_archive_mib"], 4.0)
        self.assertEqual(lv["model_weight_mib"], 7.75)

    def test_no_zeroed_special_function_in_producer_sources(self):
        # check for actual usage, not the word appearing in a "no scipy" comment
        for fn in ("m179_relu_pair_assembly.py", "m179_background_producer.py",
                   "m179_jacobian_archive.py", "m179_metering.py"):
            src = (HERE / fn).read_text()
            for banned in ("_phi2_gauss10(", "1e-24", "np.clip(",
                           "import scipy", "from scipy"):
                self.assertNotIn(banned, src, (fn, banned))


if __name__ == "__main__":
    unittest.main()
