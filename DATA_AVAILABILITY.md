# Data Availability

This school-submission repository includes the full processed datasets needed to inspect the reported paper artifacts.

Included:

- `data/processed/clean_dataset_1link_v2/`: 881 processed 1-link rows from `test-260523-2` and `test-260524-1`.
- `data/processed/clean_dataset_1link_v1000/`: 584 processed 1-link v1000 rows from `test-260524-1`.
- `data/processed/clean_dataset_2link_v1/`: 5,000 processed 2-link synthetic-label rows.
- `data/source_processed/2link_synthetic/`: the 5,000-row synthetic target plan and supervised sample CSVs used to build the 2-link dataset.
- `data/sample/`: five-row samples kept for quick smoke checks.
- `data/schema/`, `data/processed_manifest/`, and dataset-local manifests for schema, unit, coordinate-frame, and row-count provenance.
- `results/final_runs/`: sanitized 50-seed metric and prediction outputs for the reported final runs.
- `results/expected/`, `results/tables/`, and `results/figures/`: expected metrics, derived tables, and selected final figures.

Excluded:

- raw device logs
- local cache folders
- failed experiment dumps
- private notes
- machine-specific tracking-service or workspace paths

The 2-link dataset is synthetic-label data. Its coordinate-frame registration is documented in `data/processed/clean_dataset_2link_v1/manifest.json` and should not be described as physical robot-base calibration.
