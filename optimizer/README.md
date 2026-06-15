# Optimizer Source Bundle

This folder contains the optimizer-related source code and evidence used for the submission package.

The optimizer portion is included to show how the learned forward model was connected to a motor-angle search objective. It is not a closed-loop robot-control benchmark.

## Structure

```text
optimizer/
├─ optimizer_linkage_smoke.py          Lightweight sample-row smoke check.
├─ source/                             Original 2-link optimizer-linkage source and audit code.
├─ results/                            Final optimizer-linkage summary, row-level smoke results, and audit note.
├─ figures/                            ML-to-optimizer pipeline figure.
└─ legacy_1link/                       Earlier RandomForest motor-angle optimizer source and artifact.
```

## What To Run First

```bash
python optimizer/optimizer_linkage_smoke.py
```

This command uses the lightweight package files:

- `models/2link_density_aware_local_krr_fulltrain.joblib`
- `data/sample/sample_2link.csv`

It evaluates sample rows as candidate command states, predicts the Vive position with the fitted 2-link model artifact, and selects the candidate with the smallest predicted target error.

## Original 2-Link Source

The original 2-link optimizer-linkage code is preserved under `optimizer/source/`.

- `optimizer_linkage_2link_smoke.py`: final internal optimizer-linkage smoke script.
- `evaluate_2link_density_aware_local_krr.py`: model evaluation helpers required by the original smoke script.
- `audit_2link_optimizer_linkage.py`: final audit script.
- `_twolink_common.py`: shared audit utilities.
- `motor_angle_optimizer.py`: earlier motor-angle optimizer implementation retained for source traceability.

The original 2-link scripts expect `data/processed/clean_dataset_2link_v1/`, which is included in this school-submission package. The top-level `optimizer/optimizer_linkage_smoke.py` remains the fastest smoke path because it runs against five sample rows and finishes quickly.

## Results Included

- `results/optimizer_linkage_smoke_summary.json`
- `results/optimizer_linkage_smoke_results.csv`
- `results/optimizer_linkage_audit.md`
- `figures/2link_ml_to_optimizer_pipeline.png`

## Legacy 1-Link Optimizer

`legacy_1link/` keeps the earlier RandomForest-based motor-angle optimizer source and model artifact for submission traceability. It is not the final 2-link paper model.

Included:

- `legacy_1link/motor_angle_optimizer.py`
- `legacy_1link/random_forest_model.pkl`
- `legacy_1link/data/processed/clean_dataset_v2/feature_columns.txt`
- `legacy_1link/results/summary.json`
- `legacy_1link/results/summary.csv`
- `legacy_1link/results/batch_from_attached_full_summary.txt`

## Claim Boundary

The optimizer evidence shows source-code availability and ML-to-objective linkage. It does not claim final physical execution performance, closed-loop control success, or robot-base calibration.
