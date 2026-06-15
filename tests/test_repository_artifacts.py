from __future__ import annotations

import csv
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

    def test_submission_dataset_layout_when_repo_is_built(self) -> None:
        required_paths = [
            ROOT / "README.md",
            ROOT / "DATA_AVAILABILITY.md",
            ROOT / "DATA_LICENSE",
            ROOT / "paper" / "paper.pdf",
            ROOT / "paper" / "poster.pdf",
            ROOT / "data" / "sample" / "sample_1link.csv",
            ROOT / "data" / "sample" / "sample_2link.csv",
            ROOT / "data" / "processed" / "clean_dataset_1link_v2" / "dataset.csv",
            ROOT / "data" / "processed" / "clean_dataset_1link_v2" / "manifest.json",
            ROOT / "data" / "processed" / "clean_dataset_1link_v2" / "session_summary.csv",
            ROOT / "data" / "processed" / "clean_dataset_1link_v1000" / "dataset.csv",
            ROOT / "data" / "processed" / "clean_dataset_1link_v1000" / "manifest.json",
            ROOT / "data" / "processed" / "clean_dataset_1link_v1000" / "session_summary.csv",
            ROOT / "data" / "processed" / "clean_dataset_2link_v1" / "dataset.csv",
            ROOT / "data" / "processed" / "clean_dataset_2link_v1" / "manifest.json",
            ROOT / "data" / "processed" / "clean_dataset_2link_v1" / "session_summary.csv",
            ROOT / "data" / "source_processed" / "2link_synthetic" / "synthetic_only_target_plan_5000.csv",
            ROOT / "data" / "source_processed" / "2link_synthetic" / "synthetic_only_supervised_samples_5000.csv",
            ROOT / "data" / "processed_manifest" / "manifest_1link_v1000.json",
            ROOT / "data" / "processed_manifest" / "manifest_2link_v1.json",
            ROOT / "data" / "schema" / "data_dictionary.md",
            ROOT / "results" / "expected" / "expected_metrics.json",
            ROOT / "models" / "README.md",
            ROOT / "models" / "model_manifest.json",
            ROOT / "models" / "1link_density_aware_local_krr_fulltrain.joblib",
            ROOT / "models" / "2link_density_aware_local_krr_fulltrain.joblib",
            ROOT / "optimizer" / "README.md",
            ROOT / "optimizer" / "optimizer_linkage_smoke.py",
            ROOT / "optimizer" / "source" / "motor_angle_optimizer.py",
            ROOT / "optimizer" / "source" / "optimizer_linkage_2link_smoke.py",
            ROOT / "optimizer" / "source" / "audit_2link_optimizer_linkage.py",
            ROOT / "optimizer" / "source" / "_twolink_common.py",
            ROOT / "optimizer" / "results" / "optimizer_linkage_smoke_summary.json",
            ROOT / "optimizer" / "results" / "optimizer_linkage_smoke_results.csv",
            ROOT / "optimizer" / "results" / "optimizer_linkage_audit.md",
            ROOT / "optimizer" / "figures" / "2link_ml_to_optimizer_pipeline.png",
            ROOT / "optimizer" / "legacy_1link" / "motor_angle_optimizer.py",
            ROOT / "optimizer" / "legacy_1link" / "random_forest_model.pkl",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

        self.assertEqual(missing, [], "school submission repo must include required reproduction artifacts")
        self.assertFalse((ROOT / "data" / "processed" / "dataset.csv").exists())
        self.assertFalse((ROOT / "data" / "raw").exists())

    def test_submission_processed_dataset_counts_when_full_data_is_included(self) -> None:
        expected = {
            "data/processed/clean_dataset_1link_v2/dataset.csv": {
                "rows": 881,
                "source_counts": {"test-260523-2": 297, "test-260524-1": 584},
            },
            "data/processed/clean_dataset_1link_v1000/dataset.csv": {
                "rows": 584,
                "source_counts": {"test-260524-1": 584},
            },
            "data/processed/clean_dataset_2link_v1/dataset.csv": {
                "rows": 5000,
                "source_counts": {"2link_test-260525-1": 5000},
            },
        }

        for rel_path, wanted in expected.items():
            with (ROOT / rel_path).open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            source_counts: dict[str, int] = {}
            for row in rows:
                key = row["source_group"]
                source_counts[key] = source_counts.get(key, 0) + 1

            self.assertEqual(len(rows), wanted["rows"], rel_path)
            self.assertEqual(source_counts, wanted["source_counts"], rel_path)

    def test_final_run_evidence_when_submission_package_is_built(self) -> None:
        expected_metrics = json.loads((ROOT / "results" / "expected" / "expected_metrics.json").read_text(encoding="utf-8"))
        one_link_manifest = json.loads(
            (
                ROOT
                / "results/final_runs/1link_v1000_density_aware_local_krr_50seed/run_manifest.json"
            ).read_text(encoding="utf-8")
        )
        two_link_metrics = ROOT / "results/final_runs/2link_density_aware_local_krr_50seed/seed_split_metrics.csv"

        self.assertEqual(one_link_manifest["script"], "models/evaluate_v2_gpu_density_aware_local_krr.py")
        self.assertEqual(one_link_manifest["args"]["split_mode"], "v1000_only_random")
        self.assertEqual(one_link_manifest["dataset"]["rows"], 881)
        self.assertEqual(one_link_manifest["dataset"]["source_counts"]["test-260524-1"], 584)
        self.assertAlmostEqual(
            float(one_link_manifest["best_test_summary"]["mean_3d_error_mm_mean"]),
            float(expected_metrics["systems"]["1link"]["mean_3d_error_mm"]),
            places=4,
        )

        with two_link_metrics.open("r", encoding="utf-8-sig", newline="") as handle:
            test_rows = [row for row in csv.DictReader(handle) if row["split"] == "test"]
        mean_error = sum(float(row["mean_3d_error_mm"]) for row in test_rows) / len(test_rows)

        self.assertEqual(len(test_rows), 50)
        self.assertAlmostEqual(mean_error, float(expected_metrics["systems"]["2link"]["mean_3d_error_mm"]), places=4)

    def test_claim_boundary_text_when_public_reader_checks_repo(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        claim_boundary = (ROOT / "docs" / "claim_boundary.md").read_text(encoding="utf-8")
        data_readme = (ROOT / "data" / "README.md").read_text(encoding="utf-8")

        self.assertIn("position prediction metric, not closed-loop control success", readme)
        self.assertIn("optimizer linkage smoke", claim_boundary)
        self.assertIn("full processed datasets", data_readme)
        self.assertIn("v1000_only_random", claim_boundary)
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

    def test_optimizer_linkage_source_when_packaged_for_submission(self) -> None:
        source_files = [
            "optimizer/source/motor_angle_optimizer.py",
            "optimizer/source/optimizer_linkage_2link_smoke.py",
            "optimizer/source/audit_2link_optimizer_linkage.py",
            "optimizer/source/_twolink_common.py",
            "optimizer/legacy_1link/motor_angle_optimizer.py",
        ]
        compile_sources = subprocess.run(
            [sys.executable, "-m", "py_compile", *source_files],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        optimizer_smoke = subprocess.run(
            [
                sys.executable,
                "optimizer/optimizer_linkage_smoke.py",
                "--max-targets",
                "2",
                "--candidate-limit",
                "5",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        korean_paths = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if any("\uac00" <= char <= "\ud7a3" for char in path.relative_to(ROOT).as_posix())
        ]

        self.assertEqual(korean_paths, [])
        self.assertEqual(compile_sources.returncode, 0, compile_sources.stderr + compile_sources.stdout)
        self.assertEqual(optimizer_smoke.returncode, 0, optimizer_smoke.stderr + optimizer_smoke.stdout)
        self.assertIn('"targets_evaluated": 2', optimizer_smoke.stdout)
        self.assertIn('"candidate_count": 5', optimizer_smoke.stdout)

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
