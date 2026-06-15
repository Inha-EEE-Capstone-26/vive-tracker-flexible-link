from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Final

import joblib
import numpy as np


ROOT: Final[Path] = Path(__file__).resolve().parents[1]
MODEL_PATH: Final[Path] = ROOT / "models" / "2link_density_aware_local_krr_fulltrain.joblib"
SAMPLE_PATH: Final[Path] = ROOT / "data" / "sample" / "sample_2link.csv"
Q_COLUMNS: Final[tuple[str, ...]] = (
    "q1_cmd_deg",
    "q2_cmd_deg",
    "q3_cmd_deg",
    "q1_encoder_deg",
    "q2_encoder_deg",
    "q3_encoder_deg",
)
TARGET_COLUMNS: Final[tuple[str, ...]] = (
    "p_target_x_mm",
    "p_target_y_mm",
    "p_target_z_mm",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the public 2-link ML-to-optimizer linkage smoke check."
    )
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument("--sample-path", type=Path, default=SAMPLE_PATH)
    parser.add_argument("--max-targets", type=int, default=3)
    parser.add_argument("--candidate-limit", type=int, default=5)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def feature_vector(artifact: dict[str, object], row: dict[str, float]) -> np.ndarray:
    columns = artifact["feature_columns"]
    if not isinstance(columns, list):
        raise TypeError("model artifact feature_columns must be a list")
    return np.array([[float(row[str(column)]) for column in columns]], dtype=np.float32)


def predict_with_artifact(artifact: dict[str, object], row: dict[str, float]) -> np.ndarray:
    values = feature_vector(artifact, row)
    preprocess = artifact["preprocess"]
    model = artifact["model"]
    arrays = artifact["arrays"]
    if not isinstance(preprocess, dict) or not isinstance(model, dict) or not isinstance(arrays, dict):
        raise TypeError("model artifact is missing preprocess, model, or arrays")

    median = np.asarray(preprocess["nan_fill_median"], dtype=np.float32)
    mean = np.asarray(preprocess["mean"], dtype=np.float32)
    std = np.asarray(preprocess["std"], dtype=np.float32)
    query = (np.where(np.isfinite(values), values, median) - mean) / std

    train_x = np.asarray(arrays["train_x_scaled"], dtype=np.float32)
    dual_coef = np.asarray(arrays["dual_coef"], dtype=np.float32)
    residual = np.asarray(arrays["train_residual"], dtype=np.float32)
    sq_dist = np.sum((train_x[None, :, :] - query[:, None, :]) ** 2, axis=2)
    base = np.exp(-float(model["gamma"]) * sq_dist) @ dual_coef

    dist = np.sqrt(sq_dist[0])
    nearest_count = min(int(model["k"]), len(dist))
    nearest_idx = np.argpartition(dist, nearest_count - 1)[:nearest_count]
    nearest_dist = dist[nearest_idx]
    bandwidth = max(float(np.max(nearest_dist)) * float(model["bandwidth_scale"]), 1e-6)
    weights = np.exp(-0.5 * (nearest_dist / bandwidth) ** 2)
    weights = weights / max(float(weights.sum()), 1e-12)
    local_residual = weights @ residual[nearest_idx]
    return base[0] + float(model["shrink"]) * local_residual


def candidate_row(target: dict[str, str], candidate: dict[str, str]) -> dict[str, float]:
    row: dict[str, float] = {}
    for column in Q_COLUMNS:
        row[column] = float(candidate[column])
    for column in TARGET_COLUMNS:
        row[column] = float(target[column])
    return row


def target_xyz(row: dict[str, str]) -> np.ndarray:
    return np.array([float(row[column]) for column in TARGET_COLUMNS], dtype=np.float32)


def run_smoke(
    artifact: dict[str, object],
    rows: list[dict[str, str]],
    max_targets: int,
    candidate_limit: int,
) -> dict[str, object]:
    targets = rows[:max_targets]
    candidates = rows[:candidate_limit]
    records: list[dict[str, float | int]] = []
    for target_index, target in enumerate(targets):
        target_position = target_xyz(target)
        best_error: float | None = None
        best_candidate_index = -1
        for candidate_index, candidate in enumerate(candidates):
            prediction = predict_with_artifact(artifact, candidate_row(target, candidate))
            error = float(np.linalg.norm(prediction - target_position))
            if best_error is None or error < best_error:
                best_error = error
                best_candidate_index = candidate_index
        if best_error is None:
            raise RuntimeError("candidate set is empty")
        records.append(
            {
                "target_index": target_index,
                "best_candidate_index": best_candidate_index,
                "best_predicted_error_mm": best_error,
            }
        )

    errors = [float(record["best_predicted_error_mm"]) for record in records]
    return {
        "mode": "public_sample_optimizer_linkage_smoke",
        "targets_evaluated": len(targets),
        "candidate_count": len(candidates),
        "mean_best_predicted_error_mm": float(np.mean(errors)),
        "min_best_predicted_error_mm": float(np.min(errors)),
        "max_best_predicted_error_mm": float(np.max(errors)),
        "records": records,
    }


def main() -> int:
    args = parse_args()
    artifact = joblib.load(args.model_path)
    rows = read_rows(args.sample_path)
    summary = run_smoke(
        artifact=artifact,
        rows=rows,
        max_targets=args.max_targets,
        candidate_limit=args.candidate_limit,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
