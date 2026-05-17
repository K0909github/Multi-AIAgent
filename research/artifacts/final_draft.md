# Draft Paper

## Abstract
To learn the brain activities within and among different functional areas of the brain, we propose local-global-graph network (LGGNet), a novel neurologically inspired graph neural network (GNN), to learn local-globalgraph (LGG) representations of electroencephalography (EEG) for brain–computer interface (BCI). The input layer of LGGNet comprises a series of temporal convolutions with multiscale 1-D convolutional kernels and kernel-level attentive fusion. Under the robust nested crossvalidation settings, the proposed method is evaluated on three publicly available datasets for four types of cognitive classiﬁcation tasks, namely the attention, fati gue, emotion, and preference classiﬁcation tasks.

## Introduction
To learn the brain activities within and among different functional areas of the brain, we propose local-global-graph network (LGGNet), a novel neurologically inspired graph neural network (GNN), to learn local-globalgraph (LGG) representations of electroencephalography (EEG) for brain–computer interface (BCI).

## Method
The input layer of LGGNet comprises a series of temporal convolutions with multiscale 1-D convolutional kernels and kernel-level attentive fusion. Under the robust nested crossvalidation settings, the proposed method is evaluated on three publicly available datasets for four types of cognitive classiﬁcation tasks, namely the attention, fati gue, emotion, and preference classiﬁcation tasks.

## Hypotheses

- Hypothesis 1: strengthen local feature aggregation before global graph fusion to improve robustness.
- Hypothesis 2: add an ablation-controlled regularization term to stabilize cross-subject generalization.
- Hypothesis 3: test an alternative readout head or attention aggregator to capture subject-specific variance.
- Each hypothesis should be checked against baseline metrics and ablations.

## Experiments
- Baseline: reproduce the original paper configuration.
- Experiment A: change local-global fusion and compare accuracy/F1/kappa.
- Experiment B: add regularization and monitor stability across seeds.
- Experiment C: swap readout head and compare per-subject performance.
- Log: seed, split, metrics, training curves, confusion matrix, ablation table.
- Failure criteria: no statistically meaningful gain over baseline or unstable across seeds.

## Results
The results show that LGGNet outperforms these methods, and the improvements are statistically signiﬁcant ( p < 0.05) in most cases.

## Discussion
- The workflow now keeps the paper summary, hypotheses, experiment plan, and results in separate machine-readable artifacts.
- The generated scaffold is still synthetic, so paper-level claims should be verified before reuse.

## Limitations
- The local nodes inside each functional area are fully connected, so finer-grained relations within a region may be under-modeled.
- The paper also notes that stronger relations for attention, emotion, and preference could be further improved with better network or loss design.

## Conclusion
- This draft is auto-generated from the paper PDF and can be refined in Copilot Chat.
