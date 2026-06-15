from __future__ import annotations

import csv
import hashlib
import json
import struct
from pathlib import Path
from typing import Final

import joblib
import numpy as np


ROOT: Final[Path] = Path(__file__).resolve().parents[1]
EXPECTED_REMOTE_URL: Final[str] = "https://github.com/Inha-EEE-Capstone-26/vive-tracker-flexible-link.git"

REQUIRED_FILES: Final[tuple[Path, ...]] = (
    Path("README.md"),
    Path("DATA_AVAILABILITY.md"),
    Path("DATA_LICENSE"),
    Path("paper/paper.pdf"),
    Path("paper/poster.pdf"),
    Path("data/sample/sample_1link.csv"),
    Path("data/sample/sample_2link.csv"),
    Path("data/processed_manifest/manifest_1link_v1000.json"),
    Path("data/processed_manifest/manifest_2link_v1.json"),
    Path("data/schema/data_dictionary.md"),
    Path("data/schema/units_and_frames.md"),
    Path("data/checksums/derived_artifacts_sha256.txt"),
    Path("data/checksums/source_inventory_sha256.txt"),
    Path("results/expected/expected_metrics.json"),
    Path("results/tables/paper_main_baseline_to_final_table.csv"),
    Path("results/tables/2link_baseline20_to_density_aware50_summary.csv"),
    Path("models/README.md"),
    Path("models/model_manifest.json"),
    Path("models/1link_density_aware_local_krr_fulltrain.joblib"),
    Path("models/2link_density_aware_local_krr_fulltrain.joblib"),
    Path("optimizer/README.md"),
    Path("optimizer/requirements.txt"),
    Path("optimizer/optimizer_linkage_smoke.py"),
    Path("optimizer/source/motor_angle_optimizer.py"),
    Path("optimizer/source/optimizer_linkage_2link_smoke.py"),
    Path("optimizer/source/evaluate_2link_density_aware_local_krr.py"),
    Path("optimizer/source/audit_2link_optimizer_linkage.py"),
    Path("optimizer/source/_twolink_common.py"),
    Path("optimizer/results/README.md"),
    Path("optimizer/results/optimizer_linkage_smoke_summary.json"),
    Path("optimizer/results/optimizer_linkage_smoke_results.csv"),
    Path("optimizer/results/optimizer_linkage_audit.md"),
    Path("optimizer/figures/2link_ml_to_optimizer_pipeline.png"),
    Path("optimizer/legacy_1link/motor_angle_optimizer.py"),
    Path("optimizer/legacy_1link/random_forest_model.pkl"),
    Path("optimizer/legacy_1link/data/processed/clean_dataset_v2/feature_columns.txt"),
    Path("optimizer/legacy_1link/results/summary.json"),
    Path("optimizer/legacy_1link/results/summary.csv"),
    Path("optimizer/legacy_1link/results/batch_from_attached_full_summary.txt"),
)

FORBIDDEN_PATH_PARTS: Final[tuple[str, ...]] = (
    "data/raw",
    "data/processed/dataset.csv",
    ".omo",
    ".codegraph",
    "graphify-out",
    ".ipynb_checkpoints",
    "__pycache__",
    ".pytest_cache",
)

SLASH: Final[str] = chr(92)
FORBIDDEN_PRIVACY_MARKERS: Final[tuple[str, ...]] = (
    "ml" + "flow",
    "tracking" + "_uri",
    "artifact" + "_uri",
    "experiment" + "_id",
    "run" + "_id",
    "C:" + SLASH + "Users",
    "C:" + SLASH + SLASH + "Users",
    "E:" + SLASH + "01_Workspace",
    "E:" + SLASH + SLASH + "01_Workspace",
    "01_Workspace" + "_sync",
    "api" + "_key",
    "api" + "-key",
    "sec" + "ret",
    "pass" + "word",
    "pass" + "wd",
    "creden" + "tial",
    "local" + "host",
    "127" + ".0.0.1",
    "192" + ".168.",
)

FIGURES: Final[tuple[Path, ...]] = (
    Path("results/figures/1link_paper_figure_contact_sheet.png"),
    Path("results/figures/2link_paper_figure_contact_sheet.png"),
    Path("results/figures/2link_alignment_residual.png"),
    Path("results/figures/2link_model_comparison_summary.png"),
)


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _row in csv.reader(handle)) - 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path.relative_to(ROOT)}")
    return struct.unpack(">II", header[16:24])


