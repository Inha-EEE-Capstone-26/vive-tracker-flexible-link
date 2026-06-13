# Model Card

## Final model family

Both final paper results use density-aware local Kernel Ridge Regression as the reported best-performing model family.

## Reported metrics

| System | Mean 3D error | Median 3D error | P95 3D error | Pass@2mm |
|---|---:|---:|---:|---:|
| 1-link | 2.0135 mm | 1.5656 mm | 5.0003 mm | 62.68% |
| 2-link | 0.7101 mm | 0.5193 mm | 1.8215 mm | 96.00% |

## Included fitted artifacts

The repository includes full-train inference artifact exports in `models/`.

- `models/1link_density_aware_local_krr_fulltrain.joblib`
- `models/2link_density_aware_local_krr_fulltrain.joblib`

These artifacts load the fitted forward-model behavior for sample-row prediction smoke checks. They are not the original 50-seed evaluation object; the reported metrics above remain tied to the repeated random-split evaluation outputs.

## Limitations

- These metrics are random-split prediction results.
- The included `.joblib` files are inference artifacts, not a full retraining pipeline.
- The optimizer smoke check is not a closed-loop control benchmark.
