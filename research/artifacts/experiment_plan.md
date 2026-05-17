# Experiment Plan

- Baseline: reproduce the original paper configuration.
- Experiment A: change local-global fusion and compare accuracy/F1/kappa.
- Experiment B: add regularization and monitor stability across seeds.
- Experiment C: swap readout head and compare per-subject performance.
- Log: seed, split, metrics, training curves, confusion matrix, ablation table.
- Failure criteria: no statistically meaningful gain over baseline or unstable across seeds.