def missing_required_files() -> list[str]:
    return [path.as_posix() for path in REQUIRED_FILES if not (ROOT / path).exists()]


def forbidden_public_paths() -> list[str]:
    matches: list[str] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT).as_posix()
        if any(part in rel for part in FORBIDDEN_PATH_PARTS):
            matches.append(rel)
    return matches


def public_text_leaks() -> list[str]:
    leak_markers = (
        "C:" + SLASH + "Users",
        "C:" + SLASH + SLASH + "Users",
        "E:" + SLASH + "01_Workspace",
        "E:" + SLASH + SLASH + "01_Workspace",
    )
    matches: list[str] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT).as_posix()
        if ".git/" in rel or not path.is_file() or path.suffix.lower() in {".pdf", ".png", ".joblib", ".pkl"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(marker in text for marker in leak_markers):
            matches.append(rel)
    return matches


def privacy_scan_errors() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT).as_posix()
        if ".git/" in rel or not path.is_file() or path.suffix.lower() in {".pdf", ".png", ".joblib", ".pkl"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        for marker in FORBIDDEN_PRIVACY_MARKERS:
            if marker.lower() in lowered:
                errors.append(f"{rel}: contains {marker}")
    git_config = ROOT / ".git/config"
    if git_config.exists():
        config_text_raw = git_config.read_text(encoding="utf-8", errors="ignore")
        config_text = config_text_raw.lower()
        git_markers = ("creden" + "tial", "user.email", "user.name", "ml" + "flow")
        for marker in git_markers:
            if marker in config_text:
                errors.append(f".git/config: contains {marker}")
        if "url =" in config_text and EXPECTED_REMOTE_URL not in config_text_raw:
            errors.append(".git/config: contains unexpected remote URL")
    return errors


def checksum_mismatches() -> list[str]:
    checksum_path = ROOT / "data/checksums/derived_artifacts_sha256.txt"
    mismatches: list[str] = []
    with checksum_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip().lstrip("\ufeff")
            if not line:
                continue
            expected_hash, rel_path = line.split(maxsplit=1)
            artifact = ROOT / rel_path
            if not artifact.exists():
                mismatches.append(f"missing {rel_path}")
                continue
            actual_hash = sha256_file(artifact)
            if actual_hash != expected_hash:
                mismatches.append(f"{rel_path}: expected {expected_hash}, got {actual_hash}")
    return mismatches


def source_inventory_hash_entries_valid() -> bool:
    checksum_path = ROOT / "data/checksums/source_inventory_sha256.txt"
    with checksum_path.open("r", encoding="utf-8") as handle:
        lines = [line.strip().lstrip("\ufeff") for line in handle if line.strip()]
    return bool(lines) and all(len(line.split(maxsplit=1)[0]) == 64 for line in lines)


def verify_metrics() -> list[str]:
    expected = json.loads((ROOT / "results/expected/expected_metrics.json").read_text(encoding="utf-8"))
    table_path = ROOT / "results/tables/main_results.csv"
    with table_path.open("r", encoding="utf-8", newline="") as handle:
        rows = {row["system"]: row for row in csv.DictReader(handle)}

    errors: list[str] = []
    checks = (
        ("1-link", "1link"),
        ("2-link", "2link"),
    )
    for table_key, expected_key in checks:
        actual = float(rows[table_key]["mean_3d_error_mm"])
        wanted = float(expected["systems"][expected_key]["mean_3d_error_mm"])
        if actual != wanted:
            errors.append(f"{table_key} mean mismatch: expected {wanted}, got {actual}")
    return errors


def figure_records() -> list[dict[str, int | str]]:
    records: list[dict[str, int | str]] = []
    for rel_path in FIGURES:
        path = ROOT / rel_path
        width, height = png_dimensions(path)
        records.append(
            {
                "path": rel_path.as_posix(),
                "width_px": width,
                "height_px": height,
                "sha256": sha256_file(path),
            }
        )
    return records


def predict_with_artifact(artifact: dict[str, object], row: dict[str, str]) -> np.ndarray:
    feature_columns = artifact["feature_columns"]
    assert isinstance(feature_columns, list)
    values = np.array([[float(row[str(column)]) for column in feature_columns]], dtype=np.float32)
    preprocess = artifact["preprocess"]
    assert isinstance(preprocess, dict)
    median = np.asarray(preprocess["nan_fill_median"], dtype=np.float32)
    mean = np.asarray(preprocess["mean"], dtype=np.float32)
    std = np.asarray(preprocess["std"], dtype=np.float32)
    values = np.where(np.isfinite(values), values, median)
    query = (values - mean) / std

    model = artifact["model"]
    arrays = artifact["arrays"]
    assert isinstance(model, dict)
    assert isinstance(arrays, dict)
    train_x = np.asarray(arrays["train_x_scaled"], dtype=np.float32)
    dual_coef = np.asarray(arrays["dual_coef"], dtype=np.float32)
    residual = np.asarray(arrays["train_residual"], dtype=np.float32)

    diff = train_x[None, :, :] - query[:, None, :]
    sq_dist = np.sum(diff * diff, axis=2)
    base = np.exp(-float(model["gamma"]) * sq_dist) @ dual_coef

    dist = np.sqrt(sq_dist[0])
    k = min(int(model["k"]), len(dist))
    nearest_idx = np.argpartition(dist, k - 1)[:k]
    nearest_dist = dist[nearest_idx]
    bandwidth = max(float(np.max(nearest_dist)) * float(model["bandwidth_scale"]), 1e-6)
    weights = np.exp(-0.5 * (nearest_dist / bandwidth) ** 2)
    weights = weights / max(float(weights.sum()), 1e-12)
    local_residual = weights @ residual[nearest_idx]
    return base[0] + float(model["shrink"]) * local_residual


def model_prediction_smoke_errors() -> list[str]:
    manifest = json.loads((ROOT / "models/model_manifest.json").read_text(encoding="utf-8"))
    checks = (
        ("1link", ROOT / "data/sample/sample_1link.csv"),
        ("2link", ROOT / "data/sample/sample_2link.csv"),
    )
    errors: list[str] = []
    for key, sample_path in checks:
        artifact_meta = manifest["artifacts"][key]
        artifact_path = ROOT / artifact_meta["path"]
        if sha256_file(artifact_path) != artifact_meta["sha256"]:
            errors.append(f"{key} model checksum mismatch")
            continue
        artifact = joblib.load(artifact_path)
        with sample_path.open("r", encoding="utf-8-sig", newline="") as handle:
            row = next(csv.DictReader(handle))
        prediction = predict_with_artifact(artifact, row)
        if prediction.shape != (3,) or not np.all(np.isfinite(prediction)):
            errors.append(f"{key} prediction is not a finite 3-vector: {prediction}")
    return errors


def main() -> int:
    expected = json.loads((ROOT / "results/expected/expected_metrics.json").read_text(encoding="utf-8"))
    report = {
        "missing_required_files": missing_required_files(),
        "forbidden_public_paths": forbidden_public_paths(),
        "public_text_leaks": public_text_leaks(),
        "privacy_scan_errors": privacy_scan_errors(),
        "checksum_mismatches": checksum_mismatches(),
        "metric_mismatches": verify_metrics(),
        "model_prediction_smoke_errors": model_prediction_smoke_errors(),
        "source_inventory_hash_entries_valid": source_inventory_hash_entries_valid(),
        "sample_1link_rows": count_csv_rows(ROOT / "data/sample/sample_1link.csv"),
        "sample_2link_rows": count_csv_rows(ROOT / "data/sample/sample_2link.csv"),
        "expected_1link_clean_rows": expected["systems"]["1link"]["clean_rows"],
        "expected_2link_clean_rows": expected["systems"]["2link"]["clean_rows"],
        "figures": figure_records(),
    }
    print(json.dumps(report, indent=2, ensure_ascii=True))

    blocking = (
        report["missing_required_files"]
        or report["forbidden_public_paths"]
        or report["public_text_leaks"]
        or report["privacy_scan_errors"]
        or report["checksum_mismatches"]
        or report["metric_mismatches"]
        or report["model_prediction_smoke_errors"]
        or not report["source_inventory_hash_entries_valid"]
        or report["sample_1link_rows"] > 5
        or report["sample_2link_rows"] > 5
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
