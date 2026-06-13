# Data Card

## Scope

This repository provides a public-safe artifact subset for paper verification. It excludes raw logs and full row-level datasets.

## Included data

- `data/sample/sample_1link.csv`: header plus five public-safe sample rows from the 1-link clean dataset.
- `data/sample/sample_2link.csv`: header plus five public-safe sample rows from the 2-link clean dataset.
- `data/processed_manifest/`: source manifests and feature/label lists.
- `results/expected/expected_metrics.json`: expected paper-level metrics.
- `results/tables/`: derived result tables used by README and verification scripts.

## Excluded data

- raw tracker logs
- full `dataset.csv` files
- private/local paths
- cache folders and temporary experiment dumps
- failed or non-final experiment outputs

## Dataset notes

The 1-link package contains 584 clean rows after quality filtering. The 2-link package contains 5,000 synthetic-label clean rows and uses Kabsch registration into the target model frame.
