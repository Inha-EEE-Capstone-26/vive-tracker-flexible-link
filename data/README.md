# Data

This directory includes full processed datasets for school-submission reproduction, plus small samples for lightweight smoke tests.

## Included

- `processed/`: full processed datasets, dataset-local manifests, session summaries, feature/label lists, and selected dataset plots.
- `source_processed/2link_synthetic/`: 2-link synthetic target-plan and supervised-sample CSVs used to build `clean_dataset_2link_v1`.
- `sample/`: five-row samples used by quick package and optimizer smoke checks.
- `processed_manifest/`: compatibility copies of final processed dataset manifests and column lists.
- `schema/`: data dictionary and coordinate-frame notes.
- `checksums/`: hashes for included source-derived artifacts.

## Excluded

- raw tracker logs
- raw session directories
- temporary experiment dumps
- local absolute paths

## Row Counts

| Dataset | Rows | Source groups |
|---|---:|---|
| `processed/clean_dataset_1link_v2/dataset.csv` | 881 | `test-260523-2`: 297, `test-260524-1`: 584 |
| `processed/clean_dataset_1link_v1000/dataset.csv` | 584 | `test-260524-1`: 584 |
| `processed/clean_dataset_2link_v1/dataset.csv` | 5,000 | `2link_test-260525-1`: 5,000 |
