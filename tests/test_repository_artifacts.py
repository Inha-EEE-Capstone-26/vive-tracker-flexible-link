from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryArtifactsTest(unittest.TestCase):
    def setUp(self) -> None:
        for path in ROOT.rglob("__pycache__"):
            shutil.rmtree(path)

    def test_public_safe_dataset_layout_when_repo_is_built(self) -> None:
        required_paths = [
            ROOT / "README.md",
            ROOT / "DATA_AVAILABILITY.md",
            ROOT / "DATA_LICENSE",
            ROOT / "paper" / "paper.pdf",
            ROOT / "paper" / "poster.pdf",
            ROOT / "data" / "sample" / "sample_1link.csv",
            ROOT / "data" / "sample" / "sample_2link.csv",
            ROOT / "data" / "processed_manifest" / "manifest_1link_v1000.json",
            ROOT / "data" / "processed_manifest" / "manifest_2link_v1.json",
            ROOT / "data" / "schema" / "data_dictionary.md",
            ROOT / "results" / "expected" / "expected_metrics.json",
            ROOT / "models" / "README.md",
            ROOT / "models" / "model_manifest.json",
            ROOT / "models" / "1link_density_aware_local_krr_fulltrain.joblib",
            ROOT / "models" / "2link_density_aware_local_krr_fulltrain.joblib",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

        self.assertEqual(missing, [], "paper repo must include public-safe required artifacts")
        self.assertFalse((ROOT / "data" / "processed" / "dataset.csv").exists())
        self.assertFalse((ROOT / "data" / "raw").exists())

    def test_claim_boundary_text_when_public_reader_checks_repo(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        claim_boundary = (ROOT / "docs" / "claim_boundary.md").read_text(encoding="utf-8")
        data_readme = (ROOT / "data" / "README.md").read_text(encoding="utf-8")

        self.assertIn("position prediction metric, not closed-loop control success", readme)
        self.assertIn("optimizer linkage smoke", claim_boundary)
        self.assertIn("does not include raw experiment logs or full row-level datasets", data_readme)
        self.assertIn("synthetic", claim_boundary.lower())

    def test_readme_figure_gallery_when_public_reader_checks_provenance(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Source data", readme)
        self.assertIn("Related claim", readme)
        self.assertIn("Expected output", readme)
        self.assertIn("docs/figures_and_tables.md", readme)

    def test_verification_scripts_when_run_from_repo_root(self) -> None:
        verify_package = subprocess.run(
            [sys.executable, "scripts/verify_package.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(verify_package.returncode, 0, verify_package.stderr + verify_package.stdout)
        expected = json.loads((ROOT / "results" / "expected" / "expected_metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(expected["systems"]["1link"]["clean_rows"], 584)
        self.assertEqual(expected["systems"]["2link"]["clean_rows"], 5000)

    def test_public_manifest_text_when_scanned_for_local_paths(self) -> None:
        manifest_texts = [
            path.read_text(encoding="utf-8")
            for path in (ROOT / "data/processed_manifest").glob("*.json")
        ]
        joined = "\n".join(manifest_texts)
        slash = chr(92)

        self.assertNotIn("C:" + slash + "Users", joined)
        self.assertNotIn("C:" + slash + slash + "Users", joined)
        self.assertNotIn("E:" + slash + "01_Workspace", joined)
        self.assertNotIn("E:" + slash + slash + "01_Workspace", joined)

    def test_checksum_and_figure_scripts_when_public_package_is_verified(self) -> None:
        verify_package = subprocess.run(
            [sys.executable, "scripts/verify_package.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(verify_package.returncode, 0, verify_package.stderr + verify_package.stdout)
        self.assertIn('"checksum_mismatches": []', verify_package.stdout)
        self.assertIn('"metric_mismatches": []', verify_package.stdout)
        self.assertIn('"model_prediction_smoke_errors": []', verify_package.stdout)
        self.assertIn("width_px", verify_package.stdout)
        self.assertIn("sha256", verify_package.stdout)

    def test_model_card_when_release_includes_fitted_artifacts(self) -> None:
        model_readme = (ROOT / "models" / "README.md").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "models" / "model_manifest.json").read_text(encoding="utf-8"))

        self.assertIn("full-train inference artifact", model_readme)
        self.assertIn("not the original 50-seed evaluation object", model_readme)
        self.assertEqual(set(manifest["artifacts"].keys()), {"1link", "2link"})
        self.assertEqual(manifest["artifacts"]["1link"]["dataset_rows"], 584)
        self.assertEqual(manifest["artifacts"]["2link"]["dataset_rows"], 5000)

    def test_public_script_surface_when_packaged_for_release(self) -> None:
        scripts = sorted(path.name for path in (ROOT / "scripts").glob("*.py"))

        self.assertEqual(scripts, ["verify_package.py"])

    def test_privacy_scan_when_packaged_for_public_release(self) -> None:
        forbidden_roots = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.iterdir()
            if path.name in {".omo", ".codegraph", "graphify-out"}
        ]
        verify_package = subprocess.run(
            [sys.executable, "scripts/verify_package.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(forbidden_roots, [])
        self.assertEqual(verify_package.returncode, 0, verify_package.stderr + verify_package.stdout)
        self.assertIn('"privacy_scan_errors": []', verify_package.stdout)


if __name__ == "__main__":
    unittest.main()
