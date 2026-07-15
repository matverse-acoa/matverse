from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import genesis_builder


class GenesisBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = {
            "dataset_class": "SYNTHETIC_FIXTURE",
            "source": {"external_validity": "NOT_ESTABLISHED"},
            "records": [
                {
                    "name": "MAVK",
                    "psi": 0.99,
                    "cvar": 0.02,
                    "theta_hat": 0.9,
                    "pole": 1,
                },
                {
                    "name": "DAQ",
                    "psi": 0.95,
                    "cvar": 0.08,
                    "theta_hat": 0.8,
                    "pole": 1,
                },
                {
                    "name": "CSR4",
                    "psi": 0.92,
                    "cvar": 0.03,
                    "theta_hat": 0.85,
                    "pole": 1,
                },
            ],
        }

    def test_known_fixture_root_is_stable(self) -> None:
        manifest = genesis_builder.build_manifest(
            self.dataset,
            "2026-04-08T13:21:54+00:00",
        )
        self.assertEqual(
            manifest["merkle_root"],
            "87431dea7addb8a7aa0cfe6774739a98f3cd019313c2ef56e2722006f03d56fb",
        )
        self.assertEqual(
            manifest["claim_scope"],
            "LOCAL_DETERMINISTIC_DEMONSTRATION_ONLY",
        )
        genesis_builder.validate_manifest(manifest)

    def test_fixed_timestamp_produces_identical_manifest(self) -> None:
        first = genesis_builder.build_manifest(
            self.dataset,
            "2026-04-08T13:21:54+00:00",
        )
        second = genesis_builder.build_manifest(
            self.dataset,
            "2026-04-08T13:21:54+00:00",
        )
        self.assertEqual(first, second)

    def test_tampering_is_detected(self) -> None:
        manifest = genesis_builder.build_manifest(
            self.dataset,
            "2026-04-08T13:21:54+00:00",
        )
        manifest["records"][0]["psi"] = 0.5
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            genesis_builder.validate_manifest(manifest)

    def test_invalid_metric_is_rejected(self) -> None:
        invalid = dict(self.dataset["records"][0])
        invalid["cvar"] = 1.1
        with self.assertRaisesRegex(ValueError, r"within \[0, 1\]"):
            genesis_builder.normalize_input_record(invalid)

    def test_build_and_replay_use_portable_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_path = root / "fixture.json"
            output_path = root / "manifest.json"
            input_path.write_text(
                json.dumps(self.dataset, ensure_ascii=False),
                encoding="utf-8",
            )

            built = genesis_builder.build_and_write(
                input_path,
                output_path,
                "2026-04-08T13:21:54+00:00",
            )
            replayed = genesis_builder.validate_replay(output_path)
            self.assertEqual(built, replayed)


if __name__ == "__main__":
    unittest.main()
