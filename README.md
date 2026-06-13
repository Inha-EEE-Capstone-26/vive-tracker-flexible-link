# Vive Tracker Flexible Link

This repository contains the public reproduction package for a Vive Tracker-based position-prediction study on TPU flexible-link manipulators.

It is meant to be read alongside the paper and poster, with the main figures, result tables, sample data, fitted inference artifacts, and verification scripts kept in one lightweight public package.

[Paper PDF](paper/paper.pdf) | [Poster PDF](paper/poster.pdf) | [Model artifacts](models/README.md) | [Claim boundary](docs/claim_boundary.md) | [Data availability](DATA_AVAILABILITY.md)

## At A Glance

| System | Final model | Mean 3D error | Median | P95 | Pass@2mm |
|---|---|---:|---:|---:|---:|
| 1-link | Density-aware local Kernel Ridge Regression | 2.0135 mm | 1.5656 mm | 5.0003 mm | 62.68% |
| 2-link | Density-aware local Kernel Ridge Regression | 0.7101 mm | 0.5193 mm | 1.8215 mm | 96.00% |

`pass@2mm` is a settled-position prediction metric, not closed-loop control success. The optimizer result included here is a linkage smoke check, not a final robot-control benchmark.

## Main Evidence

![2-link model comparison summary](results/figures/2link_model_comparison_summary.png)

The final 2-link result is based on a density-aware local Kernel Ridge Regression model. The comparison above shows the reported model against the baseline candidates used in the paper.

The dataset also depends on a coordinate-frame alignment step before the learned model is evaluated:

![2-link alignment residual](results/figures/2link_alignment_residual.png)

This residual check supports the 2-link synthetic-label coordinate registration. It is evidence for the data-preparation pipeline, not a robot-base calibration claim.

## Figure Provenance

| Figure | Source data | Related claim | Expected output |
|---|---|---|---|
| 1-link contact sheet | `data/processed_manifest/manifest_1link_v1000.json`, `results/tables/paper_main_baseline_to_final_table.csv` | 1-link random-split settled-position prediction | `results/figures/1link_paper_figure_contact_sheet.png` |
| 2-link contact sheet | `data/processed_manifest/manifest_2link_v1.json`, `results/tables/2link_baseline20_to_density_aware50_summary.csv` | 2-link random-split settled-position prediction with synthetic labels | `results/figures/2link_paper_figure_contact_sheet.png` |
| Alignment residual | `data/processed_manifest/manifest_2link_v1.json` | Coordinate-frame registration evidence, not robot-base calibration | `results/figures/2link_alignment_residual.png` |
| Model comparison | `results/tables/2link_baseline20_to_density_aware50_summary.csv`, `results/expected/expected_metrics.json` | Density-aware local KRR as the final 2-link model family | `results/figures/2link_model_comparison_summary.png` |

The contact sheets used while assembling the paper are still included for traceability:

- [1-link paper figure contact sheet](results/figures/1link_paper_figure_contact_sheet.png)
- [2-link paper figure contact sheet](results/figures/2link_paper_figure_contact_sheet.png)

Full figure and table provenance is tracked in [docs/figures_and_tables.md](docs/figures_and_tables.md).

## Model Artifacts

Fitted `.joblib` artifacts are included in [models/](models/README.md) for sample-row inference smoke checks.

These are full-train inference artifact exports. They are not the original 50-seed evaluation objects used to produce the reported metrics. The reported numbers above remain tied to the repeated random-split evaluation outputs and expected-result tables.

## Verify The Package

```bash
python scripts/verify_package.py
python -m unittest discover -s tests
```

With GNU Make:

```bash
make smoke
make test
```

On Windows environments where GNU Make is installed as `mingw32-make`, use the same targets with `mingw32-make`.

## Data Availability

This is a public-safe artifact package. It does not include raw experiment logs or full row-level datasets.

Included:

- sample rows for smoke checks
- feature and label schemas
- processed-data manifests
- checksums
- expected metric tables
- selected paper figures
- fitted inference artifacts

See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md), [data/README.md](data/README.md), and [docs/data_card.md](docs/data_card.md).

## Repository Layout

```text
paper/                   Paper and poster PDFs using stable English aliases.
data/sample/             Small public-safe samples for smoke checks.
data/processed_manifest/ Feature, label, and dataset manifest files.
data/schema/             Column dictionary and coordinate-frame notes.
models/                  Fitted full-train inference artifacts and manifest.
results/expected/        Expected metrics used by verification scripts.
results/tables/          Derived result tables used by README and paper checks.
results/figures/         Selected final figures and contact sheets.
scripts/                 Single public verification entrypoint.
tests/                   Artifact and claim-boundary tests.
docs/                    Paper summary, data/model cards, provenance, and claim boundary.
```

## Citation

Use [CITATION.cff](CITATION.cff) as the machine-readable citation stub. Update author and venue fields before public release.

## License

Code is licensed under MIT. Documentation and figures are licensed under CC BY 4.0 unless noted otherwise. Dataset samples and derived artifacts are governed by [DATA_LICENSE](DATA_LICENSE).
