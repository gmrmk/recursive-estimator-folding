"""RED/GREEN static contract for frozen M237 durable transport."""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
M236_DIR = BASE / "m236_layer_batched_m212_m235"
for path in (HERE, M236_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import m237_durable_native_receipt as durable  # noqa: E402
import run_m237_native_process as runner  # noqa: E402


FROZEN_HASHES = {
    HERE / "M237_PREDECLARATION_20260809.md": "02934C3A34D9EF9F80CE9FCAC27A9F179A96FB200493E6BC01661765F1FBCBE8",
    HERE / "M237_FROZEN_MANIFEST_20260809.json": "9E68B52AF4CBA5B8AE0B93388029637A347045BE0A5D16B69ED004A4A0DE577D",
    HERE / "M237_PREIMPLEMENTATION_ERRATUM1_20260809.md": "2A1A083C2FEDE8239F379FA0565D86845DEA1C45F6A765C84F9A37E6867BCA72",
    M236_DIR / "m236_layer_batched_m212_m235.py": "6C9E9AF9727722CB6ADE5E1CDA56D3F7A0E7BF82EF35EBDAEFA8AA883A854B75",
    M236_DIR / "m236_official_setup_estimator.py": "18D60E0FC02D034CC0E0006CFEDFA15E9188F59697C21294BD53B501AA9BFB25",
    M236_DIR / "run_m236_native_process.py": "CFC797EFE73CF5CD16D022E60983BBC84FDB707907D01FE035DDCD5997DCF675",
    M236_DIR / "test_m236_block8_contract.py": "5E2DE041D68B0B07B437D5362D26195D4F7C7C5A1A45058E900BB4BB3AD4B722",
    M236_DIR / "test_m236_native_contract.py": "FED9175D374BAC53D2C03E01A405980F5DDE2AD93165CF5E453936B8B1BFB84F",
    M236_DIR / "M236_NATIVE_ONE_PROCESS_RESULT_20260809.json": "FF69106F5115B5EF68FBDE3683F27BFB341E18BD85594416EAC6708D31AF7969",
    M236_DIR / "M236_DISPOSITION_20260809.md": "030E7550D94EA3EF740880B86A3CF890539AE55D47AC115A1BB0EE215C22E741",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class M237DurableTransportTests(unittest.TestCase):
    def test_frozen_hashes_names_and_execution_firewall(self):
        self.assertEqual({_sha(path): expected for path, expected in FROZEN_HASHES.items()}, {expected: expected for expected in FROZEN_HASHES.values()})
        self.assertEqual(durable.INTENT_NAME, "M237_LAUNCH_INTENT_20260809.json")
        self.assertEqual(durable.RESULT_NAME, "M237_NATIVE_ONE_PROCESS_RESULT_20260809.json")
        self.assertEqual(durable.RESULT_TEMP_NAME, ".M237_NATIVE_ONE_PROCESS_RESULT_20260809.json.tmp")
        self.assertFalse((HERE / durable.INTENT_NAME).exists())
        self.assertFalse((HERE / durable.RESULT_NAME).exists())
        self.assertFalse((HERE / durable.RESULT_TEMP_NAME).exists())
        self.assertFalse((HERE / "M237_NATIVE_TEN_PROCESS_RESULT_20260809.json").exists())
        self.assertFalse((HERE / "M237_G0_RESULTS_20260809.json").exists())

    def test_hardlink_preflight_is_exact_and_leaves_no_probe(self):
        with tempfile.TemporaryDirectory(prefix="m237_preflight_test_") as raw:
            directory = Path(raw)
            receipt = durable.hardlink_preflight(directory)
            self.assertTrue(receipt["supported"])
            self.assertEqual(receipt["bytes"], len(durable.PROBE_BYTES))
            self.assertFalse((directory / durable.PROBE_TEMP_NAME).exists())
            self.assertFalse((directory / durable.PROBE_FINAL_NAME).exists())
            sentinel = b"PREEXISTING-PROBE\n"
            preexisting = directory / durable.PROBE_FINAL_NAME
            preexisting.write_bytes(sentinel)
            with self.assertRaises(FileExistsError):
                durable.hardlink_preflight(directory)
            self.assertEqual(preexisting.read_bytes(), sentinel)
        source = inspect.getsource(durable.hardlink_preflight)
        for required in ('"xb"', "flush()", "os.fsync", "os.link", "read_bytes"):
            self.assertIn(required, source)
        for forbidden in ("os.replace", "rename(", 'open("wb")'):
            self.assertNotIn(forbidden, source)

    def test_result_publication_refuses_overwrite_and_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory(prefix="m237_nooverwrite_test_") as raw:
            directory = Path(raw)
            temp_path = directory / "test-result.tmp"
            final_path = directory / "test-result.json"
            sentinel = b"DO-NOT-ALTER\n"
            final_path.write_bytes(sentinel)
            with self.assertRaises(FileExistsError):
                durable.publish_native_result(
                    temp_path=temp_path,
                    final_path=final_path,
                    payload={"status": "PASS_NATIVE_ONE_PROCESS"},
                )
            self.assertEqual(final_path.read_bytes(), sentinel)
            self.assertFalse(temp_path.exists())

            final_path.unlink()
            temp_path.write_bytes(sentinel)
            with self.assertRaises(FileExistsError):
                durable.publish_native_result(
                    temp_path=temp_path,
                    final_path=final_path,
                    payload={"status": "KILLED_FROZEN_NATIVE_GATE"},
                )
            self.assertEqual(temp_path.read_bytes(), sentinel)
            self.assertFalse(final_path.exists())

    def test_pass_and_failure_use_one_canonical_hardlink_publisher(self):
        payloads = (
            {"status": "PASS_NATIVE_ONE_PROCESS", "failure": None, "value": 1},
            {"status": "KILLED_FROZEN_NATIVE_GATE", "failure": "gate", "value": 2},
        )
        with tempfile.TemporaryDirectory(prefix="m237_common_test_") as raw:
            directory = Path(raw)
            for index, payload in enumerate(payloads):
                temp_path = directory / f"common-{index}.tmp"
                final_path = directory / f"common-{index}.json"
                receipt = durable.publish_native_result(
                    temp_path=temp_path, final_path=final_path, payload=payload
                )
                expected = durable.canonical_json_bytes(payload)
                self.assertEqual(final_path.read_bytes(), expected)
                self.assertEqual(receipt["parsed"], payload)
                self.assertEqual(receipt["sha256"], hashlib.sha256(expected).hexdigest())
                self.assertFalse(temp_path.exists())
                self.assertTrue(final_path.exists())
        source = inspect.getsource(durable.publish_native_result)
        self.assertNotIn("PASS_NATIVE", source)
        self.assertNotIn("KILLED", source)
        self.assertIn("os.link", source)
        self.assertNotIn("os.replace", source)

    def test_launch_intent_is_exclusive_durable_and_byte_verified(self):
        payload = {
            "candidate": "M237 test-only",
            "invocation_count": 1,
            "sequence": ["A", "B", "A"],
        }
        with tempfile.TemporaryDirectory(prefix="m237_intent_test_") as raw:
            path = Path(raw) / "test-only-intent.json"
            receipt = durable.write_launch_intent_exclusive(path, payload)
            frozen = path.read_bytes()
            self.assertEqual(receipt["parsed"], payload)
            self.assertEqual(receipt["sha256"], hashlib.sha256(frozen).hexdigest())
            with self.assertRaises(FileExistsError):
                durable.write_launch_intent_exclusive(path, {"changed": True})
            self.assertEqual(path.read_bytes(), frozen)
        source = "\n".join(
            (
                inspect.getsource(durable.write_launch_intent_exclusive),
                inspect.getsource(durable._write_fsync_exclusive),
                inspect.getsource(durable._verified_json_receipt),
            )
        )
        for required in ('"xb"', "flush()", "os.fsync", "read_bytes"):
            self.assertIn(required, source)

    def test_runner_pins_m236_and_preserves_exact_worker_semantics(self):
        verified = runner.verify_frozen_inputs()
        self.assertTrue(all(verified.values()))
        self.assertEqual(set(runner.FROZEN_INPUT_HASHES), set(FROZEN_HASHES))
        self.assertEqual(runner.SETUP_SEED, 0)
        self.assertEqual(runner.SOURCE_SEEDS, {"A": 227700001, "B": 227710001})
        self.assertEqual(runner.SEQUENCE, ("A", "B", "A"))
        self.assertEqual(runner.EXPECTED_M212_BILL, 1_249_253_376)
        self.assertEqual(runner.EXPECTED_M235_BILL, 864_960_512)
        self.assertEqual(runner.EXPECTED_COMBINED_BILL, 2_114_213_888)
        self.assertEqual(runner.RSS_CAP_MIB, 496.0)
        source = inspect.getsource(runner.run_durable_once)
        for required in (
            "assert_execution_paths_absent",
            "hardlink_preflight",
            "write_launch_intent_exclusive",
            "_run_live_scratch",
            "publish_native_result",
        ):
            self.assertIn(required, source)
        self.assertLess(source.index("hardlink_preflight"), source.index("write_launch_intent_exclusive"))
        self.assertLess(source.index("write_launch_intent_exclusive"), source.index("_run_live_scratch"))
        self.assertLess(source.index("_run_live_scratch"), source.index("publish_native_result"))
        live_source = inspect.getsource(runner._run_live_scratch)
        self.assertIn("official.start", live_source)
        self.assertIn("parent._prediction_receipt", live_source)
        self.assertIn("M236_DIR / \"m236_official_setup_estimator.py\"", live_source)
        self.assertIn("memory_limit_mb=512", live_source)
        self.assertNotIn("setup_component", live_source)

    def test_import_and_test_discovery_cannot_start_worker(self):
        with mock.patch.object(
            runner.SubprocessRunner,
            "start",
            side_effect=AssertionError("worker start during import"),
        ) as start:
            importlib.reload(runner)
            start.assert_not_called()
        module_source = (HERE / "run_m237_native_process.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('if __name__ == "__main__":', module_source)
        self.assertFalse((HERE / durable.INTENT_NAME).exists())
        self.assertFalse((HERE / durable.RESULT_NAME).exists())


if __name__ == "__main__":
    unittest.main()
